"""
Database connection module for PostgreSQL and MongoDB
"""
import os
from typing import Generator, Dict, Any

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pymongo import MongoClient
from pymongo.database import Database

# PostgreSQL connection
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "omra")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "omra")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create PostgreSQL engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MongoDB connection
MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_PORT = os.environ.get("MONGO_PORT", "27017")
MONGO_DB = os.environ.get("MONGO_DB", "omra")
MONGO_USER = os.environ.get("MONGO_USER", "")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "")

mongo_client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
mongo_db = mongo_client[MONGO_DB]

# Get MongoDB collections
conversations_collection = mongo_db["conversations"]
agent_logs_collection = mongo_db["agent_logs"]

# Dependency to get DB session
def get_db() -> Generator[Session, None, None]:
    """Get PostgreSQL database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mongo_db() -> Database:
    """Get MongoDB database"""
    return mongo_db

class DatabaseConnector:
    """Database connector for PostgreSQL and MongoDB"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the database connector
        
        Args:
            config: Database configuration
        """
        self.config = config
        self.postgres_session = None
        self.mongo_client = None
        self.mongo_db = None
        
    async def connect(self):
        """Connect to databases"""
        # PostgreSQL connection
        postgres_config = self.config.get("postgres", {})
        postgres_url = f"postgresql://{postgres_config.get('user')}:{postgres_config.get('password')}@{postgres_config.get('host')}:{postgres_config.get('port')}/{postgres_config.get('database')}"
        
        engine = create_engine(postgres_url)
        self.postgres_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
        
        # MongoDB connection
        mongo_config = self.config.get("mongodb", {})
        mongo_uri = mongo_config.get("uri")
        mongo_db_name = mongo_config.get("database")
        
        self.mongo_client = MongoClient(mongo_uri)
        self.mongo_db = self.mongo_client[mongo_db_name]
        
    async def disconnect(self):
        """Disconnect from databases"""
        if self.postgres_session:
            self.postgres_session.close()
            
        if self.mongo_client:
            self.mongo_client.close()
            
    def get_postgres_session(self) -> Session:
        """Get PostgreSQL session"""
        if not self.postgres_session:
            raise ValueError("PostgreSQL session not initialized. Call connect() first.")
        return self.postgres_session
    
    def get_mongo_db(self) -> Database:
        """Get MongoDB database"""
        if not self.mongo_db:
            raise ValueError("MongoDB database not initialized. Call connect() first.")
        return self.mongo_db
    
    def get_collection(self, collection_name: str):
        """Get MongoDB collection"""
        return self.get_mongo_db()[collection_name] 