"""
Pytest configuration for backend tests.
"""
import os
from typing import Generator, AsyncGenerator
import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient
import motor.motor_asyncio
from pymongo import MongoClient
from pymongo.database import Database

# Try to import application dependencies
try:
    from backend.main import app
    from backend.db.session import get_db
    from backend.db.mongodb import get_mongodb
except ImportError:
    # Create a minimal app for testing if imports fail
    from fastapi import FastAPI, Depends
    app = FastAPI()
    
    async def get_db():
        """Mock DB dependency."""
        yield None

    async def get_mongodb():
        """Mock MongoDB dependency."""
        yield None

# Test database settings
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine for testing
engine = create_async_engine(DATABASE_URL)
TestingSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, autoflush=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    # Override the default event loop with a new one
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def init_db():
    """Initialize test database."""
    try:
        # Import SQLAlchemy models to create tables
        from backend.db.base import Base
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            
        yield
        
        # Cleanup
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            
    except ImportError:
        # If models cannot be imported, just yield
        yield

@pytest.fixture
async def db_session(init_db) -> AsyncGenerator[AsyncSession, None]:
    """Get a test database session."""
    async with TestingSessionLocal() as session:
        yield session
        # Rollback changes made in the test
        await session.rollback()
        # Close the session
        await session.close()

@pytest.fixture
async def override_get_db(db_session):
    """Override the get_db dependency."""
    
    async def _override_get_db():
        yield db_session
    
    # Override the dependency in the app
    app.dependency_overrides[get_db] = _override_get_db
    yield _override_get_db
    
    # Clean up
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture
async def mongodb_client():
    """Get a test MongoDB client."""
    # Use in-memory MongoDB for testing with mongo-memory-server
    # For this example, we'll use a mock client
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_db"]
    
    # Create test collections
    await db.create_collection("documents")
    await db.create_collection("agent_tasks")
    
    yield client
    
    # Clean up
    await client.drop_database("test_db")
    client.close()

@pytest.fixture
async def test_mongodb(mongodb_client):
    """Get a test MongoDB database."""
    db = mongodb_client["test_db"]
    yield db

@pytest.fixture
async def override_get_mongodb(test_mongodb):
    """Override the get_mongodb dependency."""
    
    async def _override_get_mongodb():
        yield test_mongodb
    
    # Override the dependency in the app
    app.dependency_overrides[get_mongodb] = _override_get_mongodb
    yield _override_get_mongodb
    
    # Clean up
    app.dependency_overrides.pop(get_mongodb, None)

@pytest.fixture
async def client(override_get_db, override_get_mongodb) -> AsyncGenerator[AsyncClient, None]:
    """Get an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def test_client(override_get_db, override_get_mongodb) -> Generator[TestClient, None, None]:
    """Get a synchronous test client."""
    with TestClient(app=app) as client:
        yield client 