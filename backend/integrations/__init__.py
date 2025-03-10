"""
Integrations package for the OMRA Appliance Repair Business Automation System.
Contains modules for integrating with third-party services and APIs.
"""
import logging
from typing import Dict, Any, List, Optional

from backend.integrations.ghl import GHLConnector
from backend.integrations.kickserv import KickservConnector
from backend.core.config import settings

logger = logging.getLogger("omra")

class IntegrationManager:
    """
    Manages all third-party integrations for the OMRA system.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the integration manager with configuration.
        
        Args:
            config: Configuration dictionary with settings for each integration
        """
        self.config = config
        self._ghl_connector = None
        self._kickserv_connector = None
        
        logger.info("Integration manager initialized")
    
    async def connect_all(self):
        """
        Connect to all enabled integrations.
        """
        # Connect to GHL if enabled
        if self.config.get("ghl", {}).get("enabled", False):
            try:
                ghl_config = self.config.get("ghl", {})
                self._ghl_connector = GHLConnector(
                    api_key=ghl_config.get("api_key", ""),
                    location_id=ghl_config.get("location_id", ""),
                    base_url=ghl_config.get("base_url", "https://rest.gohighlevel.com/v1/")
                )
                logger.info("Connected to GHL")
            except Exception as e:
                logger.error(f"Failed to connect to GHL: {str(e)}")
        
        # Connect to Kickserv if enabled
        if self.config.get("kickserv", {}).get("enabled", False):
            try:
                kickserv_config = self.config.get("kickserv", {})
                self._kickserv_connector = KickservConnector(
                    api_key=kickserv_config.get("api_key", ""),
                    account_name=kickserv_config.get("account_name", ""),
                    base_url=kickserv_config.get("base_url", "https://api.kickserv.com/v1")
                )
                logger.info("Connected to Kickserv")
            except Exception as e:
                logger.error(f"Failed to connect to Kickserv: {str(e)}")
    
    def get_ghl_connector(self) -> GHLConnector:
        """
        Get the GHL connector.
        
        Returns:
            GHL connector instance
            
        Raises:
            Exception: If GHL connector is not initialized
        """
        if self._ghl_connector is None:
            raise Exception("GHL connector not initialized")
        return self._ghl_connector
    
    def get_kickserv_connector(self) -> KickservConnector:
        """
        Get the Kickserv connector.
        
        Returns:
            Kickserv connector instance
            
        Raises:
            Exception: If Kickserv connector is not initialized
        """
        if self._kickserv_connector is None:
            raise Exception("Kickserv connector not initialized")
        return self._kickserv_connector 