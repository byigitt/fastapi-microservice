import sys
import os
import json
from typing import Dict, List, Optional
from uuid import UUID
import threading

# Add infrastructure directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from infrastructure.kafka_client import KafkaClient
from models import Order, OrderCreate, OrderUpdate, OrderEvent, OrderStatus

class OrderService:
    def __init__(self):
        self.orders: Dict[UUID, Order] = {}
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
            group_id='order-service-group',
            topics=['order_events', 'product_events']
        )
        
        def handle_message(key, value):
            if key == 'order':
                try:
                    event = OrderEvent(**value)
                    print(f"Received order event: {event.event_type} for order {event.order_id}")
                except Exception as e:
                    print(f"Failed to process order event: {e}")
            elif key == 'product':
                try:
                    # Handle product events that might affect orders
                    print(f"Received product event: {value.get('event_type')}")
                    # For example, if a product is deleted, you might want to notify customers
                    # with pending orders containing this product
                except Exception as e:
                    print(f"Failed to process product event: {e}")
        
        self.kafka_client.consume_messages(consumer, handle_message)
    
    def _publish_order_event(self, event_type: str, order: Order):
        """Publish order event to Kafka"""
        event = OrderEvent(
            event_type=event_type,
            order_id=order.id,
            data=order
        )
        
        self.kafka_client.publish_message(
            topic='order_events',
            key='order',
            value=event.dict()
        )
    
    def get_all_orders(self) -> List[Order]:
        """Get all orders"""
        return list(self.orders.values())
    
    def get_order(self, order_id: UUID) -> Optional[Order]:
        """Get an order by ID"""
        return self.orders.get(order_id)

    def get_customer_orders(self, customer_id: UUID) -> List[Order]:
        """Get all orders for a specific customer"""
        return [order for order in self.orders.values() if order.customer_id == customer_id]
    
    def create_order(self, order_data: OrderCreate) -> Order:
        """Create a new order"""
        order = Order(**order_data.dict())
        self.orders[order.id] = order
        
        # Publish order created event
        self._publish_order_event("created", order)
        
        return order
    
    def update_order(self, order_id: UUID, order_data: OrderUpdate) -> Optional[Order]:
        """Update an existing order"""
        if order_id not in self.orders:
            return None
        
        # Get current order data
        stored_order = self.orders[order_id]
        
        # Update fields if provided
        update_data = order_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(stored_order, field, value)
        
        # Update the updated_at field
        from datetime import datetime
        stored_order.updated_at = datetime.now()
        
        # Publish order updated event
        self._publish_order_event("updated", stored_order)
        
        return stored_order
    
    def cancel_order(self, order_id: UUID) -> Optional[Order]:
        """Cancel an order"""
        if order_id not in self.orders:
            return None
        
        order = self.orders[order_id]
        
        # Only pending orders can be cancelled
        if order.status != OrderStatus.PENDING:
            return None
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        
        # Publish order cancelled event
        self._publish_order_event("cancelled", order)
        
        return order 