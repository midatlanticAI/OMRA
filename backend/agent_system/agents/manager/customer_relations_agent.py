"""
Manager agent responsible for customer relationships
Handles customer interactions, history, and satisfaction
"""
from typing import Dict, Any

from utils.logging import log_agent_activity
from ..task.communication_agent import CommunicationAgent
from ..task.customer_history_agent import CustomerHistoryAgent
from ..task.satisfaction_analysis_agent import SatisfactionAnalysisAgent
from .base_manager_agent import ManagerAgent

class CustomerRelationsAgent(ManagerAgent):
    """
    Manager agent responsible for customer relationships
    Handles customer interactions, history, and satisfaction
    """
    
    def __init__(self, llm_connector, config):
        """
        Initialize the customer relations manager agent
        
        Args:
            llm_connector: LLM connector for API calls
            config: Configuration for the agent
        """
        super().__init__(llm_connector, config)
        self.agent_name = "customer_relations"
    
    async def initialize_task_agents(self, llm_connector):
        """
        Initialize task agents for customer relations
        
        Args:
            llm_connector: LLM connector for API calls
        """
        log_agent_activity("manager", self.agent_name, "initialize_task_agents")
        
        # Create task agents
        self.task_agents["communication"] = CommunicationAgent(
            llm_connector,
            self.config.get("task_agents", {}).get("communication", {})
        )
        self.task_agents["communication"].parent_manager = self
        
        self.task_agents["customer_history"] = CustomerHistoryAgent(
            llm_connector,
            self.config.get("task_agents", {}).get("customer_history", {})
        )
        self.task_agents["customer_history"].parent_manager = self
        
        self.task_agents["satisfaction_analysis"] = SatisfactionAnalysisAgent(
            llm_connector,
            self.config.get("task_agents", {}).get("satisfaction_analysis", {})
        )
        self.task_agents["satisfaction_analysis"].parent_manager = self
    
    async def handle_customer_inquiry(self, inquiry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a customer inquiry
        
        Args:
            inquiry: Customer inquiry details
            
        Returns:
            Response to the inquiry
        """
        log_agent_activity("manager", self.agent_name, "handle_customer_inquiry", {"customer_id": inquiry.get("customer_id")})
        
        # Get customer history
        customer_history_task = {
            "type": "get_customer_details",
            "description": "Retrieve customer details and history",
            "parameters": {
                "customer_id": inquiry.get("customer_id")
            }
        }
        
        customer_history = await self.task_agents["customer_history"].execute_task(customer_history_task)
        
        # Generate response
        communication_task = {
            "type": "generate_response",
            "description": "Generate response to customer inquiry",
            "parameters": {
                "inquiry_text": inquiry.get("content"),
                "customer_id": inquiry.get("customer_id"),
                "response_type": "inquiry"
            },
            "context": {
                "customer_history": customer_history,
                "appliance_info": inquiry.get("appliance_info", {})
            }
        }
        
        response = await self.task_agents["communication"].execute_task(communication_task)
        
        return {
            "status": "success",
            "response": response.get("response_text"),
            "customer_id": inquiry.get("customer_id"),
            "metadata": {
                "sentiment": response.get("sentiment"),
                "topics": response.get("topics", [])
            }
        }
    
    async def schedule_follow_up(self, service_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a follow-up for a service request
        
        Args:
            service_request: Service request details
            
        Returns:
            Follow-up details
        """
        log_agent_activity("manager", self.agent_name, "schedule_follow_up", {"service_request_id": service_request.get("id")})
        
        # Create follow-up task
        follow_up_task = {
            "type": "schedule_follow_up",
            "description": "Schedule follow-up for service request",
            "parameters": {
                "service_request_id": service_request.get("id"),
                "customer_id": service_request.get("customer_id"),
                "follow_up_type": "post_service"
            },
            "context": {
                "service_date": service_request.get("service_date"),
                "technician": service_request.get("technician"),
                "service_type": service_request.get("service_type")
            }
        }
        
        result = await self.execute_task(follow_up_task)
        
        return result 