"""Create core PulseML tables.

Revision ID: 20231121_01
Revises: 
Create Date: 2025-11-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20231121_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    training_status = postgresql.ENUM(
        "pending",
        "queued",
        "running",
        "completed",
        "failed",
        "stopped",
        name="trainingstatus",
        create_type=False,
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'trainingstatus'
            ) THEN
                CREATE TYPE trainingstatus AS ENUM (
                    'pending', 'queued', 'running', 'completed', 'failed', 'stopped'
                );
            END IF;
        END
        $$;
        """
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "model_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("task_type", sa.String(length=50), nullable=False),
        sa.Column(
            "default_hparams",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "hyperparam_schema",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "datasets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column(
            "meta",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "training_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("model_template_id", sa.Integer(), nullable=False),
        sa.Column("status", training_status, nullable=False, server_default="pending"),
        sa.Column(
            "hparams",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("best_metric_name", sa.String(length=100), nullable=True),
        sa.Column("best_metric_value", sa.Float(), nullable=True),
        sa.Column("model_checkpoint_path", sa.String(length=512), nullable=True),
        sa.Column("logs_path", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ),
        sa.ForeignKeyConstraint(["model_template_id"], ["model_templates.id"], ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    training_status = postgresql.ENUM(
        "pending",
        "queued",
        "running",
        "completed",
        "failed",
        "stopped",
        name="trainingstatus",
        create_type=False,
    )
    op.drop_table("training_runs")
    op.drop_table("datasets")
    op.drop_table("model_templates")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS trainingstatus CASCADE;")


