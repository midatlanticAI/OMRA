"""
Authentication API endpoints.
"""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user,
)
from backend.models.user import User, UserCreate, UserInDB
from backend.db.session import get_db
from backend.core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/login")
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    OAuth2 compatible token login.
    """
    # In a real application, you would get the user from the database
    # Here we're using a mock user for demonstration
    if form_data.username != "admin@example.com" or form_data.password != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mock user for demonstration
    user = {
        "id": 1,
        "email": "admin@example.com",
        "full_name": "Admin User",
        "is_active": True,
        "is_superuser": True,
    }
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=user["id"], expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user,
    }

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Register a new user.
    """
    # In a real application, you would check if the user already exists
    # and insert the new user into the database
    # Here we're returning a mock user for demonstration
    
    # Check if user with same email exists
    # existing_user = await get_user_by_email(db, email=user_in.email)
    # if existing_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Email already registered",
    #     )
    
    # Create the user
    # user = User(
    #     email=user_in.email,
    #     hashed_password=get_password_hash(user_in.password),
    #     full_name=user_in.full_name,
    #     is_active=True,
    #     is_superuser=False,
    # )
    # db.add(user)
    # await db.commit()
    # await db.refresh(user)
    
    # Mock user for demonstration
    user = User(
        id=1,
        email=user_in.email,
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False,
    )
    
    return user

@router.post("/test-token", response_model=User)
async def test_token(current_user: User = Depends(get_current_user)) -> Any:
    """
    Test access token.
    """
    return current_user 