from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class PostCreate(BaseModel):
    title: str
    content: str
    category: str

class PostRead(BaseModel):
    id: UUID
    author_id: UUID
    title: str
    content: str
    category: str
    likes_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CommentCreate(BaseModel):
    post_id: UUID
    content: str
    parent_id: Optional[UUID] = None

class MessageRead(BaseModel):
    id: int
    match_id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)