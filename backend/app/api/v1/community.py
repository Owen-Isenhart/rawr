"""
Community forum endpoints for discussion and strategy sharing.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.api.v1.deps import get_current_user
from app.services.community_service import CommunityService
from app.models.user import User
from app.dto.community_dto import PostCreate, PostRead, CommentCreate
from app.dto.user_dto import LeaderboardEntry
from app.crud.community_crud import (
    get_posts_by_category,
    get_post_by_id
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/posts", response_model=PostRead, status_code=status.HTTP_201_CREATED, tags=["Community"])
@limiter.limit("20 per hour")
def create_post(
    request: Request,
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new forum post about strategies or agent designs.
    
    Content is sanitized to prevent XSS attacks.
    """
    try:
        service = CommunityService(db)
        return service.create_new_discussion(current_user.id, post_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create post: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating post")


@router.get("/posts", response_model=List[PostRead], tags=["Community"])
@limiter.limit("60 per hour")
def list_posts(
    request: Request,
    category: str = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    List forum posts with optional category filter.
    
    Parameters:
    - category: Filter by category (strategy, showcase, question, general)
    - skip: Pagination offset
    - limit: Number of posts to return (max 100)
    """
    if limit > 100:
        limit = 100
    
    from app.crud.community_crud import get_posts
    return get_posts(db, category=category, skip=skip, limit=limit)


@router.get("/posts/{post_id}", response_model=PostRead, tags=["Community"])
@limiter.limit("60 per hour")
def get_post(
    request: Request,
    post_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific post with comments."""
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.patch("/posts/{post_id}", response_model=PostRead, tags=["Community"])
@limiter.limit("20 per hour")
def update_post(
    request: Request,
    post_id: str,
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a post (author only).
    """
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Security: Only author can update
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    try:
        from app.crud.community_crud import update_post as crud_update_post
        return crud_update_post(db, post_id, post_in)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating post")


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Community"])
@limiter.limit("20 per hour")
def delete_post(
    request: Request,
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a post (author only)."""
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Security: Only author can delete
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    from app.crud.community_crud import delete_post as crud_delete_post
    crud_delete_post(db, post_id)


@router.post("/posts/{post_id}/like", tags=["Community"])
@limiter.limit("60 per hour")
def like_post(
    request: Request,
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Like a post (increment likes counter)."""
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    service = CommunityService(db)
    return service.like_post(post_id)


@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED, tags=["Community"])
@limiter.limit("30 per hour")
def create_comment(
    request: Request,
    post_id: str,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a comment on a post."""
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    try:
        service = CommunityService(db)
        return service.create_comment(current_user.id, post_id, comment_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/leaderboard", response_model=List[LeaderboardEntry], tags=["Community"])
@limiter.limit("30 per minute")
def get_leaderboard(
    request: Request,
    limit: int = 10,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    """Get the global leaderboard of top players."""
    from app.crud.user_crud import get_leaderboard
    return get_leaderboard(db, limit=limit)
