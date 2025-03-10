"""
API routes for interacting with the agent system.
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pymongo.database import Database

from backend.db.mongodb import get_mongodb
from backend.agents.executive import ExecutiveAgent
from backend.agents.manager import ManagerAgent
from backend.agents.task import TaskAgent
from backend.core.logging import log_agent_activity
from backend.services.document_service import AgentTaskDocumentService

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)

# Initialize agents
executive_agent = ExecutiveAgent()
customer_manager = ManagerAgent("CustomerManager", "customer_management")
service_manager = ManagerAgent("ServiceManager", "service_management")
integration_manager = ManagerAgent("IntegrationManager", "integration_management")

# Task agents
appointment_scheduler = TaskAgent("AppointmentScheduler", "scheduling")
email_composer = TaskAgent("EmailComposer", "communication")
data_validator = TaskAgent("DataValidator", "validation")

@router.post("/executive/query", response_model=Dict[str, Any])
async def query_executive_agent(
    query: str = Body(..., embed=True),
    context: Optional[str] = Body(None, embed=True),
    db: Database = Depends(get_mongodb)
):
    """
    Query the executive agent with an instruction or question.
    """
    # Log the request
    log_agent_activity(
        agent_type="executive",
        agent_name="ExecutiveAgent",
        action="api_query",
        details={"query_length": len(query), "has_context": bool(context)}
    )
    
    # Create a task document
    task_service = AgentTaskDocumentService(db)
    task_id = await task_service.create_task({
        "agent_type": "executive",
        "agent_name": "ExecutiveAgent",
        "status": "pending",
        "request": {
            "query": query,
            "context": context
        }
    })
    
    # Process the query
    input_data = {"query": query}
    if context:
        input_data["context"] = context
    
    try:
        response = await executive_agent.process(input_data)
        
        # Update the task document
        await task_service.update_task_status(
            task_id=task_id,
            status="completed",
            response=response
        )
        
        return response
    except Exception as e:
        # Update the task document with error
        await task_service.update_task_status(
            task_id=task_id,
            status="failed",
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing error: {str(e)}"
        )

@router.post("/executive/task-breakdown", response_model=Dict[str, Any])
async def get_task_breakdown(
    task_description: str = Body(..., embed=True),
    db: Database = Depends(get_mongodb)
):
    """
    Break down a complex task into subtasks for manager agents.
    """
    # Log the request
    log_agent_activity(
        agent_type="executive",
        agent_name="ExecutiveAgent",
        action="task_breakdown",
        details={"task_description_length": len(task_description)}
    )
    
    # Create a task document
    task_service = AgentTaskDocumentService(db)
    task_id = await task_service.create_task({
        "agent_type": "executive",
        "agent_name": "ExecutiveAgent",
        "status": "pending",
        "request": {
            "task_description": task_description
        }
    })
    
    try:
        response = await executive_agent.get_task_breakdown(task_description)
        
        # Update the task document
        await task_service.update_task_status(
            task_id=task_id,
            status="completed",
            response=response
        )
        
        return response
    except Exception as e:
        # Update the task document with error
        await task_service.update_task_status(
            task_id=task_id,
            status="failed",
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing error: {str(e)}"
        )

@router.post("/manager/{manager_name}/execute", response_model=Dict[str, Any])
async def execute_manager_task(
    manager_name: str,
    task: Dict[str, Any] = Body(...),
    db: Database = Depends(get_mongodb)
):
    """
    Execute a task with a specific manager agent.
    """
    # Get the appropriate manager
    manager_map = {
        "customer": customer_manager,
        "service": service_manager,
        "integration": integration_manager
    }
    
    manager = manager_map.get(manager_name.lower())
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manager agent '{manager_name}' not found"
        )
    
    # Log the request
    log_agent_activity(
        agent_type="manager",
        agent_name=manager.name,
        action="execute_task",
        details={"task_keys": list(task.keys())}
    )
    
    # Create a task document
    task_service = AgentTaskDocumentService(db)
    task_id = await task_service.create_task({
        "agent_type": "manager",
        "agent_name": manager.name,
        "status": "pending",
        "request": task
    })
    
    try:
        response = await manager.execute_task(task)
        
        # Update the task document
        await task_service.update_task_status(
            task_id=task_id,
            status="completed",
            response=response
        )
        
        return response
    except Exception as e:
        # Update the task document with error
        await task_service.update_task_status(
            task_id=task_id,
            status="failed",
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing error: {str(e)}"
        )

@router.post("/task/{task_name}/execute", response_model=Dict[str, Any])
async def execute_specific_task(
    task_name: str,
    task_description: str = Body(...),
    task_data: Dict[str, Any] = Body(...),
    db: Database = Depends(get_mongodb)
):
    """
    Execute a specific task with a task agent.
    """
    # Get the appropriate task agent
    task_map = {
        "appointment": appointment_scheduler,
        "email": email_composer,
        "validation": data_validator
    }
    
    task_agent = task_map.get(task_name.lower())
    if not task_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task agent for '{task_name}' not found"
        )
    
    # Log the request
    log_agent_activity(
        agent_type="task",
        agent_name=task_agent.name,
        action="execute_specific_task",
        details={
            "task_description_length": len(task_description),
            "task_data_keys": list(task_data.keys())
        }
    )
    
    # Create a task document
    task_service = AgentTaskDocumentService(db)
    task_id = await task_service.create_task({
        "agent_type": "task",
        "agent_name": task_agent.name,
        "status": "pending",
        "request": {
            "task_description": task_description,
            "task_data": task_data
        }
    })
    
    try:
        response = await task_agent.execute_specific_task(task_description, task_data)
        
        # Update the task document
        await task_service.update_task_status(
            task_id=task_id,
            status="completed",
            response=response
        )
        
        return response
    except Exception as e:
        # Update the task document with error
        await task_service.update_task_status(
            task_id=task_id,
            status="failed",
            error=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent processing error: {str(e)}"
        )

@router.get("/tasks/history", response_model=List[Dict[str, Any]])
async def get_agent_task_history(
    agent_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Database = Depends(get_mongodb)
):
    """
    Get the history of agent tasks.
    """
    task_service = AgentTaskDocumentService(db)
    tasks = await task_service.list_agent_tasks(
        agent_name=agent_name,
        status=status,
        limit=limit
    )
    
    return tasks

@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_agent_task(
    task_id: str,
    db: Database = Depends(get_mongodb)
):
    """
    Get a specific agent task by ID.
    """
    task_service = AgentTaskDocumentService(db)
    task = await task_service.get_task(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    return task 