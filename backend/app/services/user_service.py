"""
Service layer for user management and authentication.
"""
import logging
from app.core.security import hash_password, verify_password
from app.crud.user_crud import (
    create_user, 
    get_user, 
    get_user_by_email,
    get_user_by_username
)
from app.models.user import UserStats

logger = logging.getLogger(__name__)


class UserService:
    """Service for user registration, authentication, and profile management."""

    def __init__(self, db):
        self.db = db

    def register_user(self, user_in):
        """
        Register a new user with hashed password.
        
        Args:
            user_in: UserCreate DTO with username, email, and password
        
        Returns:
            User object (password hash not included in response)
        """
        # Hash password before storing
        hashed_pw = hash_password(user_in.password)
        user_in.password = hashed_pw
        return create_user(self.db, user_in)

    def authenticate_user(self, username: str, password: str):
        """
        Authenticate user by username and password.
        
        Args:
            username: Username to validate
            password: Plain text password to verify
        
        Returns:
            User object if credentials valid, None otherwise
        """
        user = get_user_by_username(self.db, username)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user

    def get_user_by_email(self, email: str):
        """Get user by email address."""
        return get_user_by_email(self.db, email)

    def get_user_by_username(self, username: str):
        """Get user by username."""
        return get_user_by_username(self.db, username)

    def update_rankings(self, winner_id, loser_id):
        """
        Update ELO-style rankings after a battle.
        
        Awards rank points to winner and updates stats.
        """
        winner_stats = self.db.query(UserStats).filter(UserStats.user_id == winner_id).first()
        
        if winner_stats:
            winner_stats.wins += 1
            winner_stats.rank_points += 20  # Could be dynamic based on difficulty
            winner_stats.matches_played += 1
            self.db.commit()
            logger.info(f"Updated rankings for winner {winner_id}: +20 points")

    def get_user_leaderboard(self, limit: int = 10):
        """Get top users by rank points."""
        from app.crud.user_crud import get_leaderboard
        return get_leaderboard(self.db, limit)
