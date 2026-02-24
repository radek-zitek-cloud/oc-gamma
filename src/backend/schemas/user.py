"""
Pydantic schemas for user-related request/response validation.
Strictly separate from SQLAlchemy models.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# Theme preference type
ThemePreference = Literal["light", "dark", "system"]


class UserBase(BaseModel):
    """Base user fields shared across schemas."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str | None = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8, max_length=255)


class UserUpdate(BaseModel):
    """Schema for user profile updates."""

    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=255)

    model_config = ConfigDict(extra="ignore")


class ThemePreferenceUpdate(BaseModel):
    """Schema for updating theme preference."""

    theme_preference: ThemePreference


class UserResponse(UserBase):
    """Schema for user API responses (excludes sensitive data)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    role: str
    theme_preference: ThemePreference
    created_at: str
    updated_at: str

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def convert_datetime_to_str(cls, v):
        """Convert datetime to ISO string format."""
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class UserInDB(UserBase):
    """Schema for internal use (includes hashed password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    role: str
    theme_preference: ThemePreference
    created_at: str
    updated_at: str

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def convert_datetime_to_str(cls, v):
        """Convert datetime to ISO string format."""
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class PasswordChange(BaseModel):
    """Schema for password change requests with confirmation."""

    model_config = ConfigDict(extra="ignore")

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=255)
    confirm_password: str = Field(..., min_length=8, max_length=255)

    @field_validator("confirm_password", mode="after")
    @classmethod
    def check_passwords_match(cls, v: str, info) -> str:
        """Validate that confirm_password matches new_password."""
        # Access other fields from validation context
        data = info.data
        if "new_password" in data and v != data["new_password"]:
            raise ValueError("Passwords do not match")
        return v
