from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

# We're keeping a simple in-memory database service for educational purposes
# In a real application, you would use a proper database like PostgreSQL, MongoDB, etc.

class DatabaseRecord(BaseModel):
    id: UUID
    collection: str
    data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
class DatabaseEvent(BaseModel):
    event_type: str  # "created", "updated", "deleted"
    collection: str
    record_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] 