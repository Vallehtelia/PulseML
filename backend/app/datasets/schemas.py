"""Dataset API schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class DatasetColumnMeta(BaseModel):
    """Metadata about a dataset column."""

    name: str
    dtype: str
    missing_pct: float
    role: str
    stats: Dict[str, Any] | None = None


class DatasetMeta(BaseModel):
    """Metadata describing dataset summary."""

    n_rows: int | None = None
    n_columns: int | None = None
    columns: List[DatasetColumnMeta]
    suggested_roles: Dict[str, str]


class DatasetRead(BaseModel):
    """Dataset response model."""

    id: int
    owner_id: int
    name: str
    description: Optional[str] = None
    type: str
    meta: DatasetMeta
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetPreview(BaseModel):
    """Dataset preview response."""

    dataset: DatasetRead
    preview: List[Dict[str, Any]]


class DatasetUploadResponse(BaseModel):
    """Response after uploading a dataset."""

    dataset: DatasetRead
    file_path: str


class ColumnRoleUpdate(BaseModel):
    """Column role change definition."""

    name: str
    role: str


class DatasetSchemaUpdate(BaseModel):
    """Payload for column-role updates."""

    columns: List[ColumnRoleUpdate]

