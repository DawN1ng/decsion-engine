from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.domain.models.entities import (
    Alert,
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
from app.providers.binance.client import BinanceMarketClient
from app.providers.bybit.client import BybitMarketClient
from app.providers.coingecko.client import CoinGeckoOnchainClient
from app.providers.defillama.client import DefiLlamaClient
from app.repositories.snapshot_repository import SnapshotRepository


async def ingest_binance_market_job(symbol: str, repo: SnapshotRepository) -> None:
    payload = await BinanceMarketClient().fetch(symbol)
    snap = MarketSnapshot(
        asset_symbol=symbol,
        ts=datetime.now(timezone.utc),
        price=Decimal(payload["price"]),
        cex_inflow=Decimal(payload["cex_inflow"]),
        cex_outflow=Decimal(payload["cex_outflow"]),
        raw_payload=payload,
    )
    await repo.add(snap)


async def ingest_bybit_derivatives_job(symbol: str, repo: SnapshotRepository) -> None:
    payload = await BybitMarketClient().fetch(symbol)
    snap = DerivativesSnapshot(
        asset_symbol=symbol,
        ts=datetime.now(timezone.utc),
        open_interest_change_pct=Decimal(payload["open_interest_change_pct"]),
        funding_rate=Decimal(payload["funding_rate"]),
        raw_payload=payload,
    )
    await repo.add(snap)


async def ingest_onchain_flow_job(symbol: str, repo: SnapshotRepository) -> None:
    payload = await CoinGeckoOnchainClient().fetch(symbol)
    snap = OnchainFlow(
        asset_symbol=symbol,
        ts=datetime.now(timezone.utc),
        whale_accumulation=Decimal(payload["whale_accumulation"]),
        team_to_exchange=Decimal(payload["team_to_exchange"]),
        raw_payload=payload,
    )
    await repo.add(snap)


async def ingest_coingecko_liquidity_job(symbol: str, repo: SnapshotRepository) -> None:
    payload = await DefiLlamaClient().fetch(symbol)
    snap = LiquiditySnapshot(
        asset_symbol=symbol,
        ts=datetime.now(timezone.utc),
        spread_bps=Decimal(payload["spread_bps"]),
        slippage_bps=Decimal(payload["slippage_bps"]),
        depth_usd=Decimal(payload["depth_usd"]),
        raw_payload=payload,
    )
    await repo.add(snap)


async def ingest_defillama_macro_job(symbol: str, repo: SnapshotRepository) -> None:
    await ingest_coingecko_liquidity_job(symbol, repo)


async def compute_factors_job(symbol: str, repo: SnapshotRepository) -> None:
    market = await repo.latest_market(symbol)
    onchain = await repo.latest_onchain(symbol)
    derivatives = await repo.latest_derivatives(symbol)
    liq = await repo.latest_liquidity(symbol)
    if not all([market, onchain, derivatives, liq]):
        return
    factors = FactorEngine().compute(
        FactorInputs(
            cex_inflow=market.cex_inflow,
            cex_outflow=market.cex_outflow,
            whale_accumulation=onchain.whale_accumulation,
            team_to_exchange=onchain.team_to_exchange,
            oi_change_pct=derivatives.open_interest_change_pct,
            funding_rate=derivatives.funding_rate,
            spread_bps=liq.spread_bps,
            slippage_bps=liq.slippage_bps,
            depth_usd=liq.depth_usd,
        )
    )
    fs = FactorScore(asset_symbol=symbol, ts=datetime.now(timezone.utc), **factors)
    await repo.add(fs)


async def compute_signals_job(symbol: str, repo: SnapshotRepository, weights: dict, thresholds: dict) -> None:
    factor = await repo.latest_factor(symbol)
    if not factor:
        return
    factors = {
        "cex_netflow_score": factor.cex_netflow_score,
        "whale_activity_score": factor.whale_activity_score,
        "oi_funding_score": factor.oi_funding_score,
        "liquidity_exec_score": factor.liquidity_exec_score,
    }
    scores = ScoringEngine(weights).compute(factors)
    action = SignalEngine(thresholds).decide(scores)
    sig = Signal(asset_symbol=symbol, ts=datetime.now(timezone.utc), action=action, **scores)
    await repo.add(sig)


async def emit_alerts_job(symbol: str, repo: SnapshotRepository) -> None:
    signal = await repo.latest_signal(symbol)
    if not signal:
        return
    alert = AlertEngine().build_alert(signal)
    if alert:
        await repo.add(alert)
