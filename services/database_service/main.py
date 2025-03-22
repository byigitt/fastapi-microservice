from fastapi import FastAPI, HTTPException
from uuid import UUID
from typing import List, Dict, Any

from service import DatabaseService

app = FastAPI(title="Database Service")
db_service = DatabaseService()

# Start Kafka consumer when the app starts
@app.on_event("startup")
async def startup_event():
    db_service.start_consumer()

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Database Service!"}

@app.get("/collections", response_model=List[str], tags=["Database"])
async def get_collections():
    return db_service.get_all_collections()

@app.get("/collections/{collection}", response_model=List[Dict[str, Any]], tags=["Database"])
async def get_collection_data(collection: str):
    return db_service.get_collection(collection)

@app.get("/collections/{collection}/{record_id}", response_model=Dict[str, Any], tags=["Database"])
async def get_record(collection: str, record_id: UUID):
    record = db_service.get_record(collection, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Record not found in collection {collection}")
    return record 