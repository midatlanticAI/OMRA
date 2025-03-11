"""
Settings API Endpoints for OMRA Lite

These endpoints handle system settings like API keys.
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from models import User
from main import get_current_active_user
from db import get_database

logger = logging.getLogger("omra_lite.api.settings")

# Create router
settings_router = APIRouter(prefix="/settings", tags=["settings"])

class ApiKeySettings(BaseModel):
    """API key settings"""
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

@settings_router.get("/api-keys")
async def get_api_keys(current_user: User = Depends(get_current_active_user)):
    """
    Get API key settings.
    
    Note: For security, this endpoint only returns whether keys are set, not the actual keys.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access settings"
        )
    
    db = await get_database()
    settings = await db.settings.find_one({"type": "api_keys"})
    
    result = {
        "anthropic_api_key": bool(settings and settings.get("anthropic_api_key")),
        "openai_api_key": bool(settings and settings.get("openai_api_key")),
    }
    
    return result

@settings_router.post("/api-keys")
async def update_api_keys(
    settings: ApiKeySettings,
    current_user: User = Depends(get_current_active_user)
):
    """Update API key settings."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update settings"
        )
    
    db = await get_database()
    
    # Get current settings
    current_settings = await db.settings.find_one({"type": "api_keys"})
    
    # Prepare update data
    update_data = {}
    
    if settings.anthropic_api_key is not None:
        update_data["anthropic_api_key"] = settings.anthropic_api_key
    elif current_settings and "anthropic_api_key" in current_settings:
        # Keep existing value if not provided
        update_data["anthropic_api_key"] = current_settings["anthropic_api_key"]
    
    if settings.openai_api_key is not None:
        update_data["openai_api_key"] = settings.openai_api_key
    elif current_settings and "openai_api_key" in current_settings:
        # Keep existing value if not provided
        update_data["openai_api_key"] = current_settings["openai_api_key"]
    
    # Update or insert settings
    if current_settings:
        await db.settings.update_one(
            {"type": "api_keys"},
            {"$set": update_data}
        )
    else:
        await db.settings.insert_one({
            "type": "api_keys",
            **update_data
        })
    
    return {"message": "API keys updated successfully"} 