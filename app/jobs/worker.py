import asyncio
from decimal import Decimal

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.jobs.pipeline import (
    compute_factors_job,
    compute_signals_job,
    emit_alerts_job,
    ingest_binance_market_job,
    ingest_bybit_derivatives_job,
    ingest_defillama_macro_job,
    ingest_onchain_flow_job,
)
from app.repositories.asset_repository import AssetRepository
from app.repositories.snapshot_repository import SnapshotRepository


async def run_once() -> None:
    settings = get_settings()
    weights_cfg = settings.load_yaml("factor_weights.yaml").get("weights", {})
    thresholds_cfg = settings.load_yaml("score_thresholds.yaml").get("thresholds", {})
    weights = {k: Decimal(str(v)) for k, v in weights_cfg.items()}
    thresholds = {k: Decimal(str(v)) for k, v in thresholds_cfg.items()}

    async with SessionLocal() as session:
        assets = await AssetRepository(session).list_assets()
        repo = SnapshotRepository(session)
        for asset in assets:
            symbol = asset.symbol
            await ingest_binance_market_job(symbol, repo)
            await ingest_bybit_derivatives_job(symbol, repo)
            await ingest_onchain_flow_job(symbol, repo)
            await ingest_defillama_macro_job(symbol, repo)
            await compute_factors_job(symbol, repo)
            await compute_signals_job(symbol, repo, weights, thresholds)
            await emit_alerts_job(symbol, repo)


if __name__ == "__main__":
    asyncio.run(run_once())
