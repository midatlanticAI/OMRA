# Agent Architecture

The Agent Architecture is a core component of OpenManus that provides AI-powered automation for various business processes. This guide explains the architecture, components, and development guidelines for working with the agent system.

## Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)
3. [Agent Types](#agent-types)
4. [Workflow Engine](#workflow-engine)
5. [Tool Registry](#tool-registry)
6. [Communication System](#communication-system)
7. [Agent Development](#agent-development)
8. [Testing Agents](#testing-agents)
9. [Best Practices](#best-practices)
10. [Examples](#examples)

## Overview

The OpenManus Agent Architecture is a hierarchical system of intelligent agents that work together to automate business processes. The architecture is designed to be:

- **Modular**: Components can be developed and deployed independently
- **Extensible**: New agent types and tools can be added easily
- **Scalable**: Components can be scaled horizontally
- **Resilient**: The system can recover from failures
- **Observable**: Comprehensive logging and monitoring

The agent system leverages large language models (LLMs) like Claude to provide natural language understanding and generation capabilities, combined with specialized tools for interacting with the OpenManus system and external services.

## Core Components

![Agent Architecture Diagram](images/agent-architecture.png)

### 1. Agent Manager

The Agent Manager is the central coordinator of the agent system. It is responsible for:

- Starting and stopping agents
- Managing agent lifecycles
- Routing messages between agents
- Handling errors and retries
- Collecting metrics and logs

```python
# Example of using the Agent Manager
from backend.agents.manager import AgentManager

# Initialize the agent manager
agent_manager = AgentManager()

# Start the agent system
await agent_manager.start()

# Create an agent
exec_agent = await agent_manager.create_agent(
    agent_type="executive",
    name="CustomerServiceExec",
    thinking_budget=4000,
    tools=["customer_lookup", "service_request_creator"]
)

# Stop the agent system
await agent_manager.stop()
```

### 2. Agent Base

The Agent Base is the foundation class for all agent types. It provides common functionality such as:

- Communication with the Agent Manager
- Access to tools
- State management
- Event handling
- Logging and metrics

```python
# Example of extending the Agent Base
from backend.agents.base import AgentBase

class MyCustomAgent(AgentBase):
    def __init__(self, name, tools=None, **kwargs):
        super().__init__(name, tools, **kwargs)
        self.custom_state = {}
    
    async def process_request(self, request):
        # Custom processing logic
        result = await self.use_tool("my_tool", {"param": "value"})
        return result
```

### 3. Tool Registry

The Tool Registry manages the tools available to agents. It provides:

- Tool registration and discovery
- Tool execution
- Access control
- Monitoring and metrics

```python
# Example of registering a tool
from backend.agents.tools import register_tool

@register_tool
async def customer_lookup(agent, params):
    """
    Look up a customer by email or phone number.
    
    Args:
        email (str, optional): Customer email
        phone (str, optional): Customer phone number
        
    Returns:
        dict: Customer information if found, None otherwise
    """
    # Tool implementation
    customer = await db.customers.find_one({"email": params.get("email")})
    return customer
```

### 4. Workflow Engine

The Workflow Engine manages business process workflows. It provides:

- Workflow definition and execution
- State management
- Transition rules
- Event handling
- Monitoring and metrics

```python
# Example of defining a workflow
from backend.agents.workflows import Workflow, Step

# Define a workflow for handling a new service request
workflow = Workflow(
    name="New Service Request",
    description="Handle a new service request from a customer"
)

# Add steps to the workflow
workflow.add_step(
    Step(
        name="Customer Verification",
        description="Verify customer information",
        agent_type="task",
        tools=["customer_lookup", "customer_create"]
    )
)

workflow.add_step(
    Step(
        name="Service Request Creation",
        description="Create a new service request",
        agent_type="task",
        tools=["service_request_create"]
    )
)

workflow.add_step(
    Step(
        name="Technician Assignment",
        description="Assign a technician to the service request",
        agent_type="manager",
        tools=["technician_finder", "service_request_update"]
    )
)
```

## Agent Types

OpenManus defines several agent types with specific responsibilities:

### 1. Executive Agent

The Executive Agent is responsible for high-level decision-making and task delegation. It has:

- Access to a wide range of tools
- The ability to create and manage workflows
- The ability to delegate tasks to other agents
- The highest level of autonomy

```python
from backend.agents.executive import ExecutiveAgent

# Create an executive agent
exec_agent = ExecutiveAgent(
    name="CustomerServiceExec",
    thinking_budget=4000,
    tools=["customer_lookup", "service_request_creator", "workflow_manager"]
)

# Executive agents can make decisions
decision = await exec_agent.make_decision(
    context={"customer_id": 123, "issue": "refrigerator not cooling"},
    options=[
        {"id": "schedule", "description": "Schedule a technician visit"},
        {"id": "troubleshoot", "description": "Attempt remote troubleshooting"},
        {"id": "escalate", "description": "Escalate to human supervisor"}
    ]
)
```

### 2. Manager Agent

The Manager Agent is responsible for coordinating specific business processes. It has:

- Specialized knowledge in a specific domain
- The ability to manage a team of task agents
- Medium level of autonomy

```python
from backend.agents.manager import ManagerAgent

# Create a manager agent
scheduler_agent = ManagerAgent(
    name="SchedulingManager",
    thinking_budget=2000,
    tools=["calendar_access", "technician_finder", "customer_notifier"]
)

# Manager agents can coordinate tasks
schedule_result = await scheduler_agent.coordinate_scheduling(
    service_request_id=456,
    customer_preferences={"preferred_time": "morning", "preferred_days": ["Mon", "Wed"]}
)
```

### 3. Task Agent

The Task Agent is responsible for executing specific tasks. It has:

- Highly specialized capabilities
- Limited scope of responsibility
- Lower level of autonomy

```python
from backend.agents.task import TaskAgent

# Create a task agent
customer_agent = TaskAgent(
    name="CustomerValidator",
    thinking_budget=1000,
    tools=["customer_lookup", "customer_create", "customer_update"]
)

# Task agents perform specific tasks
validation_result = await customer_agent.validate_customer_info(
    customer_data={
        "email": "john.doe@example.com",
        "phone": "555-123-4567",
        "address": "123 Main St"
    }
)
```

## Workflow Engine

The Workflow Engine manages business process workflows. A workflow consists of:

- A sequence of steps
- Transition rules between steps
- Input and output data
- State management

### Workflow Definition

```python
from backend.agents.workflows import Workflow, Step, Transition

# Define a workflow
workflow = Workflow(
    name="Customer Onboarding",
    description="Process for onboarding a new customer"
)

# Add steps
workflow.add_step(
    Step(
        id="collect_info",
        name="Collect Information",
        description="Collect customer information",
        agent_type="task",
        agent_name="CustomerInfoCollector",
        tools=["customer_form"]
    )
)

workflow.add_step(
    Step(
        id="validate_info",
        name="Validate Information",
        description="Validate customer information",
        agent_type="task",
        agent_name="CustomerValidator",
        tools=["customer_validator"]
    )
)

workflow.add_step(
    Step(
        id="create_account",
        name="Create Account",
        description="Create customer account",
        agent_type="task",
        agent_name="AccountCreator",
        tools=["customer_create"]
    )
)

# Add transitions
workflow.add_transition(
    Transition(
        from_step="collect_info",
        to_step="validate_info",
        condition="info_collected"
    )
)

workflow.add_transition(
    Transition(
        from_step="validate_info",
        to_step="create_account",
        condition="info_valid"
    )
)

workflow.add_transition(
    Transition(
        from_step="validate_info",
        to_step="collect_info",
        condition="info_invalid"
    )
)
```

### Workflow Execution

```python
from backend.agents.workflows import WorkflowEngine

# Initialize the workflow engine
workflow_engine = WorkflowEngine()

# Create a workflow instance
workflow_instance = await workflow_engine.create_workflow(
    workflow_id="customer_onboarding",
    initial_data={
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com"
    }
)

# Execute the workflow
await workflow_engine.execute_workflow(workflow_instance.id)

# Get workflow status
status = await workflow_engine.get_workflow_status(workflow_instance.id)
```

## Tool Registry

The Tool Registry manages the tools available to agents. Tools are Python functions with special decorators that provide:

- Documentation for the agent
- Parameter validation
- Access control
- Monitoring and metrics

### Defining Tools

```python
from backend.agents.tools import register_tool, ToolParameter

@register_tool
async def customer_lookup(agent, params):
    """
    Look up a customer by email or phone number.
    
    Args:
        email (str, optional): Customer email
        phone (str, optional): Customer phone number
        
    Returns:
        dict: Customer information if found, None otherwise
    """
    email = params.get("email")
    phone = params.get("phone")
    
    if not email and not phone:
        return {"error": "Either email or phone is required"}
    
    query = {}
    if email:
        query["email"] = email
    if phone:
        query["phone"] = phone
    
    customer = await agent.db.customers.find_one(query)
    return customer

# Tools can also use typed parameters
@register_tool
async def create_service_request(
    agent,
    customer_id: ToolParameter(type=int, description="Customer ID"),
    issue: ToolParameter(type=str, description="Description of the issue"),
    priority: ToolParameter(type=str, description="Priority (low, medium, high, urgent)", default="medium")
):
    """
    Create a new service request for a customer.
    
    Returns:
        dict: The created service request
    """
    service_request = {
        "customer_id": customer_id,
        "issue_description": issue,
        "priority": priority,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    result = await agent.db.service_requests.insert_one(service_request)
    service_request["id"] = result.inserted_id
    
    return service_request
```

### Using Tools

```python
# Agents can use tools directly
result = await agent.use_tool(
    "customer_lookup",
    {"email": "john.doe@example.com"}
)

# Or tools can be used in agent prompts
prompt = """
Please look up the customer with email john.doe@example.com and create a service request
for their refrigerator not cooling properly.
"""
response = await agent.process(prompt)
```

## Communication System

Agents communicate with each other through a messaging system. Messages can be:

- Direct: From one agent to another
- Broadcast: From one agent to many
- Group: Within a conversation group

### Message Types

- **Request**: A request for information or action
- **Response**: A response to a request
- **Notification**: An asynchronous notification
- **Error**: An error message

### Creating a Group Conversation

```python
from backend.agents.communication import GroupConversation

# Create a group conversation
conversation = GroupConversation(
    name="Service Request Discussion",
    description="Discussion about a specific service request"
)

# Add agents to the conversation
conversation.add_agent(executive_agent)
conversation.add_agent(scheduler_agent)
conversation.add_agent(technician_agent)

# Start the conversation
await conversation.start(
    initial_message="Let's discuss how to handle service request #123"
)

# Send a message to the conversation
await conversation.send_message(
    sender=executive_agent,
    content="What's the customer's history?"
)

# Get conversation history
messages = await conversation.get_messages()
```

## Agent Development

This section provides guidelines for developing new agents or extending existing ones.

### Creating a New Agent Type

```python
from backend.agents.base import AgentBase

class DiagnosticAgent(AgentBase):
    """
    Agent specialized in diagnosing appliance issues.
    """
    
    def __init__(self, name, appliance_types=None, **kwargs):
        super().__init__(name, **kwargs)
        self.appliance_types = appliance_types or ["refrigerator", "washer", "dryer"]
        
    async def diagnose_issue(self, appliance_type, symptoms):
        """
        Diagnose an appliance issue based on symptoms.
        
        Args:
            appliance_type (str): Type of appliance
            symptoms (list): List of symptoms
            
        Returns:
            dict: Diagnosis result
        """
        if appliance_type not in self.appliance_types:
            return {"error": f"Unsupported appliance type: {appliance_type}"}
        
        # Use tools to help with diagnosis
        knowledge_base_result = await self.use_tool(
            "knowledge_base_lookup",
            {"appliance_type": appliance_type, "symptoms": symptoms}
        )
        
        # Use LLM to analyze the results
        diagnosis = await self.analyze(
            context=knowledge_base_result,
            question=f"What is the most likely cause of these symptoms: {symptoms}?",
            thinking_budget=2000
        )
        
        return {
            "appliance_type": appliance_type,
            "symptoms": symptoms,
            "diagnosis": diagnosis,
            "confidence": 0.85,  # Example confidence score
            "recommended_parts": ["compressor", "refrigerant"]
        }
```

### Adding Tools for a New Agent

```python
from backend.agents.tools import register_tool

@register_tool(agent_types=["diagnostic"])
async def symptom_analyzer(agent, params):
    """
    Analyze symptoms to identify common patterns.
    
    Args:
        appliance_type (str): Type of appliance
        symptoms (list): List of symptoms
        
    Returns:
        dict: Analysis result
    """
    appliance_type = params.get("appliance_type")
    symptoms = params.get("symptoms", [])
    
    # Implementation of symptom analysis
    # ...
    
    return {
        "common_patterns": ["compressor failure", "refrigerant leak"],
        "severity": "medium",
        "recommended_diagnostic_steps": ["check compressor", "check refrigerant level"]
    }
```

## Testing Agents

This section provides guidelines for testing agents.

### Unit Testing Agents

```python
import pytest
from unittest.mock import patch, MagicMock

from backend.agents.task import TaskAgent

@pytest.fixture
def customer_agent():
    agent = TaskAgent(
        name="CustomerValidator",
        thinking_budget=1000,
        tools=["customer_lookup", "customer_create", "customer_update"]
    )
    return agent

@patch("backend.agents.task.TaskAgent.use_tool")
async def test_validate_customer_info(mock_use_tool, customer_agent):
    # Mock the customer_lookup tool
    mock_use_tool.return_value = None  # Customer not found
    
    # Test validation of new customer
    result = await customer_agent.validate_customer_info(
        customer_data={
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "address": "123 Main St"
        }
    )
    
    # Verify the tool was called with the right parameters
    mock_use_tool.assert_called_with(
        "customer_lookup",
        {"email": "john.doe@example.com"}
    )
    
    # Verify the result
    assert result["valid"] is True
    assert result["new_customer"] is True
```

### Integration Testing Agents

```python
import pytest
from backend.agents.manager import AgentManager
from backend.db.session import get_db

@pytest.fixture
async def agent_manager():
    manager = AgentManager()
    await manager.start()
    yield manager
    await manager.stop()

@pytest.mark.integration
async def test_customer_onboarding_workflow(agent_manager, test_db):
    # Create a workflow for customer onboarding
    workflow = await agent_manager.create_workflow(
        workflow_id="customer_onboarding",
        initial_data={
            "customer_name": "John Doe",
            "customer_email": "john.doe@example.com",
            "customer_phone": "555-123-4567"
        }
    )
    
    # Execute the workflow
    await agent_manager.execute_workflow(workflow.id)
    
    # Wait for workflow completion
    await agent_manager.wait_for_workflow(workflow.id)
    
    # Get workflow status
    status = await agent_manager.get_workflow_status(workflow.id)
    
    # Verify workflow completed successfully
    assert status.state == "completed"
    
    # Verify customer was created in the database
    db = await get_db()
    customer = await db.customers.find_one({"email": "john.doe@example.com"})
    assert customer is not None
    assert customer["name"] == "John Doe"
```

## Best Practices

When working with the agent system, follow these best practices:

### 1. Agent Design

- **Single Responsibility**: Each agent should have a clear, focused responsibility
- **Clear Communication**: Define clear communication interfaces between agents
- **Appropriate Autonomy**: Match the level of autonomy to the agent's responsibility
- **Tool Access Control**: Limit tool access to only what the agent needs
- **Error Handling**: Implement robust error handling

### 2. Tool Development

- **Clear Documentation**: Provide clear, detailed documentation for tools
- **Robust Validation**: Validate all input parameters
- **Appropriate Scope**: Keep tools focused on a single task
- **Error Feedback**: Provide helpful error messages
- **Logging**: Log tool usage for debugging and monitoring

### 3. Workflow Design

- **Clear Steps**: Define clear, focused steps with a single responsibility
- **Well-Defined Transitions**: Define clear conditions for transitions between steps
- **Appropriate Granularity**: Balance between too many small steps and too few large steps
- **Error Recovery**: Include error recovery paths
- **Monitoring**: Add appropriate monitoring and logging

### 4. Testing

- **Comprehensive Unit Tests**: Test individual agents and tools
- **Integration Tests**: Test agent interactions and workflows
- **Scenario Tests**: Test common business scenarios
- **Mocking**: Use mocks for external dependencies
- **Automated Testing**: Include agent tests in CI/CD pipeline

## Examples

This section provides examples of common agent usage patterns.

### Example 1: Customer Onboarding

```python
# Create a workflow for customer onboarding
workflow = Workflow(
    name="Customer Onboarding",
    description="Process for onboarding a new customer"
)

# Add steps
workflow.add_step(
    Step(
        id="collect_info",
        name="Collect Information",
        description="Collect customer information",
        agent_type="task",
        agent_name="CustomerInfoCollector",
        tools=["customer_form"]
    )
)

# ... more steps ...

# Create workflow instance
instance = await workflow_engine.create_workflow(
    workflow_id=workflow.id,
    initial_data={
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com"
    }
)

# Execute workflow
await workflow_engine.execute_workflow(instance.id)
```

### Example 2: Service Request Triage

```python
# Create an executive agent for triage
triage_agent = ExecutiveAgent(
    name="TriageExec",
    thinking_budget=4000,
    tools=[
        "customer_lookup",
        "service_history_lookup",
        "appliance_knowledge_base",
        "technician_finder"
    ]
)

# Triage a service request
triage_result = await triage_agent.triage_request(
    service_request_id=123,
    customer_id=456,
    issue_description="Refrigerator not cooling properly",
    appliance_type="refrigerator",
    appliance_model="GE XYZ123"
)

# Act on the triage result
if triage_result["priority"] == "urgent":
    await scheduler_agent.schedule_emergency_visit(
        service_request_id=123,
        technician_ids=triage_result["recommended_technicians"]
    )
else:
    await scheduler_agent.schedule_normal_visit(
        service_request_id=123,
        preferred_date_range=customer_preferences["date_range"],
        technician_ids=triage_result["recommended_technicians"]
    )
```

### Example 3: Customer Communication

```python
# Create a task agent for customer communication
communication_agent = TaskAgent(
    name="CustomerCommunicator",
    thinking_budget=2000,
    tools=["email_sender", "sms_sender", "notification_sender"]
)

# Send a service confirmation
await communication_agent.send_service_confirmation(
    customer_id=456,
    service_request_id=123,
    appointment_time="2023-04-15T10:00:00Z",
    technician_name="Jane Smith",
    estimated_duration="2 hours"
)

# Send a service reminder
await communication_agent.send_service_reminder(
    customer_id=456,
    service_request_id=123,
    appointment_time="2023-04-15T10:00:00Z",
    technician_name="Jane Smith",
    reminder_time="24 hours before"
)
``` 