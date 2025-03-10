"""
Kickserv API connector for the OMRA system.
This module provides integration with the Kickserv API for service management.
"""
import logging
import json
from typing import Dict, Any, List, Optional
import aiohttp

from backend.core.config import settings
from backend.core.logging import log_agent_activity

logger = logging.getLogger("omra")

class KickservConnector:
    """
    Connector for the Kickserv API.
    Handles communication with Kickserv for customer, job, and invoice management.
    """
    
    def __init__(
        self,
        api_key: str,
        account_name: str,
        base_url: str = "https://api.kickserv.com/v1"
    ):
        """
        Initialize the Kickserv connector.
        
        Args:
            api_key: Kickserv API key
            account_name: Kickserv account name
            base_url: Base URL for the Kickserv API
        """
        self.api_key = api_key
        self.account_name = account_name
        self.base_url = f"{base_url}/{account_name}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        logger.info(f"Initialized Kickserv connector for account: {account_name}")

    async def sync_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync a customer with Kickserv.
        Creates a new customer if they don't exist, or updates them if they do.
        
        Args:
            customer_data: Customer data to sync
            
        Returns:
            Kickserv customer data
        """
        # Transform customer data to Kickserv format
        kickserv_customer = {
            "first_name": customer_data.get("first_name", ""),
            "last_name": customer_data.get("last_name", ""),
            "email": customer_data.get("email", ""),
            "phone": customer_data.get("phone", ""),
            "address_attributes": {
                "address1": customer_data.get("address", ""),
                "city": customer_data.get("city", ""),
                "state": customer_data.get("state", ""),
                "zip": customer_data.get("zip_code", "")
            }
        }
        
        # Check if customer already exists
        existing_customer = await self._find_customer_by_email(customer_data.get("email", ""))
        
        if existing_customer:
            # Update existing customer
            customer_id = existing_customer.get("id")
            return await self._update_customer(customer_id, kickserv_customer)
        else:
            # Create new customer
            return await self._create_customer(kickserv_customer)
    
    async def _find_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find a customer by email.
        
        Args:
            email: Customer email
            
        Returns:
            Customer data if found, None otherwise
        """
        if not email:
            return None
            
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/customers"
            params = {"q": email}
            
            try:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        customers = await response.json()
                        # Find customer with matching email
                        for customer in customers:
                            if customer.get("email", "").lower() == email.lower():
                                return customer
                        return None
                    else:
                        logger.error(f"Failed to find customer in Kickserv: {response.status}")
                        return None
            except Exception as e:
                logger.error(f"Error searching for customer in Kickserv: {str(e)}")
                return None
    
    async def _create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new customer in Kickserv.
        
        Args:
            customer_data: Customer data
            
        Returns:
            Created customer data
            
        Raises:
            Exception: If customer creation fails
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/customers"
            
            try:
                async with session.post(url, headers=self.headers, json=customer_data) as response:
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"Created customer in Kickserv: {result.get('id')}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create customer in Kickserv: {response.status} - {error_text}")
                        raise Exception(f"Failed to create customer in Kickserv: {response.status} - {error_text}")
            except Exception as e:
                logger.error(f"Error creating customer in Kickserv: {str(e)}")
                raise
    
    async def _update_customer(self, customer_id: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing customer in Kickserv.
        
        Args:
            customer_id: Kickserv customer ID
            customer_data: Customer data
            
        Returns:
            Updated customer data
            
        Raises:
            Exception: If customer update fails
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/customers/{customer_id}"
            
            try:
                async with session.put(url, headers=self.headers, json=customer_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Updated customer in Kickserv: {customer_id}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to update customer in Kickserv: {response.status} - {error_text}")
                        raise Exception(f"Failed to update customer in Kickserv: {response.status} - {error_text}")
            except Exception as e:
                logger.error(f"Error updating customer in Kickserv: {str(e)}")
                raise
    
    async def create_job(self, customer_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new job in Kickserv.
        
        Args:
            customer_id: Kickserv customer ID
            job_data: Job data
            
        Returns:
            Created job data
            
        Raises:
            Exception: If job creation fails
        """
        # Transform job data to Kickserv format
        kickserv_job = {
            "customer_id": customer_id,
            "description": job_data.get("description", ""),
            "scheduled_on": job_data.get("scheduled_date", ""),
            "status": job_data.get("status", "scheduled"),
            "line_items_attributes": job_data.get("line_items", []),
            "custom_fields_attributes": {
                "appliance_type": job_data.get("appliance_type", ""),
                "brand": job_data.get("brand", ""),
                "model": job_data.get("model", ""),
                "serial_number": job_data.get("serial_number", "")
            }
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/jobs"
            
            try:
                async with session.post(url, headers=self.headers, json=kickserv_job) as response:
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"Created job in Kickserv: {result.get('id')}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create job in Kickserv: {response.status} - {error_text}")
                        raise Exception(f"Failed to create job in Kickserv: {response.status} - {error_text}")
            except Exception as e:
                logger.error(f"Error creating job in Kickserv: {str(e)}")
                raise
    
    async def get_jobs(self, customer_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get jobs from Kickserv.
        
        Args:
            customer_id: Filter by customer ID
            status: Filter by status
            
        Returns:
            List of jobs
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/jobs"
            params = {}
            
            if customer_id:
                params["customer_id"] = customer_id
            
            if status:
                params["status"] = status
            
            try:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        jobs = await response.json()
                        return jobs
                    else:
                        logger.error(f"Failed to get jobs from Kickserv: {response.status}")
                        return []
            except Exception as e:
                logger.error(f"Error getting jobs from Kickserv: {str(e)}")
                return []
    
    async def update_job_status(self, job_id: str, status: str) -> Dict[str, Any]:
        """
        Update a job's status in Kickserv.
        
        Args:
            job_id: Kickserv job ID
            status: New status
            
        Returns:
            Updated job data
            
        Raises:
            Exception: If job update fails
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/jobs/{job_id}"
            job_data = {"status": status}
            
            try:
                async with session.put(url, headers=self.headers, json=job_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Updated job status in Kickserv: {job_id} to {status}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to update job in Kickserv: {response.status} - {error_text}")
                        raise Exception(f"Failed to update job in Kickserv: {response.status} - {error_text}")
            except Exception as e:
                logger.error(f"Error updating job in Kickserv: {str(e)}")
                raise
    
    async def create_invoice(self, job_id: str, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an invoice for a job in Kickserv.
        
        Args:
            job_id: Kickserv job ID
            invoice_data: Invoice data
            
        Returns:
            Created invoice data
            
        Raises:
            Exception: If invoice creation fails
        """
        # Transform invoice data to Kickserv format
        kickserv_invoice = {
            "job_id": job_id,
            "issued_on": invoice_data.get("issued_date", ""),
            "due_on": invoice_data.get("due_date", ""),
            "line_items_attributes": invoice_data.get("line_items", [])
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/invoices"
            
            try:
                async with session.post(url, headers=self.headers, json=kickserv_invoice) as response:
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"Created invoice in Kickserv: {result.get('id')}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create invoice in Kickserv: {response.status} - {error_text}")
                        raise Exception(f"Failed to create invoice in Kickserv: {response.status} - {error_text}")
            except Exception as e:
                logger.error(f"Error creating invoice in Kickserv: {str(e)}")
                raise
    
    async def get_invoices(self, job_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get invoices from Kickserv.
        
        Args:
            job_id: Filter by job ID
            
        Returns:
            List of invoices
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/invoices"
            params = {}
            
            if job_id:
                params["job_id"] = job_id
            
            try:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        invoices = await response.json()
                        return invoices
                    else:
                        logger.error(f"Failed to get invoices from Kickserv: {response.status}")
                        return []
            except Exception as e:
                logger.error(f"Error getting invoices from Kickserv: {str(e)}")
                return [] 