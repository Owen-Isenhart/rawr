from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class AgentSelection(BaseModel):
    """Matches the frontend '{ agent_id: string }' structure."""
    agent_id: UUID

class MatchCreate(BaseModel):
    """Aligned with frontend BattleRequest."""
    player_agents: List[AgentSelection]
    opponent_agents: List[AgentSelection]

class MatchRead(BaseModel):
    id: UUID
    status: str
    creator_id: UUID
    winner_id: Optional[UUID]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class ActionLogRead(BaseModel):
    id: int
    participant_id: UUID
    command: str
    output: Optional[str]
    was_successful: Optional[bool]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)