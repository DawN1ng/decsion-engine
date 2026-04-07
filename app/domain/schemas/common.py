from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class AssetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    symbol: str
    name: str
    category: str
    chain: str | None
    token_address: str | None
    quote_currency: str
    is_active: bool


class MarketSnapshotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    asset_symbol: str
    venue: str
    ts: datetime
    last_price: Decimal
    volume_24h: Decimal
    bid_ask_spread_bps: Decimal
    orderbook_depth_usd_1pct: Decimal


class CexFlowSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    asset_symbol: str
    venue: str
    ts: datetime
    inflow_usd: Decimal
    outflow_usd: Decimal
    netflow_usd: Decimal
    source_type: str
    trust_level: str


class OnchainFlowSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    asset_symbol: str
    chain: str
    ts: datetime
    whale_inflow_usd: Decimal
    whale_outflow_usd: Decimal
    whale_netflow_usd: Decimal
    team_to_exchange_usd: Decimal
    foundation_to_exchange_usd: Decimal
    labeled_flow_count: int


class DerivativesSnapshotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    asset_symbol: str
    venue: str
    contract_type: str
    ts: datetime
    open_interest_usd: Decimal
    open_interest_change_1h_pct: Decimal | None
    funding_rate: Decimal
    funding_rate_zscore_7d: Decimal


class LiquiditySnapshotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    asset_symbol: str
    venue: str
    venue_type: str
    chain: str | None
    pool_id: str | None
    ts: datetime
    dex_liquidity_usd: Decimal
    cex_depth_usd_1pct: Decimal
    slippage_estimate_buy_10k_bps: Decimal
    slippage_estimate_sell_10k_bps: Decimal


class SnapshotBundleSchema(BaseModel):
    symbol: str
    market: MarketSnapshotSchema | None
    cex_flow: CexFlowSchema | None
    onchain: OnchainFlowSchema | None
    derivatives: DerivativesSnapshotSchema | None
    liquidity: LiquiditySnapshotSchema | None
    data_quality: dict[str, Any]


class FactorScoreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    asset_symbol: str
    ts: datetime
    cex_netflow_score: Decimal
    whale_activity_score: Decimal
    oi_funding_score: Decimal
    liquidity_exec_score: Decimal
    metadata_json: dict[str, Any]


class SignalSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    asset_symbol: str
    ts: datetime
    long_score: Decimal
    short_score: Decimal
    risk_score: Decimal
    exec_score: Decimal
    action: str
    confidence: Decimal
    reasons_json: list[str]
    invalidation_conditions_json: list[str]
    source_trust: dict[str, Any] | None = None


class AlertSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    asset_symbol: str
    ts: datetime
    severity: str
    alert_type: str
    message: str
    details_json: dict[str, Any]
