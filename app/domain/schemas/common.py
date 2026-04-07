from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AssetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    symbol: str
    name: str
    is_active: bool


class MarketSnapshotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    asset_symbol: str
    ts: datetime
    price: Decimal
    cex_inflow: Decimal
    cex_outflow: Decimal


class FactorScoreSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    asset_symbol: str
    ts: datetime
    cex_netflow_score: Decimal
    whale_activity_score: Decimal
    oi_funding_score: Decimal
    liquidity_exec_score: Decimal


class SignalSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    asset_symbol: str
    ts: datetime
    long_score: Decimal
    short_score: Decimal
    risk_score: Decimal
    exec_score: Decimal
    action: str


class AlertSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    asset_symbol: str
    ts: datetime
    severity: str
    message: str
