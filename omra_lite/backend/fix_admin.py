"""
Script to fix the admin user in the database.
This will create or update the admin user with the default credentials.
"""
import asyncio
from datetime import datetime
from bson import ObjectId

from db import get_database
from auth import get_password_hash

async def fix_admin_user():
    """Create or update the admin user in the database."""
    try:
        db = await get_database()
        print("Connected to database")
        
        # Check if admin user exists
        admin_user = await db.users.find_one({"username": "admin"})
        
        if admin_user:
            print("Admin user exists:")
            print(f"  _id: {admin_user.get('_id')}")
            print(f"  username: {admin_user.get('username')}")
            print(f"  email: {admin_user.get('email')}")
            print(f"  hashed_password: {admin_user.get('hashed_password', '')[:20]}...")
            
            # Generate hashed password
            hashed_password = get_password_hash("admin1")
            print(f"Generated new password hash: {hashed_password[:20]}...")
            
            print("Updating admin user password...")
            result = await db.users.update_one(
                {"username": "admin"},
                {"$set": {
                    "hashed_password": hashed_password,
                    "updated_at": datetime.utcnow()
                }}
            )
            print(f"Update result: {result.modified_count} document(s) modified")
        else:
            print("Admin user does not exist. Creating new admin user.")
            
            # Generate hashed password
            hashed_password = get_password_hash("admin1")
            print(f"Generated password hash: {hashed_password[:20]}...")
            
            user = {
                "_id": ObjectId(),
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Administrator",
                "hashed_password": hashed_password,
                "disabled": False,
                "is_admin": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await db.users.insert_one(user)
            print(f"Insert result: {result.inserted_id}")
        
        # Double-check that user exists
        admin_user = await db.users.find_one({"username": "admin"})
        if admin_user:
            print("\nVerified admin user in database:")
            print(f"  _id: {admin_user.get('_id')}")
            print(f"  username: {admin_user.get('username')}")
            print(f"  email: {admin_user.get('email')}")
            print(f"  hashed_password: {admin_user.get('hashed_password', '')[:20]}...")
        
        print("\nAdmin user has been fixed. You can now log in with:")
        print("  Username: admin")
        print("  Password: admin1")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_admin_user()) 