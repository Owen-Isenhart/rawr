"""
Rate limiting configuration and middleware for API endpoints.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Rate limit configuration by endpoint type
RATE_LIMITS = {
    "auth": "5 per minute",           # Strict for auth attempts
    "battle": "10 per hour",           # Battles are long operations
    "agents": "30 per hour",           # Agent management
    "community": "100 per hour",       # Community posts/comments
    "leaderboard": "30 per minute",    # Leaderboard reads
    "default": "100 per hour",         # Default rate limit
}


async def rate_limit_error_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom rate limit error handler.
    
    Returns JSON response with rate limit information.
    """
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded",
            "message": exc.detail,
            "retry_after": exc.headers.get("retry-after", "Unknown")
        },
        headers=exc.headers
    )
