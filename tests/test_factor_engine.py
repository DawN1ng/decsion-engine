from decimal import Decimal

from app.domain.services.factor_engine import FactorEngine, FactorInputs


def test_factor_engine_penalizes_team_exchange_behavior() -> None:
    factors, meta = FactorEngine().compute(
        FactorInputs(
            netflow_usd=Decimal("250000"),
            volume_24h=Decimal("5000000"),
            cex_flow_trust_level="medium",
            whale_netflow_usd=Decimal("300000"),
            team_to_exchange_usd=Decimal("400000"),
            foundation_to_exchange_usd=Decimal("200000"),
            labeled_flow_count=8,
            open_interest_change_1h_pct=Decimal("5"),
            funding_rate=Decimal("0.04"),
            funding_rate_zscore_7d=Decimal("2.5"),
            bid_ask_spread_bps=Decimal("8"),
            orderbook_depth_usd_1pct=Decimal("15000000"),
            dex_liquidity_usd=Decimal("6000000"),
            slippage_estimate_buy_10k_bps=Decimal("15"),
            slippage_estimate_sell_10k_bps=Decimal("16"),
        )
    )
    assert factors["whale_activity_score"] < 0
    assert factors["oi_funding_score"] < 0
    assert "team_pressure_ratio" in meta["whale_activity"][1]


def test_factor_engine_discounts_low_trust_cex_flow() -> None:
    base = dict(
        netflow_usd=Decimal("500000"), volume_24h=Decimal("5000000"), whale_netflow_usd=Decimal("0"),
        team_to_exchange_usd=Decimal("0"), foundation_to_exchange_usd=Decimal("0"), labeled_flow_count=10,
        open_interest_change_1h_pct=None, funding_rate=None, funding_rate_zscore_7d=None,
        bid_ask_spread_bps=Decimal("5"), orderbook_depth_usd_1pct=Decimal("10000000"), dex_liquidity_usd=Decimal("1000000"),
        slippage_estimate_buy_10k_bps=Decimal("10"), slippage_estimate_sell_10k_bps=Decimal("10")
    )
    low, _ = FactorEngine().compute(FactorInputs(cex_flow_trust_level="low", **base))
    high, _ = FactorEngine().compute(FactorInputs(cex_flow_trust_level="high", **base))
    assert abs(low["cex_netflow_score"]) < abs(high["cex_netflow_score"])
