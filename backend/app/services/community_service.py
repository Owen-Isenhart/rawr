"""
Service for community forum management and content moderation.
"""
import logging
import html
from app.crud.community_crud import (
    create_post, 
    create_comment,
    get_post_by_id
)
from app.models.community import ForumPost

logger = logging.getLogger(__name__)

# Very basic XSS prevention - in production use a library like bleach
DANGEROUS_TAGS = ["<script", "<iframe", "<object", "<embed", "javascript:", "on", "style="]


def sanitize_content(content: str) -> str:
    """
    Basic sanitization to prevent XSS attacks.
    
    This is a simple implementation - in production use bleach or similar.
    """
    # HTML escape special characters
    content = html.escape(content)
    
    # Check for suspicious patterns
    content_lower = content.lower()
    for tag in DANGEROUS_TAGS:
        if tag in content_lower:
            logger.warning(f"Suspicious content detected: {tag}")
            raise ValueError("Content contains invalid characters or tags")
    
    return content


class CommunityService:
    """Service for managing community posts, comments, and discussions."""

    def __init__(self, db):
        self.db = db

    def create_new_discussion(self, user_id, post_in):
        """
        Create a new forum post.
        
        - Sanitizes content for XSS
        - Validates post content
        - Could award points for participation  
        """
        # Validate content
        if not post_in.title or len(post_in.title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        if not post_in.content or len(post_in.content.strip()) < 10:
            raise ValueError("Content must be at least 10 characters")
        
        if len(post_in.title) > 255:
            raise ValueError("Title too long (max 255 chars)")
        
        if len(post_in.content) > 10000:
            raise ValueError("Content too long (max 10000 chars)")
        
        # Sanitize content
        try:
            sanitized_title = sanitize_content(post_in.title)
            sanitized_content = sanitize_content(post_in.content)
        except ValueError as e:
            logger.warning(f"Content sanitization failed for user {user_id}: {e}")
            raise
        
        # Create post with sanitized content
        safe_post = post_in.model_copy()
        safe_post.title = sanitized_title
        safe_post.content = sanitized_content
        
        return create_post(self.db, safe_post, user_id)

    def create_comment(self, user_id, post_id, comment_in):
        """
        Create a comment on a post.
        
        - Sanitizes comment content
        - Validates content
        """
        if not comment_in.content or len(comment_in.content.strip()) < 3:
            raise ValueError("Comment must be at least 3 characters")
        
        if len(comment_in.content) > 5000:
            raise ValueError("Comment too long (max 5000 chars)")
        
        # Sanitize content
        try:
            sanitized_content = sanitize_content(comment_in.content)
        except ValueError as e:
            raise
        
        # Update comment with sanitized content
        safe_comment = comment_in.model_copy()
        safe_comment.content = sanitized_content
        
        return create_comment(self.db, post_id, user_id, safe_comment)

    def like_post(self, post_id: str):
        """
        Increment likes on a post.
        
        Could be enhanced to prevent duplicate likes per user.
        """
        post = get_post_by_id(self.db, post_id)
        if post:
            post.likes_count += 1
            self.db.commit()
            logger.info(f"Post {post_id} liked: {post.likes_count} likes")
        return post

    def get_trending_posts(self, limit: int = 10):
        """Get most liked posts (trending)."""
        from sqlalchemy import desc
        return self.db.query(ForumPost).order_by(desc(ForumPost.likes_count)).limit(limit).all()

    def get_user_posts(self, user_id):
        """Get all posts by a user."""
        return self.db.query(ForumPost).filter(ForumPost.author_id == user_id).all()
