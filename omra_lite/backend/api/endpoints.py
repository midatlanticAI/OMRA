"""
API Endpoints for OMRA Lite

This module defines the API routes for the application.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Request, Body
from bson import ObjectId
from bson.errors import InvalidId

from models import (
    User, Customer, CustomerCreate, CustomerUpdate,
    ServiceRequest, ServiceRequestCreate, ServiceRequestUpdate,
    Technician, TechnicianCreate, TechnicianUpdate,
    Agent, AgentCreate, AgentUpdate,
    Conversation, Message, ApiKeySetting, ApiKeyCreate,
    Smartlist, SmartlistCreate, SmartlistUpdate, SmartlistType,
    KnowledgeSource, KnowledgeSourceCreate, KnowledgeSourceUpdate,
    AgentTemplate, AgentTemplateCreate, AgentTemplateUpdate,
    AgentStatus, AgentType, RagConfig, FineTuningConfig
)
from agent_system import agent_manager
from db import get_database
from auth import get_current_active_user
from fastapi.responses import JSONResponse
import httpx

# Configure logging
logger = logging.getLogger("omra_lite.api")

# Create API router
api_router = APIRouter()

# Helper function to convert MongoDB ObjectId to string
def convert_objectid(data):
    """Convert ObjectId to string in a dictionary."""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, dict):
                convert_objectid(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        convert_objectid(item)
    return data

# API Key Management endpoints
@api_router.post("/settings/api-keys", response_model=ApiKeySetting)
async def create_api_key(
    api_key: ApiKeyCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create or update an API key."""
    # Only admins can manage API keys
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage API keys"
        )
    
    db = await get_database()
    
    # Check if key already exists
    existing_key = await db.api_keys.find_one({"key_name": api_key.key_name})
    
    if existing_key:
        # Update existing key
        update_data = {
            "key_value": api_key.key_value,
            "updated_at": datetime.utcnow()
        }
        
        await db.api_keys.update_one(
            {"_id": existing_key["_id"]},
            {"$set": update_data}
        )
        
        updated_key = await db.api_keys.find_one({"_id": existing_key["_id"]})
        updated_key = convert_objectid(updated_key)
        
        return updated_key
    else:
        # Create new key
        api_key_dict = api_key.dict()
        api_key_dict["created_at"] = datetime.utcnow()
        api_key_dict["updated_at"] = datetime.utcnow()
        api_key_dict["is_encrypted"] = False
        
        result = await db.api_keys.insert_one(api_key_dict)
        
        created_key = await db.api_keys.find_one({"_id": result.inserted_id})
        created_key = convert_objectid(created_key)
        
        return created_key

@api_router.get("/settings/api-keys", response_model=List[ApiKeySetting])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user)
):
    """List all API keys."""
    # Only admins can view API keys
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view API keys"
        )
    
    db = await get_database()
    
    cursor = db.api_keys.find()
    api_keys = []
    
    async for key in cursor:
        key = convert_objectid(key)
        # In a real app, you might want to mask the actual key value for security
        # key["key_value"] = "••••••••" + key["key_value"][-4:] if key["key_value"] else ""
        api_keys.append(key)
    
    return api_keys

@api_router.delete("/settings/api-keys/{key_name}")
async def delete_api_key(
    key_name: str = Path(..., title="The name of the API key to delete"),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an API key."""
    # Only admins can delete API keys
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete API keys"
        )
    
    db = await get_database()
    
    # Check if key exists
    existing_key = await db.api_keys.find_one({"key_name": key_name})
    
    if not existing_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key not found: {key_name}"
        )
    
    # Delete the key
    await db.api_keys.delete_one({"key_name": key_name})
    
    return {"message": f"API key deleted: {key_name}"}

# Customer endpoints
@api_router.post("/customers", response_model=Customer)
async def create_customer(
    customer: CustomerCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new customer."""
    db = await get_database()
    
    # Check if customer already exists with this email
    if customer.contact_info.email:
        existing = await db.customers.find_one({"contact_info.email": customer.contact_info.email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer already exists with email: {customer.contact_info.email}"
            )
    
    # Create the customer
    customer_dict = customer.dict()
    customer_dict["created_at"] = datetime.utcnow()
    customer_dict["updated_at"] = datetime.utcnow()
    
    result = await db.customers.insert_one(customer_dict)
    
    created_customer = await db.customers.find_one({"_id": result.inserted_id})
    created_customer = convert_objectid(created_customer)
    
    return created_customer

@api_router.get("/customers", response_model=List[Customer])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """List all customers."""
    db = await get_database()
    
    cursor = db.customers.find().skip(skip).limit(limit).sort("created_at", -1)
    customers = []
    
    async for customer in cursor:
        customer = convert_objectid(customer)
        customers.append(customer)
    
    return customers

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: str = Path(..., title="The ID of the customer to get"),
    current_user: User = Depends(get_current_active_user)
):
    """Get a customer by ID."""
    db = await get_database()
    
    customer = await db.customers.find_one({"_id": ObjectId(customer_id)})
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer not found with ID: {customer_id}"
        )
    
    customer = convert_objectid(customer)
    
    return customer

@api_router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(
    customer_update: CustomerUpdate,
    customer_id: str = Path(..., title="The ID of the customer to update"),
    current_user: User = Depends(get_current_active_user)
):
    """Update a customer."""
    db = await get_database()
    
    # Check if customer exists
    customer = await db.customers.find_one({"_id": ObjectId(customer_id)})
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer not found with ID: {customer_id}"
        )
    
    # Prepare update data
    update_data = {}
    
    for field, value in customer_update.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Update the customer
    await db.customers.update_one(
        {"_id": ObjectId(customer_id)},
        {"$set": update_data}
    )
    
    # Get the updated customer
    updated_customer = await db.customers.find_one({"_id": ObjectId(customer_id)})
    updated_customer = convert_objectid(updated_customer)
    
    return updated_customer

@api_router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: str = Path(..., title="The ID of the customer to delete"),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a customer."""
    db = await get_database()
    
    # Check if customer exists
    customer = await db.customers.find_one({"_id": ObjectId(customer_id)})
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer not found with ID: {customer_id}"
        )
    
    # Delete the customer
    await db.customers.delete_one({"_id": ObjectId(customer_id)})
    
    return {"message": f"Customer deleted: {customer_id}"}

# Bulk operations for customers
@api_router.post("/customers/bulk-delete", response_model=Dict[str, Any])
async def bulk_delete_customers(
    ids: List[str],
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete multiple customers at once.
    
    Args:
        ids: List of customer IDs to delete
        current_user: Current authenticated user
        
    Returns:
        Dict with deleted_count indicating how many customers were deleted
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db = get_database()
    result = await db.customers.delete_many({"_id": {"$in": [ObjectId(id) for id in ids]}})
    
    return {"deleted_count": result.deleted_count, "message": f"Successfully deleted {result.deleted_count} customers"}

@api_router.post("/customers/bulk-update", response_model=Dict[str, Any])
async def bulk_update_customers(
    updates: Dict[str, Any],
    ids: List[str],
    current_user: User = Depends(get_current_active_user)
):
    """
    Update multiple customers at once.
    
    Args:
        updates: Dictionary of fields to update
        ids: List of customer IDs to update
        current_user: Current authenticated user
        
    Returns:
        Dict with modified_count indicating how many customers were updated
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Remove null or None values from the updates
    updates = {k: v for k, v in updates.items() if v is not None}
    
    if not updates:
        return {"modified_count": 0, "message": "No updates provided"}
    
    # Add updated_at timestamp
    updates["updated_at"] = datetime.utcnow()
    
    db = get_database()
    result = await db.customers.update_many(
        {"_id": {"$in": [ObjectId(id) for id in ids]}},
        {"$set": updates}
    )
    
    return {"modified_count": result.modified_count, "message": f"Successfully updated {result.modified_count} customers"}

@api_router.post("/customers/import", response_model=Dict[str, Any])
async def import_customers(
    customers: List[CustomerCreate],
    current_user: User = Depends(get_current_active_user)
):
    """
    Import multiple customers at once.
    
    Args:
        customers: List of customers to import
        current_user: Current authenticated user
        
    Returns:
        Dict with imported_count indicating how many customers were imported
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db = get_database()
    inserted_count = 0
    
    for customer in customers:
        # Convert the Pydantic model to dict
        customer_dict = customer.dict()
        
        # Add timestamps
        customer_dict["created_at"] = datetime.utcnow()
        customer_dict["updated_at"] = datetime.utcnow()
        
        # Insert the customer
        result = await db.customers.insert_one(customer_dict)
        
        if result.inserted_id:
            inserted_count += 1
    
    return {"imported_count": inserted_count, "message": f"Successfully imported {inserted_count} customers"}

@api_router.get("/customers/export", response_model=List[Customer])
async def export_customers(
    current_user: User = Depends(get_current_active_user)
):
    """
    Export all customers.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of all customers
    """
    db = get_database()
    customers = await db.customers.find().to_list(1000)
    
    # Convert ObjectId to string
    for customer in customers:
        convert_objectid(customer)
    
    return customers

# Service Request endpoints
@api_router.post("/service-requests", response_model=ServiceRequest)
async def create_service_request(
    service_request: ServiceRequestCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new service request."""
    db = await get_database()
    
    # Check if customer exists
    customer = await db.customers.find_one({"_id": ObjectId(service_request.customer_id)})
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer not found with ID: {service_request.customer_id}"
        )
    
    # Create the service request
    service_request_dict = service_request.dict()
    service_request_dict["status"] = "pending"
    service_request_dict["created_at"] = datetime.utcnow()
    service_request_dict["updated_at"] = datetime.utcnow()
    
    result = await db.service_requests.insert_one(service_request_dict)
    
    created_request = await db.service_requests.find_one({"_id": result.inserted_id})
    created_request = convert_objectid(created_request)
    
    return created_request

@api_router.get("/service-requests", response_model=List[ServiceRequest])
async def list_service_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, title="Filter by status"),
    customer_id: Optional[str] = Query(None, title="Filter by customer ID"),
    current_user: User = Depends(get_current_active_user)
):
    """List all service requests."""
    db = await get_database()
    
    # Build query
    query = {}
    
    if status:
        query["status"] = status
    
    if customer_id:
        query["customer_id"] = customer_id
    
    cursor = db.service_requests.find(query).skip(skip).limit(limit).sort("created_at", -1)
    requests = []
    
    async for request in cursor:
        request = convert_objectid(request)
        requests.append(request)
    
    return requests

@api_router.get("/service-requests/{request_id}", response_model=ServiceRequest)
async def get_service_request(
    request_id: str = Path(..., title="The ID of the service request to get"),
    current_user: User = Depends(get_current_active_user)
):
    """Get a service request by ID."""
    db = await get_database()
    
    request = await db.service_requests.find_one({"_id": ObjectId(request_id)})
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service request not found with ID: {request_id}"
        )
    
    request = convert_objectid(request)
    
    return request

@api_router.put("/service-requests/{request_id}", response_model=ServiceRequest)
async def update_service_request(
    request_update: ServiceRequestUpdate,
    request_id: str = Path(..., title="The ID of the service request to update"),
    current_user: User = Depends(get_current_active_user)
):
    """Update a service request."""
    db = await get_database()
    
    # Check if service request exists
    request = await db.service_requests.find_one({"_id": ObjectId(request_id)})
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service request not found with ID: {request_id}"
        )
    
    # Prepare update data
    update_data = {}
    
    for field, value in request_update.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Update the service request
    await db.service_requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": update_data}
    )
    
    # Get the updated service request
    updated_request = await db.service_requests.find_one({"_id": ObjectId(request_id)})
    updated_request = convert_objectid(updated_request)
    
    return updated_request

# Bulk operations for service requests
@api_router.post("/service-requests/bulk-delete", response_model=Dict[str, Any])
async def bulk_delete_service_requests(
    ids: List[str],
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete multiple service requests at once.
    
    Args:
        ids: List of service request IDs to delete
        current_user: Current authenticated user
        
    Returns:
        Dict with deleted_count indicating how many service requests were deleted
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db = get_database()
    result = await db.service_requests.delete_many({"_id": {"$in": [ObjectId(id) for id in ids]}})
    
    return {"deleted_count": result.deleted_count, "message": f"Successfully deleted {result.deleted_count} service requests"}

@api_router.post("/service-requests/bulk-update", response_model=Dict[str, Any])
async def bulk_update_service_requests(
    updates: Dict[str, Any],
    ids: List[str],
    current_user: User = Depends(get_current_active_user)
):
    """
    Update multiple service requests at once.
    
    Args:
        updates: Dictionary of fields to update
        ids: List of service request IDs to update
        current_user: Current authenticated user
        
    Returns:
        Dict with modified_count indicating how many service requests were updated
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Remove null or None values from the updates
    updates = {k: v for k, v in updates.items() if v is not None}
    
    if not updates:
        return {"modified_count": 0, "message": "No updates provided"}
    
    # Add updated_at timestamp
    updates["updated_at"] = datetime.utcnow()
    
    db = get_database()
    result = await db.service_requests.update_many(
        {"_id": {"$in": [ObjectId(id) for id in ids]}},
        {"$set": updates}
    )
    
    return {"modified_count": result.modified_count, "message": f"Successfully updated {result.modified_count} service requests"}

@api_router.post("/service-requests/import", response_model=Dict[str, Any])
async def import_service_requests(
    service_requests: List[ServiceRequestCreate],
    current_user: User = Depends(get_current_active_user)
):
    """
    Import multiple service requests at once.
    
    Args:
        service_requests: List of service requests to import
        current_user: Current authenticated user
        
    Returns:
        Dict with imported_count indicating how many service requests were imported
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db = get_database()
    inserted_count = 0
    
    for service_request in service_requests:
        # Convert the Pydantic model to dict
        service_request_dict = service_request.dict()
        
        # Add timestamps and default status
        service_request_dict["created_at"] = datetime.utcnow()
        service_request_dict["updated_at"] = datetime.utcnow()
        service_request_dict["status"] = service_request_dict.get("status", "pending")
        
        # Insert the service request
        result = await db.service_requests.insert_one(service_request_dict)
        
        if result.inserted_id:
            inserted_count += 1
    
    return {"imported_count": inserted_count, "message": f"Successfully imported {inserted_count} service requests"}

@api_router.get("/service-requests/export", response_model=List[ServiceRequest])
async def export_service_requests(
    current_user: User = Depends(get_current_active_user)
):
    """
    Export all service requests.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of all service requests
    """
    db = get_database()
    service_requests = await db.service_requests.find().to_list(1000)
    
    # Convert ObjectId to string
    for service_request in service_requests:
        convert_objectid(service_request)
    
    return service_requests

# Technician endpoints
@api_router.post("/technicians", response_model=Technician)
async def create_technician(
    technician: TechnicianCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new technician."""
    db = await get_database()
    
    # Check if technician already exists with this email
    existing = await db.technicians.find_one({"email": technician.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Technician already exists with email: {technician.email}"
        )
    
    # Create the technician
    technician_dict = technician.dict()
    technician_dict["created_at"] = datetime.utcnow()
    technician_dict["updated_at"] = datetime.utcnow()
    
    result = await db.technicians.insert_one(technician_dict)
    
    created_technician = await db.technicians.find_one({"_id": result.inserted_id})
    created_technician = convert_objectid(created_technician)
    
    return created_technician

@api_router.get("/technicians", response_model=List[Technician])
async def list_technicians(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active: Optional[bool] = Query(None, title="Filter by active status"),
    current_user: User = Depends(get_current_active_user)
):
    """List all technicians."""
    db = await get_database()
    
    # Build query
    query = {}
    
    if active is not None:
        query["active"] = active
    
    cursor = db.technicians.find(query).skip(skip).limit(limit).sort("created_at", -1)
    technicians = []
    
    async for tech in cursor:
        tech = convert_objectid(tech)
        technicians.append(tech)
    
    return technicians

# Agent endpoints
@api_router.post("/agents", response_model=Dict[str, Any])
async def create_agent(
    agent: AgentCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new agent."""
    # Convert to dict to allow adding additional fields
    agent_dict = agent.dict()
    agent_dict["created_at"] = datetime.utcnow()
    agent_dict["updated_at"] = datetime.utcnow()
    
    # Get database connection
    db = await get_database()
    
    # Insert into the database
    result = await db.agents.insert_one(agent_dict)
    
    # If there's a parent, update the parent's child_ids
    if agent.parent_id:
        await db.agents.update_one(
            {"_id": ObjectId(agent.parent_id)},
            {"$push": {"child_ids": str(result.inserted_id)}}
        )
    
    return {"id": str(result.inserted_id), "message": f"Agent created: {agent.name}"}

@api_router.get("/agents", response_model=List[Agent])
async def list_agents(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[AgentStatus] = None,
    type: Optional[AgentType] = None,
    parent_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """List all agents with optional filtering."""
    db = await get_database()
    query = {}
    
    if status:
        query["status"] = status
    
    if type:
        query["type"] = type
    
    if parent_id:
        if parent_id.lower() == "none":
            query["parent_id"] = None
        else:
            query["parent_id"] = parent_id
    
    cursor = db.agents.find(query).skip(skip).limit(limit)
    agents = []
    
    async for agent in cursor:
        agent = convert_objectid(agent)
        agents.append(agent)
    
    return agents

@api_router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str = Path(..., title="The ID of the agent to retrieve"),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific agent by ID."""
    db = await get_database()
    
    try:
        agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return convert_objectid(agent)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")

@api_router.put("/agents/{agent_id}", response_model=Agent)
async def update_agent(
    agent_update: AgentUpdate,
    agent_id: str = Path(..., title="The ID of the agent to update"),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing agent."""
    db = await get_database()
    
    try:
        # Get the existing agent
        existing_agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        update_data = agent_update.dict(exclude_unset=True)
        
        # Handle parent_id changes
        if "parent_id" in update_data and update_data["parent_id"] != existing_agent.get("parent_id"):
            # Remove from old parent's children if exists
            if existing_agent.get("parent_id"):
                await db.agents.update_one(
                    {"_id": ObjectId(existing_agent["parent_id"])},
                    {"$pull": {"child_ids": agent_id}}
                )
            
            # Add to new parent's children if exists
            if update_data["parent_id"]:
                await db.agents.update_one(
                    {"_id": ObjectId(update_data["parent_id"])},
                    {"$push": {"child_ids": agent_id}}
                )
        
        # Always update the updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # Update in database
        await db.agents.update_one({"_id": ObjectId(agent_id)}, {"$set": update_data})
        
        # Retrieve the updated agent
        updated_agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
        return convert_objectid(updated_agent)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")

@api_router.delete("/agents/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str = Path(..., title="The ID of the agent to delete"),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an agent."""
    db = await get_database()
    
    try:
        # Get the agent to check if it exists and to get parent_id
        agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # If agent has children, prevent deletion
        if agent.get("child_ids") and len(agent["child_ids"]) > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete an agent with child agents. Remove or reassign children first."
            )
        
        # Remove from parent's children list if it has a parent
        if agent.get("parent_id"):
            await db.agents.update_one(
                {"_id": ObjectId(agent["parent_id"])},
                {"$pull": {"child_ids": agent_id}}
            )
        
        # Delete the agent
        await db.agents.delete_one({"_id": ObjectId(agent_id)})
        
        return None
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")

@api_router.post("/agents/{agent_id}/process", response_model=Dict[str, Any])
async def process_agent_message(
    message: str,
    agent_id: str = Path(..., title="The ID of the agent to use"),
    conversation_id: Optional[str] = Query(None, title="Optional conversation ID"),
    current_user: User = Depends(get_current_active_user)
):
    """Process a message with an agent."""
    try:
        db = await get_database()
        
        # Update last_active timestamp
        await db.agents.update_one(
            {"_id": ObjectId(agent_id)},
            {"$set": {"last_active": datetime.utcnow()}}
        )
        
        # Use the agent manager to process the message
        response = await agent_manager.process_message(agent_id, message, conversation_id, current_user.id)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@api_router.post("/agents/{agent_id}/rag-config", response_model=Agent)
async def update_agent_rag_config(
    rag_config: RagConfig,
    agent_id: str = Path(..., title="The ID of the agent to update"),
    current_user: User = Depends(get_current_active_user)
):
    """Update an agent's RAG configuration."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db = await get_database()
    
    try:
        # Get the agent
        agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update RAG configuration
        update_data = {
            "rag_config": rag_config.dict(),
            "updated_at": datetime.utcnow()
        }
        
        await db.agents.update_one({"_id": ObjectId(agent_id)}, {"$set": update_data})
        
        # Return updated agent
        updated_agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
        return convert_objectid(updated_agent)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")

@api_router.post("/agents/{agent_id}/fine-tuning-config", response_model=Agent)
async def update_agent_fine_tuning_config(
    fine_tuning_config: FineTuningConfig,
    agent_id: str = Path(..., title="The ID of the agent to update"),
    current_user: User = Depends(get_current_active_user)
):
    """Update an agent's fine-tuning configuration."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db = await get_database()
    
    try:
        # Get the agent
        agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update fine-tuning configuration
        update_data = {
            "fine_tuning_config": fine_tuning_config.dict(),
            "updated_at": datetime.utcnow()
        }
        
        await db.agents.update_one({"_id": ObjectId(agent_id)}, {"$set": update_data})
        
        # Return updated agent
        updated_agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
        return convert_objectid(updated_agent)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")

@api_router.post("/agents/{agent_id}/start-fine-tuning", status_code=202)
async def start_agent_fine_tuning(
    agent_id: str = Path(..., title="The ID of the agent to fine-tune"),
    current_user: User = Depends(get_current_active_user)
):
    """Start fine-tuning for an agent."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db = await get_database()
    
    try:
        # Get the agent
        agent = await db.agents.find_one({"_id": ObjectId(agent_id)})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if fine-tuning is enabled
        if not agent.get("fine_tuning_config", {}).get("enabled", False):
            raise HTTPException(
                status_code=400,
                detail="Fine-tuning is not enabled for this agent"
            )
        
        # Update agent status to training
        await db.agents.update_one(
            {"_id": ObjectId(agent_id)},
            {
                "$set": {
                    "status": "training",
                    "updated_at": datetime.utcnow(),
                    "fine_tuning_config.training_status": "started"
                }
            }
        )
        
        # In a real implementation, you would start a background task to handle the fine-tuning process
        # For example:
        # background_tasks.add_task(fine_tune_agent, agent_id)
        
        return {"message": "Fine-tuning started"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")

@api_router.get("/knowledge-sources", response_model=List[KnowledgeSource])
async def list_knowledge_sources(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """List all knowledge sources."""
    db = await get_database()
    
    cursor = db.knowledge_sources.find().skip(skip).limit(limit)
    sources = []
    
    async for source in cursor:
        source = convert_objectid(source)
        sources.append(source)
    
    return sources

@api_router.post("/knowledge-sources", response_model=KnowledgeSource, status_code=201)
async def create_knowledge_source(
    source: KnowledgeSourceCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new knowledge source."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db = await get_database()
    
    source_dict = source.dict()
    source_dict["created_at"] = datetime.utcnow()
    source_dict["updated_at"] = datetime.utcnow()
    
    result = await db.knowledge_sources.insert_one(source_dict)
    created_source = await db.knowledge_sources.find_one({"_id": result.inserted_id})
    
    return convert_objectid(created_source)

@api_router.post("/agents/assistant", response_model=Dict[str, Any])
async def agent_creation_assistant(
    query: str,
    current_user: User = Depends(get_current_active_user)
):
    """AI-powered assistant to help with agent creation using RAG from knowledge sources."""
    db = await get_database()
    
    # Get available knowledge sources to use for augmenting the response
    knowledge_sources = []
    cursor = db.knowledge_sources.find({"source_type": {"$in": ["agent_documentation", "best_practices", "tutorials"]}})
    async for source in cursor:
        knowledge_sources.append(convert_objectid(source))
    
    # Build a more effective prompt with RAG
    system_prompt = """
    You are an expert AI agent creation assistant. Help the user create effective AI agents by providing 
    detailed, accurate information about agent architectures, capabilities, and best practices.
    
    Use the retrieved context to provide specific, actionable advice. If the information isn't in the context,
    use your general knowledge but indicate this clearly. Always provide explanations for your recommendations.
    """
    
    # In a production system, we would:
    # 1. Convert the query to embeddings
    # 2. Search vector DB for relevant documents
    # 3. Retrieve and rank the most relevant passages
    # 4. Augment the prompt with these passages
    
    # For now, we'll use a more detailed response simulation based on query analysis
    # This would actually be using a real LLM with RAG in production
    
    # Log the query for future analysis and improvement
    logger.info(f"Agent creation assistant query: {query}")
    
    # Analyze query to provide more targeted response
    query_topics = []
    if any(word in query.lower() for word in ["hierarchical", "hierarchy", "parent", "child", "structure"]):
        query_topics.append("hierarchical")
    if any(word in query.lower() for word in ["rag", "retrieval", "knowledge", "document", "context"]):
        query_topics.append("rag")
    if any(word in query.lower() for word in ["fine-tun", "training", "train", "adapt", "finetune"]):
        query_topics.append("fine-tuning")
    if any(word in query.lower() for word in ["tool", "function", "capability", "abilities"]):
        query_topics.append("tools")
    if any(word in query.lower() for word in ["model", "llm", "gpt", "claude", "mistral", "llama"]):
        query_topics.append("models")
    if any(word in query.lower() for word in ["start", "begin", "first", "new", "create"]):
        query_topics.append("getting-started")
    
    # Construct detailed response based on identified topics
    if "hierarchical" in query_topics:
        response = (
            "# Creating Hierarchical Agent Structures\n\n"
            "Hierarchical agent structures allow you to build sophisticated agent systems where specialized agents work together under supervision.\n\n"
            "## Architecture Patterns\n\n"
            "### Supervisor-Worker Pattern\n"
            "- **Supervisor Agent**: Coordinates task delegation and synthesizes results\n"
            "- **Worker Agents**: Specialized for specific domains or tasks\n"
            "- **Configuration**: Set parent_agent_id of workers to the supervisor's ID\n\n"
            "### Mesh Network Pattern\n"
            "- Agents can communicate laterally without central coordination\n"
            "- Better for collaborative problem solving across domains\n"
            "- Requires more sophisticated message routing\n\n"
            "## Implementation Steps\n\n"
            "1. Create a supervisor agent with broader capabilities\n"
            "2. Create specialized agents for specific domains\n"
            "3. Link them by setting parent/child relationships\n"
            "4. Configure system prompts to enable proper delegation\n\n"
            "## Best Practices\n\n"
            "- Keep hierarchies shallow (2-3 levels maximum)\n"
            "- Clearly define agent responsibilities\n"
            "- Provide clear communication protocols in system prompts\n"
            "- Test systematically with complex scenarios\n\n"
            "Would you like a specific example hierarchy for your use case?"
        )
    elif "rag" in query_topics:
        response = (
            "# Implementing Effective RAG for Agents\n\n"
            "Retrieval-Augmented Generation (RAG) enhances your agents with contextual knowledge, improving accuracy and relevance.\n\n"
            "## Key Components\n\n"
            "### Vector Database Selection\n"
            "- **Qdrant**: Excellent performance, easy deployment\n"
            "- **Pinecone**: Managed service with excellent scaling\n"
            "- **Chroma**: Simple integration for smaller projects\n\n"
            "### Embedding Models\n"
            "- **OpenAI**: High quality but higher cost\n"
            "- **BGE Models**: Excellent performance/cost ratio\n"
            "- **Cohere**: Good multilingual support\n\n"
            "### Chunking Strategies\n"
            "- **Fixed Size**: Simplest approach, 300-500 tokens recommended\n"
            "- **Semantic Chunking**: Better for preserving context\n"
            "- **Overlap**: 10-20% overlap prevents context fragmentation\n\n"
            "## Implementation Steps\n\n"
            "1. Upload and process knowledge sources\n"
            "2. Configure embedding model and chunking parameters\n"
            "3. Configure vector store\n"
            "4. Set up hybrid search for better results\n\n"
            "## Best Practices\n\n"
            "- Use semantic search over keyword search\n"
            "- Implement re-ranking for better relevance\n"
            "- Carefully curate knowledge sources\n"
            "- Regularly update and reindex content\n\n"
            "Would you like specific configuration recommendations for your use case?"
        )
    elif "fine-tuning" in query_topics:
        response = (
            "# Fine-Tuning Agents for Specialized Tasks\n\n"
            "Fine-tuning can significantly improve agent performance on domain-specific tasks, making responses more accurate and relevant.\n\n"
            "## Fine-Tuning Methods\n\n"
            "### LORA (Low-Rank Adaptation)\n"
            "- Most efficient approach for resource constraints\n"
            "- Excellent performance with fewer examples (100-300)\n"
            "- Faster training and deployment\n\n"
            "### Full Fine-Tuning\n"
            "- Best performance but requires more resources\n"
            "- Needs more examples (500-1000)\n"
            "- Higher computational requirements\n\n"
            "### QLORA\n"
            "- Quantized LORA for extremely efficient fine-tuning\n"
            "- Good balance of performance and resource usage\n\n"
            "## Data Preparation Guidelines\n\n"
            "1. Collect high-quality examples (100-1000 depending on method)\n"
            "2. Ensure diversity in examples\n"
            "3. Balance different types of queries\n"
            "4. Include edge cases and difficult scenarios\n\n"
            "## Training Parameters\n\n"
            "- **Learning Rate**: 1e-5 to 3e-5 recommended\n"
            "- **Epochs**: 3-5 typically sufficient\n"
            "- **Batch Size**: 4-8 for most cases\n\n"
            "## Evaluation\n\n"
            "- Always test against a validation set\n"
            "- Compare against baseline model performance\n"
            "- Check for overfitting or blind spots\n\n"
            "Would you like guidance on preparing data for fine-tuning?"
        )
    elif "tools" in query_topics:
        response = (
            "# Configuring Agent Tools and Capabilities\n\n"
            "Tools give your agents the ability to perform specific actions and access external systems.\n\n"
            "## Available Tools\n\n"
            "### Data Retrieval Tools\n"
            "- **customer_lookup**: Access customer records and history\n"
            "- **service_request_list**: Retrieve service request details\n"
            "- **knowledge_base_search**: Search knowledge bases for information\n\n"
            "### Action Tools\n"
            "- **service_request_create**: Create new service requests\n"
            "- **appliance_troubleshoot**: Run diagnostics on appliances\n"
            "- **schedule_technician**: Book technician appointments\n\n"
            "### Analysis Tools\n"
            "- **data_analysis**: Analyze customer or service data\n"
            "- **sentiment_analysis**: Analyze customer sentiment\n\n"
            "## Implementation Considerations\n\n"
            "1. Only give agents tools they need for their specific role\n"
            "2. Ensure system prompts instruct on proper tool usage\n"
            "3. Consider rate limits and permissions for each tool\n"
            "4. Balance tool complexity with agent capabilities\n\n"
            "## Best Practices\n\n"
            "- Start with fewer tools and add as needed\n"
            "- Test each tool integration thoroughly\n"
            "- Monitor tool usage patterns\n"
            "- Consider tool chains for complex operations\n\n"
            "Would you like recommendations for tools based on a specific agent role?"
        )
    elif "models" in query_topics:
        response = (
            "# Selecting the Right Model for Your Agent\n\n"
            "Model selection significantly impacts performance, cost, and capabilities of your agents.\n\n"
            "## Model Comparison\n\n"
            "### GPT Models\n"
            "- **GPT-3.5-Turbo**: Good balance of cost/performance for simpler tasks\n"
            "- **GPT-4**: Superior reasoning, instruction following, and consistency\n"
            "- **GPT-4-Turbo**: Improved performance and context length with better cost efficiency\n\n"
            "### Claude Models\n"
            "- **Claude-3-Opus**: Highest performance, excellent for complex reasoning\n"
            "- **Claude-3-Sonnet**: Good balance of performance and cost\n"
            "- **Claude-3-Haiku**: Fastest and most cost-effective for simple tasks\n\n"
            "### Open Source Models\n"
            "- **Llama-2 Series**: Good for self-hosting, variable performance\n"
            "- **Mistral Series**: Excellent performance for their size\n\n"
            "## Selection Criteria\n\n"
            "1. **Task Complexity**: Match model capability to task difficulty\n"
            "2. **Cost Constraints**: Consider usage patterns and budget\n"
            "3. **Latency Requirements**: Faster models for real-time applications\n"
            "4. **Fine-tuning Needs**: Some models fine-tune better than others\n\n"
            "## Recommended Configurations\n\n"
            "- **Customer Service**: Claude-3-Sonnet or GPT-3.5-Turbo\n"
            "- **Complex Diagnosis**: GPT-4 or Claude-3-Opus\n"
            "- **Data Analysis**: Claude-3-Opus or GPT-4\n"
            "- **Simple Scheduling**: Claude-3-Haiku or GPT-3.5-Turbo\n\n"
            "Would you like a detailed comparison for a specific use case?"
        )
    elif "getting-started" in query_topics:
        response = (
            "# Getting Started with Agent Creation\n\n"
            "Follow this step-by-step guide to create your first effective agent.\n\n"
            "## 1. Define the Agent's Purpose\n\n"
            "- Clearly define what problem the agent will solve\n"
            "- Identify target users and their needs\n"
            "- Set measurable success criteria\n\n"
            "## 2. Select the Right Configuration\n\n"
            "- **Agent Type**: Choose from customer_service, diagnosis, scheduling, etc.\n"
            "- **Model**: Start with GPT-3.5-Turbo for testing, upgrade as needed\n"
            "- **Tools**: Begin with essential tools only\n\n"
            "## 3. Design the Agent's Personality\n\n"
            "- Create a detailed system prompt (see templates in documentation)\n"
            "- Define the agent's tone and communication style\n"
            "- Set boundaries on what the agent should/shouldn't do\n\n"
            "## 4. Knowledge Configuration\n\n"
            "- Decide if RAG is needed for domain knowledge\n"
            "- Select appropriate knowledge sources\n"
            "- Configure chunking and indexing parameters\n\n"
            "## 5. Testing and Improvement\n\n"
            "- Start with simple test cases\n"
            "- Gradually introduce complexity\n"
            "- Monitor performance and iterate\n\n"
            "## Next Steps\n\n"
            "- Consider fine-tuning once you have usage data\n"
            "- Explore hierarchical structures for complex workflows\n"
            "- Integrate with other business systems\n\n"
            "Would you like a sample configuration for a specific use case?"
        )
    else:
        response = (
            "# AI Agent Creation Guide\n\n"
            "I can help you create effective AI agents tailored to your needs. Here are the key areas to consider:\n\n"
            "## Agent Fundamentals\n\n"
            "- **Purpose**: Define the specific problems your agent will solve\n"
            "- **Capabilities**: Determine what your agent should be able to do\n"
            "- **Limitations**: Establish boundaries for agent operations\n\n"
            "## Technical Components\n\n"
            "1. **Model Selection**: Choose the right model for your needs and budget\n"
            "2. **Tools Configuration**: Provide the capabilities your agent needs\n"
            "3. **System Prompt**: Define the agent's personality and instructions\n"
            "4. **Knowledge Integration**: Add domain knowledge with RAG\n"
            "5. **Fine-tuning**: Adapt the agent to your specific domain\n"
            "6. **Hierarchical Design**: Create coordinated agent systems\n\n"
            "## Getting Started\n\n"
            "I recommend beginning with:\n"
            "1. Creating a basic agent with a clear purpose\n"
            "2. Testing it on simple use cases\n"
            "3. Gradually enhancing capabilities as needs become clearer\n\n"
            "## What would you like to explore?\n\n"
            "- Agent types and their uses\n"
            "- Model selection guidelines\n"
            "- Setting up RAG for knowledge access\n"
            "- Creating effective system prompts\n"
            "- Hierarchical agent structures\n"
            "- Fine-tuning for specialized tasks\n"
            "- Tool configuration best practices\n\n"
            "Please let me know what aspect you'd like to explore first, or share your specific use case for tailored recommendations."
        )
    
    # In a production environment, we would:
    # 1. Send the augmented prompt to an LLM API
    # 2. Process the response
    # 3. Log the interaction for improvement
    
    # Create a fake latency for realism
    await asyncio.sleep(0.5)
    
    return {"response": response}

@api_router.post("/agent-templates", response_model=AgentTemplate, status_code=201)
async def create_agent_template(
    template: AgentTemplateCreate, 
    current_user: User = Depends(get_current_active_user)
):
    """Create a new agent template."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db = await get_database()
    
    template_dict = template.dict()
    template_dict["created_at"] = datetime.utcnow()
    template_dict["updated_at"] = datetime.utcnow()
    
    result = await db.agent_templates.insert_one(template_dict)
    created_template = await db.agent_templates.find_one({"_id": result.inserted_id})
    
    return convert_objectid(created_template)

@api_router.get("/agent-templates", response_model=List[AgentTemplate])
async def list_agent_templates(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """List all agent templates."""
    db = await get_database()
    
    cursor = db.agent_templates.find().skip(skip).limit(limit)
    templates = []
    
    async for template in cursor:
        template = convert_objectid(template)
        templates.append(template)
    
    return templates

# Smartlist endpoints
@api_router.post("/smartlists", response_model=Smartlist)
async def create_smartlist(
    smartlist: SmartlistCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new smartlist."""
    db = await get_database()
    
    # Create the smartlist
    smartlist_dict = smartlist.dict()
    smartlist_dict["owner_id"] = str(current_user.id)  # Set the current user as owner
    smartlist_dict["created_at"] = datetime.utcnow()
    smartlist_dict["updated_at"] = datetime.utcnow()
    
    result = await db.smartlists.insert_one(smartlist_dict)
    
    created_smartlist = await db.smartlists.find_one({"_id": result.inserted_id})
    created_smartlist = convert_objectid(created_smartlist)
    
    return created_smartlist

@api_router.get("/smartlists", response_model=List[Smartlist])
async def list_smartlists(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[SmartlistType] = None,
    current_user: User = Depends(get_current_active_user)
):
    """List all smartlists that are public or owned by the current user."""
    db = await get_database()
    
    # Build query for smartlists that are either public or owned by current user
    query = {
        "$or": [
            {"is_public": True},
            {"owner_id": str(current_user.id)}
        ]
    }
    
    # Add type filter if provided
    if type:
        query["type"] = type.value
    
    cursor = db.smartlists.find(query).skip(skip).limit(limit).sort("created_at", -1)
    smartlists = []
    
    async for smartlist in cursor:
        smartlist = convert_objectid(smartlist)
        smartlists.append(smartlist)
    
    return smartlists

@api_router.get("/smartlists/{smartlist_id}", response_model=Smartlist)
async def get_smartlist(
    smartlist_id: str = Path(..., title="The ID of the smartlist to get"),
    current_user: User = Depends(get_current_active_user)
):
    """Get a smartlist by ID."""
    db = await get_database()
    
    smartlist = await db.smartlists.find_one({"_id": ObjectId(smartlist_id)})
    
    if not smartlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Smartlist not found with ID: {smartlist_id}"
        )
    
    # Check if user has access (owner or public)
    if not smartlist["is_public"] and smartlist["owner_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this smartlist"
        )
    
    smartlist = convert_objectid(smartlist)
    
    return smartlist

@api_router.put("/smartlists/{smartlist_id}", response_model=Smartlist)
async def update_smartlist(
    smartlist_update: SmartlistUpdate,
    smartlist_id: str = Path(..., title="The ID of the smartlist to update"),
    current_user: User = Depends(get_current_active_user)
):
    """Update a smartlist."""
    db = await get_database()
    
    # Check if smartlist exists
    smartlist = await db.smartlists.find_one({"_id": ObjectId(smartlist_id)})
    
    if not smartlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Smartlist not found with ID: {smartlist_id}"
        )
    
    # Check if user is the owner
    if smartlist["owner_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this smartlist"
        )
    
    # Prepare update data
    update_data = {}
    
    for field, value in smartlist_update.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Update the smartlist
    await db.smartlists.update_one(
        {"_id": ObjectId(smartlist_id)},
        {"$set": update_data}
    )
    
    # Get the updated smartlist
    updated_smartlist = await db.smartlists.find_one({"_id": ObjectId(smartlist_id)})
    updated_smartlist = convert_objectid(updated_smartlist)
    
    return updated_smartlist

@api_router.delete("/smartlists/{smartlist_id}")
async def delete_smartlist(
    smartlist_id: str = Path(..., title="The ID of the smartlist to delete"),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a smartlist."""
    db = await get_database()
    
    # Check if smartlist exists
    smartlist = await db.smartlists.find_one({"_id": ObjectId(smartlist_id)})
    
    if not smartlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Smartlist not found with ID: {smartlist_id}"
        )
    
    # Check if user is the owner
    if smartlist["owner_id"] != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this smartlist"
        )
    
    # Delete the smartlist
    await db.smartlists.delete_one({"_id": ObjectId(smartlist_id)})
    
    return {"message": "Smartlist deleted successfully"}

# Dashboard endpoints
@api_router.get("/dashboard/summary", response_model=Dict[str, Any])
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user)
):
    """Get summary statistics for the dashboard."""
    db = await get_database()
    
    # Get counts
    customer_count = await db.customers.count_documents({})
    
    pending_requests = await db.service_requests.count_documents({"status": "pending"})
    scheduled_requests = await db.service_requests.count_documents({"status": "scheduled"})
    in_progress_requests = await db.service_requests.count_documents({"status": "in_progress"})
    completed_requests = await db.service_requests.count_documents({"status": "completed"})
    
    technician_count = await db.technicians.count_documents({"active": True})
    agent_count = await db.agents.count_documents({"status": "active"})
    conversation_count = await db.conversations.count_documents({})
    
    # Get recent service requests
    cursor = db.service_requests.find().sort("created_at", -1).limit(5)
    recent_requests = []
    
    async for request in cursor:
        request = convert_objectid(request)
        recent_requests.append(request)
    
    return {
        "counts": {
            "customers": customer_count,
            "service_requests": {
                "pending": pending_requests,
                "scheduled": scheduled_requests,
                "in_progress": in_progress_requests,
                "completed": completed_requests,
                "total": pending_requests + scheduled_requests + in_progress_requests + completed_requests
            },
            "technicians": technician_count,
            "agents": agent_count,
            "conversations": conversation_count
        },
        "recent_requests": recent_requests
    }

# AI Assistant endpoints
@api_router.post("/ai-assistant/chat", response_model=dict)
async def ai_assistant_chat(
    request: Request,
    message: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Endpoint for interacting with the Claude 3.7 AI assistant.
    
    This assistant has access to RAG with all program data and can use tools
    to perform operations within the application.
    
    Parameters:
    - message: Dict containing the user message and conversation context
    - current_user: The authenticated user making the request
    
    Returns:
    - Dict containing the assistant's response and any tool executions
    """
    try:
        # Get database connection
        db = await get_database()
        
        # Extract message content and context
        user_message = message.get("message", "")
        conversation_id = message.get("conversation_id")
        
        # If there's a conversation ID, retrieve conversation history
        conversation_history = []
        if conversation_id:
            conversation = await db["conversations"].find_one({"_id": ObjectId(conversation_id)})
            if conversation:
                messages = await db["messages"].find(
                    {"conversation_id": conversation_id}
                ).sort("timestamp", 1).to_list(1000)
                
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in messages
                ]
        
        # Define available tools for the assistant
        tools = [
            {
                "name": "retrieve_customer_info",
                "description": "Retrieve customer information from the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The ID of the customer"
                        },
                        "search_query": {
                            "type": "string",
                            "description": "Search query to find a customer by name, email, or phone"
                        }
                    }
                }
            },
            {
                "name": "retrieve_service_requests",
                "description": "Retrieve service requests from the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "Filter by customer ID"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status (pending, scheduled, in_progress, completed, cancelled)"
                        },
                        "technician_id": {
                            "type": "string",
                            "description": "Filter by technician ID"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of requests to return"
                        }
                    }
                }
            },
            {
                "name": "retrieve_agent_info",
                "description": "Retrieve information about AI agents in the system",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "The ID of the agent"
                        },
                        "agent_type": {
                            "type": "string",
                            "description": "Filter by agent type"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by agent status"
                        }
                    }
                }
            },
            {
                "name": "search_knowledge_base",
                "description": "Search the knowledge base using RAG",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "knowledge_base_ids": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of knowledge base IDs to search in"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "create_service_request",
                "description": "Create a new service request",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "The ID of the customer"
                        },
                        "appliance_type": {
                            "type": "string",
                            "description": "Type of appliance (refrigerator, washer, dryer, dishwasher, stove, oven, microwave, other)"
                        },
                        "issue_description": {
                            "type": "string",
                            "description": "Description of the issue"
                        },
                        "priority": {
                            "type": "string",
                            "description": "Priority level (low, medium, high, urgent)"
                        },
                        "scheduled_date": {
                            "type": "string",
                            "description": "Scheduled date in ISO format"
                        },
                        "technician_id": {
                            "type": "string",
                            "description": "ID of the assigned technician"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes"
                        }
                    },
                    "required": ["customer_id", "appliance_type", "issue_description"]
                }
            }
        ]
        
        # Prepare the system message
        system_message = """You are an AI assistant for the OMRA Lite application, powered by Claude 3.7 Sonnet.
        
Your role is to help users with tasks related to customer management, service requests, and AI agent configuration.
You have access to various tools that allow you to retrieve and modify data in the system.

You should:
1. Provide helpful, accurate responses to user questions
2. Use appropriate tools to access data when needed
3. Maintain a professional, friendly tone
4. Format your responses clearly with appropriate formatting
5. Refer to the documentation when providing guidance on complex topics

When accessing or modifying data, always be explicit about what you're doing and confirm important actions.
"""

        # Prepare messages for Claude
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get the API key
        api_key_setting = await db["api_keys"].find_one({"key_name": "anthropic_api_key"})
        if not api_key_setting:
            return JSONResponse(
                status_code=500,
                content={"detail": "Anthropic API key not configured"}
            )
        
        anthropic_api_key = api_key_setting["key_value"]
        
        # Call Claude 3.7 API
        headers = {
            "x-api-key": anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": "claude-3-7-sonnet-20250219",
            "max_tokens": 4000,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"detail": f"Error from Anthropic API: {response.text}"}
                )
            
            claude_response = response.json()
        
        # Extract the assistant's response
        assistant_message = claude_response["content"]
        
        # Handle tool calls if any
        tool_outputs = []
        if "tool_calls" in claude_response:
            for tool_call in claude_response["tool_calls"]:
                tool_name = tool_call["name"]
                tool_args = tool_call["parameters"]
                
                # Execute the appropriate tool
                tool_result = await execute_assistant_tool(tool_name, tool_args, current_user)
                tool_outputs.append({
                    "tool_call_id": tool_call["id"],
                    "output": tool_result
                })
            
            # If there were tool calls, we need to make a follow-up API call with the results
            if tool_outputs:
                # Add the assistant's response and tool calls to messages
                messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "tool_calls": claude_response["tool_calls"]
                })
                
                # Add tool outputs
                messages.append({
                    "role": "tool",
                    "content": tool_outputs
                })
                
                # Make follow-up call to Claude
                payload["messages"] = messages
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers=headers,
                        json=payload
                    )
                    
                    if response.status_code != 200:
                        return JSONResponse(
                            status_code=response.status_code,
                            content={"detail": f"Error from Anthropic API during tool response: {response.text}"}
                        )
                    
                    claude_response = response.json()
                    assistant_message = claude_response["content"]
        
        # Store the conversation and messages if needed
        if not conversation_id:
            # Create a new conversation
            new_conversation = {
                "title": user_message[:50] + "..." if len(user_message) > 50 else user_message,
                "user_id": str(current_user["_id"]),
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "metadata": {"source": "ai_assistant"}
            }
            
            result = await db["conversations"].insert_one(new_conversation)
            conversation_id = str(result.inserted_id)
        
        # Store user message
        await db["messages"].insert_one({
            "conversation_id": conversation_id,
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow(),
            "metadata": {}
        })
        
        # Store assistant response
        await db["messages"].insert_one({
            "conversation_id": conversation_id,
            "role": "agent",
            "content": assistant_message,
            "timestamp": datetime.utcnow(),
            "metadata": {"tool_outputs": tool_outputs if tool_outputs else []}
        })
        
        # Update conversation timestamp
        await db["conversations"].update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"updated_at": datetime.utcnow()}}
        )
        
        return {
            "response": assistant_message,
            "conversation_id": conversation_id,
            "tool_outputs": tool_outputs
        }
    
    except Exception as e:
        logger.error(f"Error in AI assistant endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"An error occurred: {str(e)}"}
        )

async def execute_assistant_tool(tool_name, tool_args, current_user):
    """
    Execute a tool called by the AI assistant
    
    Parameters:
    - tool_name: The name of the tool to execute
    - tool_args: The arguments for the tool
    - current_user: The authenticated user
    
    Returns:
    - The result of the tool execution
    """
    try:
        # Get database connection
        db = await get_database()
        
        if tool_name == "retrieve_customer_info":
            # Handle customer info retrieval
            if "customer_id" in tool_args and tool_args["customer_id"]:
                customer = await db["customers"].find_one({"_id": ObjectId(tool_args["customer_id"])})
                if customer:
                    customer["_id"] = str(customer["_id"])
                    return customer
                return {"error": "Customer not found"}
            
            elif "search_query" in tool_args and tool_args["search_query"]:
                # Search by name, email or phone
                query = tool_args["search_query"]
                pipeline = [
                    {
                        "$match": {
                            "$or": [
                                {"first_name": {"$regex": query, "$options": "i"}},
                                {"last_name": {"$regex": query, "$options": "i"}},
                                {"contact_info.email": {"$regex": query, "$options": "i"}},
                                {"contact_info.phone": {"$regex": query, "$options": "i"}}
                            ]
                        }
                    },
                    {"$limit": 5}
                ]
                
                customers = await db["customers"].aggregate(pipeline).to_list(5)
                for customer in customers:
                    customer["_id"] = str(customer["_id"])
                
                return customers
            
            return {"error": "Missing customer_id or search_query"}
            
        elif tool_name == "retrieve_service_requests":
            # Handle service request retrieval
            match_criteria = {}
            
            if "customer_id" in tool_args and tool_args["customer_id"]:
                match_criteria["customer_id"] = tool_args["customer_id"]
                
            if "status" in tool_args and tool_args["status"]:
                match_criteria["status"] = tool_args["status"]
                
            if "technician_id" in tool_args and tool_args["technician_id"]:
                match_criteria["technician_id"] = tool_args["technician_id"]
            
            limit = tool_args.get("limit", 10)
            
            service_requests = await db["service_requests"].find(match_criteria).sort("created_at", -1).limit(limit).to_list(limit)
            
            for sr in service_requests:
                sr["_id"] = str(sr["_id"])
                # Format dates for readability
                if "created_at" in sr:
                    sr["created_at"] = sr["created_at"].isoformat()
                if "updated_at" in sr:
                    sr["updated_at"] = sr["updated_at"].isoformat()
                if "scheduled_date" in sr and sr["scheduled_date"]:
                    sr["scheduled_date"] = sr["scheduled_date"].isoformat()
                if "completed_at" in sr and sr["completed_at"]:
                    sr["completed_at"] = sr["completed_at"].isoformat()
            
            return service_requests
            
        elif tool_name == "retrieve_agent_info":
            # Handle agent info retrieval
            match_criteria = {}
            
            if "agent_id" in tool_args and tool_args["agent_id"]:
                agent = await db["agents"].find_one({"_id": ObjectId(tool_args["agent_id"])})
                if agent:
                    agent["_id"] = str(agent["_id"])
                    return agent
                return {"error": "Agent not found"}
            
            if "agent_type" in tool_args and tool_args["agent_type"]:
                match_criteria["type"] = tool_args["agent_type"]
                
            if "status" in tool_args and tool_args["status"]:
                match_criteria["status"] = tool_args["status"]
            
            agents = await db["agents"].find(match_criteria).to_list(100)
            
            for agent in agents:
                agent["_id"] = str(agent["_id"])
                # Format dates for readability
                if "created_at" in agent:
                    agent["created_at"] = agent["created_at"].isoformat()
                if "updated_at" in agent:
                    agent["updated_at"] = agent["updated_at"].isoformat()
                if "last_active" in agent and agent["last_active"]:
                    agent["last_active"] = agent["last_active"].isoformat()
            
            return agents
            
        elif tool_name == "search_knowledge_base":
            # Handle knowledge base search using RAG
            query = tool_args.get("query")
            if not query:
                return {"error": "Query is required"}
                
            # Get knowledge base IDs to search
            knowledge_base_ids = tool_args.get("knowledge_base_ids", [])
            limit = tool_args.get("limit", 5)
            
            # RAG implementation would go here
            # Since we don't have the full RAG implementation details, we'll return a placeholder
            # In a real implementation, you would:
            # 1. Generate query embeddings
            # 2. Search the vector store for relevant chunks
            # 3. Return the most relevant results
            
            # For now, we'll do a basic text search on agent and system documentation
            # This would be replaced with actual RAG functionality
            
            # First, check the agent documentation from AgentDocs.js
            agent_docs_data = {
                "title": "Agent Documentation",
                "sections": [
                    "Getting Started with Agents",
                    "Agent Architecture & Implementation",
                    "Agent Hierarchy Patterns",
                    "Advanced Hierarchical Orchestration Models",
                    "RAG Configuration",
                    "Fine-tuning",
                    "Agent Best Practices"
                ]
            }
            
            # Get agents that might match the query
            agents = await db["agents"].find({
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"system_prompt": {"$regex": query, "$options": "i"}}
                ]
            }).limit(limit).to_list(limit)
            
            # Format agents for return
            agent_results = []
            for agent in agents:
                agent_results.append({
                    "id": str(agent["_id"]),
                    "type": "agent",
                    "name": agent["name"],
                    "description": agent.get("description", ""),
                    "model": agent.get("model", ""),
                    "type": agent.get("type", "")
                })
            
            # Combine results
            rag_results = [
                {
                    "id": "agent_docs",
                    "type": "documentation",
                    "title": "Agent Documentation",
                    "content": f"Documentation covering: {', '.join(agent_docs_data['sections'])}",
                    "relevance": 0.95
                }
            ]
            
            if agent_results:
                rag_results.extend([
                    {
                        "id": result["id"],
                        "type": "agent",
                        "title": result["name"],
                        "content": result["description"],
                        "agent_type": result["type"],
                        "model": result["model"],
                        "relevance": 0.85
                    } for result in agent_results
                ])
            
            return rag_results
            
        elif tool_name == "create_service_request":
            # Handle service request creation
            required_fields = ["customer_id", "appliance_type", "issue_description"]
            for field in required_fields:
                if field not in tool_args or not tool_args[field]:
                    return {"error": f"Missing required field: {field}"}
            
            # Create service request object
            service_request = {
                "customer_id": tool_args["customer_id"],
                "appliance_type": tool_args["appliance_type"],
                "issue_description": tool_args["issue_description"],
                "priority": tool_args.get("priority", "MEDIUM"),
                "status": "PENDING",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Add optional fields if provided
            if "scheduled_date" in tool_args and tool_args["scheduled_date"]:
                service_request["scheduled_date"] = datetime.fromisoformat(tool_args["scheduled_date"])
                
            if "technician_id" in tool_args and tool_args["technician_id"]:
                service_request["technician_id"] = tool_args["technician_id"]
                
            if "notes" in tool_args and tool_args["notes"]:
                service_request["notes"] = tool_args["notes"]
            
            # Insert into database
            result = await db["service_requests"].insert_one(service_request)
            
            return {
                "success": True,
                "service_request_id": str(result.inserted_id),
                "message": "Service request created successfully"
            }
            
        else:
            return {"error": f"Unknown tool: {tool_name}"}
            
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        return {"error": f"Error executing tool: {str(e)}"} 