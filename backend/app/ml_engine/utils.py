"""Utility helpers for ML engine stubs."""

from __future__ import annotations

import logging
from pathlib import Path

import torch

logger = logging.getLogger(__name__)


def get_available_device() -> str:
    """Return the device string to be used for training."""

    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def prepare_work_dir(base_dir: Path, run_id: int) -> Path:
    """Prepare a working directory for the training run."""

    work_dir = base_dir / f"run-{run_id}"
    work_dir.mkdir(parents=True, exist_ok=True)
    logger.debug("Prepared work directory %s", work_dir)
    return work_dir

