"""Model template registry for PulseML."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..db import models


@dataclass(frozen=True)
class HyperParamFieldDef:
    """Definition for a hyperparameter."""

    key: str
    label: str
    type: str
    default: object
    info: str
    min: float | None = None
    max: float | None = None
    options: List[object] | None = None


@dataclass(frozen=True)
class ModelTemplateDef:
    """Registry entry for model template."""

    id: int
    name: str
    task_type: str
    default_hparams: Dict[str, object]
    hyperparam_schema: List[HyperParamFieldDef] = field(default_factory=list)


MODEL_TEMPLATES: List[ModelTemplateDef] = [
    ModelTemplateDef(
        id=1,
        name="TCN",
        task_type="time_series_forecasting",
        default_hparams={
            "input_channels": 1,
            "output_size": 1,
            "levels": 4,
            "kernel_size": 3,
            "dropout": 0.1,
            "learning_rate": 0.001,
            "batch_size": 64,
            "epochs": 50,
        },
        hyperparam_schema=[
            HyperParamFieldDef(
                key="levels",
                label="TCN Levels",
                type="int",
                default=4,
                min=1,
                max=10,
                info="Number of residual blocks in the Temporal Convolutional Network.",
            ),
            HyperParamFieldDef(
                key="kernel_size",
                label="Kernel Size",
                type="int",
                default=3,
                min=2,
                max=9,
                info="Convolution kernel size for dilated causal convolutions.",
            ),
            HyperParamFieldDef(
                key="dropout",
                label="Dropout",
                type="float",
                default=0.1,
                min=0.0,
                max=0.9,
                info="Regularization via dropout probability.",
            ),
            HyperParamFieldDef(
                key="learning_rate",
                label="Learning Rate",
                type="float",
                default=0.001,
                min=1e-5,
                max=1e-1,
                info="Optimizer learning rate.",
            ),
            HyperParamFieldDef(
                key="batch_size",
                label="Batch Size",
                type="int",
                default=64,
                min=8,
                max=512,
                info="Mini-batch size for training.",
            ),
            HyperParamFieldDef(
                key="epochs",
                label="Epochs",
                type="int",
                default=50,
                min=1,
                max=500,
                info="Maximum number of training epochs.",
            ),
        ],
    ),
    ModelTemplateDef(
        id=2,
        name="LSTM",
        task_type="sequence_modeling",
        default_hparams={
            "hidden_size": 128,
            "num_layers": 2,
            "dropout": 0.2,
            "learning_rate": 0.001,
            "batch_size": 64,
            "epochs": 30,
        },
        hyperparam_schema=[
            HyperParamFieldDef(
                key="hidden_size",
                label="Hidden Size",
                type="int",
                default=128,
                min=16,
                max=1024,
                info="Number of units in each LSTM layer.",
            )
        ],
    ),
    ModelTemplateDef(
        id=3,
        name="CNN",
        task_type="classification",
        default_hparams={
            "num_filters": 64,
            "kernel_size": 3,
            "dropout": 0.3,
            "learning_rate": 0.0005,
        },
        hyperparam_schema=[
            HyperParamFieldDef(
                key="num_filters",
                label="Filters",
                type="int",
                default=64,
                min=8,
                max=512,
                info="Number of convolutional filters per layer.",
            )
        ],
    ),
    ModelTemplateDef(
        id=4,
        name="Transformer",
        task_type="sequence_modeling",
        default_hparams={
            "d_model": 256,
            "num_heads": 4,
            "num_layers": 4,
            "dropout": 0.1,
            "learning_rate": 0.0001,
        },
        hyperparam_schema=[
            HyperParamFieldDef(
                key="num_heads",
                label="Attention Heads",
                type="int",
                default=4,
                min=1,
                max=16,
                info="Number of attention heads per transformer block.",
            )
        ],
    ),
]


def get_templates() -> List[ModelTemplateDef]:
    """Return all registered templates."""

    return MODEL_TEMPLATES


def seed_default_templates(session: Session) -> None:
    """Persist default templates in the database if missing."""

    for template_def in MODEL_TEMPLATES:
        template = (
            session.query(models.ModelTemplate)
            .filter(models.ModelTemplate.name == template_def.name)
            .one_or_none()
        )
        payload = {
            "task_type": template_def.task_type,
            "default_hparams": template_def.default_hparams,
            "hyperparam_schema": [
                asdict(field) for field in template_def.hyperparam_schema
            ],
        }
        if template:
            for key, value in payload.items():
                setattr(template, key, value)
        else:
            template = models.ModelTemplate(
                id=template_def.id,
                name=template_def.name,
                **payload,
            )
            session.add(template)
    session.commit()
    session.execute(
        text(
            "SELECT setval("
            "pg_get_serial_sequence('model_templates','id'), "
            "(SELECT COALESCE(MAX(id), 1) FROM model_templates), "
            "true)"
        )
    )
    session.commit()

