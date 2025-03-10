"""
Base agent class for AI agents in the OpenManus system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import uuid

from backend.core.logging import log_agent_activity
from backend.core.config import settings

class AgentBase(ABC):
    """
    Base class for all AI agents in the system.
    Defines the common interface and functionality.
    """
    
    def __init__(self, name: str, agent_type: str):
        """
        Initialize the agent.
        
        Args:
            name: Name of the agent
            agent_type: Type of agent (executive, manager, task)
        """
        self.name = name
        self.agent_type = agent_type
        self.agent_id = str(uuid.uuid4())
        
        # Log agent initialization
        log_agent_activity(
            agent_type=self.agent_type,
            agent_name=self.name,
            action="initialized",
            details={"agent_id": self.agent_id}
        )
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return the result.
        
        Args:
            input_data: Input data for the agent to process
            
        Returns:
            Dict containing the agent's response
        """
        pass
    
    async def _pre_process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pre-process the input data before sending it to the LLM.
        
        Args:
            input_data: Raw input data
            
        Returns:
            Processed input data
        """
        # Log pre-processing
        log_agent_activity(
            agent_type=self.agent_type,
            agent_name=self.name,
            action="pre_processing",
            details={"input_keys": list(input_data.keys())}
        )
        return input_data
    
    async def _post_process(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process the output data from the LLM.
        
        Args:
            output_data: Raw output data from the LLM
            
        Returns:
            Processed output data
        """
        # Log post-processing
        log_agent_activity(
            agent_type=self.agent_type,
            agent_name=self.name,
            action="post_processing",
            details={"output_keys": list(output_data.keys())}
        )
        return output_data
    
    def _format_system_prompt(self, system_prompt: str) -> str:
        """
        Format the system prompt with agent-specific information.
        
        Args:
            system_prompt: Base system prompt
            
        Returns:
            Formatted system prompt
        """
        return system_prompt.format(
            agent_name=self.name,
            agent_type=self.agent_type,
            agent_id=self.agent_id
        )
    
    async def handle_error(self, error: Exception, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle errors that occur during processing.
        
        Args:
            error: The exception that occurred
            input_data: The input data that caused the error
            
        Returns:
            Error response
        """
        # Log the error
        log_agent_activity(
            agent_type=self.agent_type,
            agent_name=self.name,
            action="error",
            details={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "input_keys": list(input_data.keys())
            }
        )
        
        return {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__
        } 