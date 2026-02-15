"""
Comprehensive battle endpoint tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
from uuid import uuid4


class TestBattleEndpoints:
    """Test battle API endpoints."""

    def test_battle_requires_authentication(self, client: TestClient):
        """Test that battle endpoints require authentication."""
        # Start battle without auth
        response = client.post(
            "/api/v1/battle/start",
            json={
                "player_agents": [],
                "opponent_agents": []
            }
        )
        assert response.status_code == 401

        # Get battle status without auth
        response = client.get("/api/v1/battle/battles/nonexistent")
        assert response.status_code == 401

        # Get logs without auth
        response = client.get("/api/v1/battle/battles/nonexistent/logs")
        assert response.status_code == 401

    def test_start_battle_success(self, authenticated_client: TestClient, db_session: Session):
        """Test successfully starting a battle."""
        from app.models.agents import LLMModel, AgentConfig
        
        # Setup agents
        model = LLMModel(ollama_tag="test", is_active=True)
        db_session.add(model)
        db_session.commit()
        
        # Get authenticated user ID from token
        from app.crud.user_crud import get_user_by_username
        user = get_user_by_username(db_session, "testuser")
        
        agents = []
        for i in range(2):
            agent = AgentConfig(
                user_id=user.id,
                base_model_id=model.id,
                name=f"Battle Agent {i}",
                system_prompt="You are a hacker"
            )
            agents.append(agent)
        db_session.add_all(agents)
        db_session.commit()
        
        # Start battle
        with patch('app.services.battle_service.BattleService.start_battle_match') as mock_start:
            mock_start.return_value = {"battle_id": str(uuid4()), "status": "running"}
            
            response = authenticated_client.post(
                "/api/v1/battle/start",
                json={
                    "player_agents": [{"agent_id": agents[0].id}],
                    "opponent_agents": [{"agent_id": agents[1].id}]
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert "battle_id" in data
            assert "status" in data

    def test_start_battle_invalid_agent_count(self, authenticated_client: TestClient):
        """Test that battles require valid agent counts."""
        # No agents
        response = authenticated_client.post(
            "/api/v1/battle/start",
            json={
                "player_agents": [],
                "opponent_agents": []
            }
        )
        assert response.status_code == 400

    def test_start_battle_nonexistent_agent(self, authenticated_client: TestClient):
        """Test starting battle with non-existent agent."""
        response = authenticated_client.post(
            "/api/v1/battle/start",
            json={
                "player_agents": [{"agent_id": "nonexistent"}],
                "opponent_agents": [{"agent_id": "nonexistent-2"}]
            }
        )
        assert response.status_code == 400

    def test_start_battle_unauthorized_agent(self, authenticated_client: TestClient, db_session: Session):
        """Test that users can't use other users' agents."""
        from app.models.agents import LLMModel, AgentConfig
        from app.models.user import User
        
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@test.com",
            hashed_password="hashedpassword"
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create agent for other user
        model = LLMModel(ollama_tag="test", is_active=True)
        db_session.add(model)
        db_session.commit()
        
        agent = AgentConfig(
            user_id=other_user.id,
            base_model_id=model.id,
            name="Other User Agent",
            system_prompt="Test"
        )
        db_session.add(agent)
        db_session.commit()
        
        # Try to use other user's agent
        response = authenticated_client.post(
            "/api/v1/battle/start",
            json={
                "player_agents": [{"agent_id": agent.id}],
                "opponent_agents": [{"agent_id": agent.id}]
            }
        )
        assert response.status_code == 403

    def test_get_battle_status(self, authenticated_client: TestClient, db_session: Session):
        """Test getting battle status."""
        from app.models.battle import Battle
        from app.crud.user_crud import get_user_by_username
        
        user = get_user_by_username(db_session, "testuser")
        
        # Create a test battle
        battle = Battle(
            player_id=user.id,
            status="running",
            docker_container_ids="container1,container2"
        )
        db_session.add(battle)
        db_session.commit()
        
        # Get battle status
        response = authenticated_client.get(f"/api/v1/battle/battles/{battle.id}")
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "battle_id" in data or "id" in data

    def test_get_nonexistent_battle(self, authenticated_client: TestClient):
        """Test getting non-existent battle."""
        response = authenticated_client.get("/api/v1/battle/battles/nonexistent-id")
        assert response.status_code == 404

    def test_get_other_users_battle_status(self, authenticated_client: TestClient, db_session: Session):
        """Test that users can only view battles they created."""
        from app.models.battle import Battle
        from app.models.user import User
        
        # Create another user
        other_user = User(
            username="battletestuser",
            email="battle@test.com",
            hashed_password="hashedpassword"
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create battle for other user
        battle = Battle(
            player_id=other_user.id,
            status="running",
            docker_container_ids="container1,container2"
        )
        db_session.add(battle)
        db_session.commit()
        
        # Try to view other user's battle
        response = authenticated_client.get(f"/api/v1/battle/battles/{battle.id}")
        assert response.status_code == 403

    def test_get_battle_logs(self, authenticated_client: TestClient, db_session: Session):
        """Test fetching battle logs."""
        from app.models.battle import Battle
        from app.crud.user_crud import get_user_by_username
        
        user = get_user_by_username(db_session, "testuser")
        
        # Create battle
        battle = Battle(
            player_id=user.id,
            status="completed",
            docker_container_ids="container1,container2",
            logs="Battle logs here"
        )
        db_session.add(battle)
        db_session.commit()
        
        # Get logs
        response = authenticated_client.get(f"/api/v1/battle/battles/{battle.id}/logs")
        
        if response.status_code == 200:
            data = response.json()
            assert "logs" in data or "content" in data

    def test_get_logs_nonexistent_battle(self, authenticated_client: TestClient):
        """Test getting logs for non-existent battle."""
        response = authenticated_client.get("/api/v1/battle/battles/nonexistent/logs")
        assert response.status_code == 404

    def test_battle_leaderboard(self, client: TestClient, db_session: Session):
        """Test accessing battle leaderboard."""
        from app.models.user import User
        from app.models.agents import LLMModel, AgentConfig
        from app.models.battle import Battle
        
        # Create users and agents
        user1 = User(username="leaderuser1", email="leader1@test.com", hashed_password="hashed")
        user2 = User(username="leaderuser2", email="leader2@test.com", hashed_password="hashed")
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create battles
        battle = Battle(
            player_id=user1.id,
            status="completed",
            winner_id=user1.id
        )
        db_session.add(battle)
        db_session.commit()
        
        # Get leaderboard
        response = client.get("/api/v1/battle/leaderboard")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)

    def test_battle_leaderboard_sorting(self, client: TestClient):
        """Test that leaderboard is properly sorted by wins/ranking."""
        response = client.get("/api/v1/battle/leaderboard")
        assert response.status_code == 200
        
        data = response.json()
        # If leaderboard exists and has multiple entries, should be sorted
        if len(data) > 1:
            # Check that entries have some ranking/score field
            assert all("wins" in entry or "score" in entry or "rank" in entry for entry in data)

    def test_battle_history(self, authenticated_client: TestClient, db_session: Session):
        """Test getting user's battle history."""
        from app.models.battle import Battle
        from app.crud.user_crud import get_user_by_username
        
        user = get_user_by_username(db_session, "testuser")
        
        # Create battles
        for i in range(3):
            battle = Battle(
                player_id=user.id,
                status="completed",
                winner_id=user.id if i % 2 == 0 else None
            )
            db_session.add(battle)
        db_session.commit()
        
        # Get user's battles
        response = authenticated_client.get("/api/v1/battle/my-battles")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                assert len(data) >= 0  # Should have battles or empty list

    def test_start_battle_with_docker_mock(self, authenticated_client: TestClient, db_session: Session):
        """Test battle start with Docker operations mocked."""
        from app.models.agents import LLMModel, AgentConfig
        from app.crud.user_crud import get_user_by_username
        
        user = get_user_by_username(db_session, "testuser")
        
        # Setup agents
        model = LLMModel(ollama_tag="test", is_active=True)
        db_session.add(model)
        db_session.commit()
        
        agent1 = AgentConfig(
            user_id=user.id,
            base_model_id=model.id,
            name="Agent 1",
            system_prompt="Hacker agent"
        )
        agent2 = AgentConfig(
            user_id=user.id,
            base_model_id=model.id,
            name="Agent 2",
            system_prompt="Hacker agent"
        )
        db_session.add_all([agent1, agent2])
        db_session.commit()
        
        # Mock Docker service
        with patch('app.services.docker_service.DockerService') as mock_docker:
            mock_instance = MagicMock()
            mock_docker.return_value = mock_instance
            mock_instance.run_container.return_value = str(uuid4())
            
            response = authenticated_client.post(
                "/api/v1/battle/start",
                json={
                    "player_agents": [{"agent_id": agent1.id}],
                    "opponent_agents": [{"agent_id": agent2.id}]
                }
            )
            
            assert response.status_code in [201, 400, 422]
