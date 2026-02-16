"""
User account and statistics models.
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, Integer, ForeignKey, TypeDecorator, BigInteger
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


class User(Base):
    """User account with profile information."""
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    avatar_url = Column(Text)
    bio = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    stats = relationship("UserStats", back_populates="user", uselist=False, cascade="all, delete-orphan")
    configs = relationship("AgentConfig", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("ForumPost", back_populates="author", cascade="all, delete-orphan")


class UserStats(Base):
    """User battle statistics and rankings."""
    __tablename__ = "user_stats"

    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    matches_played = Column(Integer, default=0)
    total_hacks = Column(Integer, default=0)
    rank_points = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="stats")

    @property
    def username(self):
        """Proxy username from user relationship."""
        return self.user.username if self.user else "Unknown"
