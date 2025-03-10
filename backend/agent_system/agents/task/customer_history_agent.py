"""
Task agent responsible for retrieving and analyzing customer history
"""
from typing import Dict, Any

from utils.logging import log_agent_activity
from .base_task_agent import TaskAgent

class CustomerHistoryAgent(TaskAgent):
    """
    Task agent responsible for retrieving and analyzing customer history
    """
    
    def __init__(self, llm_connector, config):
        """
        Initialize the customer history task agent
        
        Args:
            llm_connector: LLM connector for API calls
            config: Configuration for the agent
        """
        super().__init__(llm_connector, config)
        self.agent_name = "customer_history"
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a customer history task
        
        Args:
            task: The task to execute
            
        Returns:
            Results of the task execution
        """
        log_agent_activity("task", self.agent_name, "execute_task", {"task_type": task.get("type", "unknown")})
        
        task_type = task.get("type", "")
        
        if task_type == "get_customer_details":
            return await self._get_customer_details(task)
        elif task_type == "analyze_service_history":
            return await self._analyze_service_history(task)
        else:
            # Default to base implementation for unknown task types
            return await super().execute_task(task)
    
    async def _get_customer_details(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get customer details and history
        
        Args:
            task: Task details
            
        Returns:
            Customer details and history
        """
        # In a real implementation, this would query the database
        # For now, return mock data
        customer_id = task.get("parameters", {}).get("customer_id", "unknown")
        
        # Mock customer data
        return {
            "id": customer_id,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "address": "123 Main St, Anytown, USA",
            "service_history": [
                {
                    "date": "2023-10-15",
                    "type": "Refrigerator Repair",
                    "status": "Completed",
                    "technician": "Mike Smith"
                },
                {
                    "date": "2022-05-22",
                    "type": "Dishwasher Installation",
                    "status": "Completed",
                    "technician": "Sarah Johnson"
                }
            ],
            "appliances": [
                {
                    "type": "Refrigerator",
                    "brand": "Samsung",
                    "model": "RF28R7351SG",
                    "purchase_date": "2021-08-10",
                    "warranty_status": "Active"
                },
                {
                    "type": "Dishwasher",
                    "brand": "Bosch",
                    "model": "SHEM63W55N",
                    "purchase_date": "2022-05-22",
                    "warranty_status": "Active"
                }
            ]
        }
    
    async def _analyze_service_history(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a customer's service history
        
        Args:
            task: Task details
            
        Returns:
            Analysis of service history
        """
        # In a real implementation, this would analyze actual customer data
        # For now, return mock analysis
        return {
            "total_service_requests": 2,
            "most_recent_service": "2023-10-15",
            "most_serviced_appliance": "Refrigerator",
            "average_time_between_services": "17 months",
            "common_issues": ["cooling problems", "water leakage"],
            "recommendations": [
                "Schedule regular maintenance for refrigerator",
                "Consider extended warranty for dishwasher"
            ]
        } 