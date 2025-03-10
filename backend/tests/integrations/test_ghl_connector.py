import pytest
import aiohttp
from unittest.mock import patch, AsyncMock, MagicMock
from backend.integrations.ghl import GHLConnector

pytestmark = pytest.mark.asyncio

@pytest.fixture
def ghl_config():
    """Return a sample GHL configuration."""
    return {
        "api_key": "test_api_key",
        "location_id": "test_location_id",
        "base_url": "https://rest.gohighlevel.com/v1/"
    }

@pytest.fixture
def ghl_connector(ghl_config):
    """Return a GHL connector instance with the test configuration."""
    return GHLConnector(**ghl_config)

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

@patch("aiohttp.ClientSession.post")
async def test_sync_contact(mock_post, ghl_connector, customer_data):
    """Test syncing a contact with GHL."""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"contact": {"id": "ghl_contact_123"}}
    mock_post.return_value.__aenter__.return_value = mock_response
    
    # Call the method
    result = await ghl_connector.sync_contact(customer_data)
    
    # Verify the result
    assert result == {"id": "ghl_contact_123"}
    
    # Verify the request
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://rest.gohighlevel.com/v1/contacts/"
    
    # Verify headers
    headers = call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer test_api_key"
    assert headers["Content-Type"] == "application/json"
    
    # Verify payload
    json_data = call_args[1]["json"]
    assert json_data["firstName"] == customer_data["first_name"]
    assert json_data["lastName"] == customer_data["last_name"]
    assert json_data["email"] == customer_data["email"]
    assert json_data["phone"] == customer_data["phone"]
    assert json_data["address"] == customer_data["address"]
    assert json_data["city"] == customer_data["city"]
    assert json_data["state"] == customer_data["state"]
    assert json_data["postalCode"] == customer_data["zip_code"]
    assert json_data["locationId"] == "test_location_id"

@patch("aiohttp.ClientSession.post")
async def test_sync_contact_error(mock_post, ghl_connector, customer_data):
    """Test handling errors when syncing a contact with GHL."""
    # Setup mock response for error
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.json.return_value = {"error": "Invalid data"}
    mock_post.return_value.__aenter__.return_value = mock_response
    
    # Call the method and expect an exception
    with pytest.raises(Exception) as excinfo:
        await ghl_connector.sync_contact(customer_data)
    
    # Verify the exception message
    assert "Failed to sync contact with GHL" in str(excinfo.value)

@patch("aiohttp.ClientSession.post")
async def test_create_opportunity(mock_post, ghl_connector):
    """Test creating an opportunity in GHL."""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"opportunity": {"id": "ghl_opportunity_123"}}
    mock_post.return_value.__aenter__.return_value = mock_response
    
    # Test data
    contact_id = "ghl_contact_123"
    opportunity_data = {
        "pipeline_id": "pipe_123",
        "stage_id": "stage_456",
        "title": "Test Opportunity",
        "monetary_value": 500
    }
    
    # Call the method
    result = await ghl_connector.create_opportunity(contact_id, opportunity_data)
    
    # Verify the result
    assert result == {"id": "ghl_opportunity_123"}
    
    # Verify the request
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://rest.gohighlevel.com/v1/opportunities/"
    
    # Verify payload
    json_data = call_args[1]["json"]
    assert json_data["contactId"] == contact_id
    assert json_data["pipelineId"] == opportunity_data["pipeline_id"]
    assert json_data["stageId"] == opportunity_data["stage_id"]
    assert json_data["name"] == opportunity_data["title"]
    assert json_data["monetaryValue"] == opportunity_data["monetary_value"]

@patch("aiohttp.ClientSession.post")
async def test_create_appointment(mock_post, ghl_connector):
    """Test creating an appointment in GHL."""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"appointment": {"id": "ghl_appointment_123"}}
    mock_post.return_value.__aenter__.return_value = mock_response
    
    # Test data
    contact_id = "ghl_contact_123"
    appointment_data = {
        "calendar_id": "cal_123",
        "title": "Test Appointment",
        "description": "Test Description",
        "date": "2023-12-31",
        "time": "10:00:00",
        "duration": 60
    }
    
    # Call the method
    result = await ghl_connector.create_appointment(contact_id, appointment_data)
    
    # Verify the result
    assert result == {"id": "ghl_appointment_123"}
    
    # Verify the request
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://rest.gohighlevel.com/v1/appointments/"
    
    # Verify payload
    json_data = call_args[1]["json"]
    assert json_data["contactId"] == contact_id
    assert json_data["calendarId"] == appointment_data["calendar_id"]
    assert json_data["title"] == appointment_data["title"]
    assert json_data["description"] == appointment_data["description"]
    assert json_data["startDate"] == appointment_data["date"]
    assert json_data["startTime"] == appointment_data["time"]
    assert json_data["durationInMinutes"] == appointment_data["duration"]

@patch("aiohttp.ClientSession.post")
async def test_create_task(mock_post, ghl_connector):
    """Test creating a task in GHL."""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"task": {"id": "ghl_task_123"}}
    mock_post.return_value.__aenter__.return_value = mock_response
    
    # Test data
    contact_id = "ghl_contact_123"
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "due_date": "2023-12-31",
        "assigned_to": "user_123"
    }
    
    # Call the method
    result = await ghl_connector.create_task(contact_id, task_data)
    
    # Verify the result
    assert result == {"id": "ghl_task_123"}
    
    # Verify the request
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "https://rest.gohighlevel.com/v1/tasks/"
    
    # Verify payload
    json_data = call_args[1]["json"]
    assert json_data["contactId"] == contact_id
    assert json_data["title"] == task_data["title"]
    assert json_data["description"] == task_data["description"]
    assert json_data["dueDate"] == task_data["due_date"]
    assert json_data["assignedTo"] == task_data["assigned_to"]

@patch("aiohttp.ClientSession.get")
async def test_get_contacts(mock_get, ghl_connector):
    """Test retrieving contacts from GHL."""
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "contacts": [
            {"id": "ghl_contact_1", "firstName": "John", "lastName": "Doe"},
            {"id": "ghl_contact_2", "firstName": "Jane", "lastName": "Smith"}
        ]
    }
    mock_get.return_value.__aenter__.return_value = mock_response
    
    # Call the method
    result = await ghl_connector.get_contacts()
    
    # Verify the result
    assert len(result) == 2
    assert result[0]["id"] == "ghl_contact_1"
    assert result[1]["id"] == "ghl_contact_2"
    
    # Verify the request
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args[0][0] == "https://rest.gohighlevel.com/v1/contacts/"
    
    # Verify headers
    headers = call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer test_api_key" 