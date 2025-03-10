"""
API routes for service request management
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db import get_db
from db.models import ServiceRequest, Customer, Appliance, PriorityEnum, StatusEnum
from auth.jwt import get_current_active_user
from utils.logging import log_agent_activity
from pydantic import BaseModel, constr

# Define Pydantic models for request/response
class ServiceRequestBase(BaseModel):
    customer_id: int
    appliance_id: int
    issue_description: constr(min_length=1)
    priority: PriorityEnum = PriorityEnum.medium
    status: StatusEnum = StatusEnum.pending

class ServiceRequestCreate(ServiceRequestBase):
    pass

class ServiceRequestUpdate(BaseModel):
    issue_description: Optional[constr(min_length=1)] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None

class ServiceRequestResponse(ServiceRequestBase):
    id: int
    created_at: datetime
    updated_at: datetime
    kickserv_job_id: Optional[str] = None
    
    class Config:
        orm_mode = True

class ServiceRequestDetail(ServiceRequestResponse):
    customer: dict
    appliance: dict
    appointments: List[dict] = []
    
    class Config:
        orm_mode = True

# Create router
router = APIRouter(
    prefix="/api/service-requests",
    tags=["service-requests"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/", response_model=List[ServiceRequestResponse])
async def list_service_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[StatusEnum] = None,
    priority: Optional[PriorityEnum] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get a list of service requests with optional filters
    """
    query = db.query(ServiceRequest)
    
    # Apply filters if provided
    if status:
        query = query.filter(ServiceRequest.status == status)
    
    if priority:
        query = query.filter(ServiceRequest.priority == priority)
    
    if customer_id:
        query = query.filter(ServiceRequest.customer_id == customer_id)
    
    # Apply pagination
    service_requests = query.order_by(ServiceRequest.created_at.desc()).offset(skip).limit(limit).all()
    
    return service_requests

@router.get("/{service_request_id}", response_model=ServiceRequestDetail)
async def get_service_request(
    service_request_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get a specific service request by ID
    """
    service_request = db.query(ServiceRequest).filter(ServiceRequest.id == service_request_id).first()
    if not service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service request with ID {service_request_id} not found"
        )
    
    return service_request

@router.post("/", response_model=ServiceRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_service_request(
    service_request: ServiceRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new service request
    """
    # Check if customer exists
    customer = db.query(Customer).filter(Customer.id == service_request.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {service_request.customer_id} not found"
        )
    
    # Check if appliance exists
    appliance = db.query(Appliance).filter(Appliance.id == service_request.appliance_id).first()
    if not appliance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appliance with ID {service_request.appliance_id} not found"
        )
    
    # Create new service request
    db_service_request = ServiceRequest(**service_request.dict())
    db.add(db_service_request)
    db.commit()
    db.refresh(db_service_request)
    
    # Log the activity
    log_agent_activity("api", "service_requests", "create_service_request", {"service_request_id": db_service_request.id})
    
    return db_service_request

@router.put("/{service_request_id}", response_model=ServiceRequestResponse)
async def update_service_request(
    service_request_id: int,
    service_request: ServiceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update an existing service request
    """
    # Get existing service request
    db_service_request = db.query(ServiceRequest).filter(ServiceRequest.id == service_request_id).first()
    if not db_service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service request with ID {service_request_id} not found"
        )
    
    # Update service request fields
    update_data = service_request.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_service_request, key, value)
    
    db.commit()
    db.refresh(db_service_request)
    
    # Log the activity
    log_agent_activity("api", "service_requests", "update_service_request", {
        "service_request_id": service_request_id,
        "updated_fields": list(update_data.keys())
    })
    
    return db_service_request

@router.delete("/{service_request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_request(
    service_request_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Delete a service request
    """
    # Get existing service request
    db_service_request = db.query(ServiceRequest).filter(ServiceRequest.id == service_request_id).first()
    if not db_service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service request with ID {service_request_id} not found"
        )
    
    # Delete service request
    db.delete(db_service_request)
    db.commit()
    
    # Log the activity
    log_agent_activity("api", "service_requests", "delete_service_request", {"service_request_id": service_request_id})
    
    return None

@router.post("/{service_request_id}/notes", status_code=status.HTTP_201_CREATED)
async def add_note_to_service_request(
    service_request_id: int,
    note: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Add a note to a service request
    
    In a real implementation, this would add to a service_request_notes table.
    For this example, we'll just update the notes field.
    """
    # Get existing service request
    db_service_request = db.query(ServiceRequest).filter(ServiceRequest.id == service_request_id).first()
    if not db_service_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service request with ID {service_request_id} not found"
        )
    
    # Add timestamp to note
    note_with_timestamp = {
        "content": note.get("content", ""),
        "user": current_user.get("username", "unknown"),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # For this example, just append to issue_description
    # In a real app, this would use a proper notes table
    if db_service_request.notes:
        db_service_request.notes += f"\n\n[{note_with_timestamp['timestamp']}] {note_with_timestamp['user']}: {note_with_timestamp['content']}"
    else:
        db_service_request.notes = f"[{note_with_timestamp['timestamp']}] {note_with_timestamp['user']}: {note_with_timestamp['content']}"
    
    db.commit()
    
    # Log the activity
    log_agent_activity("api", "service_requests", "add_note", {"service_request_id": service_request_id})
    
    return {"status": "success", "note": note_with_timestamp} 