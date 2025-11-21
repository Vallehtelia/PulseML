"""Add metrics_summary to training_runs.

Revision ID: 20250101_01
Revises: 20231121_01
Create Date: 2025-01-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20250101_01"
down_revision = "20231121_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "training_runs",
        sa.Column(
            "metrics_summary",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("training_runs", "metrics_summary")

