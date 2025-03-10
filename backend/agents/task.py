"""
Task agent implementation using GPT-4o-mini.
Acts as a specialized task executor in the agent hierarchy.
"""
from typing import Dict, Any, List, Optional
import json
import asyncio
from openai import AsyncOpenAI

from backend.core.config import settings
from backend.core.logging import log_agent_activity
from backend.agents.base import AgentBase

# System prompt template for the task agent
TASK_SYSTEM_PROMPT = """
You are {agent_name}, a task AI agent in the OpenManus Appliance Repair Business Automation System.
Your role is to execute specific specialized tasks efficiently.

As a task agent, you should:
1. Focus on a single, well-defined task
2. Execute the task accurately and efficiently
3. Return structured results in the requested format
4. Alert to any issues or edge cases encountered
5. Stay within your defined scope of responsibility

You should be concise and to-the-point in your responses, focusing on completing the task rather than explaining your process in detail.
Your agent ID is {agent_id}.
"""

class TaskAgent(AgentBase):
    """
    Task agent implementation using GPT-4o-mini.
    Specialized task executor in the agent hierarchy.
    """
    
    def __init__(self, name: str, task_type: str):
        """
        Initialize the task agent.
        
        Args:
            name: Name of the agent (e.g., AppointmentScheduler)
            task_type: Type of task this agent specializes in
        """
        super().__init__(name=name, agent_type="task")
        self.task_type = task_type
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        
        # Format the system prompt
        self.system_prompt = self._format_system_prompt(TASK_SYSTEM_PROMPT)
        
        log_agent_activity(
            agent_type=self.agent_type,
            agent_name=self.name,
            action="configured",
            details={
                "model": self.model,
                "task_type": self.task_type,
                "system_prompt_length": len(self.system_prompt)
            }
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input using GPT-4o-mini.
        
        Args:
            input_data: Input data with "task" and optional "data"
            
        Returns:
            Response from the task agent
        """
        try:
            # Pre-process the input
            processed_input = await self._pre_process(input_data)
            
            # Extract task and data
            task = processed_input.get("task", "")
            data = processed_input.get("data", {})
            
            # Log the task processing
            log_agent_activity(
                agent_type=self.agent_type,
                agent_name=self.name,
                action="processing_task",
                details={
                    "task_length": len(task),
                    "has_data": bool(data)
                }
            )
            
            # Format data as a string if it's a dict
            data_str = ""
            if isinstance(data, dict) and data:
                data_str = json.dumps(data, indent=2)
            elif isinstance(data, str):
                data_str = data
            
            # Construct the prompt
            prompt = f"""
TASK: {task}

{f'DATA:\n{data_str}' if data_str else ''}

Complete this task efficiently and return the results in a structured format.
"""
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Generate response from GPT-4o-mini
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1024,
                temperature=0.1
            )
            
            # Extract and structure the response
            response_content = response.choices[0].message.content
            
            output_data = {
                "success": True,
                "response": response_content,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # Post-process the output
            processed_output = await self._post_process(output_data)
            
            return processed_output
            
        except Exception as e:
            return await self.handle_error(e, input_data)
    
    async def _post_process(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process the output data from GPT-4o-mini.
        Attempts to extract structured information if available.
        """
        output_data = await super()._post_process(output_data)
        
        # Try to extract any JSON or structured data from the response
        response_text = output_data.get("response", "")
        
        try:
            # Look for JSON patterns in the response
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
                data = json.loads(json_text)
                output_data["data"] = data
            elif "```" in response_text:
                parts = response_text.split("```")
                for i in range(1, len(parts), 2):
                    try:
                        text = parts[i].strip()
                        if text.startswith("{") or text.startswith("["):
                            data = json.loads(text)
                            output_data["data"] = data
                            break
                    except:
                        continue
        except:
            # If we can't extract structured data, continue without it
            pass
        
        return output_data
    
    async def execute_specific_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific task with the provided data.
        
        Args:
            task_description: Clear description of the task to execute
            task_data: Data needed for the task
            
        Returns:
            Task execution results
        """
        input_data = {
            "task": task_description,
            "data": task_data
        }
        
        return await self.process(input_data) 