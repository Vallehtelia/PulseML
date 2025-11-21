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
                info="Number of residual blocks in the TCN architecture. More levels increase the receptive field and model capacity, allowing the network to capture longer-term dependencies in time series data. Higher values may improve accuracy but increase training time.",
            ),
            HyperParamFieldDef(
                key="kernel_size",
                label="Kernel Size",
                type="int",
                default=3,
                min=2,
                max=9,
                info="Size of the convolution kernel for dilated causal convolutions. Larger kernels capture broader temporal patterns but require more parameters. Typically 3-5 works well for most time series.",
            ),
            HyperParamFieldDef(
                key="dropout",
                label="Dropout",
                type="float",
                default=0.1,
                min=0.0,
                max=0.9,
                info="Dropout rate for regularization (probability of dropping neurons during training). Helps prevent overfitting by randomly disabling connections. Use 0.1-0.3 for small datasets, lower values for large datasets. Set to 0 to disable.",
            ),
            HyperParamFieldDef(
                key="learning_rate",
                label="Learning Rate",
                type="float",
                default=0.001,
                min=1e-5,
                max=1e-1,
                info="Controls how quickly the model adapts to the problem. Typical range: 0.0001-0.01. Higher values train faster but may overshoot optimal weights. Lower values are more stable but slower. Use learning rate scheduling for best results.",
            ),
            HyperParamFieldDef(
                key="batch_size",
                label="Batch Size",
                type="int",
                default=64,
                min=8,
                max=512,
                info="Number of training samples processed before updating model weights. Larger batches provide more stable gradients but require more memory. Smaller batches add noise which can help generalization. Powers of 2 (32, 64, 128) are computationally efficient.",
            ),
            HyperParamFieldDef(
                key="epochs",
                label="Epochs",
                type="int",
                default=50,
                min=1,
                max=500,
                info="Maximum number of complete passes through the training dataset. More epochs allow the model to learn better but risk overfitting. Monitor validation loss to determine optimal stopping point. Early stopping is recommended.",
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
                info="Number of hidden units (memory cells) in each LSTM layer. Determines the model's capacity to remember and process sequential patterns. Higher values capture more complex patterns but increase computation and memory requirements. Start with 128-256 for most tasks.",
            ),
            HyperParamFieldDef(
                key="num_layers",
                label="Number of Layers",
                type="int",
                default=2,
                min=1,
                max=5,
                info="Number of stacked LSTM layers. More layers allow learning hierarchical representations of the sequence data. 2-3 layers work well for most problems. Deeper networks require more training data to avoid overfitting.",
            ),
            HyperParamFieldDef(
                key="dropout",
                label="Dropout",
                type="float",
                default=0.2,
                min=0.0,
                max=0.9,
                info="Dropout rate applied between LSTM layers for regularization. Helps prevent overfitting by randomly disabling connections during training. Use 0.2-0.4 for recurrent networks. Higher values for smaller datasets.",
            ),
            HyperParamFieldDef(
                key="learning_rate",
                label="Learning Rate",
                type="float",
                default=0.001,
                min=1e-5,
                max=1e-1,
                info="Step size for gradient descent optimization. Controls how quickly the model learns. RNNs are sensitive to learning rate - too high causes instability, too low causes slow convergence. Start with 0.001 and adjust based on training curves.",
            ),
            HyperParamFieldDef(
                key="batch_size",
                label="Batch Size",
                type="int",
                default=64,
                min=8,
                max=256,
                info="Number of sequences processed in parallel per training step. Larger batches stabilize training but need more memory. For sequence models, batch size affects backpropagation through time efficiency. Use 32-128 for most tasks.",
            ),
            HyperParamFieldDef(
                key="epochs",
                label="Epochs",
                type="int",
                default=30,
                min=1,
                max=500,
                info="Complete passes through the training data. LSTMs typically need fewer epochs than CNNs due to their sequential processing. Use early stopping to prevent overfitting. Monitor validation metrics to find optimal epoch count.",
            ),
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
                info="Number of convolutional filters in each layer. Each filter learns to detect different features or patterns in the input data. More filters increase model capacity and ability to learn complex features, but also increase computational cost. Start with 32-128 for most vision tasks.",
            ),
            HyperParamFieldDef(
                key="kernel_size",
                label="Kernel Size",
                type="int",
                default=3,
                min=2,
                max=7,
                info="Size of the convolution kernel (filter window). Common sizes are 3x3 and 5x5. Smaller kernels (3x3) are computationally efficient and work well when stacked in deep networks. Larger kernels capture more spatial context but are more expensive.",
            ),
            HyperParamFieldDef(
                key="dropout",
                label="Dropout",
                type="float",
                default=0.3,
                min=0.0,
                max=0.9,
                info="Dropout probability for regularization in fully connected layers. Randomly drops neurons during training to prevent overfitting and improve generalization. CNNs often use higher dropout rates (0.3-0.5) in dense layers after convolution blocks.",
            ),
            HyperParamFieldDef(
                key="learning_rate",
                label="Learning Rate",
                type="float",
                default=0.0005,
                min=1e-5,
                max=1e-1,
                info="Initial learning rate for the optimizer. CNNs typically use slightly lower rates than fully connected networks. Common range is 0.0001-0.001. Consider using learning rate scheduling (reduce on plateau) for better convergence.",
            ),
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
                key="d_model",
                label="Model Dimension",
                type="int",
                default=256,
                min=64,
                max=1024,
                info="Dimensionality of the model's internal representations (embedding size). Must be divisible by the number of attention heads. Higher dimensions allow more expressive representations but increase computational cost. Common values: 256, 512, 768.",
            ),
            HyperParamFieldDef(
                key="num_heads",
                label="Attention Heads",
                type="int",
                default=4,
                min=1,
                max=16,
                info="Number of parallel attention mechanisms in each transformer layer. Multiple heads allow the model to attend to different aspects of the sequence simultaneously. More heads increase expressiveness but require more computation. Must evenly divide d_model. Typical values: 4, 8, 12.",
            ),
            HyperParamFieldDef(
                key="num_layers",
                label="Number of Layers",
                type="int",
                default=4,
                min=1,
                max=12,
                info="Number of stacked transformer encoder/decoder blocks. More layers create a deeper network that can learn more complex patterns but require significantly more data and computation. 4-6 layers work well for most tasks. Deep transformers (12+) need large datasets.",
            ),
            HyperParamFieldDef(
                key="dropout",
                label="Dropout",
                type="float",
                default=0.1,
                min=0.0,
                max=0.5,
                info="Dropout rate applied to attention weights and feed-forward layers. Transformers are prone to overfitting on small datasets. Use 0.1-0.2 for large datasets, 0.3-0.5 for smaller datasets. Higher dropout helps with generalization but may slow convergence.",
            ),
            HyperParamFieldDef(
                key="learning_rate",
                label="Learning Rate",
                type="float",
                default=0.0001,
                min=1e-6,
                max=1e-2,
                info="Initial learning rate for optimization. Transformers are sensitive to learning rate and typically use lower values (0.0001-0.001). Strongly recommended to use a warmup schedule (gradual increase) followed by decay for stable training and better convergence.",
            ),
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

