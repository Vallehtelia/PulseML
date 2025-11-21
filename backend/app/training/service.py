"""Training service logic."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..db import models
from . import schemas


class TrainingService:
    """Manage training run persistence operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_dataset(self, user: models.User, dataset_id: int) -> models.Dataset:
        dataset = (
            self.db.query(models.Dataset)
            .filter(
                models.Dataset.id == dataset_id,
                models.Dataset.owner_id == user.id,
            )
            .first()
        )
        if not dataset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
        return dataset

    def _get_model_template(self, template_id: int) -> models.ModelTemplate:
        template = (
            self.db.query(models.ModelTemplate)
            .filter(models.ModelTemplate.id == template_id)
            .first()
        )
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Model template not found"
            )
        return template

    def create_run(
        self,
        user: models.User,
        payload: schemas.TrainingRunCreate,
    ) -> models.TrainingRun:
        """Create a training run placeholder."""

        dataset = self._get_dataset(user, payload.dataset_id)
        template = self._get_model_template(payload.model_template_id)

        # Validate dataset has required column roles
        meta = dataset.meta or {}
        columns = meta.get("columns", [])
        feature_cols = [
            col["name"]
            for col in columns
            if col.get("role") == "feature"
        ]
        target_cols = [
            col["name"]
            for col in columns
            if col.get("role") == "target"
        ]

        if not feature_cols:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Dataset has no columns marked as 'feature'. "
                    "Please set column roles in the dataset detail page."
                )
            )
        if not target_cols:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Dataset has no columns marked as 'target'. "
                    "Please set at least one column role to 'target' in the dataset detail page."
                )
            )

        run = models.TrainingRun(
            owner_id=user.id,
            dataset_id=dataset.id,
            model_template_id=template.id,
            status="pending",
            hparams=payload.hparams,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def list_runs(self, user: models.User) -> List[models.TrainingRun]:
        """List runs for a user."""

        return (
            self.db.query(models.TrainingRun)
            .filter(models.TrainingRun.owner_id == user.id)
            .order_by(models.TrainingRun.created_at.desc())
            .all()
        )

    def get_run(self, user: models.User, run_id: int) -> models.TrainingRun:
        """Return a single run if owned by user."""

        run = (
            self.db.query(models.TrainingRun)
            .filter(
                models.TrainingRun.id == run_id,
                models.TrainingRun.owner_id == user.id,
            )
            .first()
        )
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Training run not found"
            )
        return run

    def get_metrics(self, run: models.TrainingRun) -> schemas.TrainingRunMetrics:
        """Return training metrics from log file."""

        metrics = []
        
        if run.logs_path:
            import csv
            from pathlib import Path
            
            logs_path = Path(run.logs_path)
            if logs_path.exists():
                try:
                    with open(logs_path, "r") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            metrics.append({
                                "epoch": int(row.get("epoch", 0)),
                                "train_loss": float(row.get("train_loss", 0.0)),
                                "val_loss": float(row.get("val_loss", 0.0)),
                                "lr": float(row.get("lr", 0.0)),
                            })
                except Exception as e:
                    # If file exists but can't be read, return empty metrics
                    # Log error but don't fail the request
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to read metrics from {logs_path}: {e}")

        return schemas.TrainingRunMetrics(run_id=run.id, metrics=metrics)

    def stop_run(self, run: models.TrainingRun) -> models.TrainingRun:
        """Mark a run as stopped."""

        run.status = "stopped"
        run.finished_at = datetime.now(timezone.utc)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

