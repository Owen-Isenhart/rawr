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
    """
    Initiate a new hacking battle in an isolated Docker arena.
    
    Validates:
    - User owns all agent configurations provided
    - At least 2 agents are provided
    - All agents are valid
    
    Returns:
    - Match object with initial setup (agents will battle in background)
    """
    # Validation: Ensure at least 2 agents
    if not match_data.agent_config_ids or len(match_data.agent_config_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Battle must have at least 2 agents"
        )
    
    if len(match_data.agent_config_ids) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 agents per battle"
        )
    
    # Validation: Ensure user owns all agents
    for agent_id in match_data.agent_config_ids:
        agent = get_agent_config(db, agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {agent_id} not found"
            )
        
        if agent.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't own agent {agent_id}"
            )
    
    try:
        battle_service = BattleService(db)
        match = battle_service.init_match_record(current_user.id)
        
        # Run the expensive battle loop in the background
        background_tasks.add_task(
            battle_service.run_battle_royale,
            match_id=match.id,
            agent_config_ids=match_data.agent_config_ids
        )
        
        logger.info(f"Started battle {match.id} for user {current_user.id}")
        return match
        
    except Exception as e:
        logger.error(f"Failed to start battle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize battle"
        )


@router.get("/matches/{match_id}", response_model=MatchRead, tags=["Battle"])
@limiter.limit("60 per hour")
def get_battle_status(
    request: Request,
    match_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current status of a battle."""
    match = get_match(db, UUID(match_id))
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Battle not found"
        )
    
    # Security: Only creator can view battle details
    if match.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this battle"
        )
    
    return match


@router.get("/matches/{match_id}/logs", response_model=List[ActionLogRead], tags=["Battle"])
@limiter.limit("30 per hour")
def get_battle_logs(
    request: Request,
    match_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get action logs from a battle.
    
    Shows commands executed by agents and their outputs.
    """
    match = get_match(db, UUID(match_id))
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Battle not found"
        )
    
    # Security: Only creator can view logs
    if match.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these logs"
        )
    
    return get_match_logs(db, UUID(match_id), skip=skip, limit=limit)


@router.get("/leaderboard", tags=["Battle"])
@limiter.limit("60 per hour")
def get_leaderboard(
    request: Request,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the global leaderboard of top players by rank points."""
    from app.crud.user_crud import get_leaderboard
    return get_leaderboard(db, limit=limit)
