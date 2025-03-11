"""
MongoDB Database Connection Module

This module handles database connections for OMRA Lite.
It uses Motor for async MongoDB operations.
"""
import os
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Configure logging
logger = logging.getLogger("omra_lite.db")

# MongoDB connection string - default to localhost if not provided
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "omra_lite")

# MongoDB client
client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None

async def get_database() -> AsyncIOMotorDatabase:
    """
    Get database connection.
    
    Returns:
        AsyncIOMotorDatabase: MongoDB database connection
    """
    global client, db
    
    # If we already have a connection, return it
    if db is not None:
        return db
    
    # Otherwise, create a new connection
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        # Ping the server to check that the connection is working
        await client.admin.command('ping')
        db = client[DATABASE_NAME]
        logger.info(f"Connected to MongoDB: {MONGODB_URL}, database: {DATABASE_NAME}")
        
        # Create indexes if they don't exist
        await create_indexes()
        
        return db
    
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close MongoDB connection."""
    global client
    
    if client is not None:
        client.close()
        logger.info("Closed MongoDB connection")

async def create_indexes():
    """Create indexes on collections for better query performance."""
    global db
    
    # Users collection
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
    
    # Customers collection
    await db.customers.create_index("email")
    await db.customers.create_index("phone")
    
    # Service requests collection
    await db.service_requests.create_index("customer_id")
    await db.service_requests.create_index("status")
    await db.service_requests.create_index("created_at")
    
    # Technicians collection
    await db.technicians.create_index("email", unique=True)
    
    # Agents collection
    await db.agents.create_index("name")
    await db.agents.create_index("type")
    
    logger.info("Created MongoDB indexes") 