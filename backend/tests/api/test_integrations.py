import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.customer import Customer
from backend.models.service_request import ServiceRequest
from datetime import datetime, timedelta

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def test_customer(db_session: AsyncSession):
    """Create a test customer in the database."""
    customer_data = {
        "first_name": "Integration",
        "last_name": "Test",
        "email": "integration@example.com",
        "phone": "555-987-6543",
        "address": "456 Integration St",
        "city": "Integration City",
        "state": "IT",
        "zip_code": "54321",
        "ghl_contact_id": "ghl_123456"  # Pre-set GHL contact ID
    }
    
    customer = Customer(**customer_data)
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)
    
    yield customer
    
    # Cleanup
    await db_session.delete(customer)
    await db_session.commit()

@pytest.fixture
async def test_service_request(db_session: AsyncSession, test_customer: Customer):
    """Create a test service request in the database."""
    tomorrow = datetime.now() + timedelta(days=1)
    service_data = {
        "customer_id": test_customer.id,
        "appliance_type": "Oven",
        "brand": "IntegrationBrand",
        "model": "IntegrationModel",
        "serial_number": "INT12345",
        "issue_description": "Not heating properly",
        "preferred_date": tomorrow.date(),
        "preferred_time": "morning",
        "status": "pending"
    }
    
    service_request = ServiceRequest(**service_data)
    db_session.add(service_request)
    await db_session.commit()
    await db_session.refresh(service_request)
    
    yield service_request

@patch("backend.integrations.ghl.connector.GHLConnector")
async def test_sync_contact_with_ghl(mock_ghl_connector, client: AsyncClient, test_customer: Customer):
    """Test syncing a customer with GHL."""
    # Setup mock
    mock_instance = AsyncMock()
    mock_instance.sync_contact.return_value = {"id": "new_ghl_id_123"}
    mock_ghl_connector.return_value = mock_instance
    
    # Test customer without GHL ID
    # First, remove the GHL ID
    test_customer.ghl_contact_id = None
    
    response = await client.post(f"/api/integrations/ghl/sync-contact/{test_customer.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "ghl_contact_id" in data
    assert data["ghl_contact_id"] == "new_ghl_id_123"
    
    # Verify the mock was called with correct data
    mock_instance.sync_contact.assert_called_once()
    call_args = mock_instance.sync_contact.call_args[0][0]
    assert call_args["first_name"] == test_customer.first_name
    assert call_args["last_name"] == test_customer.last_name
    assert call_args["email"] == test_customer.email

@patch("backend.integrations.ghl.connector.GHLConnector")
async def test_create_ghl_opportunity(mock_ghl_connector, client: AsyncClient, test_customer: Customer, test_service_request: ServiceRequest):
    """Test creating an opportunity in GHL."""
    # Setup mock
    mock_instance = AsyncMock()
    mock_instance.create_opportunity.return_value = {"id": "opp_123456"}
    mock_ghl_connector.return_value = mock_instance
    
    response = await client.post(
        f"/api/integrations/ghl/create-opportunity/{test_service_request.id}",
        json={"pipeline_id": "pipe_123", "stage_id": "stage_456"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "opportunity_id" in data
    assert data["opportunity_id"] == "opp_123456"
    
    # Verify the mock was called with correct data
    mock_instance.create_opportunity.assert_called_once()
    call_args = mock_instance.create_opportunity.call_args[0]
    assert call_args[0] == test_customer.ghl_contact_id
    assert "pipeline_id" in call_args[1]
    assert "title" in call_args[1]

@patch("backend.integrations.ghl.connector.GHLConnector")
async def test_create_ghl_appointment(mock_ghl_connector, client: AsyncClient, test_customer: Customer, test_service_request: ServiceRequest):
    """Test creating an appointment in GHL."""
    # Setup mock
    mock_instance = AsyncMock()
    mock_instance.create_appointment.return_value = {"id": "apt_123456"}
    mock_ghl_connector.return_value = mock_instance
    
    # Set a specific date for testing
    appointment_date = datetime.now() + timedelta(days=2)
    appointment_time = "10:00:00"
    
    response = await client.post(
        f"/api/integrations/ghl/create-appointment/{test_service_request.id}",
        json={
            "calendar_id": "cal_123",
            "date": appointment_date.strftime("%Y-%m-%d"),
            "time": appointment_time,
            "duration": 60
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "appointment_id" in data
    assert data["appointment_id"] == "apt_123456"
    
    # Verify the mock was called with correct data
    mock_instance.create_appointment.assert_called_once()
    call_args = mock_instance.create_appointment.call_args[0]
    assert call_args[0] == test_customer.ghl_contact_id
    assert "calendar_id" in call_args[1]
    assert "title" in call_args[1]
    assert "date" in call_args[1]
    assert "time" in call_args[1]

@patch("backend.integrations.kickserv.connector.KickservConnector", MagicMock())
async def test_sync_customer_with_kickserv_not_implemented(client: AsyncClient, test_customer: Customer):
    """Test that Kickserv integration returns not implemented."""
    response = await client.post(f"/api/integrations/kickserv/sync-customer/{test_customer.id}")
    
    assert response.status_code == 501
    data = response.json()
    assert "detail" in data
    assert "not implemented" in data["detail"].lower() 