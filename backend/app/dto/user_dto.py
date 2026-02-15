"""
Pydantic schemas for user-related endpoints.
"""
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user information."""
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """User registration schema."""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserRead(UserBase):
    """User profile read schema."""
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserStatsRead(BaseModel):
    """User statistics and rankings."""
    wins: int
    losses: int
    matches_played: int
    total_hacks: int
    rank_points: int

    model_config = ConfigDict(from_attributes=True)
