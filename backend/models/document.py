"""
MongoDB document models for storing unstructured or semi-structured data.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field

class PyObjectId(ObjectId):
    """Custom type for handling MongoDB ObjectId fields in Pydantic models."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class DocumentBase(BaseModel):
    """Base model for MongoDB documents."""
    title: str
    document_type: str
    content: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""
    pass

class DocumentUpdate(BaseModel):
    """Schema for updating an existing document."""
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class DocumentInDB(DocumentBase):
    """Schema for a document as stored in the database."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }

class Document(DocumentInDB):
    """Schema for document responses."""
    pass

class AgentTaskDocument(DocumentBase):
    """Schema for storing agent task information."""
    agent_type: str
    agent_name: str
    status: str = "pending"  # pending, in_progress, completed, failed
    task_id: str
    request: Dict[str, Any]
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        } 