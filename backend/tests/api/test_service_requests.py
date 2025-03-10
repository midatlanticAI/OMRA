import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from backend.models.customer import Customer
from backend.models.service_request import ServiceRequest
from backend.schemas.service_request import ServiceRequestCreate, ServiceRequestResponse

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def test_customer(db_session: AsyncSession):
    """Create a test customer in the database."""
    customer_data = {
        "first_name": "Service",
        "last_name": "Customer",
        "email": "service@example.com",
        "phone": "555-123-4567",
        "address": "123 Service St",
        "city": "Service City",
        "state": "SC",
        "zip_code": "12345"
    }
    
    customer = Customer(**customer_data)
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)
    
    yield customer
    
    # Cleanup will cascade to service requests
    await db_session.delete(customer)
    await db_session.commit()

@pytest.fixture
async def test_service_request(db_session: AsyncSession, test_customer: Customer):
    """Create a test service request in the database."""
    tomorrow = datetime.now() + timedelta(days=1)
    service_data = {
        "customer_id": test_customer.id,
        "appliance_type": "Refrigerator",
        "brand": "TestBrand",
        "model": "TestModel",
        "serial_number": "SN12345",
        "issue_description": "Not cooling properly",
        "preferred_date": tomorrow.date(),
        "preferred_time": "morning",
        "status": "pending"
    }
    
    service_request = ServiceRequest(**service_data)
    db_session.add(service_request)
    await db_session.commit()
    await db_session.refresh(service_request)
    
    yield service_request

async def test_create_service_request(client: AsyncClient, test_customer: Customer):
    """Test creating a new service request."""
    tomorrow = datetime.now() + timedelta(days=1)
    service_data = {
        "customer_id": test_customer.id,
        "appliance_type": "Dishwasher",
        "brand": "NewBrand",
        "model": "NewModel",
        "serial_number": "SN67890",
        "issue_description": "Not draining water",
        "preferred_date": tomorrow.strftime("%Y-%m-%d"),
        "preferred_time": "afternoon",
        "status": "pending"
    }
    
    response = await client.post("/api/service-requests/", json=service_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["appliance_type"] == service_data["appliance_type"]
    assert data["brand"] == service_data["brand"]
    assert data["customer_id"] == test_customer.id
    assert "id" in data

async def test_get_service_request(client: AsyncClient, test_service_request: ServiceRequest):
    """Test retrieving a service request by ID."""
    response = await client.get(f"/api/service-requests/{test_service_request.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_service_request.id
    assert data["appliance_type"] == test_service_request.appliance_type
    assert data["brand"] == test_service_request.brand
    assert data["customer_id"] == test_service_request.customer_id

async def test_get_all_service_requests(client: AsyncClient, test_service_request: ServiceRequest):
    """Test retrieving all service requests."""
    response = await client.get("/api/service-requests/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # Check if our test service request is in the list
    request_ids = [request["id"] for request in data]
    assert test_service_request.id in request_ids

async def test_update_service_request(client: AsyncClient, test_service_request: ServiceRequest):
    """Test updating a service request."""
    update_data = {
        "status": "scheduled",
        "technician_notes": "Parts ordered",
        "issue_description": "Updated description"
    }
    
    response = await client.patch(f"/api/service-requests/{test_service_request.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_service_request.id
    assert data["status"] == update_data["status"]
    assert data["technician_notes"] == update_data["technician_notes"]
    assert data["issue_description"] == update_data["issue_description"]
    # Fields not in update_data should remain unchanged
    assert data["appliance_type"] == test_service_request.appliance_type

async def test_delete_service_request(client: AsyncClient, db_session: AsyncSession, test_customer: Customer):
    """Test deleting a service request."""
    # Create a service request to delete
    tomorrow = datetime.now() + timedelta(days=1)
    service_data = {
        "customer_id": test_customer.id,
        "appliance_type": "Washer",
        "brand": "DeleteBrand",
        "model": "DeleteModel",
        "serial_number": "SN-DELETE",
        "issue_description": "To be deleted",
        "preferred_date": tomorrow.date(),
        "preferred_time": "evening",
        "status": "pending"
    }
    
    service_request = ServiceRequest(**service_data)
    db_session.add(service_request)
    await db_session.commit()
    await db_session.refresh(service_request)
    
    # Delete the service request
    response = await client.delete(f"/api/service-requests/{service_request.id}")
    
    assert response.status_code == 204
    
    # Verify service request is deleted
    response = await client.get(f"/api/service-requests/{service_request.id}")
    assert response.status_code == 404

async def test_get_customer_service_requests(client: AsyncClient, test_customer: Customer, test_service_request: ServiceRequest):
    """Test retrieving all service requests for a specific customer."""
    response = await client.get(f"/api/customers/{test_customer.id}/service-requests")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # Check if our test service request is in the list
    request_ids = [request["id"] for request in data]
    assert test_service_request.id in request_ids
    
    # Verify all service requests belong to the test customer
    for request in data:
        assert request["customer_id"] == test_customer.id 