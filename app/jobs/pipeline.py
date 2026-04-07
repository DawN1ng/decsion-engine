from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.core.config import get_settings
from app.domain.models.entities import (
    CexFlowSnapshot,
    DerivativesSnapshot,
    FactorScore,
    LiquiditySnapshot,
    MarketSnapshot,
    OnchainFlow,
    Signal,
)
from app.domain.services.alert_engine import AlertEngine
from app.domain.services.factor_engine import FactorEngine, FactorInputs
from app.domain.services.scoring_engine import ScoringEngine
from app.domain.services.signal_engine import SignalEngine
from app.providers.binance.client import BinanceMarketClient, BinanceWalletClient
from app.providers.bybit.client import BybitMarketClient
from app.providers.coingecko.client import CoinGeckoOnchainClient
from app.providers.defillama.client import DefiLlamaClient
from app.providers.onchain.client import OnchainClusterFlowProvider
from app.repositories.snapshot_repository import SnapshotRepository

logger = logging.getLogger(__name__)


async def ingest_binance_market_job(asset: dict, repo: SnapshotRepository) -> None:
    logger.info("ingest_binance_market start %s", asset["symbol"])
    payload = await BinanceMarketClient().fetch(asset["symbol"], quote_currency=asset.get("quote_currency", "USDT"))
    snap = MarketSnapshot(ts=datetime.now(timezone.utc), **payload)
    await repo.insert(snap)


async def ingest_bybit_derivatives_job(asset: dict, repo: SnapshotRepository) -> None:
    logger.info("ingest_bybit_derivatives start %s", asset["symbol"])
    payload = await BybitMarketClient().fetch(asset["symbol"], quote_currency=asset.get("quote_currency", "USDT"))
    snap = DerivativesSnapshot(ts=datetime.now(timezone.utc), **payload)
    await repo.insert(snap)


async def ingest_onchain_flow_job(asset: dict, repo: SnapshotRepository) -> None:
    payload = await OnchainClusterFlowProvider().fetch(asset["symbol"], chain=asset.get("chain") or "ethereum")
    snap = OnchainFlow(ts=datetime.now(timezone.utc), **payload)
    await repo.insert(snap)


async def ingest_coingecko_liquidity_job(asset: dict, repo: SnapshotRepository) -> None:
    payload = await CoinGeckoOnchainClient().fetch(asset["symbol"], chain=asset.get("chain") or "eth")
    snap = LiquiditySnapshot(ts=datetime.now(timezone.utc), **payload)
    await repo.insert(snap)


async def ingest_cex_flow_job(asset: dict, repo: SnapshotRepository) -> None:
    market = await repo.latest_market(asset["symbol"], venue="binance")
    payload = await BinanceWalletClient().fetch(asset["symbol"], market={"volume_24h": market.volume_24h if market else 0})
    snap = CexFlowSnapshot(ts=datetime.now(timezone.utc), **payload)
    await repo.insert(snap)


async def ingest_defillama_macro_job(asset: dict, repo: SnapshotRepository) -> None:
    logger.info("ingest_defillama_macro %s", asset["symbol"])
    await DefiLlamaClient().fetch(asset["symbol"])


async def compute_factors_job(asset: dict, repo: SnapshotRepository) -> None:
    symbol = asset["symbol"]
    market = await repo.latest_market(symbol)
    cex_flow = await repo.latest_cex_flow(symbol)
    onchain = await repo.latest_onchain(symbol)
    derivatives = await repo.latest_derivatives(symbol)
    liquidity = await repo.latest_liquidity(symbol)
    if not all([market, cex_flow, onchain, liquidity]):
        return

    factors, explanations = FactorEngine().compute(
        FactorInputs(
            netflow_usd=cex_flow.netflow_usd,
            volume_24h=market.volume_24h,
            whale_netflow_usd=onchain.whale_netflow_usd,
            team_to_exchange_usd=onchain.team_to_exchange_usd,
            foundation_to_exchange_usd=onchain.foundation_to_exchange_usd,
            labeled_flow_count=onchain.labeled_flow_count,
            open_interest_change_1h_pct=derivatives.open_interest_change_1h_pct if derivatives else None,
            funding_rate=derivatives.funding_rate if derivatives else None,
            funding_rate_zscore_7d=derivatives.funding_rate_zscore_7d if derivatives else None,
            bid_ask_spread_bps=market.bid_ask_spread_bps,
            orderbook_depth_usd_1pct=market.orderbook_depth_usd_1pct,
            dex_liquidity_usd=liquidity.dex_liquidity_usd,
            slippage_estimate_buy_10k_bps=liquidity.slippage_estimate_buy_10k_bps,
            slippage_estimate_sell_10k_bps=liquidity.slippage_estimate_sell_10k_bps,
        )
    )
    fs = FactorScore(asset_symbol=symbol, ts=datetime.now(timezone.utc), metadata_json=explanations, **factors)
    await repo.insert(fs)


async def compute_signals_job(asset: dict, repo: SnapshotRepository) -> None:
    settings = get_settings()
    symbol = asset["symbol"]
    factor = await repo.latest_factor(symbol)
    if not factor:
        return
    weights = settings.factor_weights(asset["category"])
    thresholds = settings.score_thresholds(asset["category"])
    scores = ScoringEngine(weights).compute(
        {
            "cex_netflow_score": factor.cex_netflow_score,
            "whale_activity_score": factor.whale_activity_score,
            "oi_funding_score": factor.oi_funding_score,
            "liquidity_exec_score": factor.liquidity_exec_score,
        }
    )
    previous = await repo.latest_signal(symbol)
    action, confidence, reasons, invalidations = SignalEngine(thresholds).decide(
        scores, previous_action=previous.action if previous else None
    )
    sig = Signal(
        asset_symbol=symbol,
        ts=datetime.now(timezone.utc),
        action=action,
        confidence=confidence,
        reasons_json=reasons,
        invalidation_conditions_json=invalidations,
        **scores,
    )
    await repo.insert(sig)


async def emit_alerts_job(asset: dict, repo: SnapshotRepository) -> None:
    settings = get_settings().load_yaml("scheduler.yaml")
    cooldown = int(settings.get("alert_cooldown_minutes", 15))
    symbol = asset["symbol"]
    cex_flow = await repo.latest_cex_flow(symbol)
    onchain = await repo.latest_onchain(symbol)
    signal = await repo.latest_signal(symbol)
    for alert in AlertEngine().build_data_alerts(symbol, cex_flow, onchain, signal):
        if not await repo.alert_exists_recent(symbol, alert.alert_type, cooldown):
            await repo.insert(alert)
