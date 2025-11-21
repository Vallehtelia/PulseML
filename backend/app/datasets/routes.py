"""Dataset API routes."""

from typing import List

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, get_db
from ..db import models
from . import schemas, service

router = APIRouter()


@router.post(
    "/upload",
    response_model=schemas.DatasetUploadResponse,
    status_code=201,
)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str | None = Form(default=None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.DatasetUploadResponse:
    """Upload and analyze a CSV dataset."""

    dataset_service = service.DatasetService(db)
    dataset = await dataset_service.upload_dataset(
        current_user,
        file,
        name=name,
        description=description,
    )
    dataset_read = schemas.DatasetRead.model_validate(dataset)
    return schemas.DatasetUploadResponse(dataset=dataset_read, file_path=dataset.file_path)


@router.get("/", response_model=List[schemas.DatasetRead])
async def list_datasets(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[schemas.DatasetRead]:
    """List datasets for the authenticated user."""

    dataset_service = service.DatasetService(db)
    datasets = dataset_service.list_datasets(current_user)
    return [schemas.DatasetRead.model_validate(ds) for ds in datasets]


@router.get("/{dataset_id}", response_model=schemas.DatasetPreview)
async def get_dataset(
    dataset_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.DatasetPreview:
    """Retrieve dataset metadata and preview."""

    dataset_service = service.DatasetService(db)
    dataset = dataset_service.get_dataset(current_user, dataset_id)
    return dataset_service.dataset_preview(dataset)


@router.put("/{dataset_id}/schema", response_model=schemas.DatasetRead)
async def update_dataset_schema(
    dataset_id: int,
    payload: schemas.DatasetSchemaUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.DatasetRead:
    """Update dataset column roles."""

    dataset_service = service.DatasetService(db)
    dataset = dataset_service.get_dataset(current_user, dataset_id)
    updated = dataset_service.update_schema(dataset, payload)
    return schemas.DatasetRead.model_validate(updated)


@router.patch("/{dataset_id}", response_model=schemas.DatasetRead)
async def rename_dataset(
    dataset_id: int,
    payload: schemas.DatasetRename,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> schemas.DatasetRead:
    """Rename a dataset and update its description."""

    dataset_service = service.DatasetService(db)
    dataset = dataset_service.get_dataset(current_user, dataset_id)
    updated = dataset_service.rename_dataset(dataset, payload)
    return schemas.DatasetRead.model_validate(updated)


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(
    dataset_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a dataset and its associated file."""

    dataset_service = service.DatasetService(db)
    dataset = dataset_service.get_dataset(current_user, dataset_id)
    dataset_service.delete_dataset(dataset)