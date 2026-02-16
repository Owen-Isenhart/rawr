"""
API endpoints for agent model management and configuration.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.api.v1.deps import get_current_user
from app.services.agents_service import AgentService
from app.crud.agents_crud import get_user_agents, get_agent_config
from app.models.user import User
from app.dto.agents_dto import (
    AgentConfigCreate, 
    AgentConfigRead,
    LLMModelRead,
    AgentConfigUpdate
)

router = APIRouter()
agent_service = AgentService()


@router.get("/models", response_model=List[LLMModelRead], tags=["Models"])
@limiter.limit("30 per hour")
def list_llm_models(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all available LLM models."""
    return agent_service.get_active_models(db)


@router.post("/agents", response_model=AgentConfigRead, status_code=status.HTTP_201_CREATED, tags=["Agents"])
@limiter.limit("30 per hour")
def create_agent_config(
    request: Request,
    config_in: AgentConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new custom agent configuration."""
    try:
        return agent_service.import_user_model_config(db, current_user.id, config_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating agent config")


@router.get("/agents", response_model=List[AgentConfigRead], tags=["Agents"])
@limiter.limit("30 per hour")
def list_user_agents(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all agent configurations for current user."""
    return get_user_agents(db, current_user.id)


@router.get("/agents/{agent_id}", response_model=AgentConfigRead, tags=["Agents"])
@limiter.limit("60 per hour")
def get_agent(
    request: Request,
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific agent configuration."""
    agent = get_agent_config(db, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    if agent.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return agent


@router.patch("/agents/{agent_id}", response_model=AgentConfigRead, tags=["Agents"])
@limiter.limit("30 per hour")
def update_agent(
    request: Request,
    agent_id: str,
    config_update: AgentConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an agent configuration."""
    agent = get_agent_config(db, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    if agent.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    try:
        update_data = config_update.model_dump(exclude_unset=True)
        from app.crud.agents_crud import update_agent_config
        return update_agent_config(db, agent_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Agents"])
@limiter.limit("30 per hour")
def delete_agent(
    request: Request,
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an agent configuration."""
    agent = get_agent_config(db, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    if agent.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    from app.crud.agents_crud import delete_agent_config
    delete_agent_config(db, agent_id)