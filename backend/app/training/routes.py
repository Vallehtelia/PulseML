"""Training run API routes."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, get_db
from ..db import models
from . import schemas, service

router = APIRouter()


@router.post("/", response_model=schemas.TrainingRunRead, status_code=201)
async def create_training_run(
    payload: schemas.TrainingRunCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.TrainingRunRead:
    """Create a training run placeholder."""

    training_service = service.TrainingService(db)
    run = training_service.create_run(current_user, payload)
    return schemas.TrainingRunRead.model_validate(run)


@router.get("/", response_model=List[schemas.TrainingRunRead])
async def list_training_runs(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[schemas.TrainingRunRead]:
    """List training runs for a user."""

    training_service = service.TrainingService(db)
    runs = training_service.list_runs(current_user)
    return [schemas.TrainingRunRead.model_validate(run) for run in runs]


@router.get("/{run_id}", response_model=schemas.TrainingRunRead)
async def get_training_run(
    run_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.TrainingRunRead:
    """Retrieve a specific training run."""

    training_service = service.TrainingService(db)
    run = training_service.get_run(current_user, run_id)
    return schemas.TrainingRunRead.model_validate(run)


@router.get("/{run_id}/metrics", response_model=schemas.TrainingRunMetrics)
async def get_training_metrics(
    run_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.TrainingRunMetrics:
    """Return placeholder metrics for a run."""

    training_service = service.TrainingService(db)
    run = training_service.get_run(current_user, run_id)
    return training_service.get_metrics(run)


@router.post("/{run_id}/stop", response_model=schemas.TrainingRunRead)
async def stop_training_run(
    run_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.TrainingRunRead:
    """Stop a running training job."""

    training_service = service.TrainingService(db)
    run = training_service.get_run(current_user, run_id)
    stopped = training_service.stop_run(run)
    return schemas.TrainingRunRead.model_validate(stopped)

