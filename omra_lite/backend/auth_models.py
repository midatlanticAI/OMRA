"""
Simplified auth models for OMRA Lite authentication system.
These models are used only for authentication and don't use PyObjectId.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    is_admin: bool = False

class User(UserBase):
    id: Optional[str] = Field(alias="_id", default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

class UserInDB(User):
    hashed_password: str 