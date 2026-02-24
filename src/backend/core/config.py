"""
Application configuration using pydantic-settings.
Loads environment variables from .env files.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Compute base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=[".env", "../../.env"], env_file_encoding="utf-8", extra="ignore"
    )

    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database settings
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR}/app.db"

    # CORS settings
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:4173"

    # Environment
    ENVIRONMENT: str = "development"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
