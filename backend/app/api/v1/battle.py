"""
Battle/Arena endpoints for starting and managing hacking battles.
"""
import logging
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.api.v1.deps import get_current_user
from app.services.battle_service import BattleService
from app.models.user import User
from app.dto.battle_dto import MatchCreate, MatchRead, ActionLogRead
from app.crud.agents_crud import get_agent_config
from app.crud.battle_crud import get_match, get_match_logs

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/start", response_model=MatchRead, status_code=status.HTTP_201_CREATED, tags=["Battle"])
@limiter.limit("10 per hour")
async def start_battle(
    request: Request,
    match_data: MatchCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initiate a battle using the structured player/opponent agent lists."""
    # Flatten IDs for validation and processing
    all_agent_ids = [a.agent_id for a in match_data.player_agents] + \
                    [a.agent_id for a in match_data.opponent_agents]
    
    if not all_agent_ids or len(all_agent_ids) < 2:
        raise HTTPException(status_code=400, detail="Battle must have at least 2 agents")
    
    # Validation: Ensure user owns all agents
    for agent_id in all_agent_ids:
        agent = get_agent_config(db, agent_id)
        if not agent or agent.user_id != current_user.id:
            raise HTTPException(status_code=403, detail=f"Invalid or unauthorized agent: {agent_id}")
    
    try:
        battle_service = BattleService(db)
        match = battle_service.init_match_record(current_user.id)
        
        background_tasks.add_task(
            battle_service.run_battle_royale,
            match_id=match.id,
            agent_config_ids=all_agent_ids
        )
        return match
    except Exception as e:
        logger.error(f"Failed to start battle: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize battle")

# ... (rest of file remains the same)