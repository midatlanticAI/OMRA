"""
API routes for customer management
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db import get_db
from db.models import Customer
from auth.jwt import get_current_active_user
from utils.logging import log_agent_activity
from pydantic import BaseModel, EmailStr, constr

# Define Pydantic models for request/response
class CustomerBase(BaseModel):
    first_name: constr(min_length=1, max_length=100)
    last_name: constr(min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[constr(min_length=1, max_length=100)] = None
    last_name: Optional[constr(min_length=1, max_length=100)] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    notes: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: int
    ghl_contact_id: Optional[str] = None
    kickserv_customer_id: Optional[str] = None
    
    class Config:
        orm_mode = True

# Create router
router = APIRouter(
    prefix="/api/customers",
    tags=["customers"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get a list of customers with optional pagination and search
    """
    query = db.query(Customer)
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Customer.first_name.ilike(search_term)) |
            (Customer.last_name.ilike(search_term)) |
            (Customer.email.ilike(search_term)) |
            (Customer.phone.ilike(search_term))
        )
    
    # Apply pagination
    customers = query.offset(skip).limit(limit).all()
    
    return customers

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get a specific customer by ID
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    return customer

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new customer
    """
    # Check if email already exists
    existing_customer = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Customer with email {customer.email} already exists"
        )
    
    # Create new customer
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    # Log the activity
    log_agent_activity("api", "customers", "create_customer", {"customer_id": db_customer.id})
    
    return db_customer

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update an existing customer
    """
    # Get existing customer
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    # Check email uniqueness if changed
    if customer.email and customer.email != db_customer.email:
        existing_customer = db.query(Customer).filter(Customer.email == customer.email).first()
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with email {customer.email} already exists"
            )
    
    # Update customer fields
    update_data = customer.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_customer, key, value)
    
    db.commit()
    db.refresh(db_customer)
    
    # Log the activity
    log_agent_activity("api", "customers", "update_customer", {"customer_id": customer_id})
    
    return db_customer

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Delete a customer
    """
    # Get existing customer
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    # Delete customer
    db.delete(db_customer)
    db.commit()
    
    # Log the activity
    log_agent_activity("api", "customers", "delete_customer", {"customer_id": customer_id})
    
    return None 