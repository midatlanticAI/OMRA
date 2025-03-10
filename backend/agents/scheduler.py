import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from enum import Enum
import json
import time
import heapq
import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from backend.agents.core import Agent, AgentConfig, AgentType, AgentProvider, AgentModel, Message
from backend.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent_scheduler")

class TaskPriority(int, Enum):
    """Priority levels for tasks."""
    LOW = 3
    MEDIUM = 2
    HIGH = 1
    CRITICAL = 0  # Will be processed first


class TaskStatus(str, Enum):
    """Status of tasks in the system."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(BaseModel):
    """A task to be processed by an agent."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for this task")
    title: str = Field(..., description="Short title of the task")
    description: str = Field(..., description="Detailed description of the task")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Priority level of the task")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Current status of the task")
    assigned_agent_id: Optional[str] = Field(None, description="ID of the agent assigned to this task")
    created_at: datetime = Field(default_factory=datetime.now, description="When the task was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the task was last updated")
    scheduled_for: Optional[datetime] = Field(None, description="When the task is scheduled to run")
    completed_at: Optional[datetime] = Field(None, description="When the task was completed")
    parent_task_id: Optional[str] = Field(None, description="ID of parent task if this is a subtask")
    subtask_ids: List[str] = Field(default_factory=list, description="IDs of child subtasks")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for the task")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data from the task")
    retry_count: int = Field(0, description="Number of times this task has been retried")
    max_retries: int = Field(3, description="Maximum number of retries allowed")
    dependencies: List[str] = Field(default_factory=list, description="IDs of tasks that must complete before this one")
    required_agent_type: Optional[AgentType] = Field(None, description="Type of agent required for this task")
    timeout_seconds: int = Field(600, description="Timeout in seconds for task execution")


class TaskScheduler:
    """Scheduler for distributing tasks among agents."""
    
    def __init__(self):
        """Initialize the task scheduler."""
        # Task queues and registries
        self.task_queue = []  # Priority queue of tasks
        self.tasks = {}  # Map of task_id to Task
        self.active_tasks = {}  # Map of task_id to (agent_id, future)
        
        # Agent registries
        self.agents = {}  # Map of agent_id to Agent
        self.available_agents = {
            AgentType.EXECUTIVE: [],  # List of available executive agent IDs
            AgentType.MANAGER: [],    # List of available manager agent IDs
            AgentType.TASK: []        # List of available task agent IDs
        }
        
        # Task result callbacks
        self.task_callbacks = {}  # Map of task_id to callback function
        
        # Metrics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_processing_time = 0
        
        # Start the scheduler loop
        self.running = False
        self.scheduler_task = None
        
        logger.info("Task scheduler initialized")
    
    def register_agent(self, agent: Agent) -> str:
        """Register an agent with the scheduler."""
        agent_id = agent.id
        self.agents[agent_id] = agent
        self.available_agents[agent.type].append(agent_id)
        logger.info(f"Registered {agent.type.value} agent with ID {agent_id}")
        return agent_id
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the scheduler."""
        if agent_id not in self.agents:
            logger.warning(f"Attempted to unregister unknown agent ID {agent_id}")
            return False
        
        agent = self.agents[agent_id]
        self.available_agents[agent.type].remove(agent_id)
        del self.agents[agent_id]
        logger.info(f"Unregistered {agent.type.value} agent with ID {agent_id}")
        return True
    
    async def submit_task(
        self, 
        task: Task, 
        callback: Optional[Callable[[Task], None]] = None
    ) -> str:
        """Submit a task to the scheduler."""
        task_id = task.task_id
        self.tasks[task_id] = task
        
        # Register callback if provided
        if callback:
            self.task_callbacks[task_id] = callback
        
        # Add to priority queue
        heapq.heappush(
            self.task_queue, 
            (task.priority.value, task.created_at.timestamp(), task_id)
        )
        
        logger.info(f"Submitted task {task_id} with priority {task.priority.name}")
        
        # Start scheduler if it's not running
        if not self.running:
            await self.start()
            
        return task_id
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        if task_id not in self.tasks:
            logger.warning(f"Attempted to cancel unknown task ID {task_id}")
            return False
        
        task = self.tasks[task_id]
        
        # If task is already completed or cancelled, can't cancel
        if task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            logger.warning(f"Cannot cancel task {task_id} with status {task.status}")
            return False
        
        # If task is active, cancel the future
        if task_id in self.active_tasks:
            agent_id, future = self.active_tasks[task_id]
            
            if not future.done():
                future.cancel()
                
            # Make agent available again
            if agent_id in self.agents:
                self.available_agents[self.agents[agent_id].type].append(agent_id)
                
            del self.active_tasks[task_id]
        
        # Update task status
        task.status = TaskStatus.CANCELLED
        task.updated_at = datetime.now()
        
        # Recursively cancel subtasks
        for subtask_id in task.subtask_ids:
            await self.cancel_task(subtask_id)
            
        logger.info(f"Cancelled task {task_id}")
        
        return True
    
    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the current status of a task."""
        if task_id not in self.tasks:
            logger.warning(f"Attempted to get status for unknown task ID {task_id}")
            return None
        
        return self.tasks[task_id].status
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a completed task."""
        if task_id not in self.tasks:
            logger.warning(f"Attempted to get result for unknown task ID {task_id}")
            return None
        
        task = self.tasks[task_id]
        
        if task.status != TaskStatus.COMPLETED:
            logger.warning(f"Attempted to get result for incomplete task {task_id}")
            return None
            
        return task.output_data
    
    def _find_available_agent(self, task: Task) -> Optional[str]:
        """Find an available agent for a task."""
        # If a specific agent type is required, only look at those agents
        if task.required_agent_type:
            available = self.available_agents[task.required_agent_type]
            if not available:
                return None
            
            # For now, just pick the first available agent
            # In a more sophisticated system, we could consider agent capabilities, load, etc.
            agent_id = available[0]
            self.available_agents[task.required_agent_type].remove(agent_id)
            return agent_id
        
        # Otherwise, try to find the most appropriate agent type based on task properties
        
        # Complex tasks with high priority go to executive agents
        if task.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]:
            if self.available_agents[AgentType.EXECUTIVE]:
                agent_id = self.available_agents[AgentType.EXECUTIVE][0]
                self.available_agents[AgentType.EXECUTIVE].remove(agent_id)
                return agent_id
        
        # Medium priority tasks go to manager agents
        if task.priority == TaskPriority.MEDIUM:
            if self.available_agents[AgentType.MANAGER]:
                agent_id = self.available_agents[AgentType.MANAGER][0]
                self.available_agents[AgentType.MANAGER].remove(agent_id)
                return agent_id
        
        # Low priority tasks go to task agents
        if task.priority == TaskPriority.LOW:
            if self.available_agents[AgentType.TASK]:
                agent_id = self.available_agents[AgentType.TASK][0]
                self.available_agents[AgentType.TASK].remove(agent_id)
                return agent_id
        
        # If no agent of the preferred type is available, try any available agent in order of capability
        for agent_type in [AgentType.EXECUTIVE, AgentType.MANAGER, AgentType.TASK]:
            if self.available_agents[agent_type]:
                agent_id = self.available_agents[agent_type][0]
                self.available_agents[agent_type].remove(agent_id)
                return agent_id
                
        # No agents available
        return None
    
    async def _process_task(self, task_id: str, agent_id: str):
        """Process a task with the assigned agent."""
        task = self.tasks[task_id]
        agent = self.agents[agent_id]
        
        logger.info(f"Processing task {task_id} with agent {agent_id}")
        
        # Update task status
        task.status = TaskStatus.IN_PROGRESS
        task.assigned_agent_id = agent_id
        task.updated_at = datetime.now()
        
        start_time = time.time()
        success = False
        
        try:
            # Create a system message
            system_message = Message(
                role="system",
                content=f"You are a {agent.type.value} agent in the OMRA system. " +
                        f"You will be given a task to complete. {task.description}\n\n" +
                        f"Use any tools available to you to complete this task. " +
                        f"When you have completed the task, provide your final result."
            )
            
            user_message = Message(
                role="user",
                content=json.dumps(task.input_data)
            )
            
            # Process task with agent
            messages = [system_message, user_message]
            response = await agent.run(messages)
            
            # Check for tool calls and handle them if present
            if response.get("tool_calls"):
                logger.info(f"Agent {agent_id} requested tool calls for task {task_id}")
                response, messages = await agent.handle_tool_calls(response, messages)
            
            # Store task result
            task.output_data = {
                "content": response.get("content", ""),
                "model": response.get("model", "")
            }
            
            # Mark task as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.updated_at = datetime.now()
            
            logger.info(f"Completed task {task_id}")
            success = True
            
        except asyncio.CancelledError:
            logger.info(f"Task {task_id} was cancelled")
            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.now()
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.updated_at = datetime.now()
            
            # Retry if possible
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                
                # Requeue with a delay based on retry count (exponential backoff)
                delay = 2 ** task.retry_count  # 2, 4, 8... seconds
                task.scheduled_for = datetime.now() + timedelta(seconds=delay)
                
                # Add back to queue
                heapq.heappush(
                    self.task_queue, 
                    (task.priority.value, task.scheduled_for.timestamp(), task_id)
                )
                
                logger.info(f"Requeued task {task_id} for retry (attempt {task.retry_count})")
            else:
                logger.warning(f"Task {task_id} failed after {task.max_retries} retries")
        
        finally:
            # Make agent available again
            self.available_agents[agent.type].append(agent_id)
            
            # Remove from active tasks
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            
            # Update metrics
            end_time = time.time()
            processing_time = end_time - start_time
            self.total_processing_time += processing_time
            
            if success:
                self.tasks_completed += 1
            else:
                self.tasks_failed += 1
            
            # Call callback if registered
            if task_id in self.task_callbacks and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                try:
                    self.task_callbacks[task_id](task)
                    del self.task_callbacks[task_id]
                except Exception as e:
                    logger.error(f"Error in callback for task {task_id}: {str(e)}")
    
    async def _scheduler_loop(self):
        """Main scheduler loop to assign tasks to agents."""
        self.running = True
        logger.info("Scheduler loop started")
        
        try:
            while self.running:
                # Check for available tasks
                if not self.task_queue:
                    # No tasks, sleep and check again
                    await asyncio.sleep(0.1)
                    continue
                
                # Check if any agent is available
                all_available = sum(len(agents) for agents in self.available_agents.values())
                if all_available == 0:
                    # No agents available, sleep and check again
                    await asyncio.sleep(0.1)
                    continue
                
                # Peek at the next task
                priority, scheduled_time, task_id = self.task_queue[0]
                task = self.tasks.get(task_id)
                
                if not task or task.status != TaskStatus.PENDING:
                    # Task has been cancelled or doesn't exist, remove it from queue
                    heapq.heappop(self.task_queue)
                    continue
                
                # Check if task is scheduled for the future
                if task.scheduled_for and task.scheduled_for > datetime.now():
                    # Not time yet, sleep and check again
                    sleep_seconds = (task.scheduled_for - datetime.now()).total_seconds()
                    await asyncio.sleep(min(sleep_seconds, 0.1))
                    continue
                
                # Check task dependencies
                dependencies_met = True
                for dep_id in task.dependencies:
                    if dep_id not in self.tasks or self.tasks[dep_id].status != TaskStatus.COMPLETED:
                        dependencies_met = False
                        break
                
                if not dependencies_met:
                    # Dependencies not met, move to back of queue with same priority
                    heapq.heappop(self.task_queue)
                    heapq.heappush(
                        self.task_queue,
                        (priority, time.time() + 5, task_id)  # Check again in 5 seconds
                    )
                    continue
                
                # Find an available agent
                agent_id = self._find_available_agent(task)
                
                if not agent_id:
                    # No suitable agent available, sleep and check again
                    await asyncio.sleep(0.1)
                    continue
                
                # Remove task from queue
                heapq.heappop(self.task_queue)
                
                # Update task status
                task.status = TaskStatus.ASSIGNED
                task.updated_at = datetime.now()
                
                # Create task future and add to active tasks
                task_future = asyncio.create_task(self._process_task(task_id, agent_id))
                self.active_tasks[task_id] = (agent_id, task_future)
                
                logger.info(f"Assigned task {task_id} to agent {agent_id}")
                
        except asyncio.CancelledError:
            logger.info("Scheduler loop cancelled")
            self.running = False
            
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}")
            self.running = False
            
    async def start(self):
        """Start the scheduler."""
        if not self.running:
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            logger.info("Task scheduler started")
    
    async def stop(self):
        """Stop the scheduler."""
        if self.running:
            self.running = False
            
            if self.scheduler_task:
                self.scheduler_task.cancel()
                try:
                    await self.scheduler_task
                except asyncio.CancelledError:
                    pass
                
            logger.info("Task scheduler stopped")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get scheduler metrics."""
        return {
            "active_tasks": len(self.active_tasks),
            "pending_tasks": len(self.task_queue),
            "completed_tasks": self.tasks_completed,
            "failed_tasks": self.tasks_failed,
            "total_processing_time": self.total_processing_time,
            "agents_available": {
                agent_type.value: len(agents) 
                for agent_type, agents in self.available_agents.items()
            },
            "agents_total": len(self.agents)
        }
    
    async def create_subtask(
        self, 
        parent_task_id: str, 
        title: str, 
        description: str, 
        input_data: Dict[str, Any], 
        priority: Optional[TaskPriority] = None,
        required_agent_type: Optional[AgentType] = None,
        callback: Optional[Callable[[Task], None]] = None
    ) -> str:
        """Create a subtask of an existing task."""
        
        if parent_task_id not in self.tasks:
            raise ValueError(f"Parent task {parent_task_id} does not exist")
        
        parent_task = self.tasks[parent_task_id]
        
        # Create subtask
        subtask = Task(
            title=title,
            description=description,
            priority=priority or parent_task.priority,
            parent_task_id=parent_task_id,
            input_data=input_data,
            required_agent_type=required_agent_type
        )
        
        # Add dependency on parent task if parent is not completed
        if parent_task.status != TaskStatus.COMPLETED:
            subtask.dependencies.append(parent_task_id)
        
        # Submit subtask
        subtask_id = await self.submit_task(subtask, callback)
        
        # Add subtask to parent
        parent_task.subtask_ids.append(subtask_id)
        parent_task.updated_at = datetime.now()
        
        logger.info(f"Created subtask {subtask_id} for parent task {parent_task_id}")
        return subtask_id 