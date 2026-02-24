"""
Application configuration using pydantic-settings.
Loads environment variables from .env files.
"""

import logging
import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Compute base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Setup basic logging for config (add handler to ensure logs are visible)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Add a handler if none exist to ensure config logs are visible
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger.addHandler(handler)


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

# Log configuration values (excluding sensitive data like SECRET_KEY)
logger.info(
    f"Configuration loaded: ENVIRONMENT={settings.ENVIRONMENT}, "
    f"ALGORITHM={settings.ALGORITHM}, "
    f"ACCESS_TOKEN_EXPIRE_MINUTES={settings.ACCESS_TOKEN_EXPIRE_MINUTES}, "
    f"DATABASE_URL={settings.DATABASE_URL}, "
    f"CORS_ORIGINS={settings.CORS_ORIGINS}, "
    f"DATA_DIR={DATA_DIR}"
)
