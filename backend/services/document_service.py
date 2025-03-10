"""
Service for working with MongoDB documents.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from backend.models.document import DocumentCreate, DocumentUpdate, Document, AgentTaskDocument

class DocumentService:
    """Service for managing documents in MongoDB."""
    
    def __init__(self, db: Database):
        """Initialize with a MongoDB database connection."""
        self.db = db
        self.collection = db.documents
    
    async def create_document(self, document: DocumentCreate) -> Document:
        """Create a new document."""
        document_dict = document.dict()
        document_dict["created_at"] = datetime.utcnow()
        document_dict["updated_at"] = datetime.utcnow()
        
        result: InsertOneResult = await self.collection.insert_one(document_dict)
        
        return await self.get_document(result.inserted_id)
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        if not ObjectId.is_valid(document_id):
            return None
            
        document = await self.collection.find_one({"_id": ObjectId(document_id)})
        if document:
            return Document(**document)
        return None
    
    async def update_document(self, document_id: str, document_update: DocumentUpdate) -> Optional[Document]:
        """Update an existing document."""
        if not ObjectId.is_valid(document_id):
            return None
            
        update_data = document_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            
            await self.collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_data}
            )
            
        return await self.get_document(document_id)
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document by ID."""
        if not ObjectId.is_valid(document_id):
            return False
            
        result: DeleteResult = await self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0
    
    async def list_documents(
        self, 
        document_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """List documents with optional filtering."""
        query = {}
        
        if document_type:
            query["document_type"] = document_type
            
        if tags:
            query["tags"] = {"$all": tags}
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        documents = await cursor.to_list(length=limit)
        
        return [Document(**doc) for doc in documents]
    
    async def search_documents(self, text: str) -> List[Document]:
        """Search for documents by text."""
        cursor = self.collection.find(
            {"$text": {"$search": text}}
        ).sort([("score", {"$meta": "textScore"})])
        
        documents = await cursor.to_list(length=100)
        return [Document(**doc) for doc in documents]

class AgentTaskDocumentService:
    """Service for managing agent task documents in MongoDB."""
    
    def __init__(self, db: Database):
        """Initialize with a MongoDB database connection."""
        self.db = db
        self.collection = db.agent_tasks
    
    async def create_task(self, task: Dict[str, Any]) -> str:
        """Create a new agent task document."""
        task["created_at"] = datetime.utcnow()
        task["updated_at"] = datetime.utcnow()
        
        result: InsertOneResult = await self.collection.insert_one(task)
        return str(result.inserted_id)
    
    async def update_task_status(self, task_id: str, status: str, response: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> bool:
        """Update the status of an agent task."""
        if not ObjectId.is_valid(task_id):
            return False
            
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if response:
            update_data["response"] = response
            
        if error:
            update_data["error"] = error
            
        result: UpdateResult = await self.collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get an agent task document by ID."""
        if not ObjectId.is_valid(task_id):
            return None
            
        task = await self.collection.find_one({"_id": ObjectId(task_id)})
        return task
    
    async def list_agent_tasks(self, agent_name: Optional[str] = None, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List agent task documents with optional filtering."""
        query = {}
        
        if agent_name:
            query["agent_name"] = agent_name
            
        if status:
            query["status"] = status
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        tasks = await cursor.to_list(length=limit)
        
        return tasks 