"""
CRUD operations for community forum management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.community import ForumPost, ForumComment, MatchMessage
from app.dto.community_dto import PostCreate
from uuid import UUID


def create_post(db: Session, post_in: PostCreate, author_id: UUID):
    """Create a new forum post."""
    db_post = ForumPost(**post_in.model_dump(), author_id=author_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_post_by_id(db: Session, post_id):
    """Get a specific post by ID."""
    try:
        post_uuid = UUID(post_id) if isinstance(post_id, str) else post_id
    except ValueError:
        return None
    return db.query(ForumPost).filter(ForumPost.id == post_uuid).first()


def get_posts(db: Session, category: str = None, skip: int = 0, limit: int = 20):
    """Get posts with optional category filter and pagination."""
    query = db.query(ForumPost).order_by(desc(ForumPost.created_at))
    
    if category:
        query = query.filter(ForumPost.category == category)
    
    return query.offset(skip).limit(limit).all()


def get_posts_by_category(db: Session, category: str):
    """Get all posts in a category."""
    return db.query(ForumPost).filter(ForumPost.category == category).all()


def update_post(db: Session, post_id, post_data):
    """Update a post."""
    post = get_post_by_id(db, post_id)
    if not post:
        return None
    
    for key, value in post_data.model_dump(exclude_unset=True).items():
        setattr(post, key, value)
    
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id):
    """Delete a post."""
    post = get_post_by_id(db, post_id)
    if post:
        db.delete(post)
        db.commit()
        return True
    return False


def create_comment(db: Session, post_id: UUID, author_id: UUID, comment_in):
    """Create a comment on a post."""
    db_comment = ForumComment(
        post_id=post_id,
        author_id=author_id,
        content=comment_in.content,
        parent_id=comment_in.parent_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_post_comments(db: Session, post_id: UUID):
    """Get all comments on a post."""
    return db.query(ForumComment).filter(ForumComment.post_id == post_id).order_by(ForumComment.created_at).all()


def create_match_message(db: Session, match_id: UUID, user_id: UUID, content: str):
    """Create a message during a match (for communication between players)."""
    msg = MatchMessage(match_id=match_id, user_id=user_id, content=content)
    db.add(msg)
    db.commit()
    return msg


def get_match_messages(db: Session, match_id: UUID):
    """Get all messages from a match."""
    return db.query(MatchMessage).filter(MatchMessage.match_id == match_id).order_by(MatchMessage.created_at).all()
