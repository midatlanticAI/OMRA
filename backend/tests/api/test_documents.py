"""
Tests for the document API endpoints.
"""
import pytest
from httpx import AsyncClient
from bson import ObjectId

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def test_document(test_mongodb):
    """Create a test document in MongoDB."""
    document_data = {
        "title": "Test Document",
        "document_type": "note",
        "content": {"text": "This is a test document"},
        "metadata": {"creator": "test_user"},
        "tags": ["test", "document"]
    }
    
    result = await test_mongodb.documents.insert_one(document_data)
    document_data["_id"] = result.inserted_id
    
    yield document_data
    
    # Cleanup
    await test_mongodb.documents.delete_one({"_id": result.inserted_id})

async def test_create_document(client: AsyncClient):
    """Test creating a document."""
    document_data = {
        "title": "New Document",
        "document_type": "note",
        "content": {"text": "This is a new document"},
        "metadata": {"creator": "test_user"},
        "tags": ["new", "document"]
    }
    
    response = await client.post("/api/documents/", json=document_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == document_data["title"]
    assert data["document_type"] == document_data["document_type"]
    assert data["content"] == document_data["content"]
    assert data["metadata"] == document_data["metadata"]
    assert data["tags"] == document_data["tags"]
    assert "_id" in data

async def test_get_document(client: AsyncClient, test_document):
    """Test retrieving a document by ID."""
    document_id = str(test_document["_id"])
    
    response = await client.get(f"/api/documents/{document_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_document["title"]
    assert data["document_type"] == test_document["document_type"]
    assert data["content"] == test_document["content"]
    assert data["metadata"] == test_document["metadata"]
    assert data["tags"] == test_document["tags"]

async def test_get_document_not_found(client: AsyncClient):
    """Test retrieving a document that doesn't exist."""
    fake_id = str(ObjectId())
    
    response = await client.get(f"/api/documents/{fake_id}")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

async def test_update_document(client: AsyncClient, test_document):
    """Test updating a document."""
    document_id = str(test_document["_id"])
    update_data = {
        "title": "Updated Document",
        "tags": ["updated", "document"]
    }
    
    response = await client.put(f"/api/documents/{document_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["tags"] == update_data["tags"]
    # Fields not in update_data should remain unchanged
    assert data["document_type"] == test_document["document_type"]
    assert data["content"] == test_document["content"]

async def test_delete_document(client: AsyncClient, test_mongodb):
    """Test deleting a document."""
    # Create a document to delete
    document_data = {
        "title": "Document to Delete",
        "document_type": "note",
        "content": {"text": "This document will be deleted"},
        "metadata": {"creator": "test_user"},
        "tags": ["delete"]
    }
    
    result = await test_mongodb.documents.insert_one(document_data)
    document_id = str(result.inserted_id)
    
    # Delete the document
    response = await client.delete(f"/api/documents/{document_id}")
    
    assert response.status_code == 204
    
    # Verify document is deleted
    assert await test_mongodb.documents.find_one({"_id": result.inserted_id}) is None

async def test_list_documents(client: AsyncClient, test_document):
    """Test listing documents."""
    response = await client.get("/api/documents/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # Create a second document with a different type
    document_data = {
        "title": "Second Document",
        "document_type": "report",
        "content": {"text": "This is another document"},
        "metadata": {"creator": "test_user"},
        "tags": ["report"]
    }
    
    await client.post("/api/documents/", json=document_data)
    
    # Test filtering by document_type
    response = await client.get("/api/documents/?document_type=report")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(doc["document_type"] == "report" for doc in data)
    
    # Test filtering by tags
    response = await client.get("/api/documents/?tags=report")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all("report" in doc["tags"] for doc in data) 