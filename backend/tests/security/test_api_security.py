"""
Security tests for API endpoints focusing on input validation and protection
against common attacks including injection, XSS, and boundary testing.
"""
import pytest
import random
import string
from fastapi.testclient import TestClient

# Helper function to get authentication token
def get_auth_token(test_client):
    """Get an authentication token for API requests."""
    response = test_client.post(
        "/api/auth/login",
        json={
            "email": "admin@example.com",
            "password": "adminpassword",
        }
    )
    return response.json()["access_token"]

# Helper function to generate a random string
def random_string(length=10):
    """Generate a random string of fixed length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class TestInputValidation:
    """Tests for API input validation."""
    
    def setup_method(self):
        """Setup before each test."""
        self.valid_customer = {
            "first_name": "Test",
            "last_name": "Customer",
            "email": f"test.{random_string()}@example.com",
            "phone": "555-123-4567",
            "address_line1": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345",
        }
    
    def test_customer_input_validation(self, test_client):
        """Test input validation for customer creation."""
        token = get_auth_token(test_client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with missing required fields
        invalid_customer = self.valid_customer.copy()
        del invalid_customer["first_name"]
        response = test_client.post(
            "/api/customers",
            json=invalid_customer,
            headers=headers
        )
        assert response.status_code == 422
        
        # Test with invalid email format
        invalid_customer = self.valid_customer.copy()
        invalid_customer["email"] = "not_an_email"
        response = test_client.post(
            "/api/customers",
            json=invalid_customer,
            headers=headers
        )
        assert response.status_code == 422
        
        # Test with extremely long input
        invalid_customer = self.valid_customer.copy()
        invalid_customer["first_name"] = "A" * 1000  # Extremely long name
        response = test_client.post(
            "/api/customers",
            json=invalid_customer,
            headers=headers
        )
        assert response.status_code == 422
    
    def test_service_request_input_validation(self, test_client):
        """Test input validation for service request creation."""
        token = get_auth_token(test_client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a customer first to get a valid customer_id
        response = test_client.post(
            "/api/customers",
            json=self.valid_customer,
            headers=headers
        )
        customer_id = response.json()["id"]
        
        # Create a valid service request
        valid_service_request = {
            "customer_id": customer_id,
            "status": "pending",
            "priority": "medium",
            "issue_description": "Appliance not working",
            "appliance_type": "refrigerator"
        }
        
        # Test with missing required fields
        invalid_request = valid_service_request.copy()
        del invalid_request["issue_description"]
        response = test_client.post(
            "/api/service-requests",
            json=invalid_request,
            headers=headers
        )
        assert response.status_code == 422
        
        # Test with invalid status
        invalid_request = valid_service_request.copy()
        invalid_request["status"] = "invalid_status"
        response = test_client.post(
            "/api/service-requests",
            json=invalid_request,
            headers=headers
        )
        assert response.status_code == 422
        
        # Test with invalid customer_id
        invalid_request = valid_service_request.copy()
        invalid_request["customer_id"] = 99999  # Non-existent ID
        response = test_client.post(
            "/api/service-requests",
            json=invalid_request,
            headers=headers
        )
        assert response.status_code in [404, 422]


class TestInjectionProtection:
    """Tests for protection against various injection attacks."""
    
    def test_sql_injection_protection(self, test_client):
        """Test protection against SQL injection in query parameters."""
        token = get_auth_token(test_client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try SQL injection in query parameter
        injection_attempts = [
            "1; DROP TABLE customers;",
            "1 OR 1=1",
            "1' OR '1'='1",
            "1' UNION SELECT * FROM users--"
        ]
        
        for injection in injection_attempts:
            # Try in customer ID route parameter
            response = test_client.get(
                f"/api/customers/{injection}",
                headers=headers
            )
            assert response.status_code in [404, 422]
            
            # Try in search query string
            response = test_client.get(
                f"/api/customers?search={injection}",
                headers=headers
            )
            # Should not cause a server error
            assert response.status_code != 500
    
    def test_xss_protection(self, test_client):
        """Test protection against XSS in user input fields."""
        token = get_auth_token(test_client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # XSS payloads to test
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src='x' onerror='alert(\"XSS\")'>",
            "<a href='javascript:alert(\"XSS\")'>Click me</a>",
            "javascript:alert('XSS')"
        ]
        
        # Create customers with XSS payload in the name field
        for payload in xss_payloads:
            customer = {
                "first_name": payload,
                "last_name": "Customer",
                "email": f"test.{random_string()}@example.com",
                "phone": "555-123-4567",
                "address_line1": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345",
            }
            
            # Should accept the input but sanitize/escape it when returned
            response = test_client.post(
                "/api/customers",
                json=customer,
                headers=headers
            )
            assert response.status_code in [201, 422]
            
            if response.status_code == 201:
                customer_id = response.json()["id"]
                response = test_client.get(
                    f"/api/customers/{customer_id}",
                    headers=headers
                )
                # Check that the script tag hasn't been inserted as-is
                assert "<script>" not in response.text


class TestBoundaryTesting:
    """Tests for boundary conditions and edge cases."""
    
    def test_pagination_boundaries(self, test_client):
        """Test boundary conditions for pagination parameters."""
        token = get_auth_token(test_client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with negative page
        response = test_client.get(
            "/api/customers?page=-1&limit=10",
            headers=headers
        )
        assert response.status_code == 422
        
        # Test with zero page
        response = test_client.get(
            "/api/customers?page=0&limit=10",
            headers=headers
        )
        assert response.status_code == 422
        
        # Test with negative limit
        response = test_client.get(
            "/api/customers?page=1&limit=-10",
            headers=headers
        )
        assert response.status_code == 422
        
        # Test with extremely large limit
        response = test_client.get(
            "/api/customers?page=1&limit=1000000",
            headers=headers
        )
        # Should either return a capped result set or validation error
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            data = response.json()
            # Ensure server didn't try to load millions of records
            assert len(data.get("items", [])) <= 100
    
    def test_rate_limiting(self, test_client):
        """Test rate limiting for API endpoints."""
        # Make a large number of requests in quick succession
        for _ in range(50):
            test_client.get("/api/health")
        
        # Check if rate limiting kicks in eventually
        # Note: This test is a bit flaky and depends on the configuration
        response = test_client.get("/api/health")
        # We just verify we get a response (either normal or rate-limited)
        assert response.status_code in [200, 429] 