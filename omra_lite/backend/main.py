"""
OMRA Lite - Main Backend Application

This is the entry point for the OMRA Lite backend, providing:
- FastAPI REST API
- MongoDB integration
- Authentication system
- Agent framework
"""
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union

import uvicorn
from bson import ObjectId
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("omra_lite")

# Import modules
from models import User, UserInDB, TokenData
from agent_system import AgentManager
from db import get_database, close_mongo_connection
from api.endpoints import api_router
from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_user,
    get_password_hash,
    verify_password,
    ALGORITHM,
    SECRET_KEY,
    oauth2_scheme,
    pwd_context
)

# Import from auth_models for token endpoint
from auth_models import Token

# Create FastAPI app
app = FastAPI(
    title="OMRA Lite",
    description="OpenManus Repair Automation Lite Version",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files - commented out until frontend build is available
# app.mount("/static", StaticFiles(directory="../frontend/build", html=True), name="static")

# Include API router
app.include_router(api_router, prefix="/api")

# Agent manager
agent_manager = AgentManager()

# Startup event - connect to database and create admin user if not exists
@app.on_event("startup")
async def startup_db_client():
    """Initialize the database connection and create admin user if not exists."""
    # Already connected by the get_database() import
    logger.info("Connected to MongoDB")
    
    # Create admin user if not exists
    db = await get_database()
    admin_user = await db.users.find_one({"username": "admin"})
    
    if not admin_user:
        hashed_password = pwd_context.hash("admin1")
        user = {
            "username": "admin",
            "email": "admin@example.com",
            "full_name": "Administrator",
            "hashed_password": hashed_password,
            "disabled": False,
            "is_admin": True,
            "created_at": datetime.utcnow(),
        }
        await db.users.insert_one(user)
        logger.info("Created admin user")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connections."""
    await close_mongo_connection()
    logger.info("Disconnected from MongoDB")

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Generate a JWT token for a user."""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=None)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Return the current user."""
    try:
        # Convert the user to a dictionary with all fields as simple types
        user_dict = {
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "disabled": current_user.disabled,
            "is_admin": current_user.is_admin,
            "_id": str(current_user.id) if current_user.id else None,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        }
        
        # Return as plain JSON
        return user_dict
    except Exception as e:
        logger.exception(f"Error in /users/me endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user data: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Check if the API is running."""
    return {"status": "ok", "version": "0.1.0"}

# Exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Run the application
def main():
    """Run the application."""
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main() 