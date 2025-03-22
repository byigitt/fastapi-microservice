import sys
import os
import json
from typing import Dict, List, Optional
from uuid import UUID
import threading

# Add infrastructure directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from infrastructure.kafka_client import KafkaClient
from models import Product, ProductCreate, ProductUpdate, ProductEvent

class ProductService:
    def __init__(self):
        self.products: Dict[UUID, Product] = {}
        self.kafka_client = KafkaClient()
        self.consumer_thread = None
        
    def start_consumer(self):
        """Start Kafka consumer in a separate thread"""
        if self.consumer_thread is None or not self.consumer_thread.is_alive():
            self.consumer_thread = threading.Thread(
                target=self._consume_product_events,
                daemon=True
            )
            self.consumer_thread.start()
    
    def _consume_product_events(self):
        """Consume product events from Kafka"""
        consumer = self.kafka_client.create_consumer(
            group_id='product-service-group',
            topics=['product_events']
        )
        
        def handle_message(key, value):
            if key == 'product':
                try:
                    event = ProductEvent(**value)
                    print(f"Received product event: {event.event_type} for product {event.product_id}")
                except Exception as e:
                    print(f"Failed to process product event: {e}")
        
        self.kafka_client.consume_messages(consumer, handle_message)
    
    def _publish_product_event(self, event_type: str, product: Product):
        """Publish product event to Kafka"""
        event = ProductEvent(
            event_type=event_type,
            product_id=product.id,
            data=product
        )
        
        self.kafka_client.publish_message(
            topic='product_events',
            key='product',
            value=event.dict()
        )
    
    def get_all_products(self) -> List[Product]:
        """Get all products"""
        return list(self.products.values())
    
    def get_product(self, product_id: UUID) -> Optional[Product]:
        """Get a product by ID"""
        return self.products.get(product_id)
    
    def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        product = Product(**product_data.dict())
        self.products[product.id] = product
        
        # Publish product created event
        self._publish_product_event("created", product)
        
        return product
    
    def update_product(self, product_id: UUID, product_data: ProductUpdate) -> Optional[Product]:
        """Update an existing product"""
        if product_id not in self.products:
            return None
        
        # Get current product data
        stored_product = self.products[product_id]
        
        # Update fields if provided
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(stored_product, field, value)
        
        # Update the updated_at field
        from datetime import datetime
        stored_product.updated_at = datetime.now()
        
        # Publish product updated event
        self._publish_product_event("updated", stored_product)
        
        return stored_product
    
    def delete_product(self, product_id: UUID) -> bool:
        """Delete a product"""
        if product_id not in self.products:
            return False
        
        product = self.products[product_id]
        del self.products[product_id]
        
        # Publish product deleted event
        self._publish_product_event("deleted", product)
        
        return True 