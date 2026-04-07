from decimal import Decimal

from app.domain.services.scoring_engine import ScoringEngine


def test_scoring_engine_outputs() -> None:
    engine = ScoringEngine(
        weights={
            "cex_netflow": Decimal("0.35"),
            "whale_activity": Decimal("0.30"),
            "oi_funding": Decimal("0.20"),
            "liquidity_exec": Decimal("0.15"),
        }
    )
    scores = engine.compute(
        {
            "cex_netflow_score": Decimal("0.4"),
            "whale_activity_score": Decimal("0.3"),
            "oi_funding_score": Decimal("0.1"),
            "liquidity_exec_score": Decimal("0.5"),
        }
    )
    assert scores["long_score"] == Decimal("0.2500")
    assert scores["short_score"] == Decimal("-0.2500")
    assert scores["exec_score"] == Decimal("0.0750")
