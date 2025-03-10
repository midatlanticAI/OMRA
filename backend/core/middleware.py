"""
Middleware for the OpenManus API.

This module provides middleware components for the FastAPI application, including:
- Audit logging middleware to track user actions
- Request ID middleware to assign unique IDs to requests for tracing
"""
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.audit import get_client_ip, log_auth_event, log_data_access_event

# Sensitive routes that should be audit logged
SENSITIVE_ROUTES = [
    "/api/auth/login",
    "/api/auth/logout",
    "/api/users",
    "/api/customers",
    "/api/service-requests",
    "/api/invoices",
    "/api/settings",
    "/api/integrations",
]

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to assign a unique ID to each request.
    
    This ID can be used for tracing requests through the system
    and correlating logs across services.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request and assign a request ID."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add the request ID to the response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to perform audit logging for sensitive operations.
    
    This middleware logs actions related to authentication, user management,
    and access to sensitive data.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request and log audit events."""
        path = request.url.path
        method = request.method
        
        # Check if this is a sensitive route that should be logged
        is_sensitive = any(path.startswith(route) for route in SENSITIVE_ROUTES)
        
        # Only perform detailed logging for sensitive routes
        if is_sensitive:
            start_time = time.time()
            
            # Get the client IP address
            ip_address = get_client_ip(request)
            
            # Try to get the current user information if available
            user_id = getattr(request.state, "user_id", None)
            username = getattr(request.state, "username", None)
            
            # Map HTTP method to audit action
            action_map = {
                "GET": "read",
                "POST": "create",
                "PUT": "update",
                "PATCH": "update",
                "DELETE": "delete"
            }
            action = action_map.get(method, method.lower())
            
            # Extract resource type from the path
            # Example: /api/customers/123 -> resource_type="customers"
            parts = path.strip("/").split("/")
            resource_type = parts[1] if len(parts) > 1 else None
            
            # Extract resource ID if present in the path
            # Example: /api/customers/123 -> resource_id="123"
            resource_id = parts[2] if len(parts) > 2 else None
            
            try:
                # Process the request
                response = await call_next(request)
                
                # Determine success based on status code
                success = response.status_code < 400
                status = "success" if success else "failure"
                
                # Log the event
                if path.startswith("/api/auth"):
                    # Authentication events
                    log_auth_event(
                        action=action,
                        status=status,
                        username=username,
                        user_id=user_id,
                        ip_address=ip_address,
                        details={
                            "path": path,
                            "status_code": response.status_code,
                            "duration_ms": round((time.time() - start_time) * 1000)
                        }
                    )
                else:
                    # Data access events
                    log_data_access_event(
                        action=action,
                        status=status,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        user_id=user_id,
                        username=username,
                        ip_address=ip_address,
                        details={
                            "path": path,
                            "method": method,
                            "status_code": response.status_code,
                            "duration_ms": round((time.time() - start_time) * 1000)
                        }
                    )
                
                return response
                
            except Exception as e:
                # Log the exception as a failure
                log_data_access_event(
                    action=action,
                    status="failure",
                    resource_type=resource_type,
                    resource_id=resource_id,
                    user_id=user_id,
                    username=username,
                    ip_address=ip_address,
                    details={
                        "path": path,
                        "method": method,
                        "error": str(e),
                        "duration_ms": round((time.time() - start_time) * 1000)
                    }
                )
                
                # Re-raise the exception for FastAPI to handle
                raise
        else:
            # For non-sensitive routes, just pass through
            return await call_next(request)

def setup_middleware(app: FastAPI):
    """
    Set up all middleware for the application.
    
    Args:
        app: The FastAPI application
    """
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(AuditLoggingMiddleware) 