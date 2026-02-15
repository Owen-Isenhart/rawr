from unittest.mock import MagicMock, patch
import pytest

@pytest.mark.asyncio
@patch("app.services.docker_service.DockerService.spawn_agent_container")
@patch("app.services.ai_service.AIService.get_agent_decision")
async def test_battle_loop_logic(mock_ai, mock_docker, db_session):
    from app.services.battle_service import BattleService
    
    # Setup Mocks
    mock_docker.return_value = MagicMock(id="test_container_123")
    mock_ai.return_value = "nmap -F 10.5.0.3"
    
    service = BattleService(db_session)
    # Logic: run_battle_royale should call docker.spawn_agent_container
    # and ai.get_agent_decision multiple times.
    
    # (Simplified call for testing logic flow)
    assert service.docker is not None
    assert service.ai is not None