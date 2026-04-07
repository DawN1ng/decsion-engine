"""normalize mvp schema"""

from alembic import op
import sqlalchemy as sa


revision = "0002_normalize_mvp_schema"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("category", sa.String(length=32), nullable=False, server_default="midcap_alt"))
    op.add_column("assets", sa.Column("chain", sa.String(length=32), nullable=True))
    op.add_column("assets", sa.Column("token_address", sa.String(length=120), nullable=True))
    op.add_column("assets", sa.Column("quote_currency", sa.String(length=16), nullable=False, server_default="USDT"))

    op.drop_table("market_snapshots")
    op.drop_table("onchain_flows")
    op.drop_table("derivatives_snapshots")
    op.drop_table("liquidity_snapshots")
    op.drop_table("factor_scores")
    op.drop_table("signals")
    op.drop_table("alerts")

    op.create_table(
        "market_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_symbol", sa.String(length=32), sa.ForeignKey("assets.symbol"), nullable=False),
        sa.Column("venue", sa.String(length=32), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_price", sa.Numeric(24, 8), nullable=False),
        sa.Column("volume_24h", sa.Numeric(24, 8), nullable=False),
        sa.Column("bid_ask_spread_bps", sa.Numeric(12, 4), nullable=False),
        sa.Column("orderbook_depth_usd_1pct", sa.Numeric(24, 8), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_table(
        "cex_flow_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_symbol", sa.String(length=32), sa.ForeignKey("assets.symbol"), nullable=False),
        sa.Column("venue", sa.String(length=32), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inflow_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("outflow_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("netflow_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_table(
        "onchain_flows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_symbol", sa.String(length=32), sa.ForeignKey("assets.symbol"), nullable=False),
        sa.Column("chain", sa.String(length=32), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("whale_inflow_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("whale_outflow_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("whale_netflow_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("team_to_exchange_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("foundation_to_exchange_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("labeled_flow_count", sa.Integer(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_table(
        "derivatives_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_symbol", sa.String(length=32), sa.ForeignKey("assets.symbol"), nullable=False),
        sa.Column("venue", sa.String(length=32), nullable=False),
        sa.Column("contract_type", sa.String(length=32), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open_interest_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("open_interest_change_1h_pct", sa.Numeric(12, 4), nullable=False),
        sa.Column("funding_rate", sa.Numeric(12, 8), nullable=False),
        sa.Column("funding_rate_zscore_7d", sa.Numeric(12, 4), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_table(
        "liquidity_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_symbol", sa.String(length=32), sa.ForeignKey("assets.symbol"), nullable=False),
        sa.Column("venue", sa.String(length=32), nullable=False),
        sa.Column("venue_type", sa.String(length=8), nullable=False),
        sa.Column("chain", sa.String(length=32), nullable=True),
        sa.Column("pool_id", sa.String(length=128), nullable=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dex_liquidity_usd", sa.Numeric(24, 8), nullable=False),
        sa.Column("cex_depth_usd_1pct", sa.Numeric(24, 8), nullable=False),
        sa.Column("slippage_estimate_buy_10k_bps", sa.Numeric(12, 4), nullable=False),
        sa.Column("slippage_estimate_sell_10k_bps", sa.Numeric(12, 4), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
    )
    op.create_table(
        "factor_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_symbol", sa.String(length=32), sa.ForeignKey("assets.symbol"), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("cex_netflow_score", sa.Numeric(8, 4), nullable=False),
        sa.Column("whale_activity_score", sa.Numeric(8, 4), nullable=False),
        sa.Column("oi_funding_score", sa.Numeric(8, 4), nullable=False),
        sa.Column("liquidity_exec_score", sa.Numeric(8, 4), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
    )
    op.create_table(
        "signals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_symbol", sa.String(length=32), sa.ForeignKey("assets.symbol"), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("long_score", sa.Numeric(8, 4), nullable=False),
        sa.Column("short_score", sa.Numeric(8, 4), nullable=False),
        sa.Column("risk_score", sa.Numeric(8, 4), nullable=False),
        sa.Column("exec_score", sa.Numeric(8, 4), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.Numeric(8, 4), nullable=False),
        sa.Column("reasons_json", sa.JSON(), nullable=False),
        sa.Column("invalidation_conditions_json", sa.JSON(), nullable=False),
    )
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_symbol", sa.String(length=32), sa.ForeignKey("assets.symbol"), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("details_json", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    raise NotImplementedError
