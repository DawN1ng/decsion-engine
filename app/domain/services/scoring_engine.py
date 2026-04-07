from __future__ import annotations

from decimal import Decimal


class ScoringEngine:
    def __init__(self, weights: dict[str, Decimal]) -> None:
        self.weights = weights

    def compute(self, factors: dict[str, Decimal]) -> dict[str, Decimal]:
        long_score = (
            factors["cex_netflow_score"] * self.weights["cex_netflow"]
            + factors["whale_activity_score"] * self.weights["whale_activity"]
            + factors["oi_funding_score"] * self.weights["oi_funding"]
        )
        short_score = -long_score
        risk_score = max(Decimal("0"), -factors["oi_funding_score"])
        exec_score = factors["liquidity_exec_score"] * self.weights["liquidity_exec"]
        return {
            "long_score": long_score.quantize(Decimal("0.0001")),
            "short_score": short_score.quantize(Decimal("0.0001")),
            "risk_score": risk_score.quantize(Decimal("0.0001")),
            "exec_score": exec_score.quantize(Decimal("0.0001")),
        }
