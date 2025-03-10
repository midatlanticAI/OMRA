"""
Manager agent implementation using GPT-4o.
Acts as a mid-level decision maker in the agent hierarchy.
"""
from typing import Dict, Any, List, Optional
import json
import asyncio
import openai
from openai import AsyncOpenAI
import logging
import uuid
from datetime import datetime
import os

from backend.core.config import settings
from backend.core.logging import log_agent_activity
from backend.agents.base import AgentBase
from backend.agents.core import (
    Agent,
    AgentConfig,
    AgentType,
    AgentProvider,
    AgentModel,
    Message,
    ThinkingConfig
)

from backend.agents.scheduler import TaskScheduler, Task, TaskPriority, TaskStatus
from backend.agents.decision_engine import DecisionEngine, DecisionContext, DecisionResult
from backend.agents.executor import ActionExecutor, Action, ActionResult, ActionType
from backend.agents.events import EventHandler, Event, EventType, EventPriority
from backend.agents.communication import CommunicationInterface, AgentMessage, MessageType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent_manager")

# System prompt template for the manager agent
MANAGER_SYSTEM_PROMPT = """
You are {agent_name}, a manager AI agent in the OMRA Appliance Repair Business Automation System.
Your role is to handle specialized tasks and coordinate the work of task agents.

As a manager agent, you should:
1. Process and understand domain-specific problems
2. Break down tasks into smaller steps for task agents
3. Execute complex workflows within your domain
4. Validate and verify the work of task agents
5. Handle exceptions and edge cases appropriately
6. Report results and status to the executive agent

Your specific area of responsibility is determined by your name:
- CustomerManager: Handle customer data, communication, and relationship management
- ServiceManager: Manage service requests, scheduling, and service delivery
- TechnicianManager: Coordinate technician assignments, training, and performance tracking
- InventoryManager: Track parts inventory, orders, and optimize stock levels
- IntegrationManager: Manage third-party system integrations and data synchronization

When responding, be thorough but efficient, focusing on actionable outcomes.
Your agent ID is {agent_id}.
"""

class ManagerAgent(AgentBase):
    """
    Manager agent implementation using GPT-4o.
    Mid-level decision maker in the agent hierarchy.
    """
    
    def __init__(self, name: str, specialization: str):
        """
        Initialize the manager agent.
        
        Args:
            name: Name of the agent (e.g., CustomerManager)
            specialization: Area of specialization
        """
        super().__init__(name=name, agent_type="manager")
        self.specialization = specialization
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"
        
        # Format the system prompt
        self.system_prompt = self._format_system_prompt(MANAGER_SYSTEM_PROMPT)
        
        log_agent_activity(
            agent_type=self.agent_type,
            agent_name=self.name,
            action="configured",
            details={
                "model": self.model,
                "specialization": self.specialization,
                "system_prompt_length": len(self.system_prompt)
            }
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input using GPT-4o.
        
        Args:
            input_data: Input data with "query", optional "context", and optional "instructions"
            
        Returns:
            Response from the manager agent
        """
        try:
            # Pre-process the input
            processed_input = await self._pre_process(input_data)
            
            # Extract query, context, and instructions
            query = processed_input.get("query", "")
            context = processed_input.get("context", "")
            instructions = processed_input.get("instructions", "")
            
            # Log the query processing
            log_agent_activity(
                agent_type=self.agent_type,
                agent_name=self.name,
                action="processing_query",
                details={
                    "query_length": len(query),
                    "has_context": bool(context),
                    "has_instructions": bool(instructions)
                }
            )
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add context if available
            if context:
                messages.append({
                    "role": "user",
                    "content": f"Context information:\n{context}"
                })
                messages.append({
                    "role": "assistant",
                    "content": "I've received the context information."
                })
            
            # Add instructions if available
            if instructions:
                messages.append({
                    "role": "user",
                    "content": f"Special instructions for this task:\n{instructions}"
                })
                messages.append({
                    "role": "assistant",
                    "content": "I understand the special instructions."
                })
            
            # Add the main query
            messages.append({
                "role": "user",
                "content": query
            })
            
            # Generate response from GPT-4o
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2048,
                temperature=0.2
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
        Post-process the output data from GPT-4o.
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
            # Also look for just ``` which might contain JSON
            elif "```" in response_text:
                parts = response_text.split("```")
                for i in range(1, len(parts), 2):
                    try:
                        json_text = parts[i].strip()
                        if json_text.startswith("{") or json_text.startswith("["):
                            json_data = json.loads(json_text)
                            json_blocks.append(json_data)
                    except:
                        pass
            
            if json_blocks:
                output_data["structured_data"] = json_blocks
        except:
            # Ignore errors in JSON extraction - it's an optional enhancement
            pass
        
        return output_data
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific task within the manager's domain.
        
        Args:
            task: Task definition and parameters
            
        Returns:
            Task execution results
        """
        task_description = task.get("description", "")
        task_params = task.get("parameters", {})
        
        input_data = {
            "query": f"""
Execute the following task within your role as {self.name}:

TASK DESCRIPTION: {task_description}

TASK PARAMETERS:
{json.dumps(task_params, indent=2)}

Please execute this task and provide your results in a structured format.
Include any relevant details about your process and any issues encountered.
""",
            "instructions": task.get("instructions", "")
        }
        
        if "context" in task:
            input_data["context"] = task["context"]
        
        return await self.process(input_data)

class AgentManager:
    """Manager for the entire agent system."""
    
    def __init__(self):
        """Initialize the agent manager."""
        # Core components
        self.event_handler = EventHandler()
        self.task_scheduler = TaskScheduler()
        self.action_executor = ActionExecutor(self.task_scheduler)
        self.decision_engine = DecisionEngine(self.task_scheduler)
        self.communication = CommunicationInterface(self.event_handler)
        
        # Agent registries
        self.agents = {}  # Map of agent_id to Agent instance
        self.agent_configs = {}  # Map of agent_id to agent configuration
        
        # Workflow state
        self.workflows = {}  # Map of workflow_id to workflow state
        
        logger.info("Agent manager initialized")
    
    async def start(self):
        """Start the agent system."""
        # Start the event handler
        await self.event_handler.start()
        
        # Start the task scheduler
        await self.task_scheduler.start()
        
        # Bind tool handlers in the decision engine
        self.decision_engine.bind_tool_handlers()
        
        logger.info("Agent system started")
    
    async def stop(self):
        """Stop the agent system."""
        # Stop all running agents
        await self.stop_all_agents()
        
        # Stop the task scheduler
        await self.task_scheduler.stop()
        
        # Stop the event handler
        await self.event_handler.stop()
        
        logger.info("Agent system stopped")
    
    async def create_agent(
        self, 
        agent_type: AgentType,
        provider: AgentProvider,
        model: AgentModel,
        system_prompt: str = "",
        tools: List[Dict[str, Any]] = None,
        thinking_config: Optional[Dict[str, Any]] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        streaming: bool = False,
        agent_id: Optional[str] = None
    ) -> str:
        """Create a new agent."""
        # Create a unique ID if not provided
        if not agent_id:
            agent_id = f"{agent_type.value}_{str(uuid.uuid4())[:8]}"
            
        # Create thinking config if provided
        thinking = None
        if thinking_config and model == AgentModel.CLAUDE_3_7_SONNET:
            thinking = ThinkingConfig(**thinking_config)
            
        # Create agent config
        config = AgentConfig(
            agent_id=agent_id,
            agent_type=agent_type,
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            tools=tools or [],
            temperature=temperature,
            max_tokens=max_tokens,
            thinking=thinking,
            streaming=streaming
        )
        
        # Create the agent
        agent = Agent(config)
        
        # Register with the scheduler
        self.task_scheduler.register_agent(agent)
        
        # Store the agent
        self.agents[agent_id] = agent
        self.agent_configs[agent_id] = config
        
        # Register with the communication interface
        self.communication.register_agent(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=[tool["name"] for tool in tools] if tools else [],
            message_handler=self._create_message_handler(agent_id)
        )
        
        logger.info(f"Created {agent_type.value} agent: {agent_id}")
        
        # Publish agent created event
        await self.event_handler.create_custom_event(
            source="agent_manager",
            name="agent_created",
            data={
                "agent_id": agent_id,
                "agent_type": agent_type.value,
                "model": model.value,
                "provider": provider.value
            }
        )
        
        return agent_id
    
    async def stop_agent(self, agent_id: str):
        """Stop and clean up an agent."""
        if agent_id not in self.agents:
            logger.warning(f"Unknown agent ID: {agent_id}")
            return
            
        # Get the agent
        agent = self.agents[agent_id]
        
        # Unregister from the scheduler
        self.task_scheduler.unregister_agent(agent_id)
        
        # Unregister from the communication interface
        self.communication.unregister_agent(agent_id)
        
        # Remove from storage
        del self.agents[agent_id]
        del self.agent_configs[agent_id]
        
        logger.info(f"Stopped agent: {agent_id}")
        
        # Publish agent destroyed event
        await self.event_handler.create_custom_event(
            source="agent_manager",
            name="agent_destroyed",
            data={
                "agent_id": agent_id,
                "agent_type": agent.type.value
            }
        )
    
    async def stop_all_agents(self):
        """Stop all running agents."""
        agent_ids = list(self.agents.keys())
        
        for agent_id in agent_ids:
            await self.stop_agent(agent_id)
            
        logger.info(f"Stopped all {len(agent_ids)} agents")
    
    async def create_executive_agent(
        self,
        system_prompt: str = None,
        tools: List[Dict[str, Any]] = None,
        thinking_budget: int = 4000,
        max_tokens: int = 8000,
        agent_id: Optional[str] = None
    ) -> str:
        """Create an executive agent (Claude 3.7 Sonnet with extended thinking)."""
        # Use default system prompt if not provided
        if not system_prompt:
            system_prompt = """You are the Executive Agent in the OMRA system, responsible for high-level decision making.
            
You oversee multiple specialized agents and coordinate complex workflows. Your role is to:
1. Understand the business needs and user requests
2. Delegate tasks to appropriate specialized agents
3. Make high-level decisions that impact the business
4. Ensure all processes are running efficiently
5. Resolve conflicts between agents or processes

Always consider the business impact of your decisions and prioritize customer satisfaction and operational efficiency.
"""
        
        # Create thinking config
        thinking_config = {
            "type": "enabled",
            "budget_tokens": thinking_budget
        }
        
        # Create the agent
        return await self.create_agent(
            agent_type=AgentType.EXECUTIVE,
            provider=AgentProvider.ANTHROPIC,
            model=AgentModel.CLAUDE_3_7_SONNET,
            system_prompt=system_prompt,
            tools=tools,
            thinking_config=thinking_config,
            max_tokens=max_tokens,
            temperature=0.3,  # Lower temperature for more consistency
            agent_id=agent_id
        )
    
    async def create_manager_agent(
        self,
        system_prompt: str = None,
        tools: List[Dict[str, Any]] = None,
        max_tokens: int = 4000,
        agent_id: Optional[str] = None
    ) -> str:
        """Create a manager agent (GPT-4o)."""
        # Use default system prompt if not provided
        if not system_prompt:
            system_prompt = """You are a Manager Agent in the OMRA system, responsible for coordinating specific domains and tasks.
            
You report to the Executive Agent and manage specific functional areas. Your role is to:
1. Manage projects and workflows within your domain
2. Coordinate the work of Task Agents under your supervision
3. Implement strategies from the Executive Agent
4. Report status and issues to the Executive Agent
5. Make operational decisions within your domain

Focus on efficiently executing your domain responsibilities while maintaining quality standards.
"""
        
        # Create the agent
        return await self.create_agent(
            agent_type=AgentType.MANAGER,
            provider=AgentProvider.OPENAI,
            model=AgentModel.GPT_4O,
            system_prompt=system_prompt,
            tools=tools,
            max_tokens=max_tokens,
            temperature=0.5,  # Moderate temperature
            agent_id=agent_id
        )
    
    async def create_task_agent(
        self,
        system_prompt: str = None,
        tools: List[Dict[str, Any]] = None,
        max_tokens: int = 2000,
        agent_id: Optional[str] = None
    ) -> str:
        """Create a task agent (GPT-4o-mini)."""
        # Use default system prompt if not provided
        if not system_prompt:
            system_prompt = """You are a Task Agent in the OMRA system, responsible for executing specific tasks.
            
You report to a Manager Agent and focus on specialized tasks. Your role is to:
1. Execute specific assigned tasks efficiently
2. Use your specialized knowledge and tools
3. Report task status and results to your Manager Agent
4. Identify issues that might affect task completion
5. Follow established procedures and guidelines

Focus on completing your assigned tasks accurately and efficiently.
"""
        
        # Create the agent
        return await self.create_agent(
            agent_type=AgentType.TASK,
            provider=AgentProvider.OPENAI,
            model=AgentModel.GPT_4O_MINI,
            system_prompt=system_prompt,
            tools=tools,
            max_tokens=max_tokens,
            temperature=0.7,  # Higher temperature for more creativity
            agent_id=agent_id
        )
    
    def _create_message_handler(self, agent_id: str) -> Callable[[AgentMessage], None]:
        """Create a message handler for an agent."""
        async def handle_message(message: AgentMessage):
            """Handle a message sent to this agent."""
            logger.debug(f"Agent {agent_id} received message: {message.subject}")
            
            # Get the agent
            agent = self.agents.get(agent_id)
            if not agent:
                logger.warning(f"Message handler called for unknown agent {agent_id}")
                return
                
            # Convert to format the agent can process
            if message.type == MessageType.REQUEST:
                # This is a request that needs a response
                try:
                    # Format the message content as a user message
                    user_message = Message(
                        role="user",
                        content=json.dumps({
                            "message_id": message.message_id,
                            "sender": message.sender,
                            "subject": message.subject,
                            "content": message.content
                        })
                    )
                    
                    # Process the message with the agent
                    response = await agent.run([user_message])
                    
                    # Check for tool calls and handle them
                    if response.get("tool_calls"):
                        history = [user_message]
                        response, history = await agent.handle_tool_calls(response, history)
                    
                    # Send a response back
                    await self.communication.reply_to_message(
                        original_message_id=message.message_id,
                        sender=agent_id,
                        content={
                            "response": response.get("content", ""),
                            "processed_at": datetime.now().isoformat()
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing message for agent {agent_id}: {str(e)}")
                    
                    # Send error response
                    await self.communication.reply_to_message(
                        original_message_id=message.message_id,
                        sender=agent_id,
                        content={
                            "error": str(e),
                            "processed_at": datetime.now().isoformat()
                        },
                        message_type=MessageType.ERROR
                    )
            else:
                # Other message types (notifications, etc.) might just be logged
                # or trigger other behaviors depending on the agent's capabilities
                pass
                
        # Return a wrapper that handles the async function
        def message_handler(message: AgentMessage):
            asyncio.create_task(handle_message(message))
            
        return message_handler
    
    async def create_workflow(
        self, 
        name: str, 
        description: str, 
        initial_data: Dict[str, Any]
    ) -> str:
        """Create a new workflow."""
        # Create workflow ID
        workflow_id = f"workflow_{str(uuid.uuid4())[:8]}"
        
        # Create workflow
        self.workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "name": name,
            "description": description,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "data": initial_data,
            "decisions": [],
            "actions": [],
            "tasks": [],
            "agents": []
        }
        
        logger.info(f"Created workflow: {workflow_id} - {name}")
        
        # Publish workflow created event
        await self.event_handler.create_workflow_event(
            event_type=EventType.WORKFLOW_STARTED,
            workflow_id=workflow_id,
            additional_data={
                "name": name,
                "description": description
            }
        )
        
        return workflow_id
    
    async def add_agent_to_workflow(self, workflow_id: str, agent_id: str) -> bool:
        """Add an agent to a workflow."""
        # Check workflow exists
        if workflow_id not in self.workflows:
            logger.warning(f"Unknown workflow ID: {workflow_id}")
            return False
            
        # Check agent exists
        if agent_id not in self.agents:
            logger.warning(f"Unknown agent ID: {agent_id}")
            return False
            
        # Add to workflow
        workflow = self.workflows[workflow_id]
        if agent_id not in workflow["agents"]:
            workflow["agents"].append(agent_id)
            workflow["updated_at"] = datetime.now().isoformat()
            
            logger.info(f"Added agent {agent_id} to workflow {workflow_id}")
            
            # Create custom event
            await self.event_handler.create_custom_event(
                source="agent_manager",
                name="agent_added_to_workflow",
                data={
                    "workflow_id": workflow_id,
                    "agent_id": agent_id
                }
            )
            
        return True
    
    async def make_workflow_decision(
        self, 
        workflow_id: str, 
        decision_type: str, 
        context_data: Dict[str, Any]
    ) -> Optional[DecisionResult]:
        """Make a decision within a workflow."""
        # Check workflow exists
        if workflow_id not in self.workflows:
            logger.warning(f"Unknown workflow ID: {workflow_id}")
            return None
            
        workflow = self.workflows[workflow_id]
        
        # Create decision context
        context = DecisionContext(
            workflow_id=workflow_id,
            input_data=context_data,
            history=workflow["decisions"],
            metadata={
                "decision_type": decision_type,
                "workflow_name": workflow["name"]
            }
        )
        
        # Make the decision
        decision = await self.decision_engine.make_decision(context, decision_type)
        
        # Store the decision
        workflow["decisions"].append(decision.dict())
        workflow["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Made decision in workflow {workflow_id}: {decision.decision_id}")
        
        # Publish decision event
        await self.event_handler.create_custom_event(
            source="agent_manager",
            name="workflow_decision_made",
            data={
                "workflow_id": workflow_id,
                "decision_id": decision.decision_id,
                "decision_type": decision_type,
                "confidence": decision.confidence
            }
        )
        
        return decision
    
    async def execute_workflow_action(
        self, 
        workflow_id: str, 
        action_type: ActionType, 
        name: str, 
        description: str, 
        parameters: Dict[str, Any]
    ) -> Optional[ActionResult]:
        """Execute an action within a workflow."""
        # Check workflow exists
        if workflow_id not in self.workflows:
            logger.warning(f"Unknown workflow ID: {workflow_id}")
            return None
            
        workflow = self.workflows[workflow_id]
        
        # Create action
        action = Action(
            type=action_type,
            name=name,
            description=description,
            parameters=parameters,
            workflow_id=workflow_id
        )
        
        # Execute the action
        result = await self.action_executor.execute_action(action)
        
        # Store the action and result
        workflow["actions"].append({
            "action_id": action.action_id,
            "type": action_type.value,
            "name": name,
            "description": description,
            "parameters": parameters,
            "result": {
                "success": result.success,
                "error": result.error,
                "duration_seconds": result.duration_seconds,
                "attempts": result.attempts
            }
        })
        workflow["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Executed action in workflow {workflow_id}: {action.action_id}")
        
        # Publish action event
        await self.event_handler.create_action_event(
            event_type=EventType.ACTION_COMPLETED if result.success else EventType.ACTION_FAILED,
            action_id=action.action_id,
            additional_data={
                "workflow_id": workflow_id,
                "action_type": action_type.value,
                "name": name,
                "success": result.success
            }
        )
        
        return result
    
    async def execute_decision_actions(self, decision: DecisionResult) -> List[ActionResult]:
        """Execute all actions from a decision."""
        results = []
        
        for action_data in decision.actions:
            # Convert decision action to executor action
            action_description = action_data.get("description", "")
            
            # Determine action type based on description or default to custom
            action_type = ActionType.CUSTOM
            
            # Try to infer action type from description
            type_keywords = {
                "api": ActionType.API_CALL,
                "database": ActionType.DATABASE_OPERATION,
                "notify": ActionType.NOTIFICATION,
                "email": ActionType.EMAIL,
                "sms": ActionType.SMS,
                "file": ActionType.FILE_OPERATION,
                "schedule": ActionType.SCHEDULE_TASK,
                "integration": ActionType.INTEGRATION
            }
            
            for keyword, action_type_value in type_keywords.items():
                if keyword.lower() in action_description.lower():
                    action_type = action_type_value
                    break
            
            # Create action parameters from action description
            # This is a simplified approach - in a real system you'd have more structure
            parameters = {
                "action_description": action_description,
                "decision_id": decision.decision_id,
                "custom_type": "decision_action"
            }
            
            # Create and execute the action
            result = await self.execute_workflow_action(
                workflow_id=decision.workflow_id,
                action_type=action_type,
                name=f"Decision action from {decision.decision_id}",
                description=action_description,
                parameters=parameters
            )
            
            if result:
                results.append(result)
        
        return results
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an agent."""
        if agent_id not in self.agents:
            logger.warning(f"Unknown agent ID: {agent_id}")
            return None
            
        agent = self.agents[agent_id]
        config = self.agent_configs[agent_id]
        
        # Get agent metrics
        metrics = agent.get_metrics()
        
        return {
            "agent_id": agent_id,
            "type": agent.type.value,
            "provider": agent.provider.value,
            "model": agent.model.value,
            "system_prompt": config.system_prompt,
            "tools": [tool.name for tool in config.tools],
            "metrics": metrics,
            "thinking_enabled": config.thinking is not None
        }
    
    def get_workflow_info(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a workflow."""
        return self.workflows.get(workflow_id)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics."""
        # Get metrics from all components
        event_metrics = self.event_handler.get_metrics()
        scheduler_metrics = self.task_scheduler.get_metrics()
        
        # Count workflows by status
        workflow_counts = {}
        for workflow in self.workflows.values():
            status = workflow["status"]
            workflow_counts[status] = workflow_counts.get(status, 0) + 1
            
        # Count agents by type
        agent_counts = {}
        for agent in self.agents.values():
            agent_type = agent.type.value
            agent_counts[agent_type] = agent_counts.get(agent_type, 0) + 1
            
        return {
            "agent_counts": agent_counts,
            "workflow_counts": workflow_counts,
            "active_tasks": scheduler_metrics["active_tasks"],
            "pending_tasks": scheduler_metrics["pending_tasks"],
            "completed_tasks": scheduler_metrics["completed_tasks"],
            "events_processed": event_metrics["events_processed"],
            "queue_size": event_metrics["queue_size"],
            "total_agents": len(self.agents),
            "total_workflows": len(self.workflows)
        } 