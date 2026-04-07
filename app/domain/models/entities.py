from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(32), default="midcap_alt")
    chain: Mapped[str | None] = mapped_column(String(32), nullable=True)
    token_address: Mapped[str | None] = mapped_column(String(120), nullable=True)
    quote_currency: Mapped[str] = mapped_column(String(16), default="USDT")
    is_active: Mapped[bool] = mapped_column(default=True)


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    venue: Mapped[str] = mapped_column(String(32), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_price: Mapped[Decimal] = mapped_column(Numeric(24, 8))
    volume_24h: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    bid_ask_spread_bps: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    orderbook_depth_usd_1pct: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)


class CexFlowSnapshot(Base):
    __tablename__ = "cex_flow_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    venue: Mapped[str] = mapped_column(String(32), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    inflow_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    outflow_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    netflow_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    source_type: Mapped[str] = mapped_column(String(32), default="derived")
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)


class OnchainFlow(Base):
    __tablename__ = "onchain_flows"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    chain: Mapped[str] = mapped_column(String(32), default="ethereum")
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    whale_inflow_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    whale_outflow_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    whale_netflow_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    team_to_exchange_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    foundation_to_exchange_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    labeled_flow_count: Mapped[int] = mapped_column(Integer, default=0)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)


class DerivativesSnapshot(Base):
    __tablename__ = "derivatives_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    venue: Mapped[str] = mapped_column(String(32), index=True)
    contract_type: Mapped[str] = mapped_column(String(32), default="perpetual")
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    open_interest_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    open_interest_change_1h_pct: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    funding_rate: Mapped[Decimal] = mapped_column(Numeric(12, 8), default=0)
    funding_rate_zscore_7d: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)


class LiquiditySnapshot(Base):
    __tablename__ = "liquidity_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    venue: Mapped[str] = mapped_column(String(32), index=True)
    venue_type: Mapped[str] = mapped_column(String(8), default="dex")
    chain: Mapped[str | None] = mapped_column(String(32), nullable=True)
    pool_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    dex_liquidity_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    cex_depth_usd_1pct: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    slippage_estimate_buy_10k_bps: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    slippage_estimate_sell_10k_bps: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)


class FactorScore(Base):
    __tablename__ = "factor_scores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    cex_netflow_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    whale_activity_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    oi_funding_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    liquidity_exec_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    long_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    short_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    risk_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    exec_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    action: Mapped[str] = mapped_column(String(32), index=True)
    confidence: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=0)
    reasons_json: Mapped[list] = mapped_column(JSON, default=list)
    invalidation_conditions_json: Mapped[list] = mapped_column(JSON, default=list)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    severity: Mapped[str] = mapped_column(String(16))
    alert_type: Mapped[str] = mapped_column(String(64), index=True)
    message: Mapped[str] = mapped_column(String(500))
    details_json: Mapped[dict] = mapped_column(JSON, default=dict)
