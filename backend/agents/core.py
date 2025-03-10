import os
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from enum import Enum
import json
import uuid
import time

import anthropic
from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel, Field

from backend.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent_core")

class AgentType(str, Enum):
    """Types of agents in the system's hierarchy."""
    EXECUTIVE = "executive"  # Top-level decision maker
    MANAGER = "manager"      # Mid-level domain managers
    TASK = "task"            # Specialized task executors


class AgentProvider(str, Enum):
    """LLM providers for agents."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class AgentModel(str, Enum):
    """Available models for agents."""
    # Anthropic models
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"
    
    # OpenAI models
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"


class ToolUseType(str, Enum):
    """Type of tool choice configuration."""
    AUTO = "auto"      # Let the model decide whether to use tools
    ANY = "any"        # Force model to use any tool
    TOOL = "tool"      # Force model to use a specific tool
    NONE = "none"      # Prevent model from using tools


class AgentTool(BaseModel):
    """Definition of a tool that an agent can use."""
    name: str = Field(..., description="The name of the tool")
    description: str = Field(..., description="Detailed description of the tool")
    input_schema: Dict[str, Any] = Field(..., description="JSON Schema for the tool input")
    handler: Optional[Callable] = Field(None, description="Function to execute when tool is called")


class Message(BaseModel):
    """A message in a conversation with an agent."""
    role: str = Field(..., description="Role of the message sender (system, user, assistant)")
    content: Union[str, List[Dict[str, Any]]] = Field(..., description="Content of the message")


class ThinkingConfig(BaseModel):
    """Configuration for Claude's extended thinking mode."""
    type: str = Field("enabled", description="Type of thinking (enabled)")
    budget_tokens: int = Field(..., description="Token budget for thinking")


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for this agent")
    agent_type: AgentType = Field(..., description="Type of agent in the hierarchy")
    provider: AgentProvider = Field(..., description="LLM provider for this agent")
    model: AgentModel = Field(..., description="LLM model to use")
    system_prompt: str = Field("", description="System prompt for the agent")
    tools: List[AgentTool] = Field(default_factory=list, description="Tools available to this agent")
    tool_choice: Dict[str, Any] = Field(default={"type": "auto"}, description="Tool choice configuration")
    temperature: float = Field(0.7, description="Temperature for generation")
    max_tokens: int = Field(4000, description="Maximum tokens to generate")
    thinking: Optional[ThinkingConfig] = Field(None, description="Configuration for extended thinking")
    streaming: bool = Field(False, description="Whether to stream responses")
    timeout: int = Field(120, description="Timeout in seconds for agent responses")


class Agent:
    """Base agent class for the OMRA system."""
    
    def __init__(self, config: AgentConfig):
        """Initialize the agent with a configuration."""
        self.config = config
        self.id = config.agent_id
        self.type = config.agent_type
        self.provider = config.provider
        self.model = config.model
        
        # Initialize LLM clients
        if self.provider == AgentProvider.ANTHROPIC:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        elif self.provider == AgentProvider.OPENAI:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.async_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        # Map tool names to handlers
        self.tool_handlers = {tool.name: tool.handler for tool in self.config.tools if tool.handler}
        
        # Performance metrics
        self.total_calls = 0
        self.total_tokens = 0
        self.total_latency = 0
        
        logger.info(f"Initialized {self.type.value} agent ({self.model.value}) with ID {self.id}")
    
    async def _run_anthropic(
        self, 
        messages: List[Message],
        stream_handler: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """Run a request through Anthropic's Claude models."""
        
        start_time = time.time()
        
        # Convert messages to Anthropic format
        anthropic_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Prepare tools if they exist
        tools = None
        if self.config.tools:
            tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema
                }
                for tool in self.config.tools
            ]
        
        # Prepare thinking config if it exists
        thinking = None
        if self.config.thinking and self.model == AgentModel.CLAUDE_3_7_SONNET:
            thinking = {
                "type": self.config.thinking.type,
                "budget_tokens": self.config.thinking.budget_tokens
            }
        
        try:
            if self.config.streaming and stream_handler:
                async with self.client.messages.stream(
                    model=self.model.value,
                    messages=anthropic_messages,
                    system=self.config.system_prompt,
                    tools=tools,
                    tool_choice=self.config.tool_choice if tools else None,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    thinking=thinking
                ) as stream:
                    response_content = []
                    
                    async for event in stream:
                        if event.type == "content_block_delta":
                            if stream_handler:
                                stream_handler(event)
                            
                            if event.delta.type == "thinking_delta":
                                # Handle thinking content
                                thinking_content = event.delta.thinking
                                # Store or process thinking content as needed
                            elif event.delta.type == "text_delta":
                                # Handle text content
                                response_content.append(event.delta.text)
                    
                    completion_text = "".join(response_content)
                    
                    response = {
                        "content": completion_text,
                        "finish_reason": "stop",
                        "model": self.model.value,
                        "usage": {"total_tokens": 0}  # Token usage not available in streaming
                    }
            else:
                completion = await asyncio.to_thread(
                    self.client.messages.create,
                    model=self.model.value,
                    messages=anthropic_messages,
                    system=self.config.system_prompt,
                    tools=tools,
                    tool_choice=self.config.tool_choice if tools else None,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    thinking=thinking
                )
                
                # Extract main response from completion
                if completion.content:
                    content = ""
                    for block in completion.content:
                        if hasattr(block, "text"):
                            content += block.text
                else:
                    content = ""
                
                response = {
                    "content": content,
                    "finish_reason": completion.stop_reason,
                    "model": completion.model,
                    "usage": {
                        "total_tokens": completion.usage.input_tokens + completion.usage.output_tokens
                    },
                    "tool_calls": self._extract_tool_calls_anthropic(completion)
                }
                
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            raise
        
        # Update metrics
        end_time = time.time()
        self.total_calls += 1
        self.total_tokens += response["usage"]["total_tokens"]
        self.total_latency += (end_time - start_time)
        
        return response
    
    async def _run_openai(
        self, 
        messages: List[Message],
        stream_handler: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """Run a request through OpenAI's GPT models."""
        
        start_time = time.time()
        
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            if msg.role == "system":
                openai_messages.append({"role": "system", "content": msg.content})
            else:
                openai_messages.append({"role": msg.role, "content": msg.content})
                
        # Prepare tools if they exist
        tools = None
        if self.config.tools:
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema
                    }
                }
                for tool in self.config.tools
            ]
        
        try:
            if self.config.streaming and stream_handler:
                stream = await self.async_client.chat.completions.create(
                    model=self.model.value,
                    messages=openai_messages,
                    tools=tools,
                    tool_choice="auto" if self.config.tool_choice["type"] == "auto" else self.config.tool_choice,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    stream=True
                )
                
                response_content = []
                tool_calls = []
                
                async for chunk in stream:
                    if stream_handler:
                        stream_handler(chunk)
                    
                    if chunk.choices and chunk.choices[0].delta.content:
                        response_content.append(chunk.choices[0].delta.content)
                    
                    # Collect tool calls from streaming response
                    if chunk.choices and chunk.choices[0].delta.tool_calls:
                        for tool_call in chunk.choices[0].delta.tool_calls:
                            # Handle tool calls in streaming
                            if len(tool_calls) <= tool_call.index:
                                tool_calls.append({
                                    "id": tool_call.id,
                                    "type": "function",
                                    "function": {
                                        "name": tool_call.function.name,
                                        "arguments": tool_call.function.arguments
                                    }
                                })
                            else:
                                # Append to existing arguments
                                tool_calls[tool_call.index]["function"]["arguments"] += tool_call.function.arguments
                
                completion_text = "".join(response_content)
                
                response = {
                    "content": completion_text,
                    "finish_reason": "stop",  # Actual finish reason not available in streaming
                    "model": self.model.value,
                    "usage": {"total_tokens": 0},  # Token usage not available in streaming
                    "tool_calls": tool_calls
                }
            else:
                completion = await self.async_client.chat.completions.create(
                    model=self.model.value,
                    messages=openai_messages,
                    tools=tools,
                    tool_choice="auto" if self.config.tool_choice["type"] == "auto" else self.config.tool_choice,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
                
                response = {
                    "content": completion.choices[0].message.content or "",
                    "finish_reason": completion.choices[0].finish_reason,
                    "model": completion.model,
                    "usage": {"total_tokens": completion.usage.total_tokens},
                    "tool_calls": self._extract_tool_calls_openai(completion)
                }
        
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise
        
        # Update metrics
        end_time = time.time()
        self.total_calls += 1
        self.total_tokens += response["usage"]["total_tokens"]
        self.total_latency += (end_time - start_time)
        
        return response
    
    async def run(
        self, 
        messages: List[Message],
        stream_handler: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """Run a request through the appropriate LLM provider."""
        if self.provider == AgentProvider.ANTHROPIC:
            return await self._run_anthropic(messages, stream_handler)
        elif self.provider == AgentProvider.OPENAI:
            return await self._run_openai(messages, stream_handler)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _extract_tool_calls_anthropic(self, completion: Any) -> List[Dict[str, Any]]:
        """Extract tool calls from Anthropic API response."""
        tool_calls = []
        
        if completion.stop_reason == "tool_use":
            for block in completion.content:
                if hasattr(block, "type") and block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "arguments": block.input
                    })
        
        return tool_calls
    
    def _extract_tool_calls_openai(self, completion: Any) -> List[Dict[str, Any]]:
        """Extract tool calls from OpenAI API response."""
        tool_calls = []
        
        if (completion.choices[0].finish_reason == "tool_calls" and 
            completion.choices[0].message.tool_calls):
            for tool_call in completion.choices[0].message.tool_calls:
                if tool_call.type == "function":
                    # Parse the arguments string into a dict
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {"error": "Failed to parse arguments"}
                    
                    tool_calls.append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": arguments
                    })
        
        return tool_calls
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool by name with the provided arguments."""
        if tool_name not in self.tool_handlers:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        handler = self.tool_handlers[tool_name]
        
        try:
            # Execute tool handler (either sync or async)
            if asyncio.iscoroutinefunction(handler):
                result = await handler(**arguments)
            else:
                result = await asyncio.to_thread(handler, **arguments)
            
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            raise
    
    async def handle_tool_calls(self, response: Dict[str, Any], history: List[Message]) -> Tuple[Dict[str, Any], List[Message]]:
        """Process tool calls in a response and add results to message history."""
        
        if not response.get("tool_calls"):
            return response, history
        
        tool_results = []
        
        for tool_call in response["tool_calls"]:
            tool_name = tool_call["name"]
            tool_arguments = tool_call["arguments"]
            tool_id = tool_call["id"]
            
            try:
                result = await self.execute_tool(tool_name, tool_arguments)
                
                # Format tool result based on provider
                if self.provider == AgentProvider.ANTHROPIC:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": str(result),
                    })
                else:  # OpenAI
                    tool_results.append({
                        "tool_call_id": tool_id,
                        "role": "tool",
                        "name": tool_name,
                        "content": str(result),
                    })
            except Exception as e:
                # Handle tool execution errors
                error_message = f"Error executing tool {tool_name}: {str(e)}"
                logger.error(error_message)
                
                if self.provider == AgentProvider.ANTHROPIC:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": error_message,
                        "is_error": True
                    })
                else:  # OpenAI
                    tool_results.append({
                        "tool_call_id": tool_id,
                        "role": "tool",
                        "name": tool_name,
                        "content": error_message,
                    })
        
        # Add tool results to history
        if self.provider == AgentProvider.ANTHROPIC:
            history.append(Message(role="user", content=tool_results))
        else:  # OpenAI
            for result in tool_results:
                history.append(Message(role=result["role"], content=result["content"], name=result.get("name")))
        
        # Get next response with tool results
        next_response = await self.run(history)
        return next_response, history
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this agent."""
        avg_latency = self.total_latency / self.total_calls if self.total_calls > 0 else 0
        
        return {
            "agent_id": self.id,
            "agent_type": self.type.value,
            "model": self.model.value,
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens,
            "avg_latency": avg_latency,
            "cost_estimate": self._calculate_cost_estimate()
        }
    
    def _calculate_cost_estimate(self) -> float:
        """Calculate estimated cost for tokens used based on model pricing."""
        # Simplified pricing based on common rates
        # In a production system, these would be more accurate and updated regularly
        pricing = {
            AgentModel.CLAUDE_3_7_SONNET: 0.000015,  # $15/1M tokens
            AgentModel.GPT_4O: 0.00001,              # $10/1M tokens
            AgentModel.GPT_4O_MINI: 0.000003,        # $3/1M tokens
        }
        
        token_price = pricing.get(self.model, 0.00001)  # Default to $10/1M if unknown
        return self.total_tokens * token_price 