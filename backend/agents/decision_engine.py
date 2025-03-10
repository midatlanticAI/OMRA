import logging
import asyncio
import re
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
import json
import time
from pydantic import BaseModel, Field

from backend.agents.core import Agent, AgentConfig, AgentType, AgentProvider, AgentModel, Message, ThinkingConfig
from backend.agents.scheduler import TaskScheduler, Task, TaskPriority, TaskStatus
from backend.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("decision_engine")

class DecisionContext(BaseModel):
    """Context for decision making."""
    workflow_id: str = Field(..., description="ID of the workflow this decision is part of")
    task_id: Optional[str] = Field(None, description="ID of the current task if applicable")
    user_id: Optional[str] = Field(None, description="ID of the user if applicable")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for the decision")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="History of previous decisions in this workflow")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Constraints for the decision")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DecisionResult(BaseModel):
    """Result of a decision."""
    decision_id: str = Field(..., description="Unique ID for this decision")
    workflow_id: str = Field(..., description="ID of the workflow this decision is part of")
    task_id: Optional[str] = Field(None, description="ID of the task if applicable")
    decision: str = Field(..., description="The actual decision")
    confidence: float = Field(..., description="Confidence level (0-1)")
    reasoning: str = Field(..., description="Reasoning behind the decision")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative decisions considered")
    actions: List[Dict[str, Any]] = Field(default_factory=list, description="Actions to take based on the decision")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DecisionEngine:
    """Decision engine that uses agents to make complex decisions."""
    
    def __init__(self, scheduler: TaskScheduler):
        """Initialize the decision engine."""
        self.scheduler = scheduler
        self.executive_agent_config = self._create_executive_agent_config()
        self.decision_cache = {}  # Simple cache for decisions
        logger.info("Decision engine initialized")
    
    def _create_executive_agent_config(self) -> AgentConfig:
        """Create config for the executive agent."""
        # Tool definitions for the executive agent
        tools = [
            {
                "name": "analyze_data",
                "description": "Analyze data to extract insights and patterns. Use this when you need to process complex information or numerical data to identify trends, correlations, or key metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "The data to analyze"
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis to perform (statistical, sentiment, pattern, etc.)"
                        }
                    },
                    "required": ["data"]
                },
                "handler": None  # Will be set later
            },
            {
                "name": "evaluate_alternatives",
                "description": "Evaluate multiple alternative options against a set of criteria to determine the best choice. Use this for comparing different possible decisions or actions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "alternatives": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "description": "An alternative to evaluate"
                            },
                            "description": "List of alternatives to evaluate"
                        },
                        "criteria": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "description": "A criterion with name, weight, and description"
                            },
                            "description": "Criteria to evaluate alternatives against"
                        }
                    },
                    "required": ["alternatives", "criteria"]
                },
                "handler": None  # Will be set later
            },
            {
                "name": "check_constraints",
                "description": "Check if a potential decision or action satisfies a set of constraints. Use this to validate decisions against business rules, user preferences, or system limitations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "decision": {
                            "type": "object",
                            "description": "The decision to check"
                        },
                        "constraints": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "description": "A constraint with rule and importance"
                            },
                            "description": "List of constraints to check against"
                        }
                    },
                    "required": ["decision", "constraints"]
                },
                "handler": None  # Will be set later
            }
        ]
        
        # Create a Claude 3.7 Sonnet agent config with extended thinking
        return AgentConfig(
            agent_type=AgentType.EXECUTIVE,
            provider=AgentProvider.ANTHROPIC,
            model=AgentModel.CLAUDE_3_7_SONNET,
            system_prompt="""You are the Executive Decision Agent for the OMRA system, responsible for making high-level decisions. 
            
Your role is to carefully analyze the provided context, consider all constraints and criteria, and make optimal decisions.

When making decisions:
1. Break down complex problems into subproblems
2. Consider multiple perspectives and alternatives
3. Weigh pros and cons of each alternative
4. Apply relevant domain knowledge
5. Provide clear reasoning for your decisions
6. Propose specific actions to implement your decisions

Always structure your reasoning process clearly, and be explicit about your assumptions and confidence level.
""",
            tools=[],  # Will be filled in later
            temperature=0.3,  # Lower temperature for more consistent decisions
            max_tokens=8000,
            thinking=ThinkingConfig(
                type="enabled",
                budget_tokens=4000
            )
        )
    
    async def make_decision(
        self, 
        context: DecisionContext, 
        decision_type: str
    ) -> DecisionResult:
        """Make a decision based on the provided context."""
        
        # Generate a prompt for the executive agent based on the context and decision type
        prompt = self._generate_decision_prompt(context, decision_type)
        
        # Create a dedicated executive agent for this decision
        executive_config = self.executive_agent_config.copy(deep=True)
        executive_agent = Agent(executive_config)
        
        # Register the agent with the scheduler
        agent_id = self.scheduler.register_agent(executive_agent)
        
        try:
            # Create system and user messages
            system_message = Message(
                role="system",
                content=executive_config.system_prompt
            )
            
            user_message = Message(
                role="user",
                content=prompt
            )
            
            # Process the decision with the agent
            messages = [system_message, user_message]
            response = await executive_agent.run(messages)
            
            # Check for tool calls and handle them if present
            if response.get("tool_calls"):
                logger.info(f"Executive agent requested tool calls for decision-making")
                response, messages = await executive_agent.handle_tool_calls(response, messages)
            
            # Parse the decision from the response
            decision_result = self._parse_decision_from_response(response.get("content", ""), context)
            
            return decision_result
            
        finally:
            # Unregister the agent when done
            self.scheduler.unregister_agent(agent_id)
    
    def _generate_decision_prompt(self, context: DecisionContext, decision_type: str) -> str:
        """Generate a prompt for the executive agent based on the context and decision type."""
        
        # Base prompt structure
        prompt = f"""# Decision Request: {decision_type}

## Context
Workflow ID: {context.workflow_id}
"""
        
        if context.task_id:
            prompt += f"Task ID: {context.task_id}\n"
            
        if context.user_id:
            prompt += f"User ID: {context.user_id}\n"
            
        # Format input data
        prompt += "\n## Input Data\n"
        prompt += json.dumps(context.input_data, indent=2)
        
        # Format constraints if any
        if context.constraints:
            prompt += "\n\n## Constraints\n"
            prompt += json.dumps(context.constraints, indent=2)
        
        # Format history if any
        if context.history:
            prompt += "\n\n## Decision History\n"
            for i, past_decision in enumerate(context.history):
                prompt += f"\n### Decision {i+1}\n"
                prompt += json.dumps(past_decision, indent=2)
        
        # Add specific instructions based on decision type
        prompt += f"\n\n## Decision Task\n"
        
        if decision_type == "workflow_planning":
            prompt += """Please create a workflow plan by:
1. Analyzing the input data and requirements
2. Breaking down the workflow into logical steps
3. Determining the appropriate agent types for each step
4. Identifying dependencies between steps
5. Estimating priority and complexity for each step
6. Proposing a sequence of actions to execute the workflow

Structure your decision as a workflow plan with specific steps, agent assignments, and dependencies.
"""
        elif decision_type == "resource_allocation":
            prompt += """Please make a resource allocation decision by:
1. Analyzing the current resource requirements and availability
2. Determining the optimal distribution of resources
3. Prioritizing competing demands based on business impact
4. Considering future resource needs and potential bottlenecks
5. Balancing efficiency and effectiveness
6. Proposing specific resource assignments

Structure your decision with clear resource allocations, justifications, and any necessary tradeoffs.
"""
        elif decision_type == "escalation_handling":
            prompt += """Please make an escalation handling decision by:
1. Assessing the severity and impact of the situation
2. Identifying the root cause of the escalation
3. Determining the appropriate response level
4. Assigning responsibility for addressing the issue
5. Establishing a timeline for resolution
6. Recommending preventive measures for the future

Structure your decision with a clear escalation response plan, assignments, and timeline.
"""
        elif decision_type == "exception_resolution":
            prompt += """Please resolve the exception by:
1. Analyzing the error or exception details
2. Identifying the root cause
3. Evaluating potential resolution approaches
4. Selecting the optimal resolution strategy
5. Determining any required compensating actions
6. Proposing steps to prevent similar exceptions

Structure your decision with a clear resolution approach, necessary actions, and preventive measures.
"""
        else:
            # Generic decision-making instructions for other types
            prompt += f"""Please make a decision regarding {decision_type} by:
1. Analyzing the context and input data thoroughly
2. Identifying key factors that influence this decision
3. Evaluating multiple alternative approaches
4. Considering constraints and requirements
5. Selecting the optimal course of action
6. Proposing specific implementation steps

Structure your decision clearly with reasoning, chosen approach, and concrete actions.
"""
        
        # Final output instructions
        prompt += """
## Output Format
Structure your response as follows:

**Decision:** [Your specific decision in 1-2 sentences]

**Confidence:** [A number between 0-1 representing your confidence in this decision]

**Reasoning:** [Detailed explanation of your thought process and justification]

**Alternatives Considered:** [List of alternative decisions you considered but rejected]

**Actions:** [Numbered list of specific actions to implement this decision]
"""
        
        return prompt
    
    def _parse_decision_from_response(self, response_text: str, context: DecisionContext) -> DecisionResult:
        """Parse a structured decision result from the agent's response."""
        
        # Generate a unique decision ID
        decision_id = f"decision_{int(time.time())}_{context.workflow_id}"
        
        # Default values
        decision = ""
        confidence = 0.5
        reasoning = ""
        alternatives = []
        actions = []
        
        # Extract decision
        decision_match = re.search(r"(?:^|\n)\s*\*\*Decision:\*\*\s*(.*?)(?:\n\s*\*\*|$)", response_text, re.DOTALL)
        if decision_match:
            decision = decision_match.group(1).strip()
            
        # Extract confidence
        confidence_match = re.search(r"(?:^|\n)\s*\*\*Confidence:\*\*\s*(0\.\d+|1\.0|1|0)", response_text)
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                # Ensure confidence is between 0 and 1
                confidence = max(0, min(1, confidence))
            except ValueError:
                pass
                
        # Extract reasoning
        reasoning_match = re.search(r"(?:^|\n)\s*\*\*Reasoning:\*\*\s*(.*?)(?:\n\s*\*\*|$)", response_text, re.DOTALL)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
            
        # Extract alternatives
        alternatives_match = re.search(r"(?:^|\n)\s*\*\*Alternatives Considered:\*\*\s*(.*?)(?:\n\s*\*\*|$)", response_text, re.DOTALL)
        if alternatives_match:
            alternatives_text = alternatives_match.group(1).strip()
            # Parse alternatives as list items
            alt_items = re.findall(r"(?:^|\n)\s*-\s*(.*?)(?:\n|$)", alternatives_text, re.DOTALL)
            alternatives = [{"option": alt.strip()} for alt in alt_items if alt.strip()]
            
        # Extract actions
        actions_match = re.search(r"(?:^|\n)\s*\*\*Actions:\*\*\s*(.*?)(?:\n\s*\*\*|$)", response_text, re.DOTALL)
        if actions_match:
            actions_text = actions_match.group(1).strip()
            # Parse actions as numbered list items
            action_items = re.findall(r"(?:^|\n)\s*\d+\.\s*(.*?)(?:\n|$)", actions_text, re.DOTALL)
            actions = [{"description": action.strip()} for action in action_items if action.strip()]
        
        # Create and return the decision result
        return DecisionResult(
            decision_id=decision_id,
            workflow_id=context.workflow_id,
            task_id=context.task_id,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            actions=actions,
            metadata={
                "timestamp": time.time(),
                "decision_type": context.metadata.get("decision_type", "general")
            }
        )
    
    async def execute_decision(self, decision: DecisionResult) -> Dict[str, Any]:
        """Execute a decision by converting its actions into tasks."""
        
        task_ids = []
        
        for i, action in enumerate(decision.actions):
            # Create a task for each action
            task = Task(
                title=f"Action {i+1} from decision {decision.decision_id}",
                description=action["description"],
                priority=TaskPriority.HIGH if decision.confidence > 0.8 else TaskPriority.MEDIUM,
                input_data={
                    "decision_id": decision.decision_id,
                    "workflow_id": decision.workflow_id,
                    "action_index": i,
                    "action_description": action["description"],
                    "context": decision.metadata
                }
            )
            
            # Submit the task to the scheduler
            task_id = await self.scheduler.submit_task(task)
            task_ids.append(task_id)
            logger.info(f"Created task {task_id} for action {i+1} from decision {decision.decision_id}")
        
        return {
            "decision_id": decision.decision_id,
            "task_ids": task_ids,
            "status": "scheduled" if task_ids else "no_actions"
        }
    
    async def reconsider_decision(
        self, 
        original_decision: DecisionResult, 
        feedback: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> DecisionResult:
        """Reconsider a decision based on feedback."""
        
        # Recreate the original context
        context = DecisionContext(
            workflow_id=original_decision.workflow_id,
            task_id=original_decision.task_id,
            input_data=additional_context or {},
            history=[original_decision.dict()],
            metadata={
                "reconsideration": True,
                "original_decision_id": original_decision.decision_id,
                "feedback": feedback
            }
        )
        
        # Generate a special prompt for reconsideration
        decision_type = f"reconsideration_of_{original_decision.metadata.get('decision_type', 'decision')}"
        
        # Make the new decision
        new_decision = await self.make_decision(context, decision_type)
        
        # Link the new decision to the original
        new_decision.metadata["reconsideration_of"] = original_decision.decision_id
        new_decision.metadata["feedback"] = feedback
        
        return new_decision
    
    async def analyze_data_tool(self, data: Dict[str, Any], analysis_type: Optional[str] = None) -> Dict[str, Any]:
        """Tool for analyzing data."""
        
        # Determine the appropriate agent for analysis
        agent_type = AgentType.MANAGER
        
        # For complex or large data, use the executive agent
        if len(json.dumps(data)) > 1000 or analysis_type in ["complex", "strategic"]:
            agent_type = AgentType.EXECUTIVE
        
        # Create a task for the analysis
        task = Task(
            title=f"Data analysis: {analysis_type or 'general'}",
            description=f"Analyze the provided data to extract insights and patterns. Analysis type: {analysis_type or 'general'}",
            priority=TaskPriority.MEDIUM,
            required_agent_type=agent_type,
            input_data={
                "data": data,
                "analysis_type": analysis_type
            }
        )
        
        # Create a future to wait for the result
        result_future = asyncio.Future()
        
        # Callback to resolve the future when the task completes
        def on_task_complete(completed_task: Task):
            if completed_task.status == TaskStatus.COMPLETED:
                result_future.set_result(completed_task.output_data)
            else:
                result_future.set_exception(Exception(f"Task failed with status {completed_task.status}"))
        
        # Submit the task
        task_id = await self.scheduler.submit_task(task, on_task_complete)
        
        # Wait for the result
        try:
            result = await asyncio.wait_for(result_future, timeout=task.timeout_seconds)
            return result
        except asyncio.TimeoutError:
            await self.scheduler.cancel_task(task_id)
            raise TimeoutError(f"Data analysis timed out after {task.timeout_seconds} seconds")
    
    async def evaluate_alternatives_tool(
        self, 
        alternatives: List[Dict[str, Any]], 
        criteria: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Tool for evaluating alternative options against criteria."""
        
        # Create a task for the evaluation
        task = Task(
            title=f"Evaluate {len(alternatives)} alternatives against {len(criteria)} criteria",
            description=f"Evaluate multiple alternative options against a set of criteria to determine the best choice.",
            priority=TaskPriority.MEDIUM,
            required_agent_type=AgentType.MANAGER,
            input_data={
                "alternatives": alternatives,
                "criteria": criteria
            }
        )
        
        # Create a future to wait for the result
        result_future = asyncio.Future()
        
        # Callback to resolve the future when the task completes
        def on_task_complete(completed_task: Task):
            if completed_task.status == TaskStatus.COMPLETED:
                result_future.set_result(completed_task.output_data)
            else:
                result_future.set_exception(Exception(f"Task failed with status {completed_task.status}"))
        
        # Submit the task
        task_id = await self.scheduler.submit_task(task, on_task_complete)
        
        # Wait for the result
        try:
            result = await asyncio.wait_for(result_future, timeout=task.timeout_seconds)
            return result
        except asyncio.TimeoutError:
            await self.scheduler.cancel_task(task_id)
            raise TimeoutError(f"Alternatives evaluation timed out after {task.timeout_seconds} seconds")
    
    async def check_constraints_tool(
        self, 
        decision: Dict[str, Any], 
        constraints: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Tool for checking if a decision satisfies constraints."""
        
        # Create a task for the constraint checking
        task = Task(
            title=f"Check decision against {len(constraints)} constraints",
            description=f"Check if a potential decision satisfies a set of constraints.",
            priority=TaskPriority.HIGH,  # Higher priority for constraint checking
            required_agent_type=AgentType.TASK,  # Simpler task for a task agent
            input_data={
                "decision": decision,
                "constraints": constraints
            }
        )
        
        # Create a future to wait for the result
        result_future = asyncio.Future()
        
        # Callback to resolve the future when the task completes
        def on_task_complete(completed_task: Task):
            if completed_task.status == TaskStatus.COMPLETED:
                result_future.set_result(completed_task.output_data)
            else:
                result_future.set_exception(Exception(f"Task failed with status {completed_task.status}"))
        
        # Submit the task
        task_id = await self.scheduler.submit_task(task, on_task_complete)
        
        # Wait for the result
        try:
            result = await asyncio.wait_for(result_future, timeout=task.timeout_seconds)
            return result
        except asyncio.TimeoutError:
            await self.scheduler.cancel_task(task_id)
            raise TimeoutError(f"Constraint checking timed out after {task.timeout_seconds} seconds")
    
    def bind_tool_handlers(self):
        """Bind tool handlers to the executive agent config."""
        for tool in self.executive_agent_config.tools:
            if tool.name == "analyze_data":
                tool.handler = self.analyze_data_tool
            elif tool.name == "evaluate_alternatives":
                tool.handler = self.evaluate_alternatives_tool
            elif tool.name == "check_constraints":
                tool.handler = self.check_constraints_tool 