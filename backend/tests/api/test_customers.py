import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.customer import Customer
from backend.schemas.customer import CustomerCreate, CustomerResponse

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def test_customer(db_session: AsyncSession):
    """Create a test customer in the database."""
    customer_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "555-123-4567",
        "address": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345"
    }
    
    customer = Customer(**customer_data)
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)
    
    yield customer
    
    # Cleanup
    await db_session.delete(customer)
    await db_session.commit()

async def test_create_customer(client: AsyncClient):
    """Test creating a new customer."""
    customer_data = {
        "first_name": "New",
        "last_name": "Customer",
        "email": "new@example.com",
        "phone": "555-987-6543",
        "address": "456 New St",
        "city": "New City",
        "state": "NS",
        "zip_code": "54321"
    }
    
    response = await client.post("/api/customers/", json=customer_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == customer_data["first_name"]
    assert data["last_name"] == customer_data["last_name"]
    assert data["email"] == customer_data["email"]
    assert "id" in data

async def test_get_customer(client: AsyncClient, test_customer: Customer):
    """Test retrieving a customer by ID."""
    response = await client.get(f"/api/customers/{test_customer.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_customer.id
    assert data["first_name"] == test_customer.first_name
    assert data["last_name"] == test_customer.last_name
    assert data["email"] == test_customer.email

async def test_get_all_customers(client: AsyncClient, test_customer: Customer):
    """Test retrieving all customers."""
    response = await client.get("/api/customers/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # Check if our test customer is in the list
    customer_ids = [customer["id"] for customer in data]
    assert test_customer.id in customer_ids

async def test_update_customer(client: AsyncClient, test_customer: Customer):
    """Test updating a customer."""
    update_data = {
        "first_name": "Updated",
        "last_name": "User",
        "email": "updated@example.com"
    }
    
    response = await client.patch(f"/api/customers/{test_customer.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_customer.id
    assert data["first_name"] == update_data["first_name"]
    assert data["last_name"] == update_data["last_name"]
    assert data["email"] == update_data["email"]
    # Fields not in update_data should remain unchanged
    assert data["phone"] == test_customer.phone

async def test_delete_customer(client: AsyncClient, db_session: AsyncSession):
    """Test deleting a customer."""
    # Create a customer to delete
    customer_data = {
        "first_name": "Delete",
        "last_name": "Me",
        "email": "delete@example.com",
        "phone": "555-111-2222",
        "address": "789 Delete St",
        "city": "Delete City",
        "state": "DL",
        "zip_code": "98765"
    }
    
    customer = Customer(**customer_data)
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)
    
    # Delete the customer
    response = await client.delete(f"/api/customers/{customer.id}")
    
    assert response.status_code == 204
    
    # Verify customer is deleted
    response = await client.get(f"/api/customers/{customer.id}")
    assert response.status_code == 404 