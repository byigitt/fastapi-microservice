from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4

class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    HOME = "home"
    TOYS = "toys"

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    category: ProductCategory
    in_stock: bool = True
    stock_quantity: int = 0

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[ProductCategory] = None
    in_stock: Optional[bool] = None
    stock_quantity: Optional[int] = None

class ProductEvent(BaseModel):
    event_type: str  # "created", "updated", "deleted"
    product_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Product 