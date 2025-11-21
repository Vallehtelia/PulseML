"""Training API schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class TrainingRunCreate(BaseModel):
    """Payload for creating a training run."""

    dataset_id: int
    model_template_id: int
    hparams: Dict[str, Any]


class TrainingRunRead(BaseModel):
    """Training run representation."""

    id: int
    owner_id: int
    dataset_id: int
    model_template_id: int
    status: str
    hparams: Dict[str, Any]
    best_metric_name: Optional[str] = None
    best_metric_value: Optional[float] = None
    model_checkpoint_path: Optional[str] = None
    logs_path: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TrainingRunMetrics(BaseModel):
    """Placeholder training metrics response."""

    run_id: int
    metrics: List[Dict[str, Any]]

