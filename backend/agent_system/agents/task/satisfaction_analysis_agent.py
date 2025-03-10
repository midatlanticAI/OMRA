"""
Task agent responsible for analyzing customer satisfaction and feedback
"""
from typing import Dict, Any

from utils.logging import log_agent_activity
from .base_task_agent import TaskAgent

class SatisfactionAnalysisAgent(TaskAgent):
    """
    Task agent responsible for analyzing customer satisfaction and feedback
    """
    
    def __init__(self, llm_connector, config):
        """
        Initialize the satisfaction analysis task agent
        
        Args:
            llm_connector: LLM connector for API calls
            config: Configuration for the agent
        """
        super().__init__(llm_connector, config)
        self.agent_name = "satisfaction_analysis"
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a satisfaction analysis task
        
        Args:
            task: The task to execute
            
        Returns:
            Results of the task execution
        """
        log_agent_activity("task", self.agent_name, "execute_task", {"task_type": task.get("type", "unknown")})
        
        task_type = task.get("type", "")
        
        if task_type == "analyze_feedback":
            return await self._analyze_feedback(task)
        elif task_type == "generate_satisfaction_report":
            return await self._generate_satisfaction_report(task)
        else:
            # Default to base implementation for unknown task types
            return await super().execute_task(task)
    
    async def _analyze_feedback(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze customer feedback
        
        Args:
            task: Task details
            
        Returns:
            Analysis of customer feedback
        """
        parameters = task.get("parameters", {})
        context = task.get("context", {})
        
        feedback_text = parameters.get("feedback_text", "")
        
        # Prepare prompt for the LLM
        prompt = f"""
        Analyze the following customer feedback:
        
        FEEDBACK: {feedback_text}
        
        Your task is to:
        1. Determine the overall sentiment (positive, neutral, negative)
        2. Identify key topics mentioned
        3. Extract specific issues or concerns
        4. Identify any compliments or positive aspects
        5. Suggest potential improvements based on the feedback
        
        Return your analysis in JSON format with these fields:
        - sentiment: The overall sentiment (positive, neutral, negative)
        - sentiment_score: A score from -1.0 (very negative) to 1.0 (very positive)
        - topics: A list of key topics mentioned
        - issues: A list of specific issues or concerns
        - compliments: A list of compliments or positive aspects
        - improvement_suggestions: A list of potential improvements
        """
        
        response = await self.llm_connector.generate(
            model=self.model,
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=1000,
            temperature=0.1
        )
        
        # Parse the result from the response
        try:
            result = self._extract_json(response)
            return result
        except Exception as e:
            raise ValueError(f"Failed to parse feedback analysis result: {str(e)}")
    
    async def _generate_satisfaction_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a customer satisfaction report
        
        Args:
            task: Task details
            
        Returns:
            Customer satisfaction report
        """
        parameters = task.get("parameters", {})
        context = task.get("context", {})
        
        time_period = parameters.get("time_period", "last_month")
        
        # In a real implementation, this would analyze actual customer data
        # For now, return mock report
        return {
            "time_period": time_period,
            "overall_satisfaction_score": 4.2,
            "total_feedback_count": 87,
            "sentiment_distribution": {
                "positive": 65,
                "neutral": 15,
                "negative": 7
            },
            "top_positive_topics": [
                "technician professionalism",
                "timely service",
                "effective repairs"
            ],
            "top_negative_topics": [
                "scheduling difficulties",
                "parts availability",
                "pricing concerns"
            ],
            "trend": "improving",
            "recommendations": [
                "Improve parts inventory management",
                "Review pricing communication process",
                "Continue technician training program"
            ]
        } 