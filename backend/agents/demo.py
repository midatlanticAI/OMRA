import asyncio
import json
import logging
from pprint import pprint

from backend.agents.manager import AgentManager
from backend.agents.core import AgentType, AgentProvider, AgentModel, Message, AgentTool
from backend.agents.events import EventType, EventPriority
from backend.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent_demo")

async def run_demo():
    """Run a demo of the agent system."""
    print("Starting OMRA Agent Architecture Demo")
    print("------------------------------------------")
    
    # Initialize the agent manager
    manager = AgentManager()
    
    # Start the agent system
    await manager.start()
    print("✅ Agent system started")
    
    try:
        # ------ Create agents ------
        
        # Create an executive agent (Claude 3.7 Sonnet with extended thinking)
        executive_agent_id = await manager.create_executive_agent(
            thinking_budget=4000,
            tools=[
                {
                    "name": "analyze_customer_data",
                    "description": "Analyze customer data to extract insights and patterns",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "The ID of the customer to analyze"
                            }
                        },
                        "required": ["customer_id"]
                    }
                }
            ]
        )
        print(f"✅ Created executive agent: {executive_agent_id}")
        
        # Create a manager agent (GPT-4o)
        manager_agent_id = await manager.create_manager_agent(
            tools=[
                {
                    "name": "schedule_service",
                    "description": "Schedule a service appointment for a customer",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "The ID of the customer"
                            },
                            "service_type": {
                                "type": "string",
                                "description": "The type of service needed"
                            },
                            "preferred_date": {
                                "type": "string",
                                "description": "The preferred date for the service (YYYY-MM-DD)"
                            }
                        },
                        "required": ["customer_id", "service_type"]
                    }
                }
            ]
        )
        print(f"✅ Created manager agent: {manager_agent_id}")
        
        # Create a task agent (GPT-4o-mini)
        task_agent_id = await manager.create_task_agent(
            tools=[
                {
                    "name": "validate_customer_info",
                    "description": "Validate customer information for completeness and accuracy",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "customer_data": {
                                "type": "object",
                                "description": "The customer data to validate"
                            }
                        },
                        "required": ["customer_data"]
                    }
                }
            ]
        )
        print(f"✅ Created task agent: {task_agent_id}")
        
        # ------ Create a workflow ------
        workflow_id = await manager.create_workflow(
            name="Customer Service Request",
            description="Process a new service request from a customer",
            initial_data={
                "customer_id": "CUST-12345",
                "customer_name": "John Smith",
                "service_type": "Refrigerator Repair",
                "urgency": "High",
                "preferred_dates": ["2023-12-01", "2023-12-02", "2023-12-03"],
                "description": "Refrigerator is not cooling properly and making a loud noise"
            }
        )
        print(f"✅ Created workflow: {workflow_id}")
        
        # Add agents to the workflow
        await manager.add_agent_to_workflow(workflow_id, executive_agent_id)
        await manager.add_agent_to_workflow(workflow_id, manager_agent_id)
        await manager.add_agent_to_workflow(workflow_id, task_agent_id)
        print("✅ Added agents to workflow")
        
        # ------ Make a decision ------
        print("\nMaking workflow decision...")
        decision = await manager.make_workflow_decision(
            workflow_id=workflow_id,
            decision_type="service_prioritization",
            context_data={
                "customer_id": "CUST-12345",
                "service_type": "Refrigerator Repair",
                "urgency": "High",
                "current_schedule": {
                    "technicians_available": 2,
                    "pending_requests": 5
                }
            }
        )
        
        print("\n📝 Decision Result:")
        print(f"Decision: {decision.decision}")
        print(f"Confidence: {decision.confidence}")
        print(f"Reasoning: {decision.reasoning[:200]}...")
        print(f"Actions: {len(decision.actions)}")
        
        # ------ Execute decision actions ------
        print("\nExecuting decision actions...")
        action_results = await manager.execute_decision_actions(decision)
        
        print(f"✅ Executed {len(action_results)} actions")
        
        # ------ System metrics ------
        print("\n📊 System Metrics:")
        metrics = manager.get_system_metrics()
        pprint(metrics)
        
        # ------ Inter-agent communication demo ------
        print("\nDemonstrating inter-agent communication...")
        
        # Create a group conversation
        conversation_id = await manager.communication.create_group_conversation(
            initiator=executive_agent_id,
            participants=[manager_agent_id, task_agent_id],
            subject="Service Request Coordination",
            initial_message={
                "message": "We need to coordinate on processing the refrigerator repair request for customer CUST-12345",
                "service_type": "Refrigerator Repair",
                "urgency": "High",
                "customer_name": "John Smith"
            }
        )
        
        print(f"✅ Created group conversation: {conversation_id}")
        
        # Wait a moment for messages to process
        await asyncio.sleep(5)
        
        # Get conversation messages
        messages = manager.communication.get_conversation_messages(conversation_id)
        
        print(f"\n💬 Conversation ({len(messages)} messages):")
        for i, msg in enumerate(messages):
            print(f"Message {i+1}: {msg.sender} -> {msg.subject}")
        
        # Wait for some processing time
        print("\nWaiting for agent system to process events...")
        await asyncio.sleep(5)
        
        # Get updated workflow info
        workflow_info = manager.get_workflow_info(workflow_id)
        print(f"\n✅ Workflow status: {workflow_info['status']}")
        print(f"✅ Decisions made: {len(workflow_info['decisions'])}")
        print(f"✅ Actions executed: {len(workflow_info['actions'])}")
        
    finally:
        # Stop the agent system
        await manager.stop()
        print("\n✅ Agent system stopped")

if __name__ == "__main__":
    asyncio.run(run_demo()) 