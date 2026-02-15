"""
Community forum models for discussions and messages.
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


class ForumPost(Base):
    """Forum post for sharing strategies and agent designs."""
    __tablename__ = "forum_posts"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    author_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50))  # strategy, showcase, question, general
    likes_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    author = relationship("User", back_populates="posts")
    comments = relationship("ForumComment", back_populates="post", cascade="all, delete-orphan")


class ForumComment(Base):
    """Comment on a forum post."""
    __tablename__ = "forum_comments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    post_id = Column(GUID, ForeignKey("forum_posts.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(GUID, ForeignKey("forum_comments.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    post = relationship("ForumPost", back_populates="comments")


class MatchMessage(Base):
    """Messages sent during a match between participants."""
    __tablename__ = "match_messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    match_id = Column(GUID, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="messages")
