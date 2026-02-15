"""
Battle/Match models for arena combat tracking.
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, Integer, ForeignKey, TypeDecorator, Boolean, BigInteger
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


class Match(Base):
    """Represents a single hacking battle session."""
    __tablename__ = "matches"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    creator_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, ongoing, completed
    winner_id = Column(GUID, ForeignKey("users.id"), nullable=True)
    start_time = Column(TIMESTAMP(timezone=True))
    end_time = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    participants = relationship("MatchParticipant", back_populates="match", cascade="all, delete-orphan")
    messages = relationship("MatchMessage", back_populates="match", cascade="all, delete-orphan")


class MatchParticipant(Base):
    """Agent participating in a match."""
    __tablename__ = "match_participants"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    match_id = Column(GUID, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    agent_config_id = Column(GUID, ForeignKey("agent_configs.id"), nullable=False)
    container_id = Column(String(100), nullable=False)
    internal_ip = Column(String(45), nullable=False)
    is_alive = Column(Boolean, default=True)
    eliminated_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="participants")
    action_logs = relationship("ActionLog", back_populates="participant", cascade="all, delete-orphan")


class ActionLog(Base):
    """Log of actions (commands) performed by agents."""
    __tablename__ = "action_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    participant_id = Column(GUID, ForeignKey("match_participants.id", ondelete="CASCADE"), nullable=False)
    command = Column(Text, nullable=False)
    output = Column(Text)
    was_successful = Column(Boolean)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    participant = relationship("MatchParticipant", back_populates="action_logs")
