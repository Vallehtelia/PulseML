"""Worker process for executing training runs."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..config import settings
from ..db import models
from ..db.session import SessionLocal
from .tcn_trainer import TCNTrainer
from .utils import get_available_device, prepare_work_dir

logger = logging.getLogger(__name__)


class TrainingWorker:
    """Worker that polls for and executes training runs."""

    def __init__(
        self,
        poll_interval: float = 5.0,
        work_base_dir: Optional[Path] = None,
    ):
        self.poll_interval = poll_interval
        self.work_base_dir = work_base_dir or Path(settings.DATA_DIR) / "training_runs"
        self.work_base_dir.mkdir(parents=True, exist_ok=True)
        self.running = False

    def _claim_run(self, db: Session) -> Optional[models.TrainingRun]:
        """Safely claim a pending or queued run using database-level locking."""
        # Use SELECT FOR UPDATE SKIP LOCKED to handle concurrency
        # This ensures only one worker can claim a run at a time
        run = (
            db.query(models.TrainingRun)
            .filter(
                or_(
                    models.TrainingRun.status == "pending",
                    models.TrainingRun.status == "queued",
                )
            )
            .order_by(models.TrainingRun.created_at.asc())
            .with_for_update(skip_locked=True)
            .first()
        )

        if run:
            # Update status to running atomically
            from datetime import datetime, timezone

            run.status = "running"
            run.started_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(run)
            logger.info(f"Claimed training run {run.id}")
            return run

        return None

    def _execute_run(self, run: models.TrainingRun, db: Session) -> None:
        """Execute a training run."""
        logger.info(f"Executing training run {run.id}")

        # Refresh to check if run was stopped
        db.refresh(run)
        if run.status == "stopped":
            logger.info(f"Training run {run.id} was stopped, skipping execution")
            return

        try:
            # Get dataset and model template
            dataset = (
                db.query(models.Dataset)
                .filter(models.Dataset.id == run.dataset_id)
                .first()
            )
            if not dataset:
                raise ValueError(f"Dataset {run.dataset_id} not found")

            model_template = (
                db.query(models.ModelTemplate)
                .filter(models.ModelTemplate.id == run.model_template_id)
                .first()
            )
            if not model_template:
                raise ValueError(f"Model template {run.model_template_id} not found")

            # Merge default hyperparameters with run hyperparameters
            hparams = model_template.default_hparams.copy()
            hparams.update(run.hparams)

            # Prepare work directory
            work_dir = prepare_work_dir(self.work_base_dir, run.id)

            # Get device
            device = get_available_device()

            # Prepare dataset dict for trainer
            dataset_dict = {
                "file_path": dataset.file_path,
                "meta": dataset.meta,
            }

            # Create and run trainer
            if model_template.name == "TCN":
                trainer = TCNTrainer(
                    dataset=dataset_dict,
                    hparams=hparams,
                    work_dir=work_dir,
                    device=device,
                    run_id=run.id,
                    db_session=db,
                )
                trainer.run()
            else:
                raise ValueError(f"Unsupported model template: {model_template.name}")

            logger.info(f"Successfully completed training run {run.id}")

        except Exception as e:
            logger.error(f"Training run {run.id} failed: {e}", exc_info=True)
            # Update status to failed
            from datetime import datetime, timezone

            run.status = "failed"
            run.error_message = str(e)
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            raise

    def run_once(self) -> bool:
        """Execute one training run if available. Returns True if a run was processed."""
        db = SessionLocal()
        try:
            run = self._claim_run(db)
            if run:
                self._execute_run(run, db)
                return True
            return False
        except Exception as e:
            logger.error(f"Error in worker run_once: {e}", exc_info=True)
            return False
        finally:
            db.close()

    def start(self) -> None:
        """Start the worker loop."""
        self.running = True
        logger.info("Training worker started")

        while self.running:
            try:
                processed = self.run_once()
                if not processed:
                    # No runs available, sleep before next poll
                    time.sleep(self.poll_interval)
            except KeyboardInterrupt:
                logger.info("Worker interrupted by user")
                self.stop()
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {e}", exc_info=True)
                time.sleep(self.poll_interval)

    def stop(self) -> None:
        """Stop the worker loop."""
        logger.info("Stopping training worker")
        self.running = False


def main() -> None:
    """Entry point for the worker process."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = TrainingWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        worker.stop()


if __name__ == "__main__":
    main()

