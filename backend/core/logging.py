"""
Logging configuration for the OMRA system.
Includes setup for standard logging and specialized agent activity logging.
"""
import logging
import os
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from backend.core.config import settings

# Create logger for the application
logger = logging.getLogger("omra")

def setup_logging():
    """
    Configure the logging system for the application.
    Sets up console and file handlers with appropriate formatting.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    
    # Create file handler for standard logs
    file_handler = RotatingFileHandler(
        filename=os.path.join(logs_dir, "omra.log"),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)
    
    # Create file handler for JSON-formatted agent logs
    agent_file_handler = RotatingFileHandler(
        filename=os.path.join(logs_dir, "agent_activity.log"),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    agent_file_handler.setLevel(log_level)
    
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            if hasattr(record, 'agent_type'):
                log_record = {
                    'timestamp': record.asctime,
                    'level': record.levelname,
                    'agent_type': record.agent_type,
                    'agent_name': record.agent_name,
                    'action': record.action,
                    'details': record.details
                }
            else:
                log_record = {
                    'timestamp': record.asctime,
                    'level': record.levelname,
                    'message': record.getMessage()
                }
            return json.dumps(log_record)
    
    agent_file_handler.setFormatter(JsonFormatter())
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(agent_file_handler)
    
    logger.info("Logging system initialized")

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