"""
Connector for Go High Level CRM integration
"""
import aiohttp
import json
from typing import Dict, Any, List, Optional

class GHLConnector:
    """
    Connector for Go High Level CRM integration
    Handles synchronization of customers, appointments, and tasks
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the GHL connector
        
        Args:
            config: GHL configuration with API key and location ID
        """
        self.config = config
        self.api_key = config.get("api_key")
        self.location_id = config.get("location_id")
        self.base_url = config.get("base_url", "https://services.leadconnectorhq.com")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Version": "2021-04-15",
            "Content-Type": "application/json"
        }
    
    async def sync_contact(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync a customer with GHL contact
        
        Args:
            customer_data: Customer data to sync
            
        Returns:
            GHL contact data
        """
        # Prepare contact data for GHL format
        contact_data = {
            "firstName": customer_data.get("first_name", ""),
            "lastName": customer_data.get("last_name", ""),
            "email": customer_data.get("email", ""),
            "phone": customer_data.get("phone", ""),
            "address": {
                "line1": customer_data.get("address_line1", ""),
                "line2": customer_data.get("address_line2", ""),
                "city": customer_data.get("city", ""),
                "state": customer_data.get("state", ""),
                "postalCode": customer_data.get("zip", ""),
                "country": "US"  # Default, can be made configurable
            },
            "locationId": self.location_id,
            "tags": ["Appliance Repair", "AI System"]
        }
        
        # Check if customer has GHL ID
        if "ghl_contact_id" in customer_data and customer_data["ghl_contact_id"]:
            # Update existing contact
            url = f"{self.base_url}/v1/contacts/{customer_data['ghl_contact_id']}"
            method = "PUT"
        else:
            # Create new contact
            url = f"{self.base_url}/v1/contacts"
            method = "POST"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, 
                url, 
                headers=self.headers, 
                json=contact_data
            ) as response:
                if response.status not in (200, 201):
                    error_text = await response.text()
                    raise ValueError(f"GHL API error: {response.status} - {error_text}")
                
                result = await response.json()
                return result
    
    async def create_opportunity(self, service_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an opportunity in GHL
        
        Args:
            service_request: Service request data
            
        Returns:
            GHL opportunity data
        """
        # Prepare opportunity data
        opportunity_data = {
            "name": f"Service Request #{service_request['id']} - {service_request.get('appliance_type', 'Appliance')} Repair",
            "contactId": service_request.get("ghl_contact_id"),
            "pipelineId": self.config.get("pipeline_id"),
            "status": "open",
            "monetaryValue": service_request.get("estimated_cost", 0),
            "locationId": self.location_id,
            "customFields": [
                {
                    "id": self.config.get("custom_fields", {}).get("service_request_id"),
                    "value": str(service_request["id"])
                },
                {
                    "id": self.config.get("custom_fields", {}).get("appliance_type"),
                    "value": service_request.get("appliance_type", "")
                },
                {
                    "id": self.config.get("custom_fields", {}).get("issue_description"),
                    "value": service_request.get("issue_description", "")
                }
            ]
        }
        
        # Create opportunity
        url = f"{self.base_url}/v1/opportunities"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                "POST", 
                url, 
                headers=self.headers, 
                json=opportunity_data
            ) as response:
                if response.status != 201:
                    error_text = await response.text()
                    raise ValueError(f"GHL API error: {response.status} - {error_text}")
                
                result = await response.json()
                return result
    
    async def create_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an appointment in GHL
        
        Args:
            appointment_data: Appointment data
            
        Returns:
            GHL calendar event data
        """
        from datetime import datetime, timedelta
        
        # Calculate end time
        start_time = datetime.fromisoformat(appointment_data["start_time"])
        duration_minutes = appointment_data.get("duration_minutes", 60)
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Prepare calendar event data
        event_data = {
            "title": f"Service Appointment - {appointment_data.get('service_type', 'Repair')}",
            "description": appointment_data.get("notes", ""),
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "contactId": appointment_data.get("ghl_contact_id"),
            "locationId": self.location_id,
            "calendarId": self.config.get("calendar_id"),
            "allDay": False,
            "isAllDayEvent": False,
            "sendNotification": True
        }
        
        # Create calendar event
        url = f"{self.base_url}/v1/calendars/{self.config.get('calendar_id')}/events"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                "POST", 
                url, 
                headers=self.headers, 
                json=event_data
            ) as response:
                if response.status != 201:
                    error_text = await response.text()
                    raise ValueError(f"GHL API error: {response.status} - {error_text}")
                
                result = await response.json()
                return result
    
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a task in GHL
        
        Args:
            task_data: Task data
            
        Returns:
            GHL task data
        """
        # Prepare task data
        ghl_task_data = {
            "title": task_data.get("title", "New Task"),
            "description": task_data.get("description", ""),
            "dueDate": task_data.get("due_date"),
            "assignedTo": task_data.get("assigned_to", self.config.get("default_assignee")),
            "contactId": task_data.get("ghl_contact_id"),
            "locationId": self.location_id,
            "status": "pending"
        }
        
        # Create task
        url = f"{self.base_url}/v1/tasks"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                "POST", 
                url, 
                headers=self.headers, 
                json=ghl_task_data
            ) as response:
                if response.status != 201:
                    error_text = await response.text()
                    raise ValueError(f"GHL API error: {response.status} - {error_text}")
                
                result = await response.json()
                return result
    
    async def get_contacts(self, search_query: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get contacts from GHL with optional search
        
        Args:
            search_query: Optional search query
            limit: Maximum number of results to return
            
        Returns:
            List of GHL contacts
        """
        url = f"{self.base_url}/v1/contacts"
        params = {
            "locationId": self.location_id,
            "limit": str(limit)
        }
        
        if search_query:
            params["query"] = search_query
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                "GET", 
                url, 
                headers=self.headers, 
                params=params
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"GHL API error: {response.status} - {error_text}")
                
                result = await response.json()
                return result.get("contacts", []) 