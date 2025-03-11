"""
Database Initialization Script for OMRA Lite

This script initializes the MongoDB database with example data for testing.
"""
import asyncio
import logging
from datetime import datetime, timedelta

from db import get_database, close_mongo_connection
from agent_system import agent_manager, AgentType
from models import ApplianceType, ServiceStatus, ServicePriority

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("omra_lite.init_db")

async def init_db():
    """Initialize the database with example data."""
    logger.info("Initializing database with example data...")
    
    db = await get_database()
    
    # Check if data already exists
    customer_count = await db.customers.count_documents({})
    if customer_count > 0:
        logger.info("Database already contains data. Skipping initialization.")
        return
    
    # Create example customers
    customers = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "contact_info": {
                "phone": "555-123-4567",
                "email": "john.doe@example.com",
                "preferred_contact": "phone"
            },
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345",
                "country": "USA"
            },
            "notes": "Prefers afternoon appointments",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "contact_info": {
                "phone": "555-987-6543",
                "email": "jane.smith@example.com",
                "preferred_contact": "email"
            },
            "address": {
                "street": "456 Oak Ave",
                "city": "Somewhere",
                "state": "NY",
                "zip_code": "67890",
                "country": "USA"
            },
            "notes": "Has a dog",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "first_name": "Bob",
            "last_name": "Johnson",
            "contact_info": {
                "phone": "555-456-7890",
                "email": "bob.johnson@example.com",
                "preferred_contact": "phone"
            },
            "address": {
                "street": "789 Pine Rd",
                "city": "Elsewhere",
                "state": "TX",
                "zip_code": "54321",
                "country": "USA"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    customer_ids = []
    for customer in customers:
        result = await db.customers.insert_one(customer)
        customer_ids.append(str(result.inserted_id))
    
    logger.info(f"Created {len(customer_ids)} example customers")
    
    # Create example technicians
    technicians = [
        {
            "first_name": "Mike",
            "last_name": "Tech",
            "email": "mike.tech@example.com",
            "phone": "555-111-2222",
            "specialties": [ApplianceType.REFRIGERATOR, ApplianceType.WASHER, ApplianceType.DRYER],
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "first_name": "Sarah",
            "last_name": "Fix",
            "email": "sarah.fix@example.com",
            "phone": "555-333-4444",
            "specialties": [ApplianceType.STOVE, ApplianceType.OVEN, ApplianceType.DISHWASHER],
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    technician_ids = []
    for technician in technicians:
        result = await db.technicians.insert_one(technician)
        technician_ids.append(str(result.inserted_id))
    
    logger.info(f"Created {len(technician_ids)} example technicians")
    
    # Create example service requests
    now = datetime.utcnow()
    service_requests = [
        {
            "customer_id": customer_ids[0],
            "appliance_type": ApplianceType.REFRIGERATOR,
            "issue_description": "Not cooling properly",
            "priority": ServicePriority.HIGH,
            "status": ServiceStatus.PENDING,
            "notes": "Customer reports freezer is still working",
            "created_at": now - timedelta(days=2),
            "updated_at": now - timedelta(days=2)
        },
        {
            "customer_id": customer_ids[1],
            "appliance_type": ApplianceType.WASHER,
            "issue_description": "Leaking water during cycle",
            "priority": ServicePriority.MEDIUM,
            "status": ServiceStatus.SCHEDULED,
            "scheduled_date": now + timedelta(days=1),
            "technician_id": technician_ids[0],
            "notes": "Bring extra towels",
            "created_at": now - timedelta(days=3),
            "updated_at": now - timedelta(days=1)
        },
        {
            "customer_id": customer_ids[2],
            "appliance_type": ApplianceType.STOVE,
            "issue_description": "Front left burner not working",
            "priority": ServicePriority.LOW,
            "status": ServiceStatus.IN_PROGRESS,
            "scheduled_date": now - timedelta(hours=3),
            "technician_id": technician_ids[1],
            "created_at": now - timedelta(days=1),
            "updated_at": now - timedelta(hours=3)
        },
        {
            "customer_id": customer_ids[0],
            "appliance_type": ApplianceType.DISHWASHER,
            "issue_description": "Not draining properly",
            "priority": ServicePriority.MEDIUM,
            "status": ServiceStatus.COMPLETED,
            "scheduled_date": now - timedelta(days=5),
            "technician_id": technician_ids[1],
            "completed_at": now - timedelta(days=5),
            "notes": "Fixed clogged drain line",
            "created_at": now - timedelta(days=7),
            "updated_at": now - timedelta(days=5)
        }
    ]
    
    for service_request in service_requests:
        await db.service_requests.insert_one(service_request)
    
    logger.info(f"Created {len(service_requests)} example service requests")
    
    # Initialize agents
    await agent_manager.initialize_default_agents()
    
    logger.info("Database initialization complete!")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(init_db())
    finally:
        loop.run_until_complete(close_mongo_connection())
        loop.close() 