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
        """Return placeholder metrics."""

        return schemas.TrainingRunMetrics(run_id=run.id, metrics=[])

    def stop_run(self, run: models.TrainingRun) -> models.TrainingRun:
        """Mark a run as stopped."""

        run.status = "stopped"
        run.finished_at = datetime.now(timezone.utc)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

