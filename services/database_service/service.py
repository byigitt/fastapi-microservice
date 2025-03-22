import sys
import os
import json
from typing import Dict, List, Optional, Any
from uuid import UUID
import threading
from datetime import datetime
from collections import defaultdict

# Add infrastructure directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from infrastructure.kafka_client import KafkaClient
from models import DatabaseRecord, DatabaseEvent

class DatabaseService:
    def __init__(self):
        # In-memory database: collection -> {id -> record}
        self.db: Dict[str, Dict[UUID, DatabaseRecord]] = defaultdict(dict)
        self.kafka_client = KafkaClient()
        self.consumer_thread = None
        
    def start_consumer(self):
        """Start Kafka consumer in a separate thread"""
        if self.consumer_thread is None or not self.consumer_thread.is_alive():
            self.consumer_thread = threading.Thread(
                target=self._consume_events,
                daemon=True
            )
            self.consumer_thread.start()
    
    def _consume_events(self):
        """Consume events from Kafka"""
        consumer = self.kafka_client.create_consumer(
            group_id='database-service-group',
            topics=['product_events', 'order_events']
        )
        
        def handle_message(key, value):
            try:
                event_type = value.get('event_type')
                
                if key == 'product':
                    collection = 'products'
                    product_data = value.get('data', {})
                    record_id = UUID(product_data.get('id'))
                    self._store_record(collection, record_id, product_data, event_type)
                    
                elif key == 'order':
                    collection = 'orders'
                    order_data = value.get('data', {})
                    record_id = UUID(order_data.get('id'))
                    self._store_record(collection, record_id, order_data, event_type)
                    
                print(f"Processed {key} event: {event_type}")
            except Exception as e:
                print(f"Failed to process event: {e}")
        
        self.kafka_client.consume_messages(consumer, handle_message)
    
    def _store_record(self, collection: str, record_id: UUID, data: Dict[str, Any], event_type: str):
        """Store or update a record based on the event type"""
        if event_type == "deleted":
            if record_id in self.db[collection]:
                del self.db[collection][record_id]
        else:  # created or updated
            if event_type == "created" or record_id not in self.db[collection]:
                # New record
                record = DatabaseRecord(
                    id=record_id,
                    collection=collection,
                    data=data
                )
                self.db[collection][record_id] = record
            else:
                # Update existing record
                self.db[collection][record_id].data = data
                self.db[collection][record_id].updated_at = datetime.now()
        
        # Publish database event
        self._publish_db_event(event_type, collection, record_id, data)
    
    def _publish_db_event(self, event_type: str, collection: str, record_id: UUID, data: Dict[str, Any]):
        """Publish database event to Kafka"""
        event = DatabaseEvent(
            event_type=event_type,
            collection=collection,
            record_id=record_id,
            data=data
        )
        
        self.kafka_client.publish_message(
            topic='database_events',
            key=collection,
            value=event.dict()
        )
    
    def get_all_collections(self) -> List[str]:
        """Get all collection names"""
        return list(self.db.keys())
    
    def get_collection(self, collection: str) -> List[Dict[str, Any]]:
        """Get all records from a collection"""
        return [record.data for record in self.db.get(collection, {}).values()]
    
    def get_record(self, collection: str, record_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a specific record from a collection"""
        record = self.db.get(collection, {}).get(record_id)
        return record.data if record else None 