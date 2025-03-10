import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Callable, Tuple, Set
import json
import time
from datetime import datetime
from enum import Enum
import uuid
from pydantic import BaseModel, Field

from backend.agents.core import Agent, AgentConfig, AgentType, AgentProvider, AgentModel, Message
from backend.agents.events import EventHandler, Event, EventType, EventPriority
from backend.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("communication_interface")

class MessageType(str, Enum):
    """Types of messages between agents."""
    REQUEST = "request"        # Request a response or action
    RESPONSE = "response"      # Response to a request
    NOTIFICATION = "notification"  # Informational message, no response needed
    STATUS = "status"          # Status update
    ERROR = "error"            # Error message
    SYSTEM = "system"          # System message
    BROADCAST = "broadcast"    # Message to all agents


class AgentMessage(BaseModel):
    """A message between agents."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for this message")
    type: MessageType = Field(..., description="Type of message")
    sender: str = Field(..., description="ID of the sender agent")
    recipients: List[str] = Field(..., description="IDs of recipient agents (empty for broadcast)")
    subject: str = Field(..., description="Subject of the message")
    content: Dict[str, Any] = Field(..., description="Message content")
    in_reply_to: Optional[str] = Field(None, description="ID of the message this is a reply to")
    conversation_id: Optional[str] = Field(None, description="ID of the conversation this message is part of")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the message was sent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    priority: int = Field(1, description="Priority of the message (1-5, 1 is highest)")
    ttl: Optional[int] = Field(None, description="Time-to-live for the message in seconds")
    requires_acknowledgment: bool = Field(False, description="Whether the message requires acknowledgment")


class AgentConversation(BaseModel):
    """A conversation between agents."""
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for this conversation")
    participants: List[str] = Field(..., description="IDs of participating agents")
    subject: str = Field(..., description="Subject of the conversation")
    messages: List[str] = Field(default_factory=list, description="IDs of messages in the conversation")
    status: str = Field("active", description="Status of the conversation")
    created_at: datetime = Field(default_factory=datetime.now, description="When the conversation was created")
    updated_at: datetime = Field(default_factory=datetime.now, description="When the conversation was last updated")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CommunicationInterface:
    """Interface for communication between agents."""
    
    def __init__(self, event_handler: EventHandler):
        """Initialize the communication interface."""
        self.event_handler = event_handler
        
        # Message store
        self.messages = {}  # Map of message_id to AgentMessage
        self.conversations = {}  # Map of conversation_id to AgentConversation
        
        # Message handlers for each agent
        self.message_handlers = {}  # Map of agent_id to message handler function
        
        # Agent directory
        self.agent_directory = {}  # Map of agent_id to agent info (type, capabilities, etc.)
        
        # Conversation state
        self.active_conversations = set()  # Set of active conversation IDs
        
        # Subscribe to agent events
        self.event_handler.subscribe(self._handle_agent_event, [
            EventType.AGENT_CREATED,
            EventType.AGENT_DESTROYED
        ])
        
        logger.info("Communication interface initialized")
    
    def register_agent(
        self, 
        agent_id: str, 
        agent_type: AgentType, 
        capabilities: List[str] = None,
        message_handler: Optional[Callable[[AgentMessage], None]] = None
    ):
        """Register an agent with the communication interface."""
        # Add to directory
        self.agent_directory[agent_id] = {
            "agent_id": agent_id,
            "agent_type": agent_type.value,
            "capabilities": capabilities or [],
            "status": "active",
            "registered_at": datetime.now().isoformat()
        }
        
        # Register message handler if provided
        if message_handler:
            self.message_handlers[agent_id] = message_handler
            
        logger.info(f"Registered agent {agent_id} ({agent_type.value}) with communication interface")
        
        # Broadcast agent registration to other agents
        self._broadcast_system_message(
            f"Agent {agent_id} ({agent_type.value}) has joined the system",
            sender=agent_id,
            additional_data={
                "event": "agent_registered",
                "agent_id": agent_id,
                "agent_type": agent_type.value,
                "capabilities": capabilities or []
            }
        )
        
        # Create agent created event
        asyncio.create_task(self.event_handler.create_custom_event(
            source="communication_interface",
            name="agent_registered",
            data={
                "agent_id": agent_id,
                "agent_type": agent_type.value,
                "capabilities": capabilities or []
            }
        ))
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the communication interface."""
        if agent_id not in self.agent_directory:
            logger.warning(f"Attempted to unregister unknown agent {agent_id}")
            return
            
        # Get agent info before removing
        agent_info = self.agent_directory[agent_id]
        
        # Remove from directory
        del self.agent_directory[agent_id]
        
        # Remove message handler
        if agent_id in self.message_handlers:
            del self.message_handlers[agent_id]
            
        logger.info(f"Unregistered agent {agent_id} from communication interface")
        
        # Broadcast agent unregistration to other agents
        self._broadcast_system_message(
            f"Agent {agent_id} ({agent_info['agent_type']}) has left the system",
            sender="system",
            additional_data={
                "event": "agent_unregistered",
                "agent_id": agent_id,
                "agent_type": agent_info['agent_type']
            }
        )
        
        # Create agent destroyed event
        asyncio.create_task(self.event_handler.create_custom_event(
            source="communication_interface",
            name="agent_unregistered",
            data={
                "agent_id": agent_id,
                "agent_type": agent_info['agent_type']
            }
        ))
        
        # Clean up agent's conversations
        for conversation_id, conversation in list(self.conversations.items()):
            if agent_id in conversation.participants:
                # Mark agent as departed in conversation metadata
                if "departed_agents" not in conversation.metadata:
                    conversation.metadata["departed_agents"] = []
                    
                conversation.metadata["departed_agents"].append({
                    "agent_id": agent_id,
                    "departed_at": datetime.now().isoformat()
                })
                
                # Update conversation
                conversation.updated_at = datetime.now()
                
                # If all participants have departed, mark conversation as closed
                remaining_participants = [p for p in conversation.participants if p != agent_id and p in self.agent_directory]
                if not remaining_participants:
                    conversation.status = "closed"
                    self.active_conversations.discard(conversation_id)
                    
                # Notify remaining participants
                self._send_system_message_to_conversation(
                    conversation_id=conversation_id,
                    message=f"Agent {agent_id} has left the conversation",
                    sender="system",
                    additional_data={
                        "event": "agent_left_conversation",
                        "agent_id": agent_id
                    }
                )
    
    async def send_message(self, message: AgentMessage) -> str:
        """Send a message from one agent to others."""
        message_id = message.message_id
        
        # Validate sender exists
        if message.sender not in self.agent_directory and message.sender != "system":
            logger.warning(f"Message from unknown sender {message.sender}")
            return None
            
        # Validate recipients exist (except for broadcasts)
        if message.type != MessageType.BROADCAST:
            for recipient in message.recipients:
                if recipient not in self.agent_directory and recipient != "system":
                    logger.warning(f"Message to unknown recipient {recipient}")
                    # Filter out unknown recipients
                    message.recipients = [r for r in message.recipients if r in self.agent_directory or r == "system"]
                    
            # If no valid recipients remain, don't send the message
            if not message.recipients:
                logger.warning(f"Message has no valid recipients")
                return None
        
        # Store the message
        self.messages[message_id] = message
        
        # Update or create conversation
        if message.conversation_id:
            # Add to existing conversation
            if message.conversation_id in self.conversations:
                conversation = self.conversations[message.conversation_id]
                conversation.messages.append(message_id)
                conversation.updated_at = datetime.now()
            else:
                # Create new conversation with the given ID
                conversation = AgentConversation(
                    conversation_id=message.conversation_id,
                    participants=[message.sender] + message.recipients,
                    subject=message.subject,
                    messages=[message_id]
                )
                self.conversations[message.conversation_id] = conversation
                self.active_conversations.add(message.conversation_id)
        else:
            # Create new conversation
            conversation_id = str(uuid.uuid4())
            conversation = AgentConversation(
                conversation_id=conversation_id,
                participants=[message.sender] + message.recipients,
                subject=message.subject,
                messages=[message_id]
            )
            self.conversations[conversation_id] = conversation
            self.active_conversations.add(conversation_id)
            
            # Update message with conversation ID
            message.conversation_id = conversation_id
            
        # Deliver the message
        if message.type == MessageType.BROADCAST:
            # Send to all registered agents except the sender
            recipients = [agent_id for agent_id in self.agent_directory if agent_id != message.sender]
        else:
            recipients = message.recipients
            
        # Create message event
        await self.event_handler.create_custom_event(
            source="communication_interface",
            name="message_sent",
            data={
                "message_id": message_id,
                "message_type": message.type,
                "sender": message.sender,
                "recipients": recipients,
                "conversation_id": message.conversation_id
            }
        )
        
        # Deliver to each recipient
        for recipient in recipients:
            if recipient in self.message_handlers:
                # Call the recipient's message handler
                try:
                    handler = self.message_handlers[recipient]
                    
                    # Call handler (which might be sync or async)
                    result = handler(message)
                    
                    # If it's a coroutine, schedule it
                    if asyncio.iscoroutine(result):
                        asyncio.create_task(result)
                        
                    logger.debug(f"Delivered message {message_id} to {recipient}")
                except Exception as e:
                    logger.error(f"Error delivering message {message_id} to {recipient}: {str(e)}")
            else:
                logger.warning(f"No message handler for recipient {recipient}")
        
        # If the message requires acknowledgment, send acknowledgments
        if message.requires_acknowledgment:
            for recipient in recipients:
                if recipient in self.agent_directory:
                    # Create acknowledgment message
                    ack_message = AgentMessage(
                        type=MessageType.RESPONSE,
                        sender="system",
                        recipients=[message.sender],
                        subject=f"Acknowledgment for {message.subject}",
                        content={
                            "acknowledgment": True,
                            "status": "delivered",
                            "recipient": recipient,
                            "timestamp": datetime.now().isoformat()
                        },
                        in_reply_to=message_id,
                        conversation_id=message.conversation_id
                    )
                    
                    # Deliver acknowledgment
                    await self.send_message(ack_message)
        
        return message_id
    
    async def create_and_send_message(
        self, 
        type: MessageType,
        sender: str,
        recipients: List[str],
        subject: str,
        content: Dict[str, Any],
        conversation_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        priority: int = 1,
        requires_acknowledgment: bool = False
    ) -> str:
        """Create and send a message."""
        message = AgentMessage(
            type=type,
            sender=sender,
            recipients=recipients,
            subject=subject,
            content=content,
            conversation_id=conversation_id,
            in_reply_to=in_reply_to,
            priority=priority,
            requires_acknowledgment=requires_acknowledgment
        )
        
        return await self.send_message(message)
    
    async def reply_to_message(
        self, 
        original_message_id: str,
        sender: str,
        content: Dict[str, Any],
        message_type: MessageType = MessageType.RESPONSE,
        subject: Optional[str] = None
    ) -> Optional[str]:
        """Reply to a message."""
        # Check if original message exists
        if original_message_id not in self.messages:
            logger.warning(f"Cannot reply to unknown message {original_message_id}")
            return None
            
        # Get the original message
        original_message = self.messages[original_message_id]
        
        # Determine recipients (sender of original message)
        recipients = [original_message.sender]
        
        # Create reply subject if not provided
        if not subject:
            subject = f"Re: {original_message.subject}"
            
        # Create and send the reply
        return await self.create_and_send_message(
            type=message_type,
            sender=sender,
            recipients=recipients,
            subject=subject,
            content=content,
            conversation_id=original_message.conversation_id,
            in_reply_to=original_message_id
        )
    
    def get_message(self, message_id: str) -> Optional[AgentMessage]:
        """Get a message by ID."""
        return self.messages.get(message_id)
    
    def get_conversation(self, conversation_id: str) -> Optional[AgentConversation]:
        """Get a conversation by ID."""
        return self.conversations.get(conversation_id)
    
    def get_conversation_messages(self, conversation_id: str) -> List[AgentMessage]:
        """Get all messages in a conversation."""
        if conversation_id not in self.conversations:
            logger.warning(f"Unknown conversation ID: {conversation_id}")
            return []
            
        conversation = self.conversations[conversation_id]
        
        # Get messages in order
        messages = []
        for message_id in conversation.messages:
            if message_id in self.messages:
                messages.append(self.messages[message_id])
                
        # Sort by timestamp
        messages.sort(key=lambda m: m.timestamp)
        
        return messages
    
    def find_agent_by_capability(self, capability: str) -> List[str]:
        """Find agents with a specific capability."""
        matching_agents = []
        
        for agent_id, info in self.agent_directory.items():
            if capability in info.get("capabilities", []):
                matching_agents.append(agent_id)
                
        return matching_agents
    
    def get_agent_conversations(self, agent_id: str) -> List[str]:
        """Get all conversation IDs an agent is participating in."""
        if agent_id not in self.agent_directory:
            logger.warning(f"Unknown agent ID: {agent_id}")
            return []
            
        # Find conversations where the agent is a participant
        conversations = []
        for conversation_id, conversation in self.conversations.items():
            if agent_id in conversation.participants:
                conversations.append(conversation_id)
                
        return conversations
    
    def _handle_agent_event(self, event: Event):
        """Handle agent-related events."""
        if event.type == EventType.AGENT_CREATED:
            # Agent was created elsewhere, register it with communication interface
            agent_id = event.data.get("agent_id")
            agent_type_str = event.data.get("agent_type")
            capabilities = event.data.get("capabilities", [])
            
            if agent_id and agent_type_str:
                # Convert string to enum
                agent_type = AgentType(agent_type_str)
                
                # Register if not already registered
                if agent_id not in self.agent_directory:
                    self.register_agent(agent_id, agent_type, capabilities)
                    
        elif event.type == EventType.AGENT_DESTROYED:
            # Agent was destroyed elsewhere, unregister it
            agent_id = event.data.get("agent_id")
            
            if agent_id and agent_id in self.agent_directory:
                self.unregister_agent(agent_id)
    
    def _broadcast_system_message(self, message: str, sender: str, additional_data: Dict[str, Any] = None):
        """Broadcast a system message to all agents."""
        # Create task to send broadcast asynchronously
        async def send_broadcast():
            await self.create_and_send_message(
                type=MessageType.BROADCAST,
                sender=sender,
                recipients=[],  # Empty for broadcast
                subject="System Broadcast",
                content={
                    "message": message,
                    **(additional_data or {})
                }
            )
            
        asyncio.create_task(send_broadcast())
    
    def _send_system_message_to_conversation(
        self, 
        conversation_id: str, 
        message: str, 
        sender: str, 
        additional_data: Dict[str, Any] = None
    ):
        """Send a system message to all participants in a conversation."""
        if conversation_id not in self.conversations:
            logger.warning(f"Cannot send to unknown conversation {conversation_id}")
            return
            
        conversation = self.conversations[conversation_id]
        
        # Get active participants (filter out those who have left)
        recipients = [p for p in conversation.participants if p in self.agent_directory]
        
        if not recipients:
            logger.warning(f"No active participants in conversation {conversation_id}")
            return
            
        # Create task to send message asynchronously
        async def send_message():
            await self.create_and_send_message(
                type=MessageType.SYSTEM,
                sender=sender,
                recipients=recipients,
                subject="System Message",
                content={
                    "message": message,
                    **(additional_data or {})
                },
                conversation_id=conversation_id
            )
            
        asyncio.create_task(send_message())
    
    async def create_group_conversation(
        self, 
        initiator: str, 
        participants: List[str], 
        subject: str,
        initial_message: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Create a new group conversation."""
        # Validate initiator and participants
        if initiator not in self.agent_directory:
            logger.warning(f"Unknown initiator {initiator}")
            return None
            
        valid_participants = []
        for participant in participants:
            if participant in self.agent_directory:
                valid_participants.append(participant)
            else:
                logger.warning(f"Unknown participant {participant}")
                
        if not valid_participants:
            logger.warning("No valid participants for group conversation")
            return None
        
        # Create conversation
        conversation_id = str(uuid.uuid4())
        conversation = AgentConversation(
            conversation_id=conversation_id,
            participants=[initiator] + valid_participants,
            subject=subject,
            messages=[]
        )
        self.conversations[conversation_id] = conversation
        self.active_conversations.add(conversation_id)
        
        # Send initial message if provided
        if initial_message:
            initial_message_id = await self.create_and_send_message(
                type=MessageType.NOTIFICATION,
                sender=initiator,
                recipients=valid_participants,
                subject=subject,
                content=initial_message,
                conversation_id=conversation_id
            )
            
            # Add to conversation messages (should already happen in send_message but just to be sure)
            if initial_message_id and initial_message_id not in conversation.messages:
                conversation.messages.append(initial_message_id)
                
        # Send system message about conversation creation
        self._send_system_message_to_conversation(
            conversation_id=conversation_id,
            message=f"Group conversation '{subject}' created by {initiator}",
            sender="system",
            additional_data={
                "event": "conversation_created",
                "initiator": initiator,
                "participants": valid_participants
            }
        )
        
        return conversation_id
    
    async def add_participant_to_conversation(self, conversation_id: str, participant_id: str, added_by: str) -> bool:
        """Add a participant to a conversation."""
        # Validate conversation exists
        if conversation_id not in self.conversations:
            logger.warning(f"Unknown conversation {conversation_id}")
            return False
            
        # Validate participant exists
        if participant_id not in self.agent_directory:
            logger.warning(f"Unknown participant {participant_id}")
            return False
            
        conversation = self.conversations[conversation_id]
        
        # Check if participant is already in the conversation
        if participant_id in conversation.participants:
            logger.warning(f"Participant {participant_id} is already in conversation {conversation_id}")
            return False
            
        # Add participant
        conversation.participants.append(participant_id)
        conversation.updated_at = datetime.now()
        
        # Send system message about new participant
        self._send_system_message_to_conversation(
            conversation_id=conversation_id,
            message=f"Agent {participant_id} added to conversation by {added_by}",
            sender="system",
            additional_data={
                "event": "participant_added",
                "participant": participant_id,
                "added_by": added_by
            }
        )
        
        return True
    
    async def leave_conversation(self, conversation_id: str, participant_id: str) -> bool:
        """Remove a participant from a conversation."""
        # Validate conversation exists
        if conversation_id not in self.conversations:
            logger.warning(f"Unknown conversation {conversation_id}")
            return False
            
        conversation = self.conversations[conversation_id]
        
        # Check if participant is in the conversation
        if participant_id not in conversation.participants:
            logger.warning(f"Participant {participant_id} is not in conversation {conversation_id}")
            return False
            
        # Mark agent as departed in conversation metadata
        if "departed_agents" not in conversation.metadata:
            conversation.metadata["departed_agents"] = []
            
        conversation.metadata["departed_agents"].append({
            "agent_id": participant_id,
            "departed_at": datetime.now().isoformat()
        })
        
        # Update conversation
        conversation.updated_at = datetime.now()
        
        # Send system message about participant leaving
        self._send_system_message_to_conversation(
            conversation_id=conversation_id,
            message=f"Agent {participant_id} has left the conversation",
            sender="system",
            additional_data={
                "event": "participant_left",
                "participant": participant_id
            }
        )
        
        # Check if any active participants remain
        remaining_participants = [p for p in conversation.participants if p != participant_id and p in self.agent_directory]
        if not remaining_participants:
            conversation.status = "closed"
            self.active_conversations.discard(conversation_id)
            
        return True 