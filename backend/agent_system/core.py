"""Core system for managing agent lifecycle and communication"""
import yaml
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

from utils.logging import logger, log_agent_activity
from .llm_connector import LLMConnector
from .agents.executive.executive_agent import ExecutiveAgent
from .agents.manager.customer_relations_agent import CustomerRelationsAgent
from .agents.manager.service_operations_agent import ServiceOperationsAgent
from .agents.manager.financial_operations_agent import FinancialOperationsAgent
from .agents.manager.marketing_agent import MarketingAgent
from .agents.manager.administrative_agent import AdministrativeAgent

class AgentSystem:
    """Core system for managing agent lifecycle and communication"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.executive_agent = None
        self.manager_agents = {}
        self.task_agents = {}
        self.active_workflows = {}
        self.llm_connector = LLMConnector(self.config["llm"])
        self.logger = logger
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from file"""
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
            
    async def initialize(self):
        """Initialize the agent system"""
        self.logger.info("Initializing agent system")
        await self._initialize_executive_agent()
        await self._initialize_manager_agents()
        self.logger.info("Agent system initialized successfully")
        
    async def _initialize_executive_agent(self):
        """Initialize the executive agent"""
        self.logger.info("Initializing executive agent")
        self.executive_agent = ExecutiveAgent(
            self.llm_connector,
            self.config["agents"]["executive"]
        )
        
    async def _initialize_manager_agents(self):
        """Initialize manager-level agents"""
        self.logger.info("Initializing manager agents")
        
        # Create manager agents
        self.manager_agents["customer_relations"] = CustomerRelationsAgent(
            self.llm_connector,
            self.config["agents"]["manager"]["customer_relations"]
        )
        
        self.manager_agents["service_operations"] = ServiceOperationsAgent(
            self.llm_connector,
            self.config["agents"]["manager"]["service_operations"]
        )
        
        self.manager_agents["financial_operations"] = FinancialOperationsAgent(
            self.llm_connector,
            self.config["agents"]["manager"]["financial_operations"]
        )
        
        self.manager_agents["marketing"] = MarketingAgent(
            self.llm_connector,
            self.config["agents"]["manager"]["marketing"]
        )
        
        self.manager_agents["administrative"] = AdministrativeAgent(
            self.llm_connector,
            self.config["agents"]["manager"]["administrative"]
        )
        
        # Initialize task agents for each manager
        for manager_name, manager_agent in self.manager_agents.items():
            await manager_agent.initialize_task_agents(self.llm_connector)
        
    async def process_request(self, request: dict) -> dict:
        """Process an incoming request through the agent system"""
        request_id = request.get('id', f"req_{self._get_timestamp()}")
        self.logger.info(f"Processing request: {request_id}")
        log_agent_activity("system", "core", "process_request", {"request_id": request_id})
        
        # Create a new workflow for this request
        workflow_id = f"workflow_{request_id}"
        self.active_workflows[workflow_id] = {
            "id": workflow_id,
            "status": "initiated",
            "request": request,
            "steps": [],
            "started_at": self._get_timestamp(),
            "completed_at": None,
            "response": None
        }
        
        try:
            # Send to executive agent for planning
            workflow_plan = await self.executive_agent.analyze_request(request)
            
            # Update workflow with plan
            self.active_workflows[workflow_id]["plan"] = workflow_plan
            self.active_workflows[workflow_id]["status"] = "planned"
            
            # Execute the workflow steps
            for step in workflow_plan["steps"]:
                step_result = await self._execute_workflow_step(workflow_id, step)
                self.active_workflows[workflow_id]["steps"].append(step_result)
                
            # Synthesize final response
            final_response = await self.executive_agent.synthesize_response(
                request,
                self.active_workflows[workflow_id]
            )
            
            # Update workflow with response
            self.active_workflows[workflow_id]["response"] = final_response
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["completed_at"] = self._get_timestamp()
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "response": final_response
            }
            
        except Exception as e:
            self.logger.error(f"Error processing workflow {workflow_id}: {str(e)}")
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = str(e)
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _execute_workflow_step(self, workflow_id: str, step: dict) -> dict:
        """Execute a single step in a workflow"""
        workflow = self.active_workflows[workflow_id]
        step_id = f"{workflow_id}_step_{len(workflow['steps']) + 1}"
        
        self.logger.info(f"Executing step {step_id}: {step['type']}")
        log_agent_activity("system", "core", "execute_step", {
            "workflow_id": workflow_id,
            "step_id": step_id,
            "step_type": step["type"]
        })
        
        step_result = {
            "id": step_id,
            "type": step["type"],
            "status": "started",
            "started_at": self._get_timestamp(),
            "completed_at": None,
            "result": None
        }
        
        try:
            if step["agent_type"] == "manager":
                # Execute with manager agent
                manager_agent = self.manager_agents[step["agent_name"]]
                result = await manager_agent.execute_task(step["task"])
                
            elif step["agent_type"] == "task":
                # Get the parent manager
                manager_agent = self.manager_agents[step["manager"]]
                # Execute with task agent
                result = await manager_agent.execute_task_agent(
                    step["agent_name"],
                    step["task"]
                )
                
            else:
                raise ValueError(f"Unknown agent type: {step['agent_type']}")
                
            step_result["status"] = "completed"
            step_result["completed_at"] = self._get_timestamp()
            step_result["result"] = result
            
            return step_result
            
        except Exception as e:
            self.logger.error(f"Error executing step {step_id}: {str(e)}")
            step_result["status"] = "failed"
            step_result["error"] = str(e)
            return step_result
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        return datetime.now().isoformat()
    
    async def shutdown(self):
        """Shutdown the agent system and clean up resources"""
        self.logger.info("Shutting down agent system")
        # Clean up any resources
        # Close connections, etc.
        self.logger.info("Agent system shutdown complete") 