from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class FactorInputs:
    netflow_usd: Decimal
    volume_24h: Decimal
    cex_flow_trust_level: str
    whale_netflow_usd: Decimal
    team_to_exchange_usd: Decimal
    foundation_to_exchange_usd: Decimal
    labeled_flow_count: int
    open_interest_change_1h_pct: Decimal | None
    funding_rate: Decimal | None
    funding_rate_zscore_7d: Decimal | None
    bid_ask_spread_bps: Decimal
    orderbook_depth_usd_1pct: Decimal
    dex_liquidity_usd: Decimal
    slippage_estimate_buy_10k_bps: Decimal
    slippage_estimate_sell_10k_bps: Decimal


class FactorEngine:
    TRUST_DISCOUNT = {"low": Decimal("0.5"), "medium": Decimal("0.8"), "high": Decimal("1")}

    @staticmethod
    def _clamp(value: Decimal) -> Decimal:
        return max(Decimal("-1"), min(Decimal("1"), value))

    def compute(self, data: FactorInputs) -> tuple[dict[str, Decimal], dict[str, list[str]]]:
        explanations: dict[str, list[str]] = {}
        volume = data.volume_24h if data.volume_24h > 0 else Decimal("1")

        trust_multiplier = self.TRUST_DISCOUNT.get(data.cex_flow_trust_level, Decimal("0.5"))
        netflow_ratio = data.netflow_usd / volume
        cex_score = self._clamp(netflow_ratio * Decimal("8") * trust_multiplier)
        explanations["cex_netflow"] = [f"netflow/volume={netflow_ratio:.6f}", f"trust={data.cex_flow_trust_level}"]

        team_pressure = data.team_to_exchange_usd + data.foundation_to_exchange_usd
        whale_ratio = data.whale_netflow_usd / volume
        pressure_ratio = team_pressure / volume
        whale_score = self._clamp((whale_ratio * Decimal("6")) - (pressure_ratio * Decimal("12")))
        if data.labeled_flow_count < 3:
            whale_score *= Decimal("0.8")
        explanations["whale_activity"] = [f"whale_ratio={whale_ratio:.6f}", f"team_pressure_ratio={pressure_ratio:.6f}"]

        oi_score = Decimal("0")
        if data.open_interest_change_1h_pct is not None and data.funding_rate is not None and data.funding_rate_zscore_7d is not None:
            overheated = data.open_interest_change_1h_pct > Decimal("4") and (
                data.funding_rate > Decimal("0.03") or data.funding_rate_zscore_7d > Decimal("2")
            )
            healthy = Decimal("0.8") <= data.open_interest_change_1h_pct <= Decimal("3") and abs(data.funding_rate_zscore_7d) < Decimal("1.5")
            if overheated:
                oi_score = Decimal("-0.8")
            elif healthy:
                oi_score = Decimal("0.35")
        explanations["oi_funding"] = ["neutral due to missing OI/funding context" if data.open_interest_change_1h_pct is None else f"oi_funding={oi_score}"]

        depth_total = data.orderbook_depth_usd_1pct + data.dex_liquidity_usd
        depth_score = self._clamp((depth_total / Decimal("10000000")) - Decimal("0.2"))
        spread_penalty = self._clamp(-(data.bid_ask_spread_bps / Decimal("30")))
        slip_avg = (data.slippage_estimate_buy_10k_bps + data.slippage_estimate_sell_10k_bps) / Decimal("2")
        slip_penalty = self._clamp(-(slip_avg / Decimal("80")))
        liquidity = self._clamp((depth_score * Decimal("0.6")) + (spread_penalty * Decimal("0.2")) + (slip_penalty * Decimal("0.2")))
        explanations["liquidity_exec"] = [f"depth_total={depth_total}", f"spread_bps={data.bid_ask_spread_bps}", f"slippage_bps={slip_avg}"]

        return {
            "cex_netflow_score": cex_score,
            "whale_activity_score": whale_score,
            "oi_funding_score": oi_score,
            "liquidity_exec_score": liquidity,
        }, explanations
