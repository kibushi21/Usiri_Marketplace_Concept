from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="USIRI_", env_file=".env", extra="ignore")

    app_name: str = "Usiri Marketplace API"
    environment: str = "development"
    database_url: str = f"sqlite:///{BASE_DIR / 'var' / 'usiri.db'}"
    jwt_secret: str = "dev-only-secret-change-me-before-anything-real"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 12
    cors_origins: str = "http://localhost:3000"

    psp_provider: str = "mock"
    psp_webhook_secret: str = "mock-webhook-secret"
    psp_public_key: str = "mock-public-key"
    psp_callback_base: str = "http://localhost:8000"

    carrier_provider: str = "mock"
    carrier_mode: str = "manual"

    llm_provider: str = "mock"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 30.0
    llm_max_tokens: int = 400

    storage_dir: Path = BASE_DIR / "var" / "uploads"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.environment == "production" and settings.jwt_secret == "dev-only-secret-change-me-before-anything-real":
        raise RuntimeError("USIRI_JWT_SECRET must be set in production")
    return settings


def reset_settings_cache() -> None:
    get_settings.cache_clear()


os.makedirs(BASE_DIR / "var", exist_ok=True)
