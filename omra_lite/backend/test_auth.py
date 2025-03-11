"""
Test script to verify MongoDB connection and user authentication.
This bypasses the FastAPI framework to test the underlying functionality.
"""
import asyncio
from datetime import datetime
import json
from bson.objectid import ObjectId

from db import get_database
from auth import get_user, authenticate_user, verify_password

# Custom JSON encoder to handle ObjectId
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def test_database_connection():
    """Test connection to MongoDB."""
    try:
        db = await get_database()
        print("Successfully connected to MongoDB")
        return True
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return False

async def test_get_user(username="admin"):
    """Test getting a user from the database."""
    try:
        db = await get_database()
        user_dict = await db.users.find_one({"username": username})
        
        if not user_dict:
            print(f"User '{username}' not found in database")
            return None
        
        print(f"Raw user from database:")
        print(json.dumps(user_dict, indent=2, cls=CustomJSONEncoder))
        
        # Try converting to a UserInDB model
        try:
            from auth_models import UserInDB
            # Convert ObjectId to string
            if "_id" in user_dict and isinstance(user_dict["_id"], ObjectId):
                user_dict["_id"] = str(user_dict["_id"])
            
            user = UserInDB(**user_dict)
            print(f"\nSuccessfully converted to UserInDB model")
            print(f"User ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Is Admin: {user.is_admin}")
            return user
        except Exception as e:
            print(f"\nFailed to convert to UserInDB model: {e}")
            return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

async def test_authenticate_user(username="admin", password="admin1"):
    """Test user authentication."""
    try:
        user = await authenticate_user(username, password)
        if user:
            print(f"Authentication successful for user '{username}'")
            return True
        else:
            print(f"Authentication failed for user '{username}'")
            return False
    except Exception as e:
        print(f"Error during authentication: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_verify_password(plain_password="admin1", hashed_password=None):
    """Test password verification."""
    if not hashed_password:
        db = await get_database()
        user = await db.users.find_one({"username": "admin"})
        if not user:
            print("Admin user not found")
            return False
        hashed_password = user.get("hashed_password")
    
    try:
        is_valid = verify_password(plain_password, hashed_password)
        print(f"Password verification result: {is_valid}")
        return is_valid
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

async def main():
    """Run all tests."""
    print("=== Testing MongoDB Connection ===")
    connected = await test_database_connection()
    if not connected:
        print("Failed to connect to MongoDB. Aborting further tests.")
        return
    
    print("\n=== Testing User Retrieval ===")
    user = await test_get_user()
    
    if user:
        print("\n=== Testing Password Verification ===")
        await test_verify_password()
    
    print("\n=== Testing User Authentication ===")
    await test_authenticate_user()

if __name__ == "__main__":
    asyncio.run(main()) 