"""SQLAlchemy ORM models for PulseML."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    Enum,
    ForeignKey,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

TrainingStatus = Enum(
    "pending",
    "queued",
    "running",
    "completed",
    "failed",
    "stopped",
    name="trainingstatus",
)


class User(Base):
    """Registered PulseML user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), nullable=False, server_default=func.now()
    )

    datasets: Mapped[list["Dataset"]] = relationship(
        back_populates="owner", cascade="all,delete-orphan"
    )
    training_runs: Mapped[list["TrainingRun"]] = relationship(
        back_populates="owner", cascade="all,delete-orphan"
    )


class Dataset(Base):
    """Uploaded dataset metadata and storage details."""

    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    type: Mapped[str] = mapped_column(String(50), default="csv", nullable=False)
    meta: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), nullable=False, server_default=func.now()
    )

    owner: Mapped["User"] = relationship(back_populates="datasets")
    training_runs: Mapped[list["TrainingRun"]] = relationship(
        back_populates="dataset", cascade="all,delete-orphan"
    )


class ModelTemplate(Base):
    """Model template definition stored in the database."""

    __tablename__ = "model_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    default_hparams: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
    hyperparam_schema: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), nullable=False, server_default=func.now()
    )

    training_runs: Mapped[list["TrainingRun"]] = relationship(
        back_populates="model_template"
    )


class TrainingRun(Base):
    """Represents a training job configuration and lifecycle."""

    __tablename__ = "training_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    model_template_id: Mapped[int] = mapped_column(
        ForeignKey("model_templates.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(TrainingStatus, nullable=False, default="pending")
    hparams: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
    best_metric_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    best_metric_value: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    model_checkpoint_path: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )
    logs_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), nullable=False, server_default=func.now()
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    owner: Mapped["User"] = relationship(back_populates="training_runs")
    dataset: Mapped["Dataset"] = relationship(back_populates="training_runs")
    model_template: Mapped["ModelTemplate"] = relationship(
        back_populates="training_runs"
    )

