"""Add device and epoch tracking to training_runs.

Revision ID: 20250101_02
Revises: 20250101_01
Create Date: 2025-01-01
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20250101_02"
down_revision = "20250101_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("training_runs", sa.Column("device", sa.String(length=50), nullable=True))
    op.add_column("training_runs", sa.Column("current_epoch", sa.Integer(), nullable=True))
    op.add_column("training_runs", sa.Column("total_epochs", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("training_runs", "total_epochs")
    op.drop_column("training_runs", "current_epoch")
    op.drop_column("training_runs", "device")

