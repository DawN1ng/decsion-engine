from __future__ import annotations

from decimal import Decimal


class SignalEngine:
    def __init__(self, thresholds: dict[str, Decimal]) -> None:
        self.thresholds = thresholds

    def decide(self, scores: dict[str, Decimal], previous_action: str | None = None) -> tuple[str, Decimal, list[str], list[str]]:
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
            return "BUILD_LONG", Decimal("0.88"), reasons, invalidations

        if scores["long_score"] >= self.thresholds["probe_long"] and scores["risk_score"] <= self.thresholds["probe_max_risk"]:
            reasons.append("early bullish setup")
            return "PROBE_LONG", Decimal("0.65"), reasons, ["long score drops below probe threshold"]

        if scores["short_score"] >= self.thresholds["reduce_or_short"] and scores["exec_score"] >= self.thresholds["min_exec_score"]:
            reasons.append("bearish evidence is strong")
            return "REDUCE_OR_SHORT", Decimal("0.82"), reasons, ["cex netflow turns positive", "funding cools"]

        if scores["risk_score"] >= self.thresholds["reduce_risk"]:
            reasons.append("risk elevated, reduce exposure")
            return "REDUCE", Decimal("0.60"), reasons, ["risk score normalizes"]

        if scores["long_score"] >= self.thresholds["watch_long"] or scores["short_score"] >= self.thresholds["watch_short"]:
            return "WATCH", Decimal("0.45"), ["mixed evidence"], ["confirm directional edge"]

        return "IGNORE", Decimal("0.25"), ["low conviction"], ["wait for stronger signals"]
