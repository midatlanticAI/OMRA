"""
Locust performance test file for the OpenManus API.

This file defines load test scenarios for the OpenManus API using Locust.
To run: locust -f locustfile.py --host=http://localhost:8000
"""
import json
import random
from locust import HttpUser, task, between, tag

class OpenManusAPIUser(HttpUser):
    """
    Simulates a user interacting with the OpenManus API.
    """
    wait_time = between(1, 5)  # Wait between 1 and 5 seconds between tasks
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.customer_ids = []
        self.service_request_ids = []
    
    def on_start(self):
        """
        Authenticate the user before starting the test.
        """
        response = self.client.post("/api/auth/login", json={
            "email": "admin@example.com",
            "password": "password123"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            # Set the Authorization header for all subsequent requests
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            print("Authentication successful")
        else:
            print(f"Authentication failed with status code: {response.status_code}")
    
    @tag('health')
    @task(10)  # Higher weight for health check as it's called frequently
    def health_check(self):
        """
        Test the health check endpoint.
        """
        self.client.get("/health")
    
    @tag('customers')
    @task(5)
    def get_customers(self):
        """
        Test retrieving the customer list.
        """
        response = self.client.get("/api/customers")
        
        if response.status_code == 200:
            data = response.json()
            customers = data.get("items", [])
            # Store customer IDs for other tasks
            self.customer_ids = [customer["id"] for customer in customers]
    
    @tag('customers')
    @task(2)
    def get_customer_detail(self):
        """
        Test retrieving a specific customer's details.
        """
        if self.customer_ids:
            customer_id = random.choice(self.customer_ids)
            self.client.get(f"/api/customers/{customer_id}")
    
    @tag('customers')
    @task(1)
    def create_customer(self):
        """
        Test creating a new customer.
        """
        # Generate a unique email to avoid conflicts
        random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        
        customer_data = {
            "first_name": "Test",
            "last_name": "Customer",
            "email": f"test.customer.{random_suffix}@example.com",
            "phone": "555-123-4567",
            "address_line1": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345"
        }
        
        response = self.client.post("/api/customers", json=customer_data)
        
        if response.status_code == 201:
            new_customer = response.json()
            self.customer_ids.append(new_customer["id"])
    
    @tag('service_requests')
    @task(3)
    def get_service_requests(self):
        """
        Test retrieving the service request list.
        """
        response = self.client.get("/api/service-requests")
        
        if response.status_code == 200:
            data = response.json()
            service_requests = data.get("items", [])
            # Store service request IDs for other tasks
            self.service_request_ids = [sr["id"] for sr in service_requests]
    
    @tag('service_requests')
    @task(2)
    def get_service_request_detail(self):
        """
        Test retrieving a specific service request's details.
        """
        if self.service_request_ids:
            service_request_id = random.choice(self.service_request_ids)
            self.client.get(f"/api/service-requests/{service_request_id}")
    
    @tag('service_requests')
    @task(1)
    def create_service_request(self):
        """
        Test creating a new service request.
        """
        if not self.customer_ids:
            return
        
        customer_id = random.choice(self.customer_ids)
        
        service_request_data = {
            "customer_id": customer_id,
            "appliance_id": None,  # Will be created if not provided
            "status": "pending",
            "priority": "medium",
            "issue_description": "Appliance not working properly",
            "appliance_type": "refrigerator",
            "appliance_brand": "GE",
            "appliance_model": "XYZ123"
        }
        
        response = self.client.post("/api/service-requests", json=service_request_data)
        
        if response.status_code == 201:
            new_sr = response.json()
            self.service_request_ids.append(new_sr["id"])
    
    @tag('dashboard')
    @task(2)
    def get_dashboard_data(self):
        """
        Test retrieving dashboard data.
        """
        self.client.get("/api/dashboard")
    
    @tag('misc')
    @task(1)
    def get_technicians(self):
        """
        Test retrieving technicians.
        """
        self.client.get("/api/technicians")
        
    @tag('misc')
    @task(1)
    def get_appointments(self):
        """
        Test retrieving appointments.
        """
        self.client.get("/api/appointments")

# Add more user classes for different user behaviors if needed
class ReadOnlyUser(OpenManusAPIUser):
    """
    Simulates a user who only reads data, never modifies it.
    """
    
    @task(0)  # Disable create tasks
    def create_customer(self):
        pass
    
    @task(0)  # Disable create tasks
    def create_service_request(self):
        pass
    
    # Override with higher weights for read operations
    @task(10)
    def get_customers(self):
        super().get_customers()
    
    @task(8)
    def get_customer_detail(self):
        super().get_customer_detail()
    
    @task(10)
    def get_service_requests(self):
        super().get_service_requests()
    
    @task(8)
    def get_service_request_detail(self):
        super().get_service_request_detail() 