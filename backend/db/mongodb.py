"""
MongoDB connection module for document storage.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

from backend.core.config import settings

logger = logging.getLogger("omra")

class MongoDB:
    client: AsyncIOMotorClient = None
    db: Database = None

async def get_mongodb() -> Database:
    """
    Get MongoDB database connection.
    Returns a database instance for the application.
    """
    if MongoDB.client is None:
        try:
            MongoDB.client = AsyncIOMotorClient(settings.MONGODB_URL)
            MongoDB.db = MongoDB.client[settings.MONGODB_DATABASE]
            # Ping the database to verify the connection is live
            await MongoDB.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {settings.MONGODB_DATABASE}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    return MongoDB.db

async def close_mongodb_connection():
    """
    Close MongoDB connection.
    """
    if MongoDB.client is not None:
        MongoDB.client.close()
        MongoDB.client = None
        MongoDB.db = None
        logger.info("Closed MongoDB connection") 