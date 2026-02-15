"""
Agent configuration and LLM model definitions.
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, Integer, ForeignKey, TypeDecorator, Boolean, Numeric, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from .base import Base


# UUID type that works with SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type."""
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


class LLMModel(Base):
    """Represents a base language model available via Ollama."""
    __tablename__ = "llm_models"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    ollama_tag = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    size_bytes = Column(BigInteger)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    agent_configs = relationship("AgentConfig", back_populates="base_model")


class AgentConfig(Base):
    """User-customized agent configuration with system prompt and parameters."""
    __tablename__ = "agent_configs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"))
    base_model_id = Column(GUID, ForeignKey("llm_models.id", ondelete="SET NULL"))
    name = Column(String(100), nullable=False)
    system_prompt = Column(Text, nullable=False)
    temperature = Column(Numeric(3, 2), default=0.7)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="configs")
    base_model = relationship("LLMModel", back_populates="agent_configs")
