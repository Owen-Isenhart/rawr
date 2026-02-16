"""
Main FastAPI application entry point for the AI Battle Arena.

Orchestrates:
- User authentication and authorization
- Agent model management
- Arena battle orchestration
- Community forum
"""
import os
import logging
import uvicorn
from sqlalchemy import text
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded

# Import routers
from app.api.v1 import auth, models, battle, community
from app.core.database import engine
from app.core.rate_limiter import limiter, rate_limit_error_handler
from app.models.base import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- DATABASE INITIALIZATION ---
def init_db():
    """
    Create all database tables defined in models.
    
    In production with migrations, use Alembic instead.
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Startup: Initialize database
    Shutdown: Cleanup resources
    """
    # Startup
    init_db()
    logger.info("=== [ARENA] Database initialized and connected ===")
    yield
    # Shutdown
    logger.info("=== [ARENA] Shutting down systems ===")


# --- APP INITIALIZATION ---
app = FastAPI(
    title="AI Battle Arena API",
    description="Backend orchestrator for autonomous AI hacking simulations in isolated Docker containers.",
    version="1.0.0",
    lifespan=lifespan
)

# --- RATE LIMITING ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_error_handler)

# --- MIDDLEWARE ---
# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


# --- EXCEPTION HANDLERS ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors gracefully."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# --- ROUTER REGISTRATION ---
# Modularize routes by domain
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    models.router,
    prefix="/api/v1/agents",
    tags=["Agent Management"]
)

app.include_router(
    battle.router,
    prefix="/api/v1/battles",
    tags=["Battle Arena"]
)

app.include_router(
    community.router,
    prefix="/api/v1/community",
    tags=["Community Forum"]
)

# --- HEALTH CHECKS ---
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with service information."""
    return {
        "status": "online",
        "service": "AI Battle Arena",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        from app.core.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "version": "1.0.0"
    }