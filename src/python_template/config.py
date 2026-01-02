"""Application configuration via environment variables.

All settings are loaded from environment variables using pydantic-settings.
See env.example for the full list of available variables.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file before validation
# __file__ = src/python_template/config.py -> parent.parent.parent = project root
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PYTHON_TEMPLATE_",
        extra="ignore",
    )

    # Runtime
    host: str = Field(default="127.0.0.1", description="API server host")
    port: int = Field(default=8000, description="API server port")

    # Logging
    log_level: Literal["debug", "info", "warning", "error", "critical"] = Field(
        default="info", description="Logging level"
    )
    log_format: Literal["json", "pretty"] = Field(
        default="json", description="Log output format"
    )

    # Debugger (for Docker dev)
    debugpy: bool = Field(default=False, description="Enable debugpy")
    debugpy_host: str = Field(default="0.0.0.0", description="Debugpy listen host")
    debugpy_port: int = Field(default=5678, description="Debugpy listen port")
    debugpy_wait: bool = Field(
        default=False, description="Wait for debugger to attach before starting"
    )


# Singleton settings instance
settings = Settings()
