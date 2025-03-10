"""
Audit logging for sensitive operations.

This module provides functionality for logging security-relevant operations
within the application, maintaining a separate audit trail that can be used
for compliance and security investigations.
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union

from fastapi import Request
from pydantic import BaseModel

from backend.core.config import settings

# Set up audit logger
audit_logger = logging.getLogger("omra.audit")

class AuditEvent(BaseModel):
    """Model representing an audit event"""
    timestamp: str 
    event_type: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: str
    status: str  # success, failure
    details: Dict[str, Any] = {}
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

def setup_audit_logging():
    """
    Configure the audit logging system.
    Sets up file handler with appropriate formatting.
    """
    if not settings.AUDIT_LOG_ENABLED:
        return
    
    # Create logs directory if it doesn't exist
    logs_dir = Path(os.path.dirname(settings.AUDIT_LOG_FILE))
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
    
    audit_logger.setLevel(logging.INFO)
    
    # Create file handler for audit logs
    audit_file_handler = logging.FileHandler(settings.AUDIT_LOG_FILE)
    audit_file_handler.setLevel(logging.INFO)
    
    # Create a custom formatter that outputs JSON
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            return record.getMessage()
    
    audit_file_handler.setFormatter(JsonFormatter())
    
    # Add handler to logger
    audit_logger.addHandler(audit_file_handler)
    
    # Ensure audit logs aren't propagated to the root logger
    audit_logger.propagate = False

def get_client_ip(request: Request) -> str:
    """
    Extract the client IP address from the request.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # Get the client's IP from the X-Forwarded-For header
        return x_forwarded_for.split(",")[0].strip()
    else:
        # Get the client's IP from the request
        return request.client.host if request.client else "unknown"

def log_audit_event(
    event_type: str,
    action: str,
    status: str,
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log an audit event.
    
    Args:
        event_type: Type of the event (auth, data_access, admin, etc.)
        action: The action being performed (login, logout, create, update, delete, etc.)
        status: Success or failure
        user_id: ID of the user performing the action
        username: Username of the user performing the action
        ip_address: IP address of the client
        resource_type: Type of resource being accessed
        resource_id: ID of the resource being accessed
        details: Additional details about the event
    """
    if not settings.AUDIT_LOG_ENABLED:
        return
    
    event = AuditEvent(
        timestamp=datetime.utcnow().isoformat(),
        event_type=event_type,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        status=status,
        details=details or {}
    )
    
    audit_logger.info(json.dumps(event.dict()))

def log_auth_event(
    action: str, 
    status: str, 
    username: Optional[str] = None, 
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log an authentication-related audit event.
    
    Args:
        action: The auth action (login, logout, password_change, etc.)
        status: Success or failure
        username: Username of the user
        user_id: ID of the user
        ip_address: IP address of the client
        details: Additional details about the event
    """
    log_audit_event(
        event_type="auth",
        action=action,
        status=status,
        username=username,
        user_id=user_id,
        ip_address=ip_address,
        details=details
    )

def log_data_access_event(
    action: str,
    status: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log a data access audit event.
    
    Args:
        action: The data action (read, create, update, delete, etc.)
        status: Success or failure
        resource_type: Type of resource being accessed
        resource_id: ID of the resource being accessed
        user_id: ID of the user performing the action
        username: Username of the user performing the action
        ip_address: IP address of the client
        details: Additional details about the event
    """
    log_audit_event(
        event_type="data_access",
        action=action,
        status=status,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        details=details
    )

def log_admin_event(
    action: str,
    status: str,
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log an administrative action audit event.
    
    Args:
        action: The admin action (user_create, user_delete, role_change, etc.)
        status: Success or failure
        user_id: ID of the admin performing the action
        username: Username of the admin performing the action
        ip_address: IP address of the client
        resource_type: Type of resource being administered
        resource_id: ID of the resource being administered
        details: Additional details about the event
    """
    log_audit_event(
        event_type="admin",
        action=action,
        status=status,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details
    ) 