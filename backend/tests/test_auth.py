"""
Comprehensive tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAuthEndpoints:
    """Test suite for authentication endpoints."""

    def test_register_success(self, client: TestClient, test_user_data: dict):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 201
        assert response.json()["username"] == test_user_data["username"]
        assert response.json()["email"] == test_user_data["email"]
        assert "password" not in response.json()

    def test_register_duplicate_email(self, client: TestClient, test_user_data: dict):
        """Test registration fails with duplicate email."""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register with same email
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "different_user"
        response = client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_register_duplicate_username(self, client: TestClient, test_user_data: dict):
        """Test registration fails with duplicate username."""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to register with same username
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        response = client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert response.status_code == 409
        assert "username" in response.json()["detail"].lower() or "taken" in response.json()["detail"].lower()

    def test_register_weak_password(self, client: TestClient, test_user_data: dict):
        """Test registration fails with weak password."""
        weak_password_data = test_user_data.copy()
        weak_password_data["password"] = "weak"
        
        response = client.post("/api/v1/auth/register", json=weak_password_data)
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient, test_user_data: dict):
        """Test registration fails with invalid email."""
        invalid_email_data = test_user_data.copy()
        invalid_email_data["email"] = "not-an-email"
        
        response = client.post("/api/v1/auth/register", json=invalid_email_data)
        assert response.status_code == 422  # Validation error

    def test_login_success(self, client: TestClient, test_user_data: dict):
        """Test successful login."""
        # Register user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Login
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
        assert response.json()["user"]["username"] == test_user_data["username"]

    def test_login_invalid_credentials(self, client: TestClient, test_user_data: dict):
        """Test login fails with invalid credentials."""
        # Register user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login fails for nonexistent user."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent_user",
                "password": "SomePassword123!"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_password_strength_requirements(self, client: TestClient):
        """Test all password strength requirements are enforced."""
        base_data = {
            "username": "testuser",
            "email": "test@example.com"
        }
        
        # Too short
        response = client.post(
            "/api/v1/auth/register",
            json={**base_data, "password": "Short1!"}
        )
        assert response.status_code == 400
        
        # No uppercase
        response = client.post(
            "/api/v1/auth/register",
            json={**base_data, "password": "lowercase123!"}
        )
        assert response.status_code == 400
        
        # No lowercase
        response = client.post(
            "/api/v1/auth/register",
            json={**base_data, "password": "UPPERCASE123!"}
        )
        assert response.status_code == 400
        
        # No digit
        response = client.post(
            "/api/v1/auth/register",
            json={**base_data, "password": "NoDigits!!!"}
        )
        assert response.status_code == 400

    def test_token_returned_has_correct_user_id(self, client: TestClient, test_user_data: dict):
        """Test that token is issued for correct user."""
        # Register user
        reg_response = client.post("/api/v1/auth/register", json=test_user_data)
        user_id = reg_response.json()["id"]
        
        # Login and verify token has correct user ID
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        
        assert login_response.json()["user"]["id"] == user_id


def test_login_success(client):
    # Ensure user exists
    client.post("/api/v1/auth/register", json={
        "username": "login_user",
        "email": "login@arena.io",
        "password": "password123"
    })
    
    # Attempt login
    response = client.post("/api/v1/auth/login", data={
        "username": "login@arena.io",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    response = client.post("/api/v1/auth/login", data={
        "username": "wrong@arena.io",
        "password": "wrongpassword"
    })
    assert response.status_code == 401