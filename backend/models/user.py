"""
User models for SQL database.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import Boolean, Column, String, DateTime, Integer
from sqlalchemy.orm import relationship

from backend.db.base_class import Base

class User(Base):
    """User model for authentication and user management."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # service_requests = relationship("ServiceRequest", back_populates="created_by")
    # customers = relationship("Customer", back_populates="created_by")

# Pydantic models for API schema validation

from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """Base user schema."""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """User creation schema."""
    email: EmailStr
    password: str

class UserUpdate(UserBase):
    """User update schema."""
    password: Optional[str] = None

class UserInDBBase(UserBase):
    """User schema with ID."""
    id: Optional[int] = None
    
    class Config:
        orm_mode = True

class User(UserInDBBase):
    """User schema for API responses."""
    pass

class UserInDB(UserInDBBase):
    """User schema with hashed password."""
    hashed_password: str 