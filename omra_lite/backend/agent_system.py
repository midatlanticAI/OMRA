"""
Agent System for OMRA Lite

This module provides a simplified agent system with the following features:
- Agent management
- Tool registration and execution
- Agent state persistence in MongoDB
"""
import asyncio
import logging
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Callable

from models import Agent, AgentType, AgentStatus, Message, MessageRole, Conversation
from db import get_database
import httpx

# Configure logging
logger = logging.getLogger("omra_lite.agent_system")

# Tool registry
TOOL_REGISTRY: Dict[str, "Tool"] = {}

async def get_api_key(key_name: str) -> Optional[str]:
    """
    Get an API key from the database.
    
    Args:
        key_name: Name of the API key to retrieve
        
    Returns:
        The API key value if found, None otherwise
    """
    db = await get_database()
    key_doc = await db.api_keys.find_one({"key_name": key_name})
    
    if key_doc:
        # In a production environment, you would decrypt the key here if it's encrypted
        return key_doc["key_value"]
    
    # Fall back to environment variable if not in database
    return os.environ.get(key_name)

class Tool:
    """
    Tool that can be used by agents.
    """
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any] = None,
        required_params: List[str] = None,
    ):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters or {}
        self.required_params = required_params or []

def register_tool(
    name: str, 
    description: str, 
    parameters: Dict[str, Any] = None,
    required_params: List[str] = None
):
    """
    Decorator to register a tool in the global registry.
    
    Args:
        name: Tool name
        description: Tool description
        parameters: Parameter descriptions
        required_params: List of required parameter names
    """
    def decorator(func):
        TOOL_REGISTRY[name] = Tool(
            name=name,
            description=description,
            function=func,
            parameters=parameters or {},
            required_params=required_params or [],
        )
        logger.info(f"Registered tool: {name}")
        return func
    return decorator

class AgentInstance:
    """
    Instance of an agent with methods for processing requests.
    """
    def __init__(self, agent_data: Agent):
        self.id = str(agent_data.id) if agent_data.id else str(uuid.uuid4())
        self.name = agent_data.name
        self.type = agent_data.type
        self.description = agent_data.description
        self.tools = agent_data.tools
        self.status = agent_data.status
        self.created_at = agent_data.created_at
        self.updated_at = agent_data.updated_at
        self.last_active = agent_data.last_active or datetime.utcnow()
        
        # Available tools for this agent
        self.available_tools: Dict[str, Tool] = {}
        
        # Load tools
        for tool_name in self.tools:
            if tool_name in TOOL_REGISTRY:
                self.available_tools[tool_name] = TOOL_REGISTRY[tool_name]
        
        logger.info(f"Initialized agent: {self.name} ({self.id}) with {len(self.available_tools)} tools")
    
    async def process_message(self, message: str, conversation_id: str = None) -> str:
        """
        Process a message using the agent.
        
        Args:
            message: The message to process
            conversation_id: Optional conversation ID
            
        Returns:
            The agent's response
        """
        # Update agent status
        self.status = AgentStatus.ACTIVE
        self.last_active = datetime.utcnow()
        await self._update_agent_status()
        
        try:
            # Get or create conversation
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                await self._create_conversation(conversation_id, f"Conversation with {self.name}")
            
            # Save user message
            await self._save_message(conversation_id, MessageRole.USER, message)
            
            # Process message - this is a simple echo for now
            # In a real implementation, this would use LLM or other logic
            response = await self._process_message_content(message, conversation_id)
            
            # Save agent response
            await self._save_message(conversation_id, MessageRole.AGENT, response)
            
            return response
        
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            self.status = AgentStatus.ERROR
            await self._update_agent_status()
            raise
    
    async def _process_message_content(self, message: str, conversation_id: str) -> str:
        """
        Process the content of a message and determine the response.
        
        In a full implementation, this would use an LLM or other AI system.
        For this MVP, we'll use simple rules to determine the response.
        """
        # Check if the message contains any tool names
        for tool_name, tool in self.available_tools.items():
            if tool_name.lower() in message.lower():
                # Extract parameters from message - in a real system this would be more sophisticated
                params = {}
                
                # Example: If message contains "customer" and "email", try to extract an email
                if "customer" in message.lower() and "email" in message.lower():
                    # Very simple email extraction - in a real system this would be more robust
                    import re
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+', message)
                    if email_match:
                        params["email"] = email_match.group(0)
                
                # Example: If message contains "service request" and a priority level
                if "service request" in message.lower():
                    for priority in ["low", "medium", "high", "urgent"]:
                        if priority in message.lower():
                            params["priority"] = priority
                            break
                
                # If the tool requires certain parameters that we haven't extracted, don't use it
                missing_params = [param for param in tool.required_params if param not in params]
                if missing_params:
                    continue
                
                try:
                    # Execute the tool
                    result = await tool.function(self, params)
                    
                    # Format the response
                    if isinstance(result, dict):
                        return f"I used the {tool_name} tool. Result: {json.dumps(result, indent=2)}"
                    else:
                        return f"I used the {tool_name} tool. Result: {result}"
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
                    return f"I tried to use the {tool_name} tool, but there was an error: {str(e)}"
        
        # If no tool was used, provide a generic response
        if "hello" in message.lower() or "hi" in message.lower():
            return f"Hello! I'm {self.name}, an AI assistant that can help with {self.type}. How can I assist you today?"
        
        if "help" in message.lower():
            tools_info = "\n".join([f"- {name}: {tool.description}" for name, tool in self.available_tools.items()])
            return f"I'm {self.name}, an AI assistant that can help with {self.type}. I can use these tools:\n\n{tools_info}\n\nHow can I assist you today?"
        
        # Default response
        return f"I'm {self.name}, an AI assistant. I understand you said: '{message}'. How can I help you with that?"
    
    async def use_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Use a tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to use
            parameters: Parameters for the tool
            
        Returns:
            The result of the tool execution
        """
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available to this agent")
        
        tool = self.available_tools[tool_name]
        
        # Validate required parameters
        missing_params = [param for param in tool.required_params if param not in parameters]
        if missing_params:
            raise ValueError(f"Missing required parameters for tool '{tool_name}': {', '.join(missing_params)}")
        
        try:
            return await tool.function(self, parameters)
        except Exception as e:
            logger.error(f"Error using tool {tool_name}: {e}", exc_info=True)
            raise
    
    async def _update_agent_status(self):
        """Update agent status in database."""
        db = await get_database()
        await db.agents.update_one(
            {"_id": self.id},
            {
                "$set": {
                    "status": self.status,
                    "updated_at": datetime.utcnow(),
                    "last_active": self.last_active
                }
            }
        )
    
    async def _create_conversation(self, conversation_id: str, title: str):
        """Create a new conversation in database."""
        db = await get_database()
        conversation = {
            "_id": conversation_id,
            "title": title,
            "agent_id": self.id,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "metadata": {}
        }
        await db.conversations.insert_one(conversation)
    
    async def _save_message(self, conversation_id: str, role: MessageRole, content: str):
        """Save a message to the conversation in database."""
        db = await get_database()
        message = {
            "_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
            "metadata": {}
        }
        await db.messages.insert_one(message)
        
        # Update conversation last updated time
        await db.conversations.update_one(
            {"_id": conversation_id},
            {"$set": {"updated_at": datetime.utcnow()}}
        )

    async def _get_llm_response(self, prompt: str) -> str:
        """Get a response from the LLM."""
        # Get API key from database or environment
        api_key = await get_api_key("ANTHROPIC_API_KEY")
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in settings or environment variables")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-sonnet-20240229",
                        "max_tokens": 1024,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                return result["content"][0]["text"]
        
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}", exc_info=True)
            raise

class AgentManager:
    """
    Manager for creating and managing agents.
    """
    def __init__(self):
        self.agents: Dict[str, AgentInstance] = {}
        self._initialize_default_tools()
    
    def _initialize_default_tools(self):
        """Initialize default tools."""
        # If tools are already registered, don't register them again
        if 'customer_lookup' in TOOL_REGISTRY:
            return
            
        @register_tool(
            name="customer_lookup",
            description="Look up a customer by email or phone number",
            parameters={
                "email": {"type": "string", "description": "Customer email"},
                "phone": {"type": "string", "description": "Customer phone number"}
            },
            required_params=[]
        )
        async def customer_lookup(agent, params):
            """
            Look up a customer by email or phone number.
            
            Args:
                email: Customer email (optional)
                phone: Customer phone number (optional)
                
            Returns:
                The customer information if found, None otherwise
            """
            email = params.get("email")
            phone = params.get("phone")
            
            if not email and not phone:
                return {"error": "Either email or phone is required"}
            
            # Query the database
            db = await get_database()
            query = {}
            
            if email:
                query["contact_info.email"] = email
            if phone:
                query["contact_info.phone"] = phone
            
            customer = await db.customers.find_one(query)
            
            if not customer:
                return {"message": "Customer not found"}
            
            # Convert ObjectId to string for JSON serialization
            customer["_id"] = str(customer["_id"])
            
            return customer
        
        @register_tool(
            name="service_request_create",
            description="Create a new service request for a customer",
            parameters={
                "customer_id": {"type": "string", "description": "Customer ID"},
                "appliance_type": {"type": "string", "description": "Type of appliance"},
                "issue_description": {"type": "string", "description": "Description of the issue"},
                "priority": {"type": "string", "description": "Priority (low, medium, high, urgent)"}
            },
            required_params=["customer_id", "appliance_type", "issue_description"]
        )
        async def service_request_create(agent, params):
            """
            Create a new service request for a customer.
            
            Args:
                customer_id: Customer ID
                appliance_type: Type of appliance
                issue_description: Description of the issue
                priority: Priority (low, medium, high, urgent) (optional)
                
            Returns:
                The created service request
            """
            customer_id = params.get("customer_id")
            appliance_type = params.get("appliance_type")
            issue_description = params.get("issue_description")
            priority = params.get("priority", "medium")
            
            # Create the service request
            db = await get_database()
            
            # Verify customer exists
            customer = await db.customers.find_one({"_id": customer_id})
            if not customer:
                return {"error": f"Customer not found with ID: {customer_id}"}
            
            # Create the service request
            service_request = {
                "customer_id": customer_id,
                "appliance_type": appliance_type,
                "issue_description": issue_description,
                "priority": priority,
                "status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await db.service_requests.insert_one(service_request)
            service_request["_id"] = str(result.inserted_id)
            
            return service_request
        
        @register_tool(
            name="service_request_list",
            description="List service requests for a customer",
            parameters={
                "customer_id": {"type": "string", "description": "Customer ID"},
                "status": {"type": "string", "description": "Status filter (optional)"}
            },
            required_params=["customer_id"]
        )
        async def service_request_list(agent, params):
            """
            List service requests for a customer.
            
            Args:
                customer_id: Customer ID
                status: Status filter (optional)
                
            Returns:
                List of service requests
            """
            customer_id = params.get("customer_id")
            status = params.get("status")
            
            # Query the database
            db = await get_database()
            query = {"customer_id": customer_id}
            
            if status:
                query["status"] = status
            
            cursor = db.service_requests.find(query).sort("created_at", -1)
            service_requests = []
            
            async for service_request in cursor:
                # Convert ObjectId to string for JSON serialization
                service_request["_id"] = str(service_request["_id"])
                service_requests.append(service_request)
            
            return {"service_requests": service_requests, "count": len(service_requests)}
        
        @register_tool(
            name="appliance_troubleshoot",
            description="Troubleshoot an appliance issue",
            parameters={
                "appliance_type": {"type": "string", "description": "Type of appliance"},
                "symptoms": {"type": "array", "description": "List of symptoms"}
            },
            required_params=["appliance_type"]
        )
        async def appliance_troubleshoot(agent, params):
            """
            Troubleshoot an appliance issue.
            
            Args:
                appliance_type: Type of appliance
                symptoms: List of symptoms (optional)
                
            Returns:
                Troubleshooting steps and likely issues
            """
            appliance_type = params.get("appliance_type", "").lower()
            symptoms = params.get("symptoms", [])
            
            # In a full implementation, this could use a knowledge base or LLM
            # For the MVP, we'll use some hardcoded troubleshooting steps
            
            troubleshooting_steps = []
            likely_issues = []
            
            if appliance_type == "refrigerator":
                if "not cooling" in symptoms:
                    troubleshooting_steps = [
                        "Check if the refrigerator is plugged in",
                        "Ensure temperature settings are correct",
                        "Check if the condenser coils are dirty",
                        "Verify the door seals are intact"
                    ]
                    likely_issues = ["Dirty condenser coils", "Faulty thermostat", "Refrigerant leak"]
                elif "making noise" in symptoms:
                    troubleshooting_steps = [
                        "Check if the refrigerator is level",
                        "Inspect the fan for obstructions",
                        "Check the compressor"
                    ]
                    likely_issues = ["Unlevel appliance", "Faulty fan", "Worn compressor"]
                else:
                    troubleshooting_steps = [
                        "Check if the refrigerator is plugged in and has power",
                        "Inspect the temperature settings",
                        "Check for any unusual sounds or smells",
                        "Verify the door seals are intact"
                    ]
                    likely_issues = ["Unknown issue - requires inspection"]
            
            elif appliance_type == "washer":
                if "not draining" in symptoms:
                    troubleshooting_steps = [
                        "Check the drain hose for kinks",
                        "Clean the drain pump filter",
                        "Verify the drain pump is working"
                    ]
                    likely_issues = ["Blocked drain pump", "Faulty drain pump", "Kinked hose"]
                elif "not spinning" in symptoms:
                    troubleshooting_steps = [
                        "Check if the washer is overloaded",
                        "Ensure the washer is level",
                        "Inspect the drive belt"
                    ]
                    likely_issues = ["Overloaded washer", "Worn drive belt", "Faulty motor"]
                else:
                    troubleshooting_steps = [
                        "Check if the washer is plugged in and has power",
                        "Verify water supply is connected and turned on",
                        "Ensure the washer is not overloaded",
                        "Check for any error codes on the display"
                    ]
                    likely_issues = ["Unknown issue - requires inspection"]
            
            else:
                # Generic troubleshooting for other appliance types
                troubleshooting_steps = [
                    f"Check if the {appliance_type} is plugged in and has power",
                    "Inspect for any visible damage",
                    "Check for any error codes or unusual behavior",
                    "Consult the user manual for specific troubleshooting steps"
                ]
                likely_issues = ["Unknown issue - requires inspection"]
            
            return {
                "appliance_type": appliance_type,
                "symptoms": symptoms,
                "troubleshooting_steps": troubleshooting_steps,
                "likely_issues": likely_issues,
                "requires_technician": len(likely_issues) > 1
            }
    
    async def load_agents(self):
        """
        Load all agents from the database.
        """
        db = await get_database()
        async for agent_data in db.agents.find({"status": "active"}):
            agent_model = Agent(
                id=agent_data["_id"],
                name=agent_data["name"],
                type=agent_data["type"],
                description=agent_data.get("description"),
                tools=agent_data.get("tools", []),
                status=agent_data.get("status", "active"),
                created_at=agent_data.get("created_at", datetime.utcnow()),
                updated_at=agent_data.get("updated_at", datetime.utcnow()),
                last_active=agent_data.get("last_active")
            )
            agent_instance = AgentInstance(agent_model)
            self.agents[str(agent_data["_id"])] = agent_instance
        
        logger.info(f"Loaded {len(self.agents)} agents from database")
    
    async def create_agent(self, agent_data: Dict[str, Any]) -> str:
        """
        Create a new agent.
        
        Args:
            agent_data: Agent data including name, type, description, and tools
            
        Returns:
            The agent ID
        """
        db = await get_database()
        
        # Prepare agent data for database
        agent_doc = {
            "name": agent_data["name"],
            "type": agent_data["type"],
            "description": agent_data.get("description", ""),
            "tools": agent_data.get("tools", []),
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }
        
        # Insert agent into database
        result = await db.agents.insert_one(agent_doc)
        agent_id = str(result.inserted_id)
        
        # Get the full agent data with ID
        agent_doc["_id"] = result.inserted_id
        
        # Create agent instance
        agent_model = Agent(**agent_doc)
        agent_instance = AgentInstance(agent_model)
        self.agents[agent_id] = agent_instance
        
        logger.info(f"Created agent: {agent_data['name']} ({agent_id})")
        
        return agent_id
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInstance]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            The agent instance if found, None otherwise
        """
        # If agent is already loaded, return it
        if agent_id in self.agents:
            return self.agents[agent_id]
        
        # Otherwise, try to load it from the database
        db = await get_database()
        agent_data = await db.agents.find_one({"_id": agent_id})
        
        if not agent_data:
            return None
        
        # Create agent instance
        agent_model = Agent(
            id=agent_data["_id"],
            name=agent_data["name"],
            type=agent_data["type"],
            description=agent_data.get("description"),
            tools=agent_data.get("tools", []),
            status=agent_data.get("status", "active"),
            created_at=agent_data.get("created_at", datetime.utcnow()),
            updated_at=agent_data.get("updated_at", datetime.utcnow()),
            last_active=agent_data.get("last_active")
        )
        agent_instance = AgentInstance(agent_model)
        self.agents[agent_id] = agent_instance
        
        return agent_instance
    
    async def process_message(self, agent_id: str, message: str, conversation_id: Optional[str] = None) -> str:
        """
        Process a message using an agent.
        
        Args:
            agent_id: Agent ID
            message: The message to process
            conversation_id: Optional conversation ID
            
        Returns:
            The agent's response
        """
        agent = await self.get_agent(agent_id)
        
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        return await agent.process_message(message, conversation_id)
    
    async def update_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> bool:
        """
        Update an agent.
        
        Args:
            agent_id: Agent ID
            agent_data: Updated agent data
            
        Returns:
            True if successful, False otherwise
        """
        db = await get_database()
        
        # Prepare update data
        update_data = {
            "updated_at": datetime.utcnow()
        }
        
        if "name" in agent_data:
            update_data["name"] = agent_data["name"]
        if "type" in agent_data:
            update_data["type"] = agent_data["type"]
        if "description" in agent_data:
            update_data["description"] = agent_data["description"]
        if "tools" in agent_data:
            update_data["tools"] = agent_data["tools"]
        if "status" in agent_data:
            update_data["status"] = agent_data["status"]
        
        # Update in database
        result = await db.agents.update_one(
            {"_id": agent_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return False
        
        # If the agent is loaded, refresh it
        if agent_id in self.agents:
            # Get updated agent data
            agent_data = await db.agents.find_one({"_id": agent_id})
            
            if agent_data:
                # Create updated agent instance
                agent_model = Agent(
                    id=agent_data["_id"],
                    name=agent_data["name"],
                    type=agent_data["type"],
                    description=agent_data.get("description"),
                    tools=agent_data.get("tools", []),
                    status=agent_data.get("status", "active"),
                    created_at=agent_data.get("created_at", datetime.utcnow()),
                    updated_at=agent_data.get("updated_at", datetime.utcnow()),
                    last_active=agent_data.get("last_active")
                )
                agent_instance = AgentInstance(agent_model)
                self.agents[agent_id] = agent_instance
        
        return True
    
    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if successful, False otherwise
        """
        db = await get_database()
        
        # Delete from database
        result = await db.agents.delete_one({"_id": agent_id})
        
        if result.deleted_count == 0:
            return False
        
        # Remove from loaded agents
        if agent_id in self.agents:
            del self.agents[agent_id]
        
        return True
    
    async def initialize_default_agents(self):
        """
        Initialize default agents if they don't exist.
        """
        db = await get_database()
        
        # Check if we have any agents
        count = await db.agents.count_documents({})
        
        if count == 0:
            # Create default customer service agent
            await self.create_agent({
                "name": "Customer Service Agent",
                "type": AgentType.CUSTOMER_SERVICE,
                "description": "Handles customer inquiries and service requests",
                "tools": ["customer_lookup", "service_request_create", "service_request_list"]
            })
            
            # Create default diagnosis agent
            await self.create_agent({
                "name": "Diagnosis Agent",
                "type": AgentType.DIAGNOSIS,
                "description": "Helps diagnose appliance issues",
                "tools": ["appliance_troubleshoot"]
            })
            
            logger.info("Created default agents")

# Initialize the agent manager
agent_manager = AgentManager() 