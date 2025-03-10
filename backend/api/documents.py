"""
API routes for working with MongoDB documents.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pymongo.database import Database

from backend.db.mongodb import get_mongodb
from backend.models.document import DocumentCreate, DocumentUpdate, Document
from backend.services.document_service import DocumentService

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Document, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    db: Database = Depends(get_mongodb)
):
    """
    Create a new document.
    """
    document_service = DocumentService(db)
    return await document_service.create_document(document)

@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    db: Database = Depends(get_mongodb)
):
    """
    Get a document by ID.
    """
    document_service = DocumentService(db)
    document = await document_service.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return document

@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    db: Database = Depends(get_mongodb)
):
    """
    Update a document.
    """
    document_service = DocumentService(db)
    document = await document_service.update_document(document_id, document_update)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: Database = Depends(get_mongodb)
):
    """
    Delete a document.
    """
    document_service = DocumentService(db)
    success = await document_service.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return None

@router.get("/", response_model=List[Document])
async def list_documents(
    document_type: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Database = Depends(get_mongodb)
):
    """
    List documents with optional filtering.
    """
    document_service = DocumentService(db)
    return await document_service.list_documents(document_type, tags, skip, limit)

@router.get("/search/", response_model=List[Document])
async def search_documents(
    q: str,
    db: Database = Depends(get_mongodb)
):
    """
    Search for documents by text.
    """
    document_service = DocumentService(db)
    return await document_service.search_documents(q) 