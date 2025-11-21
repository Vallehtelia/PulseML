"""Model template schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class HyperParamField(BaseModel):
    """Definition of a single hyperparameter."""

    key: str
    label: str
    type: str
    default: Any
    min: Optional[float] = None
    max: Optional[float] = None
    options: Optional[List[Any]] = None
    info: Optional[str] = None


class ModelTemplateSchema(BaseModel):
    """Representation of a model template."""

    id: int
    name: str
    task_type: str
    default_hparams: Dict[str, Any]
    hyperparam_schema: List[HyperParamField]

