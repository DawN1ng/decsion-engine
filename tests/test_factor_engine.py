from decimal import Decimal

from app.domain.services.factor_engine import FactorEngine, FactorInputs


def test_factor_engine_positive_netflow() -> None:
    engine = FactorEngine()
    factors = engine.compute(
        FactorInputs(
            cex_inflow=Decimal("100000"),
            cex_outflow=Decimal("400000"),
            whale_accumulation=Decimal("300000"),
            team_to_exchange=Decimal("10000"),
            oi_change_pct=Decimal("3"),
            funding_rate=Decimal("0.01"),
            spread_bps=Decimal("4"),
            slippage_bps=Decimal("5"),
            depth_usd=Decimal("15000000"),
        )
    )
    assert factors["cex_netflow_score"] > 0
    assert factors["whale_activity_score"] > 0
    assert factors["liquidity_exec_score"] > 0
