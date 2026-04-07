from __future__ import annotations

from decimal import Decimal


class SignalEngine:
    def __init__(self, thresholds: dict[str, Decimal]) -> None:
        self.thresholds = thresholds

    def decide(
        self,
        scores: dict[str, Decimal],
        previous_action: str | None = None,
        cex_flow_trust_level: str = "medium",
    ) -> tuple[str, Decimal, list[str], list[str]]:
        reasons: list[str] = []
        invalidations: list[str] = []

        if scores["exec_score"] < self.thresholds["min_exec_score"]:
            reasons.append("execution quality below minimum")
            return "IGNORE", Decimal("0.20"), reasons, ["exec_score rises above minimum"]

        if previous_action in {"BUILD_LONG", "PROBE_LONG"} and (
            scores["short_score"] >= self.thresholds["exit_short_score"] or scores["risk_score"] >= self.thresholds["exit_risk_score"]
        ):
            reasons.append("bullish thesis invalidated")
            return "EXIT", Decimal("0.85"), reasons, ["short/risk pressure cools"]

        if scores["long_score"] >= self.thresholds["build_long"] and scores["risk_score"] <= self.thresholds["max_risk"]:
            reasons.append("strong bullish evidence with acceptable risk")
            invalidations = ["team/foundation exchange flows spike", "funding overheats"]
            action = "BUILD_LONG"
            confidence = Decimal("0.88")
        elif scores["long_score"] >= self.thresholds["probe_long"] and scores["risk_score"] <= self.thresholds["probe_max_risk"]:
            reasons.append("early bullish setup")
            action = "PROBE_LONG"
            confidence = Decimal("0.65")
            invalidations = ["long score drops below probe threshold"]
        elif scores["short_score"] >= self.thresholds["reduce_or_short"] and scores["exec_score"] >= self.thresholds["min_exec_score"]:
            reasons.append("bearish evidence is strong")
            action = "REDUCE_OR_SHORT"
            confidence = Decimal("0.82")
            invalidations = ["cex netflow turns positive", "funding cools"]
        elif scores["risk_score"] >= self.thresholds["reduce_risk"]:
            reasons.append("risk elevated, reduce exposure")
            action = "REDUCE"
            confidence = Decimal("0.60")
            invalidations = ["risk score normalizes"]
        elif scores["long_score"] >= self.thresholds["watch_long"] or scores["short_score"] >= self.thresholds["watch_short"]:
            action = "WATCH"
            confidence = Decimal("0.45")
            reasons = ["mixed evidence"]
            invalidations = ["confirm directional edge"]
        else:
            action = "IGNORE"
            confidence = Decimal("0.25")
            reasons = ["low conviction"]
            invalidations = ["wait for stronger signals"]

        if cex_flow_trust_level == "low":
            reasons.append("cex flow signal is derived, not exchange-cluster verified")
            confidence = max(Decimal("0"), confidence - Decimal("0.08"))

        return action, confidence, reasons, invalidations
