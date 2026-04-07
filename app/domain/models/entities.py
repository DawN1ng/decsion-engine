from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(default=True)


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(24, 8))
    cex_inflow: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    cex_outflow: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)


class OnchainFlow(Base):
    __tablename__ = "onchain_flows"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    whale_accumulation: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    team_to_exchange: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)


class DerivativesSnapshot(Base):
    __tablename__ = "derivatives_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    open_interest_change_pct: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=0)
    funding_rate: Mapped[Decimal] = mapped_column(Numeric(12, 8), default=0)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)


class LiquiditySnapshot(Base):
    __tablename__ = "liquidity_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    spread_bps: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=0)
    slippage_bps: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=0)
    depth_usd: Mapped[Decimal] = mapped_column(Numeric(24, 8), default=0)
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


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    asset_symbol: Mapped[str] = mapped_column(ForeignKey("assets.symbol"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    severity: Mapped[str] = mapped_column(String(16))
    message: Mapped[str] = mapped_column(String(500))
