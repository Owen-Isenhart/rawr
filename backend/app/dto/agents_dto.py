"""
Data Transfer Objects for agent and model configuration endpoints.
"""
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional
from decimal import Decimal


class LLMModelCreate(BaseModel):
    """Schema for creating a new LLM model record."""
    ollama_tag: str = Field(..., description="Ollama model tag (e.g., 'dolphin-llama3')")
    description: Optional[str] = None
    size_bytes: Optional[int] = None


class LLMModelRead(BaseModel):
    """Schema for reading LLM model information."""
    id: UUID
    ollama_tag: str
    description: Optional[str]
    size_bytes: Optional[int]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class AgentConfigCreate(BaseModel):
    """Schema for creating a new agent configuration."""
    base_model_id: UUID = Field(..., description="ID of the base LLM model")
    name: str = Field(..., min_length=1, max_length=100)
    system_prompt: str = Field(..., min_length=10, description="Custom system instructions")
    temperature: Decimal = Field(default=0.7, ge=0.0, le=2.0)


class AgentConfigRead(BaseModel):
    """Schema for reading agent configuration."""
    id: UUID
    user_id: UUID
    base_model_id: Optional[UUID]
    name: str
    system_prompt: str
    temperature: Decimal

    model_config = ConfigDict(from_attributes=True)


class AgentConfigUpdate(BaseModel):
    """Schema for updating agent configuration."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    system_prompt: Optional[str] = Field(None, min_length=10)
    temperature: Optional[Decimal] = Field(None, ge=0.0, le=2.0)
