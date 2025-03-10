import logging
import json
import time
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log', mode='a')
    ]
)

logger = logging.getLogger('omra')

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Generate request ID
        request_id = f"{int(time.time())}-{id(request)}"
        
        # Log request details
        await self._log_request(request, request_id)
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Log response details
            process_time = time.time() - start_time
            self._log_response(response, process_time, request_id)
            
            return response
        except Exception as e:
            # Log exceptions
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request_id} - {str(e)}",
                extra={
                    'request_id': request_id,
                    'process_time': process_time,
                    'error': str(e)
                }
            )
            raise
    
    async def _log_request(self, request: Request, request_id: str):
        body = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = await request.json()
                    # Redact sensitive information
                    if isinstance(body, dict) and 'password' in body:
                        body['password'] = '********'
            except:
                body = 'Could not parse request body'
        
        logger.info(
            f"Request: {request_id} - {request.method} {request.url.path}",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'query_params': dict(request.query_params),
                'client_ip': request.client.host,
                'body': body
            }
        )
    
    def _log_response(self, response: Response, process_time: float, request_id: str):
        logger.info(
            f"Response: {request_id} - Status: {response.status_code} - Time: {process_time:.4f}s",
            extra={
                'request_id': request_id,
                'status_code': response.status_code,
                'process_time': process_time
            }
        )

def log_agent_activity(agent_type: str, agent_name: str, action: str, details: dict = None):
    """
    Log agent activity for monitoring and debugging.
    
    Args:
        agent_type: Type of agent (executive, manager, task)
        agent_name: Name of the agent
        action: Action being performed
        details: Additional details about the action
    """
    logger.info(
        f"Agent Activity: {agent_type}:{agent_name} - {action}",
        extra={
            'timestamp': datetime.now().isoformat(),
            'agent_type': agent_type,
            'agent_name': agent_name,
            'action': action,
            'details': details or {}
        }
    ) 