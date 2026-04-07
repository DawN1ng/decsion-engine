from __future__ import annotations

from decimal import Decimal


class SignalEngine:
    def __init__(self, thresholds: dict[str, Decimal]) -> None:
        self.thresholds = thresholds

    def decide(self, scores: dict[str, Decimal]) -> str:
        if scores["exec_score"] < self.thresholds["min_exec_score"]:
            return "IGNORE"
        if scores["long_score"] >= self.thresholds["build_long"] and scores["risk_score"] <= self.thresholds["max_risk"]:
            return "BUILD_LONG"
        if scores["long_score"] >= self.thresholds["probe_long"]:
            return "PROBE_LONG"
        if scores["short_score"] >= self.thresholds["reduce_or_short"] or scores["risk_score"] > self.thresholds["max_risk"]:
            return "REDUCE_OR_SHORT"
        return "WATCH"
