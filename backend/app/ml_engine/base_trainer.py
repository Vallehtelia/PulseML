"""Base trainer interface for PulseML."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


class BaseTrainer:
    """Abstract base trainer used by Phase 1 stub implementations."""

    def __init__(
        self,
        dataset: Dict[str, Any],
        hparams: Dict[str, Any],
        work_dir: Path,
        device: str,
    ) -> None:
        self.dataset = dataset
        self.hparams = hparams
        self.work_dir = work_dir
        self.device = device

    def run(self) -> None:
        """Execute the training routine."""

        raise NotImplementedError

