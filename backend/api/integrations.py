"""
API routes for third-party integrations (GHL and Kickserv)
"""
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session

from db import get_db
from db.models import Customer, ServiceRequest
from auth.jwt import get_current_active_user
from utils.logging import log_agent_activity
from agent_system.core import AgentSystem
from integrations import IntegrationManager
from pydantic import BaseModel

# Create routers
ghl_router = APIRouter(
    prefix="/api/integrations/ghl",
    tags=["integrations", "ghl"],
    dependencies=[Depends(get_current_active_user)]
)

kickserv_router = APIRouter(
    prefix="/api/integrations/kickserv",
    tags=["integrations", "kickserv"],
    dependencies=[Depends(get_current_active_user)]
)

# Combined router
router = APIRouter(
    prefix="/api/integrations",
    tags=["integrations"],
    dependencies=[Depends(get_current_active_user)]
)

# Dependency to get the agent system
def get_agent_system():
    # In a real implementation, this would be a singleton
    return AgentSystem("config/agent_system.yaml")

def get_integration_manager(agent_system: AgentSystem = Depends(get_agent_system)):
    return agent_system.integration_manager

# GHL Routes
@ghl_router.post("/sync-contact/{customer_id}", response_model=Dict[str, Any])
async def sync_contact_with_ghl(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Sync a customer with GHL contacts
    """
    try:
        # Get customer from database
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        # Get GHL connector
        ghl_connector = integration_manager.get_ghl_connector()
        
        # Prepare customer data for GHL
        customer_data = {
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address,
            "city": customer.city,
            "state": customer.state,
            "zip_code": customer.zip_code
        }
        
        # Sync with GHL
        result = await ghl_connector.sync_contact(customer_data)
        
        # Update customer with GHL contact ID
        customer.ghl_contact_id = result.get("id")
        db.commit()
        
        # Log the activity
        log_agent_activity("api", "integrations", "sync_ghl_contact", {"customer_id": customer_id})
        
        return {
            "success": True,
            "ghl_contact_id": customer.ghl_contact_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync with GHL: {str(e)}"
        )

@ghl_router.post("/create-opportunity/{service_request_id}", response_model=Dict[str, Any])
async def create_ghl_opportunity(
    service_request_id: int,
    pipeline_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Create an opportunity in GHL for a service request
    """
    try:
        # Get service request from database
        service_request = db.query(ServiceRequest).filter(ServiceRequest.id == service_request_id).first()
        if not service_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service request with ID {service_request_id} not found"
            )
        
        # Get customer
        customer = db.query(Customer).filter(Customer.id == service_request.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {service_request.customer_id} not found"
            )
        
        # Check if customer has GHL contact ID
        if not customer.ghl_contact_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer does not have a GHL contact ID. Sync customer with GHL first."
            )
        
        # Get GHL connector
        ghl_connector = integration_manager.get_ghl_connector()
        
        # Prepare opportunity data
        opportunity_data = {
            "pipeline_id": pipeline_data.get("pipeline_id"),
            "stage_id": pipeline_data.get("stage_id"),
            "title": f"Service Request #{service_request.id} - {service_request.appliance_type}",
            "monetary_value": pipeline_data.get("monetary_value", 0),
            "description": service_request.issue_description
        }
        
        # Create opportunity in GHL
        result = await ghl_connector.create_opportunity(customer.ghl_contact_id, opportunity_data)
        
        # Update service request with GHL opportunity ID
        service_request.ghl_opportunity_id = result.get("id")
        db.commit()
        
        # Log the activity
        log_agent_activity("api", "integrations", "create_ghl_opportunity", {"service_request_id": service_request_id})
        
        return {
            "success": True,
            "opportunity_id": service_request.ghl_opportunity_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create opportunity in GHL: {str(e)}"
        )

@ghl_router.post("/create-appointment/{service_request_id}", response_model=Dict[str, Any])
async def create_ghl_appointment(
    service_request_id: int,
    appointment_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Create an appointment in GHL
    """
    try:
        # Get service request from database
        service_request = db.query(ServiceRequest).filter(ServiceRequest.id == service_request_id).first()
        if not service_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service request with ID {service_request_id} not found"
            )
        
        # Get customer
        customer = db.query(Customer).filter(Customer.id == service_request.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {service_request.customer_id} not found"
            )
        
        # Check if customer has GHL contact ID
        if not customer.ghl_contact_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer does not have a GHL contact ID. Sync customer with GHL first."
            )
        
        # Get GHL connector
        ghl_connector = integration_manager.get_ghl_connector()
        
        # Prepare appointment data
        ghl_appointment_data = {
            "calendar_id": appointment_data.get("calendar_id"),
            "title": f"Service Appointment - {service_request.appliance_type}",
            "description": service_request.issue_description,
            "date": appointment_data.get("date"),
            "time": appointment_data.get("time"),
            "duration": appointment_data.get("duration", 60)
        }
        
        # Create appointment in GHL
        result = await ghl_connector.create_appointment(customer.ghl_contact_id, ghl_appointment_data)
        
        # Update service request with GHL appointment ID if applicable
        if hasattr(service_request, 'ghl_appointment_id'):
            service_request.ghl_appointment_id = result.get("id")
            db.commit()
        
        # Log the activity
        log_agent_activity("api", "integrations", "create_ghl_appointment", {"customer_id": customer.id})
        
        return {
            "success": True,
            "appointment_id": result.get("id")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create appointment in GHL: {str(e)}"
        )

# Kickserv Routes
@kickserv_router.post("/sync-customer/{customer_id}", response_model=Dict[str, Any])
async def sync_customer_with_kickserv(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Sync a customer with Kickserv
    """
    try:
        # Get customer from database
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        # Get Kickserv connector
        kickserv_connector = integration_manager.get_kickserv_connector()
        
        # Prepare customer data for Kickserv
        customer_data = {
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address,
            "city": customer.city,
            "state": customer.state,
            "zip_code": customer.zip_code
        }
        
        # Sync with Kickserv
        result = await kickserv_connector.sync_customer(customer_data)
        
        # Update customer with Kickserv customer ID
        customer.kickserv_customer_id = result.get("id")
        db.commit()
        
        # Log the activity
        log_agent_activity("api", "integrations", "sync_kickserv_customer", {"customer_id": customer_id})
        
        return {
            "success": True,
            "kickserv_customer_id": customer.kickserv_customer_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync with Kickserv: {str(e)}"
        )

@kickserv_router.post("/create-job/{service_request_id}", response_model=Dict[str, Any])
async def create_kickserv_job(
    service_request_id: int,
    job_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Create a job in Kickserv for a service request
    """
    try:
        # Get service request from database
        service_request = db.query(ServiceRequest).filter(ServiceRequest.id == service_request_id).first()
        if not service_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service request with ID {service_request_id} not found"
            )
        
        # Get customer
        customer = db.query(Customer).filter(Customer.id == service_request.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {service_request.customer_id} not found"
            )
        
        # Check if customer has Kickserv customer ID
        if not hasattr(customer, 'kickserv_customer_id') or not customer.kickserv_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer does not have a Kickserv customer ID. Sync customer with Kickserv first."
            )
        
        # Get Kickserv connector
        kickserv_connector = integration_manager.get_kickserv_connector()
        
        # Prepare job data
        kickserv_job_data = {
            "description": service_request.issue_description,
            "scheduled_date": job_data.get("scheduled_date"),
            "status": job_data.get("status", "scheduled"),
            "appliance_type": service_request.appliance_type,
            "brand": service_request.brand,
            "model": service_request.model,
            "serial_number": service_request.serial_number,
            "line_items": job_data.get("line_items", [])
        }
        
        # Create job in Kickserv
        result = await kickserv_connector.create_job(customer.kickserv_customer_id, kickserv_job_data)
        
        # Update service request with Kickserv job ID
        if hasattr(service_request, 'kickserv_job_id'):
            service_request.kickserv_job_id = result.get("id")
            db.commit()
        
        # Log the activity
        log_agent_activity("api", "integrations", "create_kickserv_job", {"service_request_id": service_request_id})
        
        return {
            "success": True,
            "kickserv_job_id": result.get("id")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job in Kickserv: {str(e)}"
        )

@kickserv_router.post("/create-invoice/{service_request_id}", response_model=Dict[str, Any])
async def create_kickserv_invoice(
    service_request_id: int,
    invoice_data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Create an invoice in Kickserv for a service request
    """
    try:
        # Get service request from database
        service_request = db.query(ServiceRequest).filter(ServiceRequest.id == service_request_id).first()
        if not service_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service request with ID {service_request_id} not found"
            )
        
        # Check if service request has Kickserv job ID
        if not hasattr(service_request, 'kickserv_job_id') or not service_request.kickserv_job_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service request does not have a Kickserv job ID. Create a job in Kickserv first."
            )
        
        # Get Kickserv connector
        kickserv_connector = integration_manager.get_kickserv_connector()
        
        # Prepare invoice data
        kickserv_invoice_data = {
            "issued_date": invoice_data.get("issued_date"),
            "due_date": invoice_data.get("due_date"),
            "line_items": invoice_data.get("line_items", [])
        }
        
        # Create invoice in Kickserv
        result = await kickserv_connector.create_invoice(service_request.kickserv_job_id, kickserv_invoice_data)
        
        # Update service request with Kickserv invoice ID if applicable
        if hasattr(service_request, 'kickserv_invoice_id'):
            service_request.kickserv_invoice_id = result.get("id")
            db.commit()
        
        # Log the activity
        log_agent_activity("api", "integrations", "create_kickserv_invoice", {"service_request_id": service_request_id})
        
        return {
            "success": True,
            "kickserv_invoice_id": result.get("id")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invoice in Kickserv: {str(e)}"
        )

@kickserv_router.get("/jobs/{customer_id}", response_model=List[Dict[str, Any]])
async def get_kickserv_jobs(
    customer_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    integration_manager: IntegrationManager = Depends(get_integration_manager)
):
    """
    Get jobs from Kickserv for a customer
    """
    try:
        # Get customer from database
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        # Check if customer has Kickserv customer ID
        if not hasattr(customer, 'kickserv_customer_id') or not customer.kickserv_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer does not have a Kickserv customer ID. Sync customer with Kickserv first."
            )
        
        # Get Kickserv connector
        kickserv_connector = integration_manager.get_kickserv_connector()
        
        # Get jobs from Kickserv
        jobs = await kickserv_connector.get_jobs(customer.kickserv_customer_id, status)
        
        return jobs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get jobs from Kickserv: {str(e)}"
        )

# Register the sub-routers
router.include_router(ghl_router)
router.include_router(kickserv_router) 