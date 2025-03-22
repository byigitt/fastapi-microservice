from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: float
    
    @property
    def total_price(self) -> float:
        return self.quantity * self.unit_price

class OrderBase(BaseModel):
    customer_id: UUID
    items: List[OrderItem]
    
    @property
    def total_amount(self) -> float:
        return sum(item.total_price for item in self.items)

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: UUID = Field(default_factory=uuid4)
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    items: Optional[List[OrderItem]] = None

class OrderEvent(BaseModel):
    event_type: str  # "created", "updated", "cancelled"
    order_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Order 