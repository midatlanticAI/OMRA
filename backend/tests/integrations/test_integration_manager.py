import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from backend.integrations import IntegrationManager
from backend.integrations.ghl import GHLConnector

pytestmark = pytest.mark.asyncio

@pytest.fixture
def integration_config():
    """Return a sample integration configuration."""
    return {
        "ghl": {
            "enabled": True,
            "api_key": "test_api_key",
            "location_id": "test_location_id",
            "base_url": "https://rest.gohighlevel.com/v1/"
        },
        "kickserv": {
            "enabled": False,
            "api_key": "test_kickserv_key",
            "account_name": "test_account"
        }
    }

@pytest.fixture
def integration_manager(integration_config):
    """Return an integration manager instance with the test configuration."""
    return IntegrationManager(integration_config)

@patch("backend.integrations.ghl.GHLConnector")
async def test_connect_all(mock_ghl_connector, integration_manager):
    """Test connecting to all enabled integrations."""
    # Setup mock
    mock_ghl_instance = AsyncMock()
    mock_ghl_connector.return_value = mock_ghl_instance
    
    # Call the method
    await integration_manager.connect_all()
    
    # Verify GHL connector was created with correct config
    mock_ghl_connector.assert_called_once_with(
        api_key="test_api_key",
        location_id="test_location_id",
        base_url="https://rest.gohighlevel.com/v1/"
    )
    
    # Verify the connector was stored
    assert integration_manager._ghl_connector == mock_ghl_instance
    
    # Verify Kickserv connector was not created (disabled in config)
    assert integration_manager._kickserv_connector is None

@patch("backend.integrations.ghl.GHLConnector")
async def test_get_ghl_connector(mock_ghl_connector, integration_manager):
    """Test retrieving the GHL connector."""
    # Setup mock
    mock_ghl_instance = AsyncMock()
    mock_ghl_connector.return_value = mock_ghl_instance
    
    # Connect first
    await integration_manager.connect_all()
    
    # Get the connector
    connector = integration_manager.get_ghl_connector()
    
    # Verify the correct connector is returned
    assert connector == mock_ghl_instance

async def test_get_ghl_connector_not_initialized(integration_manager):
    """Test retrieving the GHL connector when not initialized."""
    # Try to get the connector without connecting first
    with pytest.raises(Exception) as excinfo:
        integration_manager.get_ghl_connector()
    
    # Verify the exception message
    assert "GHL connector not initialized" in str(excinfo.value)

async def test_get_kickserv_connector_not_initialized(integration_manager):
    """Test retrieving the Kickserv connector when not initialized."""
    # Try to get the connector without connecting first
    with pytest.raises(Exception) as excinfo:
        integration_manager.get_kickserv_connector()
    
    # Verify the exception message
    assert "Kickserv connector not initialized" in str(excinfo.value)

@patch("backend.integrations.ghl.GHLConnector")
async def test_disabled_integration(mock_ghl_connector, integration_config):
    """Test that disabled integrations are not connected."""
    # Disable GHL in the config
    integration_config["ghl"]["enabled"] = False
    
    # Create manager with updated config
    manager = IntegrationManager(integration_config)
    
    # Connect
    await manager.connect_all()
    
    # Verify GHL connector was not created
    mock_ghl_connector.assert_not_called()
    
    # Verify the connector is not stored
    assert manager._ghl_connector is None

@patch("backend.integrations.ghl.GHLConnector")
async def test_missing_config(mock_ghl_connector):
    """Test handling missing configuration."""
    # Create manager with empty config
    manager = IntegrationManager({})
    
    # Connect
    await manager.connect_all()
    
    # Verify GHL connector was not created
    mock_ghl_connector.assert_not_called()
    
    # Verify the connector is not stored
    assert manager._ghl_connector is None

@patch("backend.integrations.ghl.GHLConnector")
async def test_partial_config(mock_ghl_connector):
    """Test handling partial configuration."""
    # Create manager with partial config
    manager = IntegrationManager({
        "ghl": {
            "enabled": True
            # Missing required config values
        }
    })
    
    # Connect should not raise an exception but log a warning
    await manager.connect_all()
    
    # Verify GHL connector was not created
    mock_ghl_connector.assert_not_called()
    
    # Verify the connector is not stored
    assert manager._ghl_connector is None 