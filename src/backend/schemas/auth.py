"""
Pydantic schemas for authentication-related request/response validation.
"""

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for decoded JWT payload."""

    sub: str | None = None  # User ID as string
    exp: int | None = None  # Expiration timestamp


class LoginRequest(BaseModel):
    """Schema for login credentials."""

    username: str
    password: str
