"""
Tests for the Kickserv connector.
"""
import pytest
import aiohttp
from unittest.mock import patch, AsyncMock, MagicMock
from backend.integrations.kickserv import KickservConnector

pytestmark = pytest.mark.asyncio

@pytest.fixture
def kickserv_config():
    """Return a sample Kickserv configuration."""
    return {
        "api_key": "test_api_key",
        "account_name": "test_account",
        "base_url": "https://api.kickserv.com/v1"
    }

@pytest.fixture
def kickserv_connector(kickserv_config):
    """Return a Kickserv connector instance with the test configuration."""
    return KickservConnector(**kickserv_config)

@pytest.fixture
def customer_data():
    """Return sample customer data."""
    return {
        "first_name": "Test",
        "last_name": "Customer",
        "email": "test@example.com",
        "phone": "555-123-4567",
        "address": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345"
    }

@patch("aiohttp.ClientSession.get")
async def test_find_customer_by_email(mock_get, kickserv_connector):
    """Test finding a customer by email."""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = [
        {"id": "123", "email": "test@example.com", "first_name": "Test", "last_name": "Customer"},
        {"id": "456", "email": "other@example.com", "first_name": "Other", "last_name": "Person"}
    ]
    mock_get.return_value.__aenter__.return_value = mock_response
    
    # Call the method
    result = await kickserv_connector._find_customer_by_email("test@example.com")
    
    # Verify the result
    assert result is not None
    assert result["id"] == "123"
    assert result["email"] == "test@example.com"
    
    # Verify the request
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args[0][0] == "https://api.kickserv.com/v1/test_account/customers"
    
    # Verify headers
    headers = call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer test_api_key"
    
    # Verify params
    params = call_args[1]["params"]
    assert params["q"] == "test@example.com"

@patch("aiohttp.ClientSession.get")
async def test_find_customer_by_email_not_found(mock_get, kickserv_connector):
    """Test finding a customer by email when not found."""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = [
        {"id": "456", "email": "other@example.com", "first_name": "Other", "last_name": "Person"}
    ]
    mock_get.return_value.__aenter__.return_value = mock_response
    
    # Call the method
    result = await kickserv_connector._find_customer_by_email("test@example.com")
    
    # Verify the result
    assert result is None

@patch("aiohttp.ClientSession.post")
async def test_create_customer(mock_post, kickserv_connector, customer_data):
    """Test creating a customer in Kickserv."""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 201
    mock_response.json.return_value = {"id": "789", "first_name": "Test", "last_name": "Customer"}
    mock_post.return_value.__aenter__.return_value = mock_response
    
    # Call the method
    result = await kickserv_connector._create_customer(customer_data)
    
    # Verify the result
    assert result["id"] == "789"
    
    # Verify the request
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://api.kickserv.com/v1/test_account/customers"
    
    # Verify headers
    headers = call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer test_api_key"
    assert headers["Content-Type"] == "application/json"
    
    # Verify payload
    json_data = call_args[1]["json"]
    assert json_data["first_name"] == customer_data["first_name"]
    assert json_data["last_name"] == customer_data["last_name"]
    assert json_data["email"] == customer_data["email"]
    assert json_data["phone"] == customer_data["phone"]

@patch("aiohttp.ClientSession.put")
async def test_update_customer(mock_put, kickserv_connector, customer_data):
    """Test updating a customer in Kickserv."""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"id": "123", "first_name": "Updated", "last_name": "Customer"}
    mock_put.return_value.__aenter__.return_value = mock_response
    
    # Call the method
    result = await kickserv_connector._update_customer("123", customer_data)
    
    # Verify the result
    assert result["id"] == "123"
    assert result["first_name"] == "Updated"
    
    # Verify the request
    mock_put.assert_called_once()
    call_args = mock_put.call_args
    assert call_args[0][0] == "https://api.kickserv.com/v1/test_account/customers/123"
    
    # Verify headers
    headers = call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer test_api_key"
    assert headers["Content-Type"] == "application/json"
    
    # Verify payload
    json_data = call_args[1]["json"]
    assert json_data["first_name"] == customer_data["first_name"]
    assert json_data["last_name"] == customer_data["last_name"]

@patch("backend.integrations.kickserv.connector.KickservConnector._find_customer_by_email")
@patch("backend.integrations.kickserv.connector.KickservConnector._create_customer")
@patch("backend.integrations.kickserv.connector.KickservConnector._update_customer")
async def test_sync_customer_new(mock_update, mock_create, mock_find, kickserv_connector, customer_data):
    """Test syncing a new customer with Kickserv."""
    # Setup mocks
    mock_find.return_value = None
    mock_create.return_value = {"id": "789", "first_name": "Test", "last_name": "Customer"}
    
    # Call the method
    result = await kickserv_connector.sync_customer(customer_data)
    
    # Verify the result
    assert result["id"] == "789"
    
    # Verify the mocks were called correctly
    mock_find.assert_called_once_with(customer_data["email"])
    mock_create.assert_called_once()
    mock_update.assert_not_called()

@patch("backend.integrations.kickserv.connector.KickservConnector._find_customer_by_email")
@patch("backend.integrations.kickserv.connector.KickservConnector._create_customer")
@patch("backend.integrations.kickserv.connector.KickservConnector._update_customer")
async def test_sync_customer_existing(mock_update, mock_create, mock_find, kickserv_connector, customer_data):
    """Test syncing an existing customer with Kickserv."""
    # Setup mocks
    mock_find.return_value = {"id": "123", "email": "test@example.com"}
    mock_update.return_value = {"id": "123", "first_name": "Updated", "last_name": "Customer"}
    
    # Call the method
    result = await kickserv_connector.sync_customer(customer_data)
    
    # Verify the result
    assert result["id"] == "123"
    
    # Verify the mocks were called correctly
    mock_find.assert_called_once_with(customer_data["email"])
    mock_update.assert_called_once_with("123", customer_data)
    mock_create.assert_not_called()

@patch("aiohttp.ClientSession.post")
async def test_create_job(mock_post, kickserv_connector):
    """Test creating a job in Kickserv."""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 201
    mock_response.json.return_value = {"id": "job_123", "description": "Test job"}
    mock_post.return_value.__aenter__.return_value = mock_response
    
    # Test data
    customer_id = "cust_123"
    job_data = {
        "description": "Test job",
        "scheduled_date": "2023-12-31",
        "status": "scheduled",
        "appliance_type": "Refrigerator",
        "brand": "TestBrand",
        "model": "TestModel",
        "serial_number": "SN12345",
        "line_items": []
    }
    
    # Call the method
    result = await kickserv_connector.create_job(customer_id, job_data)
    
    # Verify the result
    assert result["id"] == "job_123"
    
    # Verify the request
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://api.kickserv.com/v1/test_account/jobs"
    
    # Verify payload
    json_data = call_args[1]["json"]
    assert json_data["customer_id"] == customer_id
    assert json_data["description"] == job_data["description"]
    assert json_data["scheduled_on"] == job_data["scheduled_date"]
    assert json_data["status"] == job_data["status"]
    assert json_data["custom_fields_attributes"]["appliance_type"] == job_data["appliance_type"]

@patch("aiohttp.ClientSession.get")
async def test_get_jobs(mock_get, kickserv_connector):
    """Test getting jobs from Kickserv."""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = [
        {"id": "job_123", "customer_id": "cust_123", "description": "Job 1", "status": "scheduled"},
        {"id": "job_456", "customer_id": "cust_123", "description": "Job 2", "status": "completed"}
    ]
    mock_get.return_value.__aenter__.return_value = mock_response
    
    # Call the method
    result = await kickserv_connector.get_jobs("cust_123", "scheduled")
    
    # Verify the result
    assert len(result) == 2
    assert result[0]["id"] == "job_123"
    assert result[1]["id"] == "job_456"
    
    # Verify the request
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args[0][0] == "https://api.kickserv.com/v1/test_account/jobs"
    
    # Verify params
    params = call_args[1]["params"]
    assert params["customer_id"] == "cust_123"
    assert params["status"] == "scheduled"

@patch("aiohttp.ClientSession.post")
async def test_create_invoice(mock_post, kickserv_connector):
    """Test creating an invoice in Kickserv."""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 201
    mock_response.json.return_value = {"id": "inv_123", "job_id": "job_123"}
    mock_post.return_value.__aenter__.return_value = mock_response
    
    # Test data
    job_id = "job_123"
    invoice_data = {
        "issued_date": "2023-12-31",
        "due_date": "2024-01-15",
        "line_items": [
            {"description": "Labor", "quantity": 2, "price": 100}
        ]
    }
    
    # Call the method
    result = await kickserv_connector.create_invoice(job_id, invoice_data)
    
    # Verify the result
    assert result["id"] == "inv_123"
    
    # Verify the request
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://api.kickserv.com/v1/test_account/invoices"
    
    # Verify payload
    json_data = call_args[1]["json"]
    assert json_data["job_id"] == job_id
    assert json_data["issued_on"] == invoice_data["issued_date"]
    assert json_data["due_on"] == invoice_data["due_date"]
    assert json_data["line_items_attributes"] == invoice_data["line_items"] 