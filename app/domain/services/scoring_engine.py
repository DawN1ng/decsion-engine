from __future__ import annotations

from decimal import Decimal


class ScoringEngine:
    def __init__(self, weights: dict[str, Decimal]) -> None:
        self.weights = weights

    @staticmethod
    def _q(v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.0001"))

    def compute(self, factors: dict[str, Decimal]) -> dict[str, Decimal]:
        exec_score = self._q(max(Decimal("0"), (factors["liquidity_exec_score"] + Decimal("1")) / Decimal("2")))

        bullish_deriv = max(Decimal("0"), factors["oi_funding_score"])
        bearish_deriv = max(Decimal("0"), -factors["oi_funding_score"])
        bullish_flow = max(Decimal("0"), factors["cex_netflow_score"])
        bearish_flow = max(Decimal("0"), -factors["cex_netflow_score"])
        bullish_whale = max(Decimal("0"), factors["whale_activity_score"])
        bearish_whale = max(Decimal("0"), -factors["whale_activity_score"])

        long_score = (
            bullish_flow * self.weights["long_cex"]
            + bullish_whale * self.weights["long_whale"]
            + bullish_deriv * self.weights["long_derivatives"]
            + exec_score * self.weights["long_exec"]
        )
        short_score = (
            bearish_flow * self.weights["short_cex"]
            + bearish_whale * self.weights["short_whale"]
            + bearish_deriv * self.weights["short_derivatives"]
            + (Decimal("1") - exec_score) * self.weights["short_liquidity_weakness"]
        )
        risk_score = (
            bearish_deriv * self.weights["risk_derivatives"]
            + (Decimal("1") - exec_score) * self.weights["risk_exec"]
            + bearish_whale * self.weights["risk_team_pressure"]
        )

        return {
            "long_score": self._q(min(Decimal("1"), long_score)),
            "short_score": self._q(min(Decimal("1"), short_score)),
            "risk_score": self._q(min(Decimal("1"), risk_score)),
            "exec_score": exec_score,
        }
