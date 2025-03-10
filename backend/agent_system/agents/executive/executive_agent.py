"""
Executive Agent powered by Claude 3.7 Sonnet
Responsible for high-level planning and coordination
"""
import json
import re
from typing import Dict, Any, List, Optional

from utils.logging import log_agent_activity

class ExecutiveAgent:
    """
    Executive Agent powered by Claude 3.7 Sonnet
    Responsible for high-level planning and coordination
    """
    
    def __init__(self, llm_connector, config):
        """
        Initialize the executive agent
        
        Args:
            llm_connector: LLM connector for API calls
            config: Configuration for the agent
        """
        self.llm_connector = llm_connector
        self.config = config
        self.model = "claude-3-sonnet-20240229"
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Load the system prompt for the executive agent"""
        try:
            with open(self.config["system_prompt_path"], "r") as file:
                return file.read()
        except (FileNotFoundError, KeyError):
            # Return a default system prompt if file not found
            return """
            You are the Executive Agent in a hierarchical AI system for an appliance repair business.
            Your role is to analyze user requests, create workflow plans, and coordinate the work of specialized manager agents.
            You should break down complex tasks, delegate to appropriate manager agents, and synthesize final responses.
            Always be thorough, professional, and focused on providing excellent service to appliance repair customers.
            """
            
    async def analyze_request(self, request: dict) -> dict:
        """
        Analyze a request and create a workflow plan
        
        Args:
            request: The incoming request
            
        Returns:
            A workflow plan with steps to execute
        """
        log_agent_activity("executive", "claude", "analyze_request", {"request_id": request.get('id', 'unknown')})
        
        json_structure = """
{
    "domain": "primary domain of the request",
    "priority": "low/medium/high/urgent",
    "required_agents": ["list of required manager agents"],
    "steps": [
        {
            "agent_type": "manager or task",
            "agent_name": "name of the agent",
            "manager": "parent manager name (only for task agents)",
            "type": "step type/name",
            "task": {
                "type": "task type",
                "description": "task description",
                "parameters": {},
                "context": {}
            }
        }
    ]
}
"""
        
        prompt = f"""
        Analyze the following request and create a detailed workflow plan:
        
        REQUEST ID: {request.get('id', 'unknown')}
        REQUEST TYPE: {request.get('type', 'unknown')}
        USER: {request.get('user', 'unknown')}
        CONTENT: {request.get('content', '')}
        CONTEXT: {json.dumps(request.get('context', {}), indent=2)}
        
        Your task is to:
        1. Determine the primary domain this request belongs to
        2. Identify which manager agents should handle parts of this request
        3. Break down the request into specific tasks for each agent
        4. Define the sequence of steps needed to fulfill the request
        5. Set priority levels for each step
        
        Output your analysis as a structured workflow plan in JSON format with the following structure:
        {json_structure}
        """
        
        response = await self.llm_connector.generate(
            model=self.model,
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=4000,
            temperature=0.2
        )
        
        # Parse the workflow plan from the response
        try:
            # Find JSON content in the response
            workflow_plan = self._extract_json(response)
            return workflow_plan
        except Exception as e:
            raise ValueError(f"Failed to parse workflow plan: {str(e)}")
            
    async def synthesize_response(self, request: dict, workflow: dict) -> dict:
        """
        Synthesize a final response based on workflow results
        
        Args:
            request: The original request
            workflow: The completed workflow with results
            
        Returns:
            A formatted final response
        """
        log_agent_activity("executive", "claude", "synthesize_response", {"workflow_id": workflow.get('id', 'unknown')})
        
        # Prepare prompt with workflow results
        steps_results = []
        for step in workflow["steps"]:
            step_info = {
                "id": step["id"],
                "type": step["type"],
                "status": step["status"],
                "result": step.get("result", "No result")
            }
            steps_results.append(step_info)
            
        prompt = f"""
        Synthesize a comprehensive response based on the following workflow results:
        
        ORIGINAL REQUEST: {request.get('content', '')}
        
        WORKFLOW RESULTS:
        {json.dumps(steps_results, indent=2)}
        
        Your task is to create a coherent and helpful response that:
        1. Addresses all aspects of the original request
        2. Integrates information from all workflow steps
        3. Provides clear next actions or recommendations
        4. Uses a professional but friendly tone
        5. Is formatted appropriately for the user
        
        Generate a complete response that can be sent directly to the user.
        """
        
        response = await self.llm_connector.generate(
            model=self.model,
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=2000,
            temperature=0.3
        )
        
        return {
            "content": response,
            "format": "text"
        }
        
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