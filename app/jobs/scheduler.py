from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.jobs.pipeline import (
    compute_factors_job,
    compute_signals_job,
    emit_alerts_job,
    ingest_binance_market_job,
    ingest_bybit_derivatives_job,
    ingest_cex_flow_job,
    ingest_coingecko_liquidity_job,
    ingest_defillama_macro_job,
    ingest_onchain_flow_job,
)
from app.repositories.asset_repository import AssetRepository
from app.repositories.snapshot_repository import SnapshotRepository

logger = logging.getLogger(__name__)


async def _run_for_assets(handler_name: str) -> None:
    handlers = {
        "market": ingest_binance_market_job,
        "cex_flow": ingest_cex_flow_job,
        "derivatives": ingest_bybit_derivatives_job,
        "onchain": ingest_onchain_flow_job,
        "liquidity": ingest_coingecko_liquidity_job,
        "macro": ingest_defillama_macro_job,
        "factors": compute_factors_job,
        "signals": compute_signals_job,
        "alerts": emit_alerts_job,
    }
    handler = handlers[handler_name]
    async with SessionLocal() as session:
        assets = [a.__dict__ for a in await AssetRepository(session).list_assets()]
        repo = SnapshotRepository(session)
        for asset in assets:
            try:
                await handler(asset, repo)
            except Exception:
                logger.exception("job %s failed for %s", handler_name, asset.get("symbol"))


def build_scheduler() -> AsyncIOScheduler:
    cfg = get_settings().load_yaml("scheduler.yaml")
    scheduler = AsyncIOScheduler(timezone=get_settings().scheduler_timezone)
    for name, seconds in cfg.get("interval_seconds", {}).items():
        scheduler.add_job(_run_for_assets, "interval", seconds=int(seconds), args=[name], id=f"job_{name}", replace_existing=True)
    return scheduler
