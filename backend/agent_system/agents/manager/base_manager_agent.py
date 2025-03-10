"""
Base class for manager-level agents
Uses GPT-4o for complex reasoning tasks
"""
import json
import re
from typing import Dict, Any, List, Optional

from utils.logging import log_agent_activity

class ManagerAgent:
    """
    Base class for manager-level agents
    Uses GPT-4o for complex reasoning tasks
    """
    
    def __init__(self, llm_connector, config):
        """
        Initialize the manager agent
        
        Args:
            llm_connector: LLM connector for API calls
            config: Configuration for the agent
        """
        self.llm_connector = llm_connector
        self.config = config
        self.model = "gpt-4o"
        self.system_prompt = self._load_system_prompt()
        self.task_agents = {}
        self.agent_name = "base_manager"  # Override in subclasses
        
    def _load_system_prompt(self) -> str:
        """Load the system prompt for this agent"""
        try:
            with open(self.config["system_prompt_path"], "r") as file:
                return file.read()
        except (FileNotFoundError, KeyError):
            # Return a default system prompt if file not found
            return """
            You are a Manager Agent in a hierarchical AI system for an appliance repair business.
            Your role is to handle specialized tasks in your domain and coordinate task agents.
            Always be thorough, professional, and focused on providing excellent service to appliance repair customers.
            """
            
    async def initialize_task_agents(self, llm_connector):
        """
        Initialize task agents for this manager
        
        Args:
            llm_connector: LLM connector for API calls
        """
        # To be implemented by subclasses
        pass
        
    async def execute_task(self, task: dict) -> dict:
        """
        Execute a task assigned to this manager agent
        
        Args:
            task: The task to execute
            
        Returns:
            Results of the task execution
        """
        log_agent_activity("manager", self.agent_name, "execute_task", {"task_type": task.get('type', 'unknown')})
        
        prompt = f"""
        Execute the following task:
        
        TASK TYPE: {task.get('type', 'unknown')}
        TASK DESCRIPTION: {task.get('description', '')}
        TASK PARAMETERS: {json.dumps(task.get('parameters', {}), indent=2)}
        TASK CONTEXT: {json.dumps(task.get('context', {}), indent=2)}
        
        Your task is to:
        1. Analyze the requirements of this task
        2. Determine the best approach to fulfill it
        3. Execute the necessary steps
        4. Return a structured result
        
        Output your result in JSON format.
        """
        
        response = await self.llm_connector.generate(
            model=self.model,
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=2000,
            temperature=0.2
        )
        
        # Parse the result from the response
        try:
            result = self._extract_json(response)
            return result
        except Exception as e:
            raise ValueError(f"Failed to parse task result: {str(e)}")
            
    async def execute_task_agent(self, agent_name: str, task: dict) -> dict:
        """
        Execute a task using a specific task agent
        
        Args:
            agent_name: Name of the task agent to use
            task: The task to execute
            
        Returns:
            Results of the task execution
        """
        if agent_name not in self.task_agents:
            raise ValueError(f"Task agent not found: {agent_name}")
            
        return await self.task_agents[agent_name].execute_task(task)
        
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from text, handling various formats"""
        import json
        import re
        
        # Try to find JSON block
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            json_str = json_match.group(1)
            return json.loads(json_str)
            
        # Try to find JSON without markdown formatting
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)
            
        # Try the whole text as JSON
        return json.loads(text) 