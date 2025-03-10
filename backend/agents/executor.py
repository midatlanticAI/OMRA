import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
import json
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field

from backend.agents.core import Agent, AgentConfig, AgentType, AgentProvider, AgentModel, Message
from backend.agents.scheduler import TaskScheduler, Task, TaskPriority, TaskStatus
from backend.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("action_executor")

class ActionType(str, Enum):
    """Types of actions that can be executed."""
    API_CALL = "api_call"              # Call an external API
    DATABASE_OPERATION = "db_op"       # Perform a database operation
    NOTIFICATION = "notification"      # Send a notification
    EMAIL = "email"                    # Send an email
    SMS = "sms"                        # Send an SMS
    FILE_OPERATION = "file_op"         # Perform a file operation
    SCHEDULE_TASK = "schedule_task"    # Schedule a task for later
    INTEGRATION = "integration"        # Run an integration operation
    CUSTOM = "custom"                  # Custom action


class Action(BaseModel):
    """An action to be executed."""
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for this action")
    type: ActionType = Field(..., description="Type of action")
    name: str = Field(..., description="Name of the action")
    description: str = Field(..., description="Description of what the action does")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the action")
    timeout_seconds: int = Field(300, description="Timeout in seconds for the action")
    retryable: bool = Field(True, description="Whether the action can be retried on failure")
    max_retries: int = Field(3, description="Maximum number of retries")
    dependencies: List[str] = Field(default_factory=list, description="IDs of actions that must complete before this one")
    workflow_id: Optional[str] = Field(None, description="ID of the workflow this action is part of")
    task_id: Optional[str] = Field(None, description="ID of the task this action is part of")
    created_at: datetime = Field(default_factory=datetime.now, description="When the action was created")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ActionResult(BaseModel):
    """Result of an action execution."""
    action_id: str = Field(..., description="ID of the action")
    success: bool = Field(..., description="Whether the action was successful")
    result: Optional[Any] = Field(None, description="Result of the action if successful")
    error: Optional[str] = Field(None, description="Error message if the action failed")
    start_time: datetime = Field(..., description="When the action started")
    end_time: datetime = Field(..., description="When the action completed")
    duration_seconds: float = Field(..., description="Duration of the action in seconds")
    attempts: int = Field(1, description="Number of attempts made")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ActionExecutor:
    """Executor for actions determined by agents."""
    
    def __init__(self, scheduler: Optional[TaskScheduler] = None):
        """Initialize the action executor."""
        self.scheduler = scheduler
        self.action_handlers = {}  # Map of action type to handler function
        self.action_results = {}  # Map of action_id to ActionResult
        self.active_executions = {}  # Map of action_id to (future, cancel_event)
        self.register_default_handlers()
        logger.info("Action executor initialized")
    
    def register_handler(self, action_type: ActionType, handler: Callable[[Action], Any]):
        """Register a handler for an action type."""
        self.action_handlers[action_type] = handler
        logger.info(f"Registered handler for action type: {action_type}")
    
    def register_default_handlers(self):
        """Register default handlers for common action types."""
        self.register_handler(ActionType.API_CALL, self._handle_api_call)
        self.register_handler(ActionType.DATABASE_OPERATION, self._handle_db_operation)
        self.register_handler(ActionType.NOTIFICATION, self._handle_notification)
        self.register_handler(ActionType.EMAIL, self._handle_email)
        self.register_handler(ActionType.SMS, self._handle_sms)
        self.register_handler(ActionType.FILE_OPERATION, self._handle_file_operation)
        self.register_handler(ActionType.SCHEDULE_TASK, self._handle_schedule_task)
        self.register_handler(ActionType.INTEGRATION, self._handle_integration)
        self.register_handler(ActionType.CUSTOM, self._handle_custom)
    
    async def execute_action(self, action: Action) -> ActionResult:
        """Execute an action and return the result."""
        action_id = action.action_id
        
        # Check if handler exists for this action type
        if action.type not in self.action_handlers:
            logger.error(f"No handler registered for action type: {action.type}")
            return ActionResult(
                action_id=action_id,
                success=False,
                error=f"No handler registered for action type: {action.type}",
                start_time=datetime.now(),
                end_time=datetime.now(),
                duration_seconds=0
            )
        
        # Create a cancellation event
        cancel_event = asyncio.Event()
        
        # Start timing
        start_time = datetime.now()
        
        # Create a task to execute the action with timeout
        handler = self.action_handlers[action.type]
        execution_task = asyncio.create_task(
            self._execute_with_timeout(
                handler, 
                action, 
                action.timeout_seconds,
                cancel_event
            )
        )
        
        # Store the active execution
        self.active_executions[action_id] = (execution_task, cancel_event)
        
        attempts = 1
        result = None
        error = None
        success = False
        
        try:
            # Wait for the execution to complete
            result = await execution_task
            success = True
            logger.info(f"Action {action_id} ({action.name}) executed successfully")
            
        except asyncio.TimeoutError:
            error = f"Action timed out after {action.timeout_seconds} seconds"
            logger.warning(f"Action {action_id} ({action.name}) timed out")
            
        except asyncio.CancelledError:
            error = "Action was cancelled"
            logger.info(f"Action {action_id} ({action.name}) was cancelled")
            
        except Exception as e:
            error = f"Action failed: {str(e)}"
            logger.error(f"Action {action_id} ({action.name}) failed: {str(e)}")
            
            # Retry if the action is retryable and we haven't exceeded max_retries
            if action.retryable and attempts < action.max_retries:
                retry_success = await self._retry_action(action, attempts)
                if retry_success:
                    success = True
                    error = None
                    result = self.action_results[action_id].result
                    attempts = self.action_results[action_id].attempts
        
        finally:
            # Remove from active executions
            if action_id in self.active_executions:
                del self.active_executions[action_id]
            
            # Calculate duration
            end_time = datetime.now()
            duration_seconds = (end_time - start_time).total_seconds()
            
            # Create and store the result
            action_result = ActionResult(
                action_id=action_id,
                success=success,
                result=result,
                error=error,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration_seconds,
                attempts=attempts,
                metadata={
                    "action_type": action.type,
                    "workflow_id": action.workflow_id,
                    "task_id": action.task_id
                }
            )
            
            self.action_results[action_id] = action_result
            return action_result
    
    async def _execute_with_timeout(
        self, 
        handler: Callable, 
        action: Action, 
        timeout: int,
        cancel_event: asyncio.Event
    ) -> Any:
        """Execute a handler with a timeout."""
        # Create a task for the handler
        handler_task = asyncio.create_task(self._execute_handler(handler, action, cancel_event))
        
        # Wait for either the handler to complete or the timeout to expire
        try:
            return await asyncio.wait_for(handler_task, timeout=timeout)
        except asyncio.TimeoutError:
            # Cancel the handler task
            handler_task.cancel()
            try:
                await handler_task
            except asyncio.CancelledError:
                pass
            raise
    
    async def _execute_handler(self, handler: Callable, action: Action, cancel_event: asyncio.Event) -> Any:
        """Execute a handler and check for cancellation."""
        # Check if we should cancel periodically
        task = asyncio.create_task(handler(action))
        
        done, pending = await asyncio.wait(
            [task, self._wait_for_cancel(cancel_event)],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # If the cancel event completed first, cancel the task
        if task in pending:
            task.cancel()
            raise asyncio.CancelledError("Action was cancelled")
        
        # Otherwise, return the result
        return task.result()
    
    async def _wait_for_cancel(self, cancel_event: asyncio.Event):
        """Wait for a cancellation event."""
        await cancel_event.wait()
        return True
    
    async def cancel_action(self, action_id: str) -> bool:
        """Cancel an ongoing action."""
        if action_id not in self.active_executions:
            logger.warning(f"Cannot cancel action {action_id}: not active")
            return False
        
        _, cancel_event = self.active_executions[action_id]
        cancel_event.set()
        
        logger.info(f"Requested cancellation of action {action_id}")
        return True
    
    async def _retry_action(self, action: Action, previous_attempts: int) -> bool:
        """Retry a failed action."""
        logger.info(f"Retrying action {action.action_id} (attempt {previous_attempts + 1}/{action.max_retries})")
        
        # Implement exponential backoff
        backoff_seconds = 2 ** previous_attempts
        await asyncio.sleep(backoff_seconds)
        
        # Create a copy of the action with updated metadata
        retry_action = action.copy(deep=True)
        retry_action.metadata["retry_count"] = previous_attempts
        retry_action.metadata["original_action_id"] = action.action_id
        
        # Execute the action again
        result = await self.execute_action(retry_action)
        
        # Update the original action's result
        if result.success:
            self.action_results[action.action_id] = ActionResult(
                action_id=action.action_id,
                success=True,
                result=result.result,
                error=None,
                start_time=self.action_results[action.action_id].start_time,
                end_time=datetime.now(),
                duration_seconds=(datetime.now() - self.action_results[action.action_id].start_time).total_seconds(),
                attempts=previous_attempts + 1,
                metadata={
                    **self.action_results[action.action_id].metadata,
                    "retry_success": True,
                    "successful_retry_attempt": previous_attempts + 1
                }
            )
            return True
        
        return False
    
    async def execute_actions(self, actions: List[Action], parallel: bool = False) -> Dict[str, ActionResult]:
        """Execute multiple actions, optionally in parallel."""
        results = {}
        
        if parallel:
            # Execute all actions in parallel
            tasks = [self.execute_action(action) for action in actions]
            action_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(action_results):
                action_id = actions[i].action_id
                if isinstance(result, Exception):
                    # Handle the exception case
                    results[action_id] = ActionResult(
                        action_id=action_id,
                        success=False,
                        error=f"Execution failed: {str(result)}",
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        duration_seconds=0
                    )
                else:
                    # Normal result case
                    results[action_id] = result
        else:
            # Execute actions sequentially
            for action in actions:
                results[action.action_id] = await self.execute_action(action)
        
        return results
    
    async def execute_with_dependencies(self, actions: List[Action]) -> Dict[str, ActionResult]:
        """Execute actions respecting their dependencies."""
        results = {}
        pending = {action.action_id: action for action in actions}
        completed = set()
        
        while pending:
            # Find actions whose dependencies are all satisfied
            executable = []
            for action_id, action in list(pending.items()):
                if all(dep_id in completed for dep_id in action.dependencies):
                    executable.append(action)
                    del pending[action_id]
            
            if not executable:
                # We have a circular dependency or missing dependency
                logger.error(f"Circular or missing dependency detected in actions: {list(pending.keys())}")
                for action_id in pending:
                    results[action_id] = ActionResult(
                        action_id=action_id,
                        success=False,
                        error="Circular or missing dependency",
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        duration_seconds=0
                    )
                break
            
            # Execute the executable actions in parallel
            batch_results = await self.execute_actions(executable, parallel=True)
            results.update(batch_results)
            
            # Add successfully completed actions to the completed set
            for action_id, result in batch_results.items():
                if result.success:
                    completed.add(action_id)
        
        return results
    
    async def get_action_result(self, action_id: str) -> Optional[ActionResult]:
        """Get the result of a previously executed action."""
        return self.action_results.get(action_id)
    
    def get_all_results(self) -> Dict[str, ActionResult]:
        """Get all action results."""
        return self.action_results.copy()
    
    def clear_results(self, older_than: Optional[datetime] = None):
        """Clear action results, optionally only those older than a certain time."""
        if older_than:
            self.action_results = {
                action_id: result 
                for action_id, result in self.action_results.items() 
                if result.end_time >= older_than
            }
        else:
            self.action_results = {}
    
    # Handler implementations
    
    async def _handle_api_call(self, action: Action) -> Any:
        """Handle an API call action."""
        import aiohttp
        
        params = action.parameters
        method = params.get("method", "GET")
        url = params.get("url")
        headers = params.get("headers", {})
        data = params.get("data")
        json_data = params.get("json")
        timeout = params.get("timeout", 60)
        
        if not url:
            raise ValueError("URL is required for API call action")
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                json=json_data,
                timeout=timeout
            ) as response:
                response.raise_for_status()
                
                # Try to parse as JSON, fall back to text
                try:
                    return await response.json()
                except:
                    return await response.text()
    
    async def _handle_db_operation(self, action: Action) -> Any:
        """Handle a database operation action."""
        # This is a simplified implementation
        # In a real application, you'd connect to your database and execute the query
        
        params = action.parameters
        operation_type = params.get("operation_type")
        model_name = params.get("model_name")
        query_params = params.get("query_params", {})
        
        if not operation_type or not model_name:
            raise ValueError("operation_type and model_name are required for database operation action")
        
        # Mock database operations
        if operation_type == "query":
            # Return mock query results
            return {"records": [], "count": 0}
        elif operation_type == "insert":
            # Return mock insert result
            return {"id": str(uuid.uuid4()), "created": True}
        elif operation_type == "update":
            # Return mock update result
            return {"updated": True, "count": 1}
        elif operation_type == "delete":
            # Return mock delete result
            return {"deleted": True, "count": 1}
        else:
            raise ValueError(f"Unsupported database operation type: {operation_type}")
    
    async def _handle_notification(self, action: Action) -> Any:
        """Handle sending a notification."""
        try:
            params = action.parameters
            recipients = params.get("recipients", [])
            message = params.get("message", "")
            subject = params.get("subject", "Notification from OMRA")
            channel = params.get("channel", "email")
            
            logger.info(f"Sending notification to {len(recipients)} recipients via {channel}")
            
            # Mock notification - in a real system, this would integrate with notification systems
            if channel == "email":
                for recipient in recipients:
                    logger.info(f"[MOCK] Sending email notification to {recipient}: {subject}")
                    # In a real system: await email_service.send_email(recipient, subject, message)
            
            elif channel == "sms":
                for recipient in recipients:
                    logger.info(f"[MOCK] Sending SMS notification to {recipient}: {message[:20]}...")
                    # In a real system: await sms_service.send_sms(recipient, message)
            
            elif channel == "in_app":
                for recipient in recipients:
                    logger.info(f"[MOCK] Sending in-app notification to user {recipient}")
                    # In a real system: await notification_service.send_notification(recipient, subject, message)
            
            return {"status": "success", "sent_to": len(recipients), "channel": channel}
        
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            raise
    
    async def _handle_email(self, action: Action) -> Any:
        """Handle sending an email."""
        try:
            params = action.parameters
            to_email = params.get("to", "")
            cc = params.get("cc", [])
            bcc = params.get("bcc", [])
            subject = params.get("subject", "Email from OMRA")
            body = params.get("body", "")
            html_body = params.get("html_body", None)
            attachments = params.get("attachments", [])
            
            logger.info(f"Sending email to {to_email}, cc: {len(cc)}, bcc: {len(bcc)}")
            
            # Mock email sending
            logger.info(f"Sending email to {to_email}: {subject}")
            
            # In a real application, you would integrate with your email service
            return {
                "sent": True,
                "recipients": {
                    "to": to_email,
                    "cc": cc,
                    "bcc": bcc
                },
                "email_id": str(uuid.uuid4())
            }
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise
    
    async def _handle_sms(self, action: Action) -> Any:
        """Handle an SMS action."""
        params = action.parameters
        to_numbers = params.get("to", [])
        message = params.get("message", "")
        
        if not to_numbers or not message:
            raise ValueError("to_numbers and message are required for SMS action")
        
        # Mock SMS sending
        logger.info(f"Sending SMS to {to_numbers}: {message[:20]}...")
        
        # In a real application, you would integrate with your SMS service
        return {
            "sent": True,
            "recipients": to_numbers,
            "sms_id": str(uuid.uuid4())
        }
    
    async def _handle_file_operation(self, action: Action) -> Any:
        """Handle a file operation action."""
        import os
        import aiofiles
        
        params = action.parameters
        operation_type = params.get("operation_type")
        file_path = params.get("file_path")
        content = params.get("content")
        
        if not operation_type or not file_path:
            raise ValueError("operation_type and file_path are required for file operation action")
        
        # Handle different file operations
        if operation_type == "read":
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                return {"content": content}
                
        elif operation_type == "write":
            if content is None:
                raise ValueError("content is required for write operation")
                
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(content)
                return {"written": True, "bytes": len(content)}
                
        elif operation_type == "append":
            if content is None:
                raise ValueError("content is required for append operation")
                
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            async with aiofiles.open(file_path, 'a') as f:
                await f.write(content)
                return {"appended": True, "bytes": len(content)}
                
        elif operation_type == "delete":
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            os.remove(file_path)
            return {"deleted": True}
            
        else:
            raise ValueError(f"Unsupported file operation type: {operation_type}")
    
    async def _handle_schedule_task(self, action: Action) -> Any:
        """Handle a task scheduling action."""
        if not self.scheduler:
            raise ValueError("Scheduler is not available")
            
        params = action.parameters
        task_title = params.get("title")
        task_description = params.get("description", "")
        task_priority_str = params.get("priority", "MEDIUM")
        task_input_data = params.get("input_data", {})
        task_dependencies = params.get("dependencies", [])
        task_agent_type_str = params.get("agent_type")
        delay_seconds = params.get("delay_seconds")
        
        if not task_title:
            raise ValueError("task_title is required for schedule_task action")
            
        # Convert string enum values to actual enums
        task_priority = TaskPriority[task_priority_str] if task_priority_str else TaskPriority.MEDIUM
        task_agent_type = AgentType[task_agent_type_str] if task_agent_type_str else None
        
        # Create the task
        task = Task(
            title=task_title,
            description=task_description,
            priority=task_priority,
            input_data=task_input_data,
            dependencies=task_dependencies,
            required_agent_type=task_agent_type
        )
        
        # Set scheduled time if delay is specified
        if delay_seconds:
            task.scheduled_for = datetime.now() + timedelta(seconds=delay_seconds)
            
        # Submit the task
        task_id = await self.scheduler.submit_task(task)
        
        return {
            "scheduled": True,
            "task_id": task_id
        }
    
    async def _handle_integration(self, action: Action) -> Any:
        """Handle an integration action."""
        params = action.parameters
        integration_name = params.get("integration_name")
        operation = params.get("operation")
        operation_params = params.get("operation_params", {})
        
        if not integration_name or not operation:
            raise ValueError("integration_name and operation are required for integration action")
            
        # In a real application, you would route this to the appropriate integration
        # For this example, we'll just mock the results
        
        logger.info(f"Executing {operation} operation on {integration_name} integration")
        
        # Mock integration results based on the integration name
        if integration_name == "ghl":
            return self._mock_ghl_integration(operation, operation_params)
        elif integration_name == "kickserv":
            return self._mock_kickserv_integration(operation, operation_params)
        else:
            return {
                "success": True,
                "integration": integration_name,
                "operation": operation,
                "result": "Integration operation completed"
            }
    
    def _mock_ghl_integration(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock GHL integration operations."""
        if operation == "get_customer":
            return {
                "id": str(uuid.uuid4()),
                "name": params.get("name", "Sample Customer"),
                "email": params.get("email", "customer@example.com"),
                "phone": params.get("phone", "123-456-7890"),
                "created_at": datetime.now().isoformat()
            }
        elif operation == "create_customer":
            return {
                "id": str(uuid.uuid4()),
                "name": params.get("name", "New Customer"),
                "email": params.get("email", "new.customer@example.com"),
                "phone": params.get("phone", "987-654-3210"),
                "created_at": datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "operation": operation,
                "params": params
            }
    
    def _mock_kickserv_integration(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Kickserv integration operations."""
        if operation == "get_job":
            return {
                "id": str(uuid.uuid4()),
                "title": params.get("title", "Sample Job"),
                "customer_id": params.get("customer_id", str(uuid.uuid4())),
                "status": "scheduled",
                "scheduled_date": datetime.now().isoformat(),
                "estimated_cost": 150.00
            }
        elif operation == "create_job":
            return {
                "id": str(uuid.uuid4()),
                "title": params.get("title", "New Job"),
                "customer_id": params.get("customer_id", str(uuid.uuid4())),
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
        else:
            return {
                "success": True,
                "operation": operation,
                "params": params
            }
    
    async def _handle_custom(self, action: Action) -> Any:
        """Handle a custom action."""
        params = action.parameters
        custom_type = params.get("custom_type")
        
        if not custom_type:
            raise ValueError("custom_type is required for custom action")
            
        # This is where you'd implement handling for your custom actions
        # For this example, we'll just return the parameters
        
        logger.info(f"Executing custom action of type: {custom_type}")
        
        return {
            "success": True,
            "custom_type": custom_type,
            "params": params
        } 