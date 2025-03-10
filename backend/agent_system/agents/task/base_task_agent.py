"""
Base class for task-specific agents
Uses GPT-4o-mini for well-defined tasks
"""
import json
import re
from typing import Dict, Any, List, Optional

from utils.logging import log_agent_activity

class TaskAgent:
    """
    Base class for task-specific agents
    Uses GPT-4o-mini for well-defined tasks
    """
    
    def __init__(self, llm_connector, config):
        """
        Initialize the task agent
        
        Args:
            llm_connector: LLM connector for API calls
            config: Configuration for the agent
        """
        self.llm_connector = llm_connector
        self.config = config
        self.model = "gpt-4o-mini"  # Default model, can be overridden
        self.system_prompt = self._load_system_prompt()
        self.agent_name = "base_task"  # Override in subclasses
        self.parent_manager = None  # Set by the parent manager
        
    def _load_system_prompt(self) -> str:
        """Load the system prompt for this agent"""
        try:
            with open(self.config["system_prompt_path"], "r") as file:
                return file.read()
        except (FileNotFoundError, KeyError):
            # Return a default system prompt if file not found
            return """
            You are a Task Agent in a hierarchical AI system for an appliance repair business.
            Your role is to handle specific, well-defined tasks in your domain.
            Always be thorough, professional, and focused on providing excellent service to appliance repair customers.
            """
            
    async def execute_task(self, task: dict) -> dict:
        """
        Execute a specific task
        
        Args:
            task: The task to execute
            
        Returns:
            Results of the task execution
        """
        log_agent_activity("task", self.agent_name, "execute_task", {"task_type": task.get('type', 'unknown')})
        
        prompt = f"""
        Execute the following task:
        
        TASK TYPE: {task.get('type', 'unknown')}
        TASK DESCRIPTION: {task.get('description', '')}
        TASK PARAMETERS: {json.dumps(task.get('parameters', {}), indent=2)}
        TASK CONTEXT: {json.dumps(task.get('context', {}), indent=2)}
        
        Provide your result in JSON format.
        """
        
        response = await self.llm_connector.generate(
            model=self.model,
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=1000,
            temperature=0.1
        )
        
        # Parse the result from the response
        try:
            result = self._extract_json(response)
            return result
        except Exception as e:
            raise ValueError(f"Failed to parse task result: {str(e)}")
            
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