"""
Security tests for authentication and authorization in the OpenManus API.
"""
import pytest
from fastapi.testclient import TestClient

# For these tests, we need specific test data
USER_CREDENTIALS = {
    "admin": {
        "email": "admin@example.com",
        "password": "adminpassword",
        "is_admin": True
    },
    "regular": {
        "email": "user@example.com",
        "password": "userpassword",
        "is_admin": False
    },
    "invalid": {
        "email": "invalid@example.com",
        "password": "wrongpassword",
    }
}

class TestAuthentication:
    """Tests for user authentication."""
    
    def test_login_success(self, test_client):
        """Test successful login with valid credentials."""
        user = USER_CREDENTIALS["admin"]
        response = test_client.post(
            "/api/auth/login",
            json={
                "email": user["email"],
                "password": user["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, test_client):
        """Test login with invalid credentials."""
        user = USER_CREDENTIALS["invalid"]
        response = test_client.post(
            "/api/auth/login",
            json={
                "email": user["email"],
                "password": user["password"]
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid" in data["detail"]
    
    def test_login_brute_force_protection(self, test_client, monkeypatch):
        """Test protection against brute force attacks."""
        # Attempt login multiple times with wrong password
        user = USER_CREDENTIALS["admin"]
        
        # Mock the rate limiter to enforce limits sooner
        from backend.api.auth import RATE_LIMIT_ATTEMPTS
        monkeypatch.setattr("backend.api.auth.RATE_LIMIT_ATTEMPTS", 3)
        
        # First few attempts should just fail normally
        for _ in range(RATE_LIMIT_ATTEMPTS - 1):
            test_client.post(
                "/api/auth/login",
                json={
                    "email": user["email"],
                    "password": "wrongpassword"
                }
            )
        
        # The next attempt should trigger rate limiting
        response = test_client.post(
            "/api/auth/login",
            json={
                "email": user["email"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 429
        assert "Too many attempts" in response.json()["detail"]
    
    def test_login_sql_injection_attempts(self, test_client):
        """Test that SQL injection attempts are properly handled."""
        injection_attempts = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users; --"
        ]
        
        for injection in injection_attempts:
            response = test_client.post(
                "/api/auth/login",
                json={
                    "email": "admin@example.com",
                    "password": injection
                }
            )
            # Should not cause a server error, just a normal auth failure
            assert response.status_code in [401, 422]
            
            # Try injection in the email field too
            response = test_client.post(
                "/api/auth/login",
                json={
                    "email": injection,
                    "password": "password"
                }
            )
            assert response.status_code in [401, 422]


class TestAuthorization:
    """Tests for user authorization."""
    
    def get_auth_header(self, test_client, user_type="admin"):
        """Helper to get an auth header for a user type."""
        user = USER_CREDENTIALS[user_type]
        response = test_client.post(
            "/api/auth/login",
            json={
                "email": user["email"],
                "password": user["password"]
            }
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_protected_route_with_valid_token(self, test_client):
        """Test accessing a protected route with a valid token."""
        headers = self.get_auth_header(test_client)
        response = test_client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
    
    def test_protected_route_without_token(self, test_client):
        """Test accessing a protected route without a token."""
        response = test_client.get("/api/users/me")
        assert response.status_code == 401
    
    def test_protected_route_with_expired_token(self, test_client, monkeypatch):
        """Test accessing a protected route with an expired token."""
        # Mock token expiration time to 0 minutes
        monkeypatch.setattr("backend.core.security.ACCESS_TOKEN_EXPIRE_MINUTES", 0)
        
        # Get a token that will expire immediately
        headers = self.get_auth_header(test_client)
        
        # Wait a short time to ensure token expiry
        import time
        time.sleep(1)
        
        response = test_client.get("/api/users/me", headers=headers)
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    
    def test_admin_route_with_admin_user(self, test_client):
        """Test accessing an admin-only route with an admin user."""
        headers = self.get_auth_header(test_client, "admin")
        response = test_client.get("/api/admin/users", headers=headers)
        assert response.status_code == 200
    
    def test_admin_route_with_regular_user(self, test_client):
        """Test accessing an admin-only route with a regular user."""
        headers = self.get_auth_header(test_client, "regular")
        response = test_client.get("/api/admin/users", headers=headers)
        assert response.status_code == 403
    
    def test_token_manipulation(self, test_client):
        """Test that manipulated tokens are rejected."""
        headers = self.get_auth_header(test_client)
        token = headers["Authorization"].split()[1]
        
        # Try manipulating the token
        manipulated_token = token[:-5] + "XXXXX"
        headers["Authorization"] = f"Bearer {manipulated_token}"
        
        response = test_client.get("/api/users/me", headers=headers)
        assert response.status_code == 401 