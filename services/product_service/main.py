from fastapi import FastAPI, HTTPException, Depends
from uuid import UUID
from typing import List

from models import Product, ProductCreate, ProductUpdate
from service import ProductService

app = FastAPI(title="Product Service")
product_service = ProductService()

# Start Kafka consumer when the app starts
@app.on_event("startup")
async def startup_event():
    product_service.start_consumer()

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Product Service!"}

@app.get("/products", response_model=List[Product], tags=["Products"])
async def get_products():
    return product_service.get_all_products()

@app.get("/products/{product_id}", response_model=Product, tags=["Products"])
async def get_product(product_id: UUID):
    product = product_service.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products", response_model=Product, status_code=201, tags=["Products"])
async def create_product(product_data: ProductCreate):
    product = product_service.create_product(product_data)
    return product

@app.put("/products/{product_id}", response_model=Product, tags=["Products"])
async def update_product(product_id: UUID, product_data: ProductUpdate):
    product = product_service.update_product(product_id, product_data)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.delete("/products/{product_id}", status_code=204, tags=["Products"])
async def delete_product(product_id: UUID):
    success = product_service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return None 