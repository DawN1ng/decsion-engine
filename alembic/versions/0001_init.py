"""init tables"""

from alembic import op
import sqlalchemy as sa


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_assets_symbol", "assets", ["symbol"], unique=True)

    for name in ["market_snapshots", "onchain_flows", "derivatives_snapshots", "liquidity_snapshots", "factor_scores", "signals", "alerts"]:
        op.create_table(
            name,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("asset_symbol", sa.String(length=32), nullable=False),
            sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["asset_symbol"], ["assets.symbol"]),
        )


def downgrade() -> None:
    for name in ["alerts", "signals", "factor_scores", "liquidity_snapshots", "derivatives_snapshots", "onchain_flows", "market_snapshots", "assets"]:
        op.drop_table(name)
