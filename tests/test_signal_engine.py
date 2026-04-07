from decimal import Decimal

from app.domain.services.signal_engine import SignalEngine


THRESHOLDS = {
    "build_long": Decimal("0.45"),
    "probe_long": Decimal("0.25"),
    "reduce_or_short": Decimal("0.30"),
    "max_risk": Decimal("0.60"),
    "min_exec_score": Decimal("0.05"),
}


def test_signal_engine_build_long() -> None:
    action = SignalEngine(THRESHOLDS).decide(
        {
            "long_score": Decimal("0.50"),
            "short_score": Decimal("-0.50"),
            "risk_score": Decimal("0.20"),
            "exec_score": Decimal("0.10"),
        }
    )
    assert action == "BUILD_LONG"


def test_signal_engine_ignore_low_exec() -> None:
    action = SignalEngine(THRESHOLDS).decide(
        {
            "long_score": Decimal("0.80"),
            "short_score": Decimal("-0.80"),
            "risk_score": Decimal("0.10"),
            "exec_score": Decimal("0.01"),
        }
    )
    assert action == "IGNORE"
