from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.services.normalization_service import NormalizationService


@dataclass
class FactorInputs:
    cex_inflow: Decimal
    cex_outflow: Decimal
    whale_accumulation: Decimal
    team_to_exchange: Decimal
    oi_change_pct: Decimal
    funding_rate: Decimal
    spread_bps: Decimal
    slippage_bps: Decimal
    depth_usd: Decimal


class FactorEngine:
    def __init__(self) -> None:
        self.norm = NormalizationService()

    def compute(self, data: FactorInputs) -> dict[str, Decimal]:
        netflow = self.norm.clamp((data.cex_outflow - data.cex_inflow) / Decimal("1000000"))
        whale = self.norm.clamp((data.whale_accumulation - data.team_to_exchange) / Decimal("500000"))

        oi_penalty = Decimal("0")
        if data.oi_change_pct > Decimal("8") and data.funding_rate > Decimal("0.03"):
            oi_penalty = Decimal("-0.8")
        elif data.oi_change_pct > Decimal("2") and data.funding_rate < Decimal("0.02"):
            oi_penalty = Decimal("0.3")
        oi_funding = self.norm.clamp(oi_penalty)

        liq_raw = (data.depth_usd / Decimal("10000000")) - (data.spread_bps / Decimal("100")) - (data.slippage_bps / Decimal("100"))
        liquidity = self.norm.clamp(liq_raw)

        return {
            "cex_netflow_score": netflow,
            "whale_activity_score": whale,
            "oi_funding_score": oi_funding,
            "liquidity_exec_score": liquidity,
        }
