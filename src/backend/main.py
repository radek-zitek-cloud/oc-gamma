"""
Main application entry point for the FastAPI backend.
"""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.api import api_router
from backend.core.config import settings
from backend.core.database import init_db
from backend.core.logging import get_logger

logger = get_logger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting up...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="OC Gamma API",
    description="Full-stack application backend",
    version="0.1.1",
    lifespan=lifespan,
)

# Add rate limiter to app state
app.state.limiter = limiter

# Rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    logger.warning(f"Rate limit exceeded: {request.client.host if request.client else 'unknown'}")
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )

# Correlation ID middleware
@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    """Add correlation ID to request and response for tracing."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    
    # Store in request state for access in route handlers
    request.state.correlation_id = correlation_id
    
    # Process request
    response = await call_next(request)
    
    # Add correlation ID to response headers
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.1"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to OC Gamma API", "version": "0.1.1"}
