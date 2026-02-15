from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class MatchCreate(BaseModel):
    agent_config_ids: List[UUID] # The agents the user wants to put in the arena

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