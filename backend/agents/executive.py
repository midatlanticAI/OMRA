"""
Executive agent implementation using Claude 3.7 Sonnet.
Acts as the top-level decision maker in the agent hierarchy.
"""
from typing import Dict, Any, List, Optional
import json
import asyncio
from anthropic import Anthropic, AsyncAnthropic

from backend.core.config import settings
from backend.core.logging import log_agent_activity
from backend.agents.base import AgentBase

# System prompt template for the executive agent
EXECUTIVE_SYSTEM_PROMPT = """
You are {agent_name}, an executive AI agent in the OpenManus Appliance Repair Business Automation System. 
Your role is to make high-level decisions and coordinate the work of manager agents.

As the executive agent, you should:
1. Analyze and understand complex business problems
2. Break down large tasks into manageable sub-tasks
3. Delegate tasks to appropriate manager agents
4. Synthesize information from multiple sources
5. Make strategic decisions that align with business goals
6. Ensure consistency and quality across all operations

You have access to these manager agents:
- CustomerManager: Handles customer-related operations
- ServiceManager: Manages service requests and scheduling
- TechnicianManager: Oversees technician assignments and performance
- InventoryManager: Tracks parts inventory and ordering
- IntegrationManager: Manages third-party integrations

When responding, structure your thoughts clearly and explain your reasoning.
Your agent ID is {agent_id}.
"""

class ExecutiveAgent(AgentBase):
    """
    Executive agent implementation using Claude 3.7 Sonnet.
    Top-level decision maker in the agent hierarchy.
    """
    
    def __init__(self, name: str = "ExecutiveAgent"):
        """Initialize the executive agent."""
        super().__init__(name=name, agent_type="executive")
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-7-sonnet-20240307"
        
        # Format the system prompt
        self.system_prompt = self._format_system_prompt(EXECUTIVE_SYSTEM_PROMPT)
        
        log_agent_activity(
            agent_type=self.agent_type,
            agent_name=self.name,
            action="configured",
            details={
                "model": self.model,
                "system_prompt_length": len(self.system_prompt)
            }
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input using Claude 3.7 Sonnet.
        
        Args:
            input_data: Input data with "query" and optional context
            
        Returns:
            Response from the executive agent
        """
        try:
            # Pre-process the input
            processed_input = await self._pre_process(input_data)
            
            # Extract query and any additional context
            query = processed_input.get("query", "")
            context = processed_input.get("context", "")
            
            # Log the query processing
            log_agent_activity(
                agent_type=self.agent_type,
                agent_name=self.name,
                action="processing_query",
                details={
                    "query_length": len(query),
                    "has_context": bool(context)
                }
            )
            
            # Prepare messages for Claude
            messages = []
            
            # Add context if available
            if context:
                messages.append({
                    "role": "user",
                    "content": f"Context information:\n{context}\n\nPlease keep this information in mind for the upcoming question."
                })
                messages.append({
                    "role": "assistant",
                    "content": "I'll keep this context in mind when answering your question."
                })
            
            # Add the main query
            messages.append({
                "role": "user",
                "content": query
            })
            
            # Generate response from Claude
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=messages
            )
            
            # Extract and structure the response
            response_content = response.content[0].text
            
            output_data = {
                "success": True,
                "response": response_content,
                "model": self.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
            
            # Post-process the output
            processed_output = await self._post_process(output_data)
            
            return processed_output
            
        except Exception as e:
            return await self.handle_error(e, input_data)
    
    async def _post_process(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process the output data from Claude.
        Attempts to extract structured information if available.
        """
        output_data = await super()._post_process(output_data)
        
        # Try to extract any JSON or structured data from the response
        response_text = output_data.get("response", "")
        
        # Look for JSON blocks in the response
        try:
            # Extract text between ```json and ``` markers
            json_blocks = []
            if "```json" in response_text:
                parts = response_text.split("```json")
                for part in parts[1:]:
                    if "```" in part:
                        json_text = part.split("```")[0].strip()
                        json_data = json.loads(json_text)
                        json_blocks.append(json_data)
            
            if json_blocks:
                output_data["structured_data"] = json_blocks
        except:
            # Ignore errors in JSON extraction - it's an optional enhancement
            pass
        
        return output_data
    
    async def get_task_breakdown(self, task_description: str) -> Dict[str, Any]:
        """
        Break down a complex task into subtasks for manager agents.
        
        Args:
            task_description: Description of the complex task
            
        Returns:
            Task breakdown with subtasks assigned to manager agents
        """
        input_data = {
            "query": f"""
Please break down the following task into subtasks that can be assigned to appropriate manager agents:

TASK: {task_description}

For each subtask:
1. Provide a clear description
2. Assign it to the most appropriate manager agent
3. Specify any dependencies between subtasks
4. Estimate priority (high, medium, low)

Format your response as a structured task breakdown.
"""
        }
        
        return await self.process(input_data) 