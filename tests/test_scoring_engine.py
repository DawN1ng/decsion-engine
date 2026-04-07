from decimal import Decimal

from app.domain.services.scoring_engine import ScoringEngine


WEIGHTS = {
    "long_cex": Decimal("0.28"),
    "long_whale": Decimal("0.30"),
    "long_derivatives": Decimal("0.20"),
    "long_exec": Decimal("0.22"),
    "short_cex": Decimal("0.30"),
    "short_whale": Decimal("0.28"),
    "short_derivatives": Decimal("0.27"),
    "short_liquidity_weakness": Decimal("0.15"),
    "risk_derivatives": Decimal("0.45"),
    "risk_exec": Decimal("0.35"),
    "risk_team_pressure": Decimal("0.20"),
}


def test_scoring_engine_independent_short_score() -> None:
    scores = ScoringEngine(WEIGHTS).compute(
        {
            "cex_netflow_score": Decimal("-0.6"),
            "whale_activity_score": Decimal("-0.7"),
            "oi_funding_score": Decimal("-0.5"),
            "liquidity_exec_score": Decimal("0.1"),
        }
    )
    assert scores["short_score"] > scores["long_score"]
    assert scores["short_score"] != -scores["long_score"]
    assert Decimal("0") <= scores["exec_score"] <= Decimal("1")
