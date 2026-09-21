"""
Central application configuration.
Loaded once from environment variables / .env file.
"""
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # mock changes only the video source. Analysis always uses Gemini.
    APP_MODE: Literal["live", "mock"] = "live"

    YOUTUBE_API_KEY: str = ""

    DATABASE_URL: str = "sqlite:///./sports_gemini.db"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = Field("gemini-3.5-flash-lite", pattern=r"^[a-zA-Z0-9._-]+$")
    GEMINI_TIMEOUT_SECONDS: int = Field(90, ge=1, le=120)
    MAX_COMMENTS_PER_ANALYSIS: int = Field(100, ge=1, le=100)
    CACHE_TTL_SECONDS: int = 1800


settings = Settings()
