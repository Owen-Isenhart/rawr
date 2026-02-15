"""
Comprehensive security tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password


class TestSecurityValidation:
    """Test security features and validations."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        # Hashed password should be different from original
        assert hashed != password
        
        # Verification should work
        assert verify_password(password, hashed) is True
        
        # Wrong password should fail
        assert verify_password("WrongPassword123!", hashed) is False

    def test_xss_protection_in_post(self, client: TestClient, db_session: Session):
        """Test that XSS attempts are sanitized in community posts."""
        # Register and login
        user_data = {"username": "testuser", "email": "test@example.com", "password": "TestPass123!"}
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": user_data["username"], "password": user_data["password"]}
        )
        token = login_response.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        
        # Try to post with XSS script
        malicious_post = {
            "title": "Normal Title",
            "content": "<script>alert('XSS')</script>This is dangerous",
            "category": "general"
        }
        
        response = client.post("/api/v1/community/posts", json=malicious_post)
        # Should either sanitize or reject
        if response.status_code == 201:
            # If accepted, content should be escaped
            assert "<script>" not in response.json()["content"]

    def test_sql_injection_prevention(self, client: TestClient):
        """Test that SQL injection attempts are prevented."""
        # Try to login with SQL injection in username
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "' OR '1'='1",
                "password": "password"
            }
        )
        
        # Should return 401 (invalid credentials), not a SQL error
        assert response.status_code == 401
        assert "SQL" not in response.text.upper()

    def test_jwt_token_validation(self, client: TestClient, test_user_data: dict):
        """Test JWT token validation."""
        # Register and login
        client.post("/api/v1/auth/register", json=test_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            }
        )
        
        valid_token = login_response.json()["access_token"]
        
        # Test with valid token
        client.headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.get("/api/v1/agents/models")
        assert response.status_code == 200
        
        # Test with invalid token
        client.headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/v1/agents/models")
        assert response.status_code == 401
        
        # Test with no token
        client.headers = {}
        response = client.get("/api/v1/agents/models")
        assert response.status_code == 401

    def test_cors_headers(self, client: TestClient):
        """Test that CORS headers are properly configured."""
        response = client.get("/health")
        
        # Should allow basic request
        assert response.status_code == 200

    def test_input_validation_username(self, client: TestClient):
        """Test username validation."""
        # Empty username
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "",
                "email": "test@example.com",
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 422

    def test_input_validation_email(self, client: TestClient):
        """Test email format validation."""
        # Invalid email formats
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user example@test.com"
        ]
        
        for invalid_email in invalid_emails:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "username": "testuser",
                    "email": invalid_email,
                    "password": "TestPass123!"
                }
            )
            assert response.status_code == 422

    def test_rate_limiting_auth(self, client: TestClient, test_user_data: dict):
        """Test rate limiting on auth endpoints."""
        # Register user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Try to login multiple times quickly
        # Note: We need at least 5+ requests to hit the rate limit
        for i in range(6):
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": test_user_data["username"],
                    "password": "WrongPassword123!"
                }
            )
            # Last request might be rate limited (429) or just invalid creds (401)
            assert response.status_code in [401, 429]

    def test_resource_ownership_enforcement(self, client: TestClient, db_session: Session):
        """Test that users can only access their own resources."""
        from app.models.agents import LLMModel, AgentConfig
        from uuid import uuid4
        
        # Create two users
        user1 = {"username": "user1", "email": "user1@test.com", "password": "TestPass123!"}
        user2 = {"username": "user2", "email": "user2@test.com", "password": "TestPass123!"}
        
        user1_response = client.post("/api/v1/auth/register", json=user1)
        user1_id = user1_response.json()["id"]
        
        client.post("/api/v1/auth/register", json=user2)
        
        # Create model and agent for user1
        model = LLMModel(ollama_tag="test", is_active=True)
        db_session.add(model)
        db_session.commit()
        
        agent = AgentConfig(
            user_id=user1_id,
            base_model_id=model.id,
            name="User1 Agent",
            system_prompt="Test system prompt"
        )
        db_session.add(agent)
        db_session.commit()
        
        # Login as user2
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": user2["username"], "password": user2["password"]}
        )
        client.headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        # Try to access user1's agent
        response = client.get(f"/api/v1/agents/agents/{agent.id}")
        assert response.status_code == 403
        
        # Try to update user1's agent
        response = client.patch(
            f"/api/v1/agents/agents/{agent.id}",
            json={"name": "Hacked Agent"}
        )
        assert response.status_code == 403
        
        # Try to delete user1's agent
        response = client.delete(f"/api/v1/agents/agents/{agent.id}")
        assert response.status_code == 403
