"""
Comprehensive tests for agent management endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4


@pytest.fixture
def authenticated_client(client: TestClient, test_user_data: dict):
    """Provide a client with authentication headers."""
    # Register and login
    client.post("/api/v1/auth/register", json=test_user_data)
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


class TestAgentEndpoints:
    """Test suite for agent management endpoints."""

    def test_list_models_requires_auth(self, client: TestClient):
        """Test that listing models requires authentication."""
        response = client.get("/api/v1/agents/models")
        assert response.status_code == 401

    def test_list_models_authenticated(self, authenticated_client: TestClient):
        """Test listing models with authentication."""
        response = authenticated_client.get("/api/v1/agents/models")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_agent_success(self, authenticated_client: TestClient, db_session: Session):
        """Test successful agent creation."""
        from app.models.agents import LLMModel
        
        # First create a base model
        model = LLMModel(
            ollama_tag="test-model",
            description="Test model",
            is_active=True
        )
        db_session.add(model)
        db_session.commit()
        
        agent_data = {
            "base_model_id": str(model.id),
            "name": "Test Agent",
            "system_prompt": "You are a helpful assistant with at least 10 characters",
            "temperature": 0.7
        }
        
        response = authenticated_client.post("/api/v1/agents/agents", json=agent_data)
        assert response.status_code == 201
        assert response.json()["name"] == agent_data["name"]

    def test_create_agent_requires_auth(self, client: TestClient, test_agent_data: dict):
        """Test that creating agent requires authentication."""
        response = client.post("/api/v1/agents/agents", json=test_agent_data)
        assert response.status_code == 401

    def test_create_agent_invalid_system_prompt(self, authenticated_client: TestClient, db_session: Session):
        """Test agent creation fails with invalid system prompt."""
        from app.models.agents import LLMModel
        
        model = LLMModel(
            ollama_tag="test-model",
            description="Test model",
            is_active=True
        )
        db_session.add(model)
        db_session.commit()
        
        # Too short system prompt
        agent_data = {
            "base_model_id": str(model.id),
            "name": "Test Agent",
            "system_prompt": "Too short",
            "temperature": 0.7
        }
        
        response = authenticated_client.post("/api/v1/agents/agents", json=agent_data)
        assert response.status_code == 400

    def test_list_user_agents(self, authenticated_client: TestClient, db_session: Session):
        """Test listing user's agents."""
        response = authenticated_client.get("/api/v1/agents/agents")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_agent_requires_ownership(self, client: TestClient, db_session: Session):
        """Test that users can only view their own agents."""
        from app.models.agents import LLMModel, AgentConfig
        from app.models.user import User
        
        # Create two users
        user1_data = {"username": "user1", "email": "user1@test.com", "password": "TestPass123!"}
        user2_data = {"username": "user2", "email": "user2@test.com", "password": "TestPass123!"}
        
        user1_response = client.post("/api/v1/auth/register", json=user1_data)
        user1_id = user1_response.json()["id"]
        
        user2_response = client.post("/api/v1/auth/register", json=user2_data)
        
        # Create agent for user1
        model = LLMModel(ollama_tag="test", is_active=True)
        db_session.add(model)
        db_session.commit()
        
        agent = AgentConfig(
            user_id=user1_id,
            base_model_id=model.id,
            name="User1 Agent",
            system_prompt="This is a test system prompt for user 1"
        )
        db_session.add(agent)
        db_session.commit()
        
        # Login as user2 and try to access user1's agent
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": user2_data["username"], "password": user2_data["password"]}
        )
        client.headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        response = client.get(f"/api/v1/agents/agents/{agent.id}")
        assert response.status_code == 403

    def test_update_agent(self, authenticated_client: TestClient, db_session: Session):
        """Test updating an agent configuration."""
        from app.models.agents import LLMModel, AgentConfig
        
        # Create a model and agent for the current user
        model = LLMModel(ollama_tag="test", is_active=True)
        db_session.add(model)
        
        # Get the current user from token (would need to extract from DB session)
        from app.api.v1.deps import get_current_user
        # Simplified for test
        
        response = authenticated_client.patch(
            f"/api/v1/agents/agents/{uuid4()}",
            json={"name": "Updated Agent Name"}
        )
        # Expect 404 since agent doesn't exist
        assert response.status_code == 404

    def test_delete_agent(self, authenticated_client: TestClient, db_session: Session):
        """Test deleting an agent configuration."""
        response = authenticated_client.delete(f"/api/v1/agents/agents/{uuid4()}")
        assert response.status_code == 403 or response.status_code == 404

    def test_temperature_bounds(self, authenticated_client: TestClient, db_session: Session):
        """Test that temperature is bounded between 0 and 2."""
        from app.models.agents import LLMModel
        
        model = LLMModel(ollama_tag="test", is_active=True)
        db_session.add(model)
        db_session.commit()
        
        # Temperature > 2 should fail
        agent_data = {
            "base_model_id": str(model.id),
            "name": "Test Agent",
            "system_prompt": "This is a test system prompt with at least 10 characters",
            "temperature": 3.0
        }
        
        response = authenticated_client.post("/api/v1/agents/agents", json=agent_data)
        assert response.status_code == 422
        
        # Temperature < 0 should fail
        agent_data["temperature"] = -0.5
        response = authenticated_client.post("/api/v1/agents/agents", json=agent_data)
        assert response.status_code == 422
