"""Dataset helper utilities."""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from fastapi import UploadFile
from pandas.api import types as pd_types

from ..config import settings

logger = logging.getLogger(__name__)


def _safe_number(value: Any) -> float | None:
    """Convert numeric values to floats while preserving NaN as None."""

    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    return float(value)


def datasets_root() -> Path:
    """Return the base datasets directory, ensuring it exists."""

    path = Path(settings.DATA_DIR) / "datasets"
    path.mkdir(parents=True, exist_ok=True)
    return path


def dataset_storage_path(user_id: int, dataset_id: int) -> Path:
    """Return the dataset-specific directory."""

    path = datasets_root() / str(user_id) / str(dataset_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


async def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    """Persist an uploaded file to disk."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    logger.debug("Saving upload to %s", destination)
    contents = await upload_file.read()
    destination.write_bytes(contents)


def _column_role(name: str, series: pd.Series) -> str:
    """Infer the semantic role for a column."""

    lowered = name.lower()
    if lowered in {"target", "label", "y"}:
        return "target"
    if pd_types.is_datetime64_any_dtype(series):
        return "timestamp"
    return "feature"


def analyze_dataset(file_path: Path) -> Dict[str, Any]:
    """Analyze a CSV dataset and return metadata."""

    logger.info("Analyzing dataset at %s", file_path)
    # Read entire dataset to get accurate row count and statistics
    # For very large files, pandas is efficient with chunked reading internally
    df = pd.read_csv(file_path)
    n_rows, n_cols = df.shape
    columns: List[Dict[str, Any]] = []
    suggested_roles: Dict[str, str] = {}

    for column in df.columns:
        series = df[column]
        missing_pct = float(series.isna().mean() * 100) if len(series) else 0.0
        dtype = str(series.dtype)
        role = _column_role(column, series)
        stats: Dict[str, Any] | None = None

        if pd_types.is_numeric_dtype(series):
            stats = {
                "mean": _safe_number(series.mean()),
                "std": _safe_number(series.std()),
                "min": _safe_number(series.min()),
                "max": _safe_number(series.max()),
            }

        columns.append(
            {
                "name": column,
                "dtype": dtype,
                "missing_pct": round(missing_pct, 2),
                "role": role,
                "stats": stats,
            }
        )
        suggested_roles[column] = role

    metadata = {
        "n_rows": int(n_rows),
        "n_columns": int(n_cols),
        "columns": columns,
        "suggested_roles": suggested_roles,
    }
    return metadata


def dataset_preview(file_path: Path, limit: int = 20) -> List[Dict[str, Any]]:
    """Return a preview of the dataset."""

    df = pd.read_csv(file_path, nrows=limit)
    clean_df = df.where(pd.notnull(df), None)
    return clean_df.to_dict(orient="records")

