from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "crypto_decision_engine"
    env: str = "dev"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/crypto_engine"
    redis_url: str = "redis://redis:6379/0"

    provider_timeout_seconds: float = 10.0
    provider_retries: int = 3
    provider_rate_limit_per_second: float = 5.0

    config_dir: Path = Path("configs")

    def load_yaml(self, name: str) -> dict[str, Any]:
        with open(self.config_dir / name, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
