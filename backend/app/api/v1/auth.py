"""
Authentication endpoints for user registration and login.
"""
import re
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.rate_limiter import limiter
from app.services.user_service import UserService
from app.dto.user_dto import UserCreate, UserRead

logger = logging.getLogger(__name__)

router = APIRouter()

# Password validation rules
PASSWORD_MIN_LENGTH = 8
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d!@#$%^&*()_+\-=\[\]{};:,.<>?]{8,}$")


def validate_password(password: str) -> bool:
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    return bool(PASSWORD_REGEX.match(password))


def validate_email(email: str) -> bool:
    """Basic email validation."""
    email_regex = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    return bool(email_regex.match(email))


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
@limiter.limit("5 per minute")
def register(
    request,
    user_in: UserCreate, 
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Password requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    # Validate email format
    if not validate_email(user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Validate password strength
    if not validate_password(user_in.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, and number"
        )
    
    user_service = UserService(db)
    
    # Check if email already exists
    if user_service.get_user_by_email(user_in.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists"
        )
    
    # Check if username already exists
    if user_service.get_user_by_username(user_in.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is already taken"
        )
    
    try:
        return user_service.register_user(user_in)
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user account"
        )


@router.post("/login", tags=["Authentication"])
@limiter.limit("5 per minute")
def login(
    request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Login with username and password.
    
    Returns JWT access token for subsequent authenticated requests.
    """
    user_service = UserService(db)
    user = user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        # Don't reveal whether username or password was wrong (security best practice)
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create access token with custom expiration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email
        }
    }
