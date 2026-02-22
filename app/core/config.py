"""
Application configuration loaded from environment variables.
Uses pydantic-settings for type-safe, validated settings management.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "AI Mental Health Assistant"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "A production-ready AI-powered mental health support chatbot backend."
    )
    DEBUG: bool = False
    ALLOWED_HOSTS: List[str] = ["*"]

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:123@localhost:6001/mental_health_db"
    DATABASE_ECHO: bool = False

    # ── JWT ───────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_use_a_long_random_string_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── OpenAI ────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = "sk-your-openai-api-key"
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 1024
    OPENAI_TEMPERATURE: float = 0.7

    # ── Crisis Detection ──────────────────────────────────────────────────────
    CRISIS_HOTLINE: str = "988 (Suicide & Crisis Lifeline)"
    CRISIS_EMERGENCY_NUMBER: str = "911"

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True}


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance (singleton via lru_cache)."""
    return Settings()


settings = get_settings()
