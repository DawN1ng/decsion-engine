from decimal import Decimal

from app.domain.services.signal_engine import SignalEngine


THRESHOLDS = {
    "build_long": Decimal("0.72"),
    "probe_long": Decimal("0.55"),
    "reduce_or_short": Decimal("0.68"),
    "reduce_risk": Decimal("0.62"),
    "max_risk": Decimal("0.55"),
    "probe_max_risk": Decimal("0.65"),
    "min_exec_score": Decimal("0.45"),
    "watch_long": Decimal("0.40"),
    "watch_short": Decimal("0.40"),
    "exit_short_score": Decimal("0.75"),
    "exit_risk_score": Decimal("0.72"),
}


def test_signal_engine_exit_from_previous_long() -> None:
    action, confidence, _, _ = SignalEngine(THRESHOLDS).decide(
        {
            "long_score": Decimal("0.30"),
            "short_score": Decimal("0.80"),
            "risk_score": Decimal("0.60"),
            "exec_score": Decimal("0.70"),
        },
        previous_action="BUILD_LONG",
    )
    assert action == "EXIT"
    assert confidence >= Decimal("0.80")
