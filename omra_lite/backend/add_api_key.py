"""
Simple script to add API keys directly to the database.
This bypasses the need for authentication.
"""
import asyncio
import sys
from datetime import datetime
from bson import ObjectId

from db import get_database

async def add_api_key(key_name, key_value):
    """Add an API key to the database."""
    db = await get_database()
    
    # Check if key already exists
    existing_key = await db.api_keys.find_one({"key_name": key_name})
    if existing_key:
        print(f"API key {key_name} already exists. Updating value.")
        await db.api_keys.update_one(
            {"key_name": key_name},
            {"$set": {
                "key_value": key_value,
                "updated_at": datetime.utcnow()
            }}
        )
    else:
        print(f"Adding new API key: {key_name}")
        await db.api_keys.insert_one({
            "_id": ObjectId(),
            "key_name": key_name,
            "key_value": key_value,
            "is_encrypted": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
    
    print(f"API key {key_name} has been saved successfully.")

async def list_api_keys():
    """List all API keys in the database."""
    db = await get_database()
    keys = await db.api_keys.find().to_list(length=100)
    
    if not keys:
        print("No API keys found in the database.")
        return
    
    print("\nAvailable API keys:")
    print("-" * 40)
    for key in keys:
        created = key.get("created_at", datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")
        print(f"Name: {key['key_name']}")
        print(f"Value: {key['key_value'][:5]}{'*' * 10}")
        print(f"Created: {created}")
        print("-" * 40)

async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python add_api_key.py list")
        print("  python add_api_key.py add KEY_NAME KEY_VALUE")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        await list_api_keys()
    elif command == "add" and len(sys.argv) == 4:
        key_name = sys.argv[2]
        key_value = sys.argv[3]
        await add_api_key(key_name, key_value)
    else:
        print("Invalid command or missing arguments.")
        print("Usage:")
        print("  python add_api_key.py list")
        print("  python add_api_key.py add KEY_NAME KEY_VALUE")

if __name__ == "__main__":
    asyncio.run(main()) 