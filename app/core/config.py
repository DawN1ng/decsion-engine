from __future__ import annotations

from decimal import Decimal
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

    scheduler_enabled: bool = True
    scheduler_timezone: str = "UTC"

    config_dir: Path = Path("configs")
    onchain_manual_flows_path: Path = Path("configs/onchain_flows.json")

    def load_yaml(self, name: str) -> dict[str, Any]:
        with open(self.config_dir / name, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def factor_weights(self, category: str) -> dict[str, Decimal]:
        raw = self.load_yaml("factor_weights.yaml").get("weights", {})
        selected = raw.get(category, raw.get("midcap_alt", {}))
        return {k: Decimal(str(v)) for k, v in selected.items()}

    def score_thresholds(self, category: str) -> dict[str, Decimal]:
        raw = self.load_yaml("score_thresholds.yaml").get("thresholds", {})
        selected = raw.get(category, raw.get("midcap_alt", {}))
        return {k: Decimal(str(v)) for k, v in selected.items()}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
