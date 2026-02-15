"""
CRUD operations for user management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.user import User, UserStats
from app.dto.user_dto import UserCreate
from uuid import UUID


def get_user(db: Session, user_id: UUID):
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """Get a user by email address."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user_in: UserCreate):
    """
    Create a new user account.
    
    Note: Password should already be hashed before calling this function.
    """
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=user_in.password  # Should be hashed by caller
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Initialize empty stats for the new user
    stats = UserStats(user_id=new_user.id)
    db.add(stats)
    db.commit()
    
    return new_user


def update_user(db: Session, user_id: UUID, user_data: dict):
    """Update user profile information."""
    user = get_user(db, user_id)
    if not user:
        return None
    
    for key, value in user_data.items():
        if value is not None and key != "password_hash":  # Don't update password via this method
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


def get_leaderboard(db: Session, limit: int = 10):
    """Get top users by rank points."""
    return db.query(UserStats).order_by(desc(UserStats.rank_points)).limit(limit).all()


def delete_user(db: Session, user_id: UUID):
    """Delete a user account and their stats."""
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
