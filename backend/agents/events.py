import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Callable, Tuple, Set
import json
import time
from datetime import datetime
from enum import Enum
import uuid
import traceback
from pydantic import BaseModel, Field, root_validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("event_handler")

class EventType(str, Enum):
    """Types of events in the system."""
    TASK_CREATED = "task_created"
    TASK_ASSIGNED = "task_assigned"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_CANCELLED = "task_cancelled"
    
    DECISION_MADE = "decision_made"
    
    ACTION_STARTED = "action_started"
    ACTION_COMPLETED = "action_completed"
    ACTION_FAILED = "action_failed"
    
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    
    USER_NOTIFICATION = "user_notification"
    SYSTEM_NOTIFICATION = "system_notification"
    
    AGENT_CREATED = "agent_created"
    AGENT_DESTROYED = "agent_destroyed"
    
    INTEGRATION_EVENT = "integration_event"
    
    CUSTOM_EVENT = "custom_event"


class EventPriority(int, Enum):
    """Priority levels for events."""
    LOW = 3
    MEDIUM = 2
    HIGH = 1
    CRITICAL = 0


class Event(BaseModel):
    """An event in the system."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for this event")
    type: EventType = Field(..., description="Type of event")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the event occurred")
    source: str = Field(..., description="Source of the event (component, agent, etc.)")
    priority: EventPriority = Field(EventPriority.MEDIUM, description="Priority level of the event")
    data: Dict[str, Any] = Field(..., description="Event data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @root_validator
    def ensure_required_data(cls, values):
        """Ensure required data fields are present based on event type."""
        event_type = values.get('type')
        data = values.get('data', {})
        
        if event_type in [
            EventType.TASK_CREATED, 
            EventType.TASK_ASSIGNED, 
            EventType.TASK_STARTED, 
            EventType.TASK_COMPLETED,
            EventType.TASK_FAILED,
            EventType.TASK_CANCELLED
        ]:
            if 'task_id' not in data:
                raise ValueError(f"Task events require task_id in data for event type: {event_type}")
                
        if event_type in [EventType.TASK_ASSIGNED]:
            if 'agent_id' not in data:
                raise ValueError(f"Task assignment events require agent_id in data for event type: {event_type}")
                
        if event_type in [
            EventType.ACTION_STARTED, 
            EventType.ACTION_COMPLETED, 
            EventType.ACTION_FAILED
        ]:
            if 'action_id' not in data:
                raise ValueError(f"Action events require action_id in data for event type: {event_type}")
                
        if event_type in [
            EventType.WORKFLOW_STARTED, 
            EventType.WORKFLOW_COMPLETED, 
            EventType.WORKFLOW_FAILED
        ]:
            if 'workflow_id' not in data:
                raise ValueError(f"Workflow events require workflow_id in data for event type: {event_type}")
                
        if event_type == EventType.DECISION_MADE:
            if 'decision_id' not in data:
                raise ValueError(f"Decision events require decision_id in data for event type: {event_type}")
                
        return values


class EventHandler:
    """Handler for system events."""
    
    def __init__(self):
        """Initialize the event handler."""
        # Event queues
        self.event_queue = asyncio.Queue()
        self.event_history = []  # Limited history of processed events
        self.max_history_size = 1000
        
        # Subscribers
        self.subscribers = {event_type: set() for event_type in EventType}
        self.global_subscribers = set()
        
        # Event filters for each subscriber
        self.subscriber_filters = {}
        
        # Processing state
        self.running = False
        self.event_processors = []
        self.num_processors = 2  # Number of event processing tasks
        
        # Metrics
        self.events_processed = 0
        self.events_by_type = {event_type: 0 for event_type in EventType}
        self.processing_times = []
        self.max_processing_times = 100  # Keep last 100 processing times
        
        logger.info("Event handler initialized")
    
    async def start(self):
        """Start the event processing loop."""
        if self.running:
            return
            
        self.running = True
        
        # Start event processors
        for i in range(self.num_processors):
            processor = asyncio.create_task(self._event_processing_loop(i))
            self.event_processors.append(processor)
            
        logger.info(f"Started {self.num_processors} event processors")
    
    async def stop(self):
        """Stop the event processing loop."""
        if not self.running:
            return
            
        self.running = False
        
        # Cancel all event processors
        for processor in self.event_processors:
            processor.cancel()
            
        # Wait for them to complete
        for processor in self.event_processors:
            try:
                await processor
            except asyncio.CancelledError:
                pass
                
        self.event_processors = []
        logger.info("Stopped event processors")
    
    async def publish_event(self, event: Event):
        """Publish an event to the event queue."""
        await self.event_queue.put(event)
        logger.debug(f"Published event: {event.type} (ID: {event.event_id})")
    
    def subscribe(
        self, 
        callback: Callable[[Event], None], 
        event_types: Optional[List[EventType]] = None,
        filter_func: Optional[Callable[[Event], bool]] = None
    ):
        """Subscribe to events of specified types."""
        # If no event types specified, subscribe to all events
        if event_types is None:
            self.global_subscribers.add(callback)
            logger.info(f"Added global subscriber: {callback.__name__}")
        else:
            # Subscribe to specified event types
            for event_type in event_types:
                self.subscribers[event_type].add(callback)
                logger.info(f"Added subscriber for event type {event_type}: {callback.__name__}")
                
        # Store filter if provided
        if filter_func:
            self.subscriber_filters[callback] = filter_func
    
    def unsubscribe(self, callback: Callable[[Event], None], event_types: Optional[List[EventType]] = None):
        """Unsubscribe from events of specified types."""
        # If no event types specified, unsubscribe from all events
        if event_types is None:
            if callback in self.global_subscribers:
                self.global_subscribers.remove(callback)
                logger.info(f"Removed global subscriber: {callback.__name__}")
                
            # Remove from all event type subscribers
            for event_type in EventType:
                if callback in self.subscribers[event_type]:
                    self.subscribers[event_type].remove(callback)
        else:
            # Unsubscribe from specified event types
            for event_type in event_types:
                if callback in self.subscribers[event_type]:
                    self.subscribers[event_type].remove(callback)
                    logger.info(f"Removed subscriber for event type {event_type}: {callback.__name__}")
                    
        # Remove any filters
        if callback in self.subscriber_filters:
            del self.subscriber_filters[callback]
    
    async def _event_processing_loop(self, processor_id: int):
        """Process events from the event queue."""
        logger.info(f"Event processor {processor_id} started")
        
        try:
            while self.running:
                try:
                    # Get the next event
                    event = await self.event_queue.get()
                    
                    start_time = time.time()
                    
                    # Process the event
                    await self._process_event(event)
                    
                    # Update metrics
                    processing_time = time.time() - start_time
                    self.events_processed += 1
                    self.events_by_type[event.type] += 1
                    
                    # Store processing time for metrics
                    self.processing_times.append(processing_time)
                    if len(self.processing_times) > self.max_processing_times:
                        self.processing_times.pop(0)
                        
                    # Add to history
                    self.event_history.append(event)
                    if len(self.event_history) > self.max_history_size:
                        self.event_history.pop(0)
                        
                    # Mark as done
                    self.event_queue.task_done()
                    
                except Exception as e:
                    logger.error(f"Error processing event: {str(e)}")
                    logger.error(traceback.format_exc())
        except asyncio.CancelledError:
            logger.info(f"Event processor {processor_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Event processor {processor_id} crashed: {str(e)}")
            logger.error(traceback.format_exc())
    
    async def _process_event(self, event: Event):
        """Process a single event."""
        logger.debug(f"Processing event: {event.type} (ID: {event.event_id})")
        
        # Collect all matching subscribers
        subscribers_to_notify = set()
        
        # Add type-specific subscribers
        subscribers_to_notify.update(self.subscribers[event.type])
        
        # Add global subscribers
        subscribers_to_notify.update(self.global_subscribers)
        
        # Apply filters
        filtered_subscribers = []
        for subscriber in subscribers_to_notify:
            if subscriber in self.subscriber_filters:
                filter_func = self.subscriber_filters[subscriber]
                if filter_func(event):
                    filtered_subscribers.append(subscriber)
            else:
                # No filter, always notify
                filtered_subscribers.append(subscriber)
        
        # Notify all subscribers
        for subscriber in filtered_subscribers:
            try:
                # Call the subscriber
                result = subscriber(event)
                
                # If it's a coroutine, await it
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error in subscriber {subscriber.__name__} for event {event.type}: {str(e)}")
                logger.error(traceback.format_exc())
    
    async def wait_for_event(
        self, 
        event_type: EventType, 
        filter_func: Optional[Callable[[Event], bool]] = None,
        timeout: Optional[float] = None
    ) -> Optional[Event]:
        """Wait for a specific event to occur."""
        future = asyncio.Future()
        
        def event_callback(event: Event):
            if not filter_func or filter_func(event):
                future.set_result(event)
                return True  # Signal to unsubscribe
            return False
        
        # Subscribe to the event
        self.subscribe(event_callback, [event_type])
        
        try:
            # Wait for the event or timeout
            if timeout:
                return await asyncio.wait_for(future, timeout)
            else:
                return await future
        except asyncio.TimeoutError:
            return None
        finally:
            # Unsubscribe from the event
            self.unsubscribe(event_callback, [event_type])
    
    def get_recent_events(
        self, 
        event_types: Optional[List[EventType]] = None,
        limit: int = 100,
        filter_func: Optional[Callable[[Event], bool]] = None
    ) -> List[Event]:
        """Get recent events of specified types."""
        # Start with all events in history
        events = self.event_history.copy()
        
        # Filter by event type if specified
        if event_types:
            events = [e for e in events if e.type in event_types]
            
        # Apply custom filter if provided
        if filter_func:
            events = [e for e in events if filter_func(e)]
            
        # Sort by timestamp (newest first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Limit the number of events
        return events[:limit]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics about event processing."""
        avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        
        return {
            "events_processed": self.events_processed,
            "events_by_type": {event_type.value: count for event_type, count in self.events_by_type.items()},
            "queue_size": self.event_queue.qsize(),
            "avg_processing_time_ms": avg_processing_time * 1000,
            "subscriber_count": sum(len(subs) for subs in self.subscribers.values()) + len(self.global_subscribers),
        }
    
    async def create_task_event(self, event_type: EventType, task_id: str, additional_data: Dict[str, Any] = None):
        """Helper to create and publish a task-related event."""
        event_data = {
            "task_id": task_id,
            **(additional_data or {})
        }
        
        event = Event(
            type=event_type,
            source="task_scheduler",
            data=event_data
        )
        
        await self.publish_event(event)
    
    async def create_action_event(self, event_type: EventType, action_id: str, additional_data: Dict[str, Any] = None):
        """Helper to create and publish an action-related event."""
        event_data = {
            "action_id": action_id,
            **(additional_data or {})
        }
        
        event = Event(
            type=event_type,
            source="action_executor",
            data=event_data
        )
        
        await self.publish_event(event)
    
    async def create_workflow_event(self, event_type: EventType, workflow_id: str, additional_data: Dict[str, Any] = None):
        """Helper to create and publish a workflow-related event."""
        event_data = {
            "workflow_id": workflow_id,
            **(additional_data or {})
        }
        
        event = Event(
            type=event_type,
            source="workflow_manager",
            data=event_data
        )
        
        await self.publish_event(event)
    
    async def create_notification_event(
        self, 
        message: str, 
        level: str = "info", 
        user_id: Optional[str] = None,
        additional_data: Dict[str, Any] = None
    ):
        """Helper to create and publish a notification event."""
        # Determine if it's a user or system notification
        if user_id:
            event_type = EventType.USER_NOTIFICATION
        else:
            event_type = EventType.SYSTEM_NOTIFICATION
            
        event_data = {
            "message": message,
            "level": level,
            **(additional_data or {})
        }
        
        if user_id:
            event_data["user_id"] = user_id
            
        event = Event(
            type=event_type,
            source="notification_service",
            data=event_data
        )
        
        await self.publish_event(event)
    
    async def create_custom_event(self, source: str, name: str, data: Dict[str, Any], priority: EventPriority = EventPriority.MEDIUM):
        """Helper to create and publish a custom event."""
        event_data = {
            "name": name,
            **data
        }
        
        event = Event(
            type=EventType.CUSTOM_EVENT,
            source=source,
            priority=priority,
            data=event_data
        )
        
        await self.publish_event(event)
    
    async def create_integration_event(self, integration: str, event_name: str, data: Dict[str, Any]):
        """Helper to create and publish an integration event."""
        event_data = {
            "integration": integration,
            "event_name": event_name,
            **data
        }
        
        event = Event(
            type=EventType.INTEGRATION_EVENT,
            source=f"integration_{integration}",
            data=event_data
        )
        
        await self.publish_event(event) 