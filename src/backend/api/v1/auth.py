"""
Authentication API endpoints.
"""

import time
from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.repositories.user import UserRepository
from backend.schemas.auth import LoginRequest, Token
from backend.schemas.user import (
    PasswordChange,
    ThemePreferenceUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from backend.services.auth_service import authenticate_user, register_user
from backend.api.deps import get_current_user, get_db, get_user_repo

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

# Cookie settings
COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 1800  # 30 minutes

# Simple in-memory rate limiter
# Format: {key: [(timestamp1), (timestamp2), ...]}
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


def _get_client_ip(request: Request) -> str:
    """Get client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
    """
    Check if request is within rate limit.
    
    Args:
        key: Rate limit key (typically IP address).
        max_requests: Maximum number of requests allowed in the window.
        window_seconds: Time window in seconds.
    
    Returns:
        True if rate limit is exceeded, False otherwise.
    """
    now = time.time()
    window_start = now - window_seconds
    
    # Clean old entries and count recent ones
    requests = _rate_limit_store[key]
    recent_requests = [t for t in requests if t > window_start]
    _rate_limit_store[key] = recent_requests
    
    if len(recent_requests) >= max_requests:
        return True
    
    # Add current request
    recent_requests.append(now)
    return False


def check_rate_limit(request: Request, max_requests: int = 5, window_seconds: int = 60, endpoint: str = None) -> None:
    """
    Check and enforce rate limit for the request.
    
    Args:
        request: FastAPI request object.
        max_requests: Maximum number of requests allowed in the window.
        window_seconds: Time window in seconds.
        endpoint: Optional endpoint identifier for endpoint-specific rate limiting.
    
    Raises:
        HTTPException: If rate limit is exceeded.
    """
    ip = _get_client_ip(request)
    # Use endpoint-specific key if provided, otherwise use IP only
    key = f"{ip}:{endpoint}" if endpoint else ip
    
    if _check_rate_limit(key, max_requests, window_seconds):
        logger.warning(f"Rate limit exceeded for IP: {ip} on endpoint: {endpoint or 'global'}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    request: Request,
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    Register a new user account.

    Args:
        request: FastAPI request object (for rate limiting).
        user_data: User registration data.
        db: Database session.

    Returns:
        The created user (without password).

    Raises:
        HTTPException: If email or username already exists.
    """
    # Check rate limit (3 requests per minute for registration)
    check_rate_limit(request, max_requests=3, window_seconds=60)
    
    try:
        user = await register_user(db, user_data)
        logger.info(f"User registered: {user.username}", {"user_id": user.id})
        return UserResponse.model_validate(user)
    except ValueError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login and get access token",
)
async def login(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    Login with username and password.

    Args:
        request: FastAPI request object (required by rate limiter).
        response: FastAPI response object for setting cookies.
        form_data: OAuth2 form with username and password.
        db: Database session.

    Returns:
        Token response and sets HttpOnly cookie.

    Raises:
        HTTPException: If credentials are invalid.
    """
    # Check rate limit (5 requests per minute)
    check_rate_limit(request, max_requests=5, window_seconds=60)
    
    user = await authenticate_user(db, form_data.username, form_data.password)

    if not user:
        logger.warning(f"Login failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Set HttpOnly cookie
    response.set_cookie(
        key=COOKIE_NAME,
        value=access_token,
        httponly=True,
        max_age=COOKIE_MAX_AGE,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
    )

    logger.info(f"User logged in: {user.username}", {"user_id": user.id})
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout and clear session",
)
async def logout(response: Response) -> dict:
    """
    Logout the current user.

    Args:
        response: FastAPI response object for clearing cookies.

    Returns:
        Success message.
    """
    response.delete_cookie(key=COOKIE_NAME)
    logger.info("User logged out")
    return {"message": "Logged out successfully"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_me(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
    """
    Get the current authenticated user's profile.

    Args:
        current_user: The authenticated user from dependency.

    Returns:
        The user's profile information.
    """
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
async def update_me(
    user_update: UserUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserResponse:
    """
    Update the current user's profile.

    Args:
        user_update: The fields to update.
        current_user: The authenticated user.
        repo: User repository.

    Returns:
        The updated user profile.
    """
    # Filter out None values
    update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}

    if update_data:
        updated = await repo.update_user(current_user, update_data)
        logger.info(
            f"User profile updated: {updated.username}", {"user_id": updated.id}
        )
        return UserResponse.model_validate(updated)

    return UserResponse.model_validate(current_user)


@router.put(
    "/me/password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
)
async def change_password(
    password_data: PasswordChange,
    request: Request,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> dict:
    """
    Change the current user's password.

    Args:
        password_data: Current and new password.
        request: The HTTP request for rate limiting.
        current_user: The authenticated user.
        repo: User repository.

    Returns:
        Success message.

    Raises:
        HTTPException: If current password is incorrect or rate limit exceeded.
    """
    # Check rate limit: 3 attempts per minute per IP for password change endpoint
    check_rate_limit(request, max_requests=3, window_seconds=60, endpoint="password_change")

    # Verify current password
    if not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        logger.warning(
            f"Password change failed: incorrect current password",
            {"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    # Hash and update new password
    new_hashed = hash_password(password_data.new_password)
    await repo.change_password(current_user, new_hashed)

    logger.info(
        f"Password changed for user: {current_user.username}",
        {"user_id": current_user.id},
    )
    return {"message": "Password changed successfully"}


@router.patch(
    "/me/theme",
    response_model=UserResponse,
    summary="Update theme preference",
)
async def update_theme_preference(
    request: Request,
    theme_data: ThemePreferenceUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserResponse:
    """
    Update the current user's theme preference.

    Args:
        request: FastAPI request object (for rate limiting).
        theme_data: The theme preference to set (light, dark, or system).
        current_user: The authenticated user.
        repo: User repository.

    Returns:
        The updated user profile.
    """
    # Check rate limit (10 requests per minute for theme updates)
    check_rate_limit(request, max_requests=10, window_seconds=60)

    updated = await repo.update_user(
        current_user, {"theme_preference": theme_data.theme_preference}
    )
    logger.info(
        f"Theme preference updated: {theme_data.theme_preference}",
        {"user_id": updated.id}
    )
    return UserResponse.model_validate(updated)
