"""
Debug script to test authentication.
"""
import asyncio
import sys
import traceback
from auth import authenticate_user, verify_password, get_user
from models import UserInDB

async def debug_auth():
    """Debug authentication issues."""
    try:
        username = "admin"
        password = "admin1"
        
        print(f"Trying to authenticate user: {username}")
        
        # Get user
        print("Fetching user from database...")
        user = await get_user(username)
        
        if not user:
            print(f"Error: User '{username}' not found in database.")
            return
        
        print(f"User found: {user.username}, Email: {user.email}, Admin: {user.is_admin}")
        print(f"Stored hashed password: {user.hashed_password}")
        
        # Test password verification
        print(f"Testing password verification...")
        password_match = verify_password(password, user.hashed_password)
        print(f"Password match: {password_match}")
        
        # Test full authentication
        print(f"Testing full authentication...")
        authenticated_user = await authenticate_user(username, password)
        
        if authenticated_user:
            print(f"Authentication successful!")
            print(f"Authenticated user: {authenticated_user}")
        else:
            print(f"Authentication failed!")
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_auth()) 