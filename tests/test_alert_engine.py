from datetime import datetime, timezone
from decimal import Decimal

from app.domain.models.entities import CexFlowSnapshot, OnchainFlow, Signal
from app.domain.services.alert_engine import AlertEngine


def test_alert_engine_builds_expected_alert_types() -> None:
    cex = CexFlowSnapshot(
        asset_symbol="ETH",
        venue="binance",
        ts=datetime.now(timezone.utc),
        inflow_usd=Decimal("100"),
        outflow_usd=Decimal("80"),
        netflow_usd=Decimal("-20"),
        source_type="derived",
        raw_payload={},
    )
    onchain = OnchainFlow(
        asset_symbol="ETH",
        chain="ethereum",
        ts=datetime.now(timezone.utc),
        whale_inflow_usd=Decimal("0"),
        whale_outflow_usd=Decimal("0"),
        whale_netflow_usd=Decimal("0"),
        team_to_exchange_usd=Decimal("25"),
        foundation_to_exchange_usd=Decimal("10"),
        labeled_flow_count=2,
        raw_payload={},
    )
    signal = Signal(
        asset_symbol="ETH",
        ts=datetime.now(timezone.utc),
        long_score=Decimal("0.2"),
        short_score=Decimal("0.8"),
        risk_score=Decimal("0.7"),
        exec_score=Decimal("0.6"),
        action="REDUCE_OR_SHORT",
        confidence=Decimal("0.8"),
        reasons_json=["bearish"],
        invalidation_conditions_json=["cooling"],
    )
    alerts = AlertEngine().build_data_alerts("ETH", cex, onchain, signal)
    types = {a.alert_type for a in alerts}
    assert "HIGH_EXCHANGE_INFLOW" in types
    assert "TEAM_TO_EXCHANGE" in types
    assert "SIGNAL_DOWNGRADE" in types
