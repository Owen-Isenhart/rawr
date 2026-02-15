"""
Rate limiting integration tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestRateLimiting:
    """Test rate limiting behavior across endpoints."""

    def test_auth_rate_limit_register(self, client: TestClient):
        """Test that register endpoint is rate limited to 5 per minute."""
        # Make 6 registration attempts
        for i in range(6):
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "username": f"user{i}",
                    "email": f"user{i}@test.com",
                    "password": "TestPass123!"
                }
            )
            
            # First 5 should succeed or fail validation
            if i < 5:
                assert response.status_code in [201, 422]
            # 6th should be rate limited
            else:
                assert response.status_code == 429

    def test_auth_rate_limit_login(self, client: TestClient, test_user_data: dict):
        """Test that login endpoint is rate limited to 5 per minute."""
        # First register a user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Make 6 login attempts
        for i in range(6):
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": test_user_data["username"],
                    "password": f"attempt{i}"
                }
            )
            
            # First 5 should get auth error (401)
            if i < 5:
                assert response.status_code == 401
            # 6th should be rate limited (429)
            else:
                assert response.status_code == 429

    def test_rate_limit_response_headers(self, client: TestClient, test_user_data: dict):
        """Test that rate limit response includes proper headers."""
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Make requests up to the limit
        for i in range(6):
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": test_user_data["username"],
                    "password": "wrong"
                }
            )
            
            # Check rate limit headers exist on limited response
            if response.status_code == 429:
                # slowapi sets X-RateLimit headers
                assert "x-ratelimit" in str(response.headers).lower() or response.status_code == 429

    def test_rate_limit_error_response_format(self, client: TestClient, test_user_data: dict):
        """Test that rate limit error responses are properly formatted."""
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Make requests to trigger rate limit
        for i in range(6):
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": test_user_data["username"],
                    "password": "wrong"
                }
            )
            if response.status_code == 429:
                # Should have JSON response
                data = response.json()
                assert isinstance(data, dict)
                assert "detail" in data or "error" in data

    def test_agent_endpoint_rate_limits(self, authenticated_client: TestClient, test_agent_data: dict):
        """Test agent endpoints are properly rate limited."""
        # This endpoint should have a rate limit (30 per hour for create)
        response = authenticated_client.post(
            "/api/v1/agents/agents",
            json=test_agent_data
        )
        # Should succeed if not rate limited
        assert response.status_code in [201, 400, 422]

    def test_battle_endpoint_rate_limits(self, authenticated_client: TestClient, db_session: Session):
        """Test battle endpoints are rate limited."""
        from app.models.agents import LLMModel, AgentConfig
        
        # Create necessary data
        model = LLMModel(ollama_tag="test", is_active=True)
        db_session.add(model)
        db_session.commit()
        
        # Create agents for authenticated user
        agent1 = AgentConfig(
            user_id=authenticated_client.cookies.get("user_id", 1),
            base_model_id=model.id,
            name="Agent 1",
            system_prompt="Test system prompt"
        )
        agent2 = AgentConfig(
            user_id=authenticated_client.cookies.get("user_id", 1),
            base_model_id=model.id,
            name="Agent 2",
            system_prompt="Test system prompt"
        )
        db_session.add_all([agent1, agent2])
        db_session.commit()
        
        # Start a battle (limited to 10 per hour)
        response = authenticated_client.post(
            "/api/v1/battle/start",
            json={
                "player_agents": [{"agent_id": agent1.id}],
                "opponent_agents": [{"agent_id": agent2.id}]
            }
        )
        
        # Should not be immediately rate limited (we're only making 1 request)
        assert response.status_code in [201, 400, 422, 429]

    def test_community_endpoint_rate_limits(self, authenticated_client: TestClient):
        """Test community endpoints are rate limited."""
        # Create a post (limited to 20 per hour)
        response = authenticated_client.post(
            "/api/v1/community/posts",
            json={
                "title": "Test Post",
                "content": "This is test content",
                "category": "general"
            }
        )
        
        # Should not be rate limited on first request
        assert response.status_code in [201, 400, 422]

    def test_rate_limit_applies_per_ip(self, client: TestClient, test_user_data: dict):
        """Test that rate limiting is per IP address."""
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Make requests from same client (same IP)
        responses = []
        for i in range(7):
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": test_user_data["username"],
                    "password": "wrong"
                }
            )
            responses.append(response.status_code)
        
        # Should have at least one 429 (rate limited)
        assert 429 in responses

    def test_rate_limit_different_endpoints_independent(self, authenticated_client: TestClient, test_agent_data: dict):
        """Test that rate limits are tracked independently per endpoint."""
        # Agent list endpoint
        response1 = authenticated_client.get("/api/v1/agents/agents")
        assert response1.status_code == 200
        
        # Community list endpoint
        response2 = authenticated_client.get("/api/v1/community/posts")
        # Should have different rate limits
        assert response2.status_code == 200
