"""
Task agent responsible for communication with customers
Generates emails, SMS, and other customer communications
"""
from typing import Dict, Any

from utils.logging import log_agent_activity
from .base_task_agent import TaskAgent

class CommunicationAgent(TaskAgent):
    """
    Task agent responsible for communication with customers
    Generates emails, SMS, and other customer communications
    """
    
    def __init__(self, llm_connector, config):
        """
        Initialize the communication task agent
        
        Args:
            llm_connector: LLM connector for API calls
            config: Configuration for the agent
        """
        super().__init__(llm_connector, config)
        self.agent_name = "communication"
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a communication task
        
        Args:
            task: The task to execute
            
        Returns:
            Results of the task execution
        """
        log_agent_activity("task", self.agent_name, "execute_task", {"task_type": task.get("type", "unknown")})
        
        task_type = task.get("type", "")
        
        if task_type == "generate_response":
            return await self._generate_response(task)
        elif task_type == "create_email":
            return await self._create_email(task)
        elif task_type == "create_sms":
            return await self._create_sms(task)
        else:
            # Default to base implementation for unknown task types
            return await super().execute_task(task)
    
    async def _generate_response(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a response to a customer inquiry
        
        Args:
            task: Task details
            
        Returns:
            Generated response
        """
        parameters = task.get("parameters", {})
        context = task.get("context", {})
        
        inquiry_text = parameters.get("inquiry_text", "")
        customer_history = context.get("customer_history", {})
        appliance_info = context.get("appliance_info", {})
        
        # Prepare prompt for the LLM
        prompt = f"""
        Generate a response to the following customer inquiry:
        
        CUSTOMER INQUIRY: {inquiry_text}
        
        CUSTOMER HISTORY:
        {self._format_customer_history(customer_history)}
        
        APPLIANCE INFORMATION:
        {self._format_appliance_info(appliance_info)}
        
        Your task is to:
        1. Generate a helpful, professional response to the customer
        2. Address their specific concerns
        3. Provide relevant information based on their history and appliance details
        4. Use a friendly but professional tone
        5. Include any necessary next steps or recommendations
        
        Also analyze the sentiment of the inquiry and identify key topics.
        
        Return your response in JSON format with these fields:
        - response_text: The full text response to send to the customer
        - sentiment: The sentiment of the customer's inquiry (positive, neutral, negative)
        - topics: A list of key topics mentioned in the inquiry
        - recommended_actions: Any recommended follow-up actions
        """
        
        response = await self.llm_connector.generate(
            model=self.model,
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=1000,
            temperature=0.3
        )
        
        # Parse the result from the response
        try:
            result = self._extract_json(response)
            return result
        except Exception as e:
            raise ValueError(f"Failed to parse response generation result: {str(e)}")
    
    async def _create_email(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an email for a customer
        
        Args:
            task: Task details
            
        Returns:
            Generated email
        """
        parameters = task.get("parameters", {})
        context = task.get("context", {})
        
        email_type = parameters.get("email_type", "general")
        customer_info = context.get("customer_info", {})
        service_info = context.get("service_info", {})
        
        # Prepare prompt for the LLM
        prompt = f"""
        Create an email for a customer based on the following information:
        
        EMAIL TYPE: {email_type}
        
        CUSTOMER INFORMATION:
        Name: {customer_info.get('first_name', '')} {customer_info.get('last_name', '')}
        Email: {customer_info.get('email', '')}
        
        SERVICE INFORMATION:
        {self._format_service_info(service_info)}
        
        Your task is to:
        1. Generate a complete email with subject line and body
        2. Use appropriate formatting and structure
        3. Include all relevant details based on the email type
        4. Use a professional tone appropriate for an appliance repair business
        
        Return your response in JSON format with these fields:
        - subject: The email subject line
        - body: The complete email body
        - attachments: Any recommended attachments (list)
        """
        
        response = await self.llm_connector.generate(
            model=self.model,
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=1000,
            temperature=0.3
        )
        
        # Parse the result from the response
        try:
            result = self._extract_json(response)
            return result
        except Exception as e:
            raise ValueError(f"Failed to parse email creation result: {str(e)}")
    
    async def _create_sms(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an SMS for a customer
        
        Args:
            task: Task details
            
        Returns:
            Generated SMS
        """
        parameters = task.get("parameters", {})
        context = task.get("context", {})
        
        sms_type = parameters.get("sms_type", "appointment_reminder")
        customer_info = context.get("customer_info", {})
        appointment_info = context.get("appointment_info", {})
        
        # Prepare prompt for the LLM
        prompt = f"""
        Create an SMS message for a customer based on the following information:
        
        SMS TYPE: {sms_type}
        
        CUSTOMER INFORMATION:
        Name: {customer_info.get('first_name', '')} {customer_info.get('last_name', '')}
        Phone: {customer_info.get('phone', '')}
        
        APPOINTMENT INFORMATION:
        Date: {appointment_info.get('date', '')}
        Time: {appointment_info.get('time', '')}
        Technician: {appointment_info.get('technician_name', '')}
        Service Type: {appointment_info.get('service_type', '')}
        
        Your task is to:
        1. Generate a concise SMS message (160 characters or less if possible)
        2. Include all critical information
        3. Use a professional but friendly tone
        4. Include any necessary call-to-action
        
        Return your response in JSON format with these fields:
        - message: The SMS message text
        - character_count: The number of characters in the message
        """
        
        response = await self.llm_connector.generate(
            model=self.model,
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=500,
            temperature=0.2
        )
        
        # Parse the result from the response
        try:
            result = self._extract_json(response)
            return result
        except Exception as e:
            raise ValueError(f"Failed to parse SMS creation result: {str(e)}")
    
    def _format_customer_history(self, customer_history: Dict[str, Any]) -> str:
        """Format customer history for inclusion in prompts"""
        if not customer_history:
            return "No customer history available."
            
        history_str = f"Customer ID: {customer_history.get('id', 'Unknown')}\n"
        history_str += f"Name: {customer_history.get('first_name', '')} {customer_history.get('last_name', '')}\n"
        history_str += f"Email: {customer_history.get('email', 'Unknown')}\n"
        history_str += f"Phone: {customer_history.get('phone', 'Unknown')}\n\n"
        
        # Add service history if available
        service_history = customer_history.get('service_history', [])
        if service_history:
            history_str += "Service History:\n"
            for service in service_history:
                history_str += f"- {service.get('date', 'Unknown')}: {service.get('type', 'Unknown')} - {service.get('status', 'Unknown')}\n"
        else:
            history_str += "No previous service history.\n"
            
        return history_str
    
    def _format_appliance_info(self, appliance_info: Dict[str, Any]) -> str:
        """Format appliance information for inclusion in prompts"""
        if not appliance_info:
            return "No appliance information available."
            
        info_str = f"Type: {appliance_info.get('type', 'Unknown')}\n"
        info_str += f"Brand: {appliance_info.get('brand', 'Unknown')}\n"
        info_str += f"Model: {appliance_info.get('model', 'Unknown')}\n"
        info_str += f"Serial Number: {appliance_info.get('serial_number', 'Unknown')}\n"
        info_str += f"Purchase Date: {appliance_info.get('purchase_date', 'Unknown')}\n"
        info_str += f"Warranty Status: {appliance_info.get('warranty_status', 'Unknown')}\n"
        
        return info_str
    
    def _format_service_info(self, service_info: Dict[str, Any]) -> str:
        """Format service information for inclusion in prompts"""
        if not service_info:
            return "No service information available."
            
        info_str = f"Service ID: {service_info.get('id', 'Unknown')}\n"
        info_str += f"Type: {service_info.get('type', 'Unknown')}\n"
        info_str += f"Status: {service_info.get('status', 'Unknown')}\n"
        info_str += f"Scheduled Date: {service_info.get('scheduled_date', 'Unknown')}\n"
        info_str += f"Scheduled Time: {service_info.get('scheduled_time', 'Unknown')}\n"
        info_str += f"Technician: {service_info.get('technician_name', 'Unknown')}\n"
        
        # Add parts if available
        parts = service_info.get('parts', [])
        if parts:
            info_str += "Parts:\n"
            for part in parts:
                info_str += f"- {part.get('name', 'Unknown')}: ${part.get('price', '0.00')}\n"
                
        # Add total cost if available
        if 'total_cost' in service_info:
            info_str += f"Total Cost: ${service_info.get('total_cost', '0.00')}\n"
            
        return info_str 