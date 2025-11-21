"""Dataset service layer."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List
from uuid import uuid4

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..db import models

from . import schemas, utils

logger = logging.getLogger(__name__)


class DatasetService:
    """Encapsulates dataset persistence and analysis logic."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def upload_dataset(
        self,
        user: models.User,
        upload_file: UploadFile,
        name: str,
        description: str | None = None,
    ) -> models.Dataset:
        """Store a dataset file and persist metadata."""

        original_name = upload_file.filename or f"dataset-{uuid4().hex}"
        dataset = models.Dataset(
            owner_id=user.id,
            name=name or original_name,
            description=description,
            file_path="",
            type="csv",
            meta={"columns": [], "suggested_roles": {}},
        )
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)

        dataset_dir = utils.dataset_storage_path(user.id, dataset.id)
        destination = dataset_dir / "raw.csv"
        await utils.save_upload_file(upload_file, destination)

        meta = utils.analyze_dataset(destination)
        dataset.file_path = str(destination)
        dataset.meta = meta
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        logger.info(
            "Stored dataset %s for user %s at %s", dataset.id, user.id, dataset.file_path
        )
        return dataset

    def list_datasets(self, user: models.User) -> List[models.Dataset]:
        """Return datasets owned by the user."""

        return (
            self.db.query(models.Dataset)
            .filter(models.Dataset.owner_id == user.id)
            .order_by(models.Dataset.created_at.desc())
            .all()
        )

    def get_dataset(self, user: models.User, dataset_id: int) -> models.Dataset:
        """Return a single dataset ensuring ownership."""

        dataset = (
            self.db.query(models.Dataset)
            .filter(
                models.Dataset.id == dataset_id,
                models.Dataset.owner_id == user.id,
            )
            .first()
        )
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
            )
        return dataset

    def dataset_preview(self, dataset: models.Dataset) -> schemas.DatasetPreview:
        """Return metadata with sample rows."""

        file_path = Path(dataset.file_path)
        data = utils.dataset_preview(file_path)
        dataset_read = schemas.DatasetRead.model_validate(dataset)
        return schemas.DatasetPreview(dataset=dataset_read, preview=data)

    def update_schema(
        self, dataset: models.Dataset, payload: schemas.DatasetSchemaUpdate
    ) -> models.Dataset:
        """Update dataset column roles."""

        meta = dataset.meta or {}
        columns = meta.get("columns", [])
        columns_by_name = {col["name"]: col for col in columns}

        for column_update in payload.columns:
            current = columns_by_name.get(column_update.name)
            if current:
                current["role"] = column_update.role

        meta["columns"] = list(columns_by_name.values())
        suggested_roles = meta.get("suggested_roles", {})
        for column_update in payload.columns:
            suggested_roles[column_update.name] = column_update.role
        meta["suggested_roles"] = suggested_roles

        dataset.meta = meta
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def rename_dataset(
        self, dataset: models.Dataset, payload: schemas.DatasetRename
    ) -> models.Dataset:
        """Rename a dataset and optionally update its description."""

        dataset.name = payload.name
        if payload.description is not None:
            dataset.description = payload.description
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        logger.info("Renamed dataset %s to %s", dataset.id, payload.name)
        return dataset

    def create_target_column(
        self, dataset: models.Dataset, source_column: str, target_column_name: str | None = None
    ) -> models.Dataset:
        """Create a target column by copying values from a source column."""

        file_path = Path(dataset.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dataset file not found"
            )

        # Read the dataset
        df = pd.read_csv(file_path)

        # Check if source column exists
        if source_column not in df.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source column '{source_column}' not found in dataset",
            )

        # Determine target column name
        if target_column_name is None:
            target_column_name = "target"
        
        # Check if target column already exists
        if target_column_name in df.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column '{target_column_name}' already exists",
            )

        # Copy the source column to target column
        df[target_column_name] = df[source_column].copy()

        # Save the updated dataset
        df.to_csv(file_path, index=False)
        logger.info(
            "Created target column '%s' from '%s' in dataset %s",
            target_column_name,
            source_column,
            dataset.id,
        )

        # Re-analyze the dataset to update metadata
        meta = utils.analyze_dataset(file_path)

        # Set the new target column's role to "target"
        columns = meta.get("columns", [])
        for col in columns:
            if col["name"] == target_column_name:
                col["role"] = "target"
                # Also update suggested_roles
                meta.setdefault("suggested_roles", {})[target_column_name] = "target"

        dataset.meta = meta
        dataset.file_path = str(file_path)
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)

        logger.info("Updated dataset %s metadata with new target column", dataset.id)
        return dataset

    def delete_dataset(self, dataset: models.Dataset) -> None:
        """Delete a dataset and its associated file."""

        dataset_id = dataset.id
        file_path = Path(dataset.file_path)
        
        # Delete from database first
        self.db.delete(dataset)
        self.db.commit()
        
        # Delete the file if it exists
        if file_path.exists():
            try:
                file_path.unlink()
                logger.info("Deleted dataset file: %s", file_path)
            except Exception as e:
                logger.warning("Failed to delete dataset file %s: %s", file_path, e)
        
        logger.info("Deleted dataset %s", dataset_id)

