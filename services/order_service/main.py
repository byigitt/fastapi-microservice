from fastapi import FastAPI, HTTPException, Depends
from uuid import UUID
from typing import List

from models import Order, OrderCreate, OrderUpdate
from service import OrderService

app = FastAPI(title="Order Service")
order_service = OrderService()

# Start Kafka consumer when the app starts
@app.on_event("startup")
async def startup_event():
    order_service.start_consumer()

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Order Service!"}

@app.get("/orders", response_model=List[Order], tags=["Orders"])
async def get_orders():
    return order_service.get_all_orders()

@app.get("/orders/{order_id}", response_model=Order, tags=["Orders"])
async def get_order(order_id: UUID):
    order = order_service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/customers/{customer_id}/orders", response_model=List[Order], tags=["Orders"])
async def get_customer_orders(customer_id: UUID):
    return order_service.get_customer_orders(customer_id)

@app.post("/orders", response_model=Order, status_code=201, tags=["Orders"])
async def create_order(order_data: OrderCreate):
    order = order_service.create_order(order_data)
    return order

@app.put("/orders/{order_id}", response_model=Order, tags=["Orders"])
async def update_order(order_id: UUID, order_data: OrderUpdate):
    order = order_service.update_order(order_id, order_data)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders/{order_id}/cancel", response_model=Order, tags=["Orders"])
async def cancel_order(order_id: UUID):
    order = order_service.cancel_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found or not in a cancelable state")
    return order 