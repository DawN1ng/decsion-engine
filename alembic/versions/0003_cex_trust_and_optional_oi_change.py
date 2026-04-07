"""add cex trust and optional oi change"""

from alembic import op
import sqlalchemy as sa


revision = "0003_cex_trust_and_optional_oi_change"
down_revision = "0002_normalize_mvp_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cex_flow_snapshots", sa.Column("trust_level", sa.String(length=16), nullable=False, server_default="low"))
    op.alter_column("derivatives_snapshots", "open_interest_change_1h_pct", nullable=True)


def downgrade() -> None:
    op.alter_column("derivatives_snapshots", "open_interest_change_1h_pct", nullable=False)
    op.drop_column("cex_flow_snapshots", "trust_level")
