"""TCN trainer implementation for PulseML."""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, Dataset as TorchDataset

from ..config import settings
from .base_trainer import BaseTrainer

logger = logging.getLogger(__name__)


class TemporalBlock(nn.Module):
    """Temporal block for TCN architecture."""

    def __init__(
        self,
        n_inputs: int,
        n_outputs: int,
        kernel_size: int,
        stride: int,
        dilation: int,
        padding: int,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.conv1 = nn.Conv1d(
            n_inputs,
            n_outputs,
            kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
        )
        self.chomp1 = Chomp1d(padding)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(dropout)

        self.conv2 = nn.Conv1d(
            n_outputs,
            n_outputs,
            kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
        )
        self.chomp2 = Chomp1d(padding)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(dropout)

        self.net = nn.Sequential(
            self.conv1,
            self.chomp1,
            self.relu1,
            self.dropout1,
            self.conv2,
            self.chomp2,
            self.relu2,
            self.dropout2,
        )

        self.downsample = (
            nn.Conv1d(n_inputs, n_outputs, 1) if n_inputs != n_outputs else None
        )
        self.relu = nn.ReLU()
        self.init_weights()

    def init_weights(self):
        """Initialize weights."""
        self.conv1.weight.data.normal_(0, 0.01)
        self.conv2.weight.data.normal_(0, 0.01)
        if self.downsample is not None:
            self.downsample.weight.data.normal_(0, 0.01)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        out = self.net(x)
        res = x if self.downsample is None else self.downsample(x)
        return self.relu(out + res)


class Chomp1d(nn.Module):
    """Remove padding from the right side."""

    def __init__(self, chomp_size: int):
        super().__init__()
        self.chomp_size = chomp_size

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        if self.chomp_size == 0:
            return x
        return x[:, :, : -self.chomp_size].contiguous()


class TCN(nn.Module):
    """Temporal Convolutional Network for time series forecasting."""

    def __init__(
        self,
        input_size: int,
        output_size: int,
        num_channels: list[int],
        kernel_size: int = 3,
        dropout: float = 0.1,
    ):
        super().__init__()
        layers = []
        num_levels = len(num_channels)
        for i in range(num_levels):
            dilation_size = 2 ** i
            in_channels = input_size if i == 0 else num_channels[i - 1]
            out_channels = num_channels[i]
            layers += [
                TemporalBlock(
                    in_channels,
                    out_channels,
                    kernel_size,
                    stride=1,
                    dilation=dilation_size,
                    padding=(kernel_size - 1) * dilation_size,
                    dropout=dropout,
                )
            ]

        self.network = nn.Sequential(*layers)
        self.linear = nn.Linear(num_channels[-1], output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        # x shape: (batch, features, sequence_length)
        y = self.network(x)
        # Take the last time step
        y = y[:, :, -1]
        return self.linear(y)


class TimeSeriesDataset(TorchDataset):
    """PyTorch dataset for time series data."""

    def __init__(
        self,
        features: np.ndarray,
        targets: np.ndarray,
        sequence_length: int = 10,
    ):
        self.features = features
        self.targets = targets
        self.sequence_length = sequence_length

    def __len__(self) -> int:
        return len(self.features) - self.sequence_length + 1

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        end_idx = idx + self.sequence_length
        x = self.features[idx:end_idx]
        y = self.targets[end_idx - 1]
        return torch.FloatTensor(x.T), torch.FloatTensor([y])


class TCNTrainer(BaseTrainer):
    """TCN trainer implementation."""

    def __init__(
        self,
        dataset: Dict[str, Any],
        hparams: Dict[str, Any],
        work_dir: Path,
        device: str,
        run_id: int,
        db_session: Any,
    ):
        super().__init__(dataset, hparams, work_dir, device)
        self.run_id = run_id
        self.db_session = db_session
        self.sequence_length = hparams.get("sequence_length", 10)
        self.train_ratio = hparams.get("train_ratio", 0.7)
        self.val_ratio = hparams.get("val_ratio", 0.15)
        # test_ratio = 1 - train_ratio - val_ratio

    def _load_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler, StandardScaler]:
        """Load and preprocess data from dataset."""
        dataset_path = Path(self.dataset["file_path"])
        # If path doesn't exist, try resolving relative to DATA_DIR
        if not dataset_path.exists():
            dataset_path = Path(settings.DATA_DIR) / dataset_path
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {self.dataset['file_path']}")

        df = pd.read_csv(dataset_path)
        meta = self.dataset.get("meta", {})
        columns = meta.get("columns", [])

        # Identify feature, target, and timestamp columns
        feature_cols = [
            col["name"]
            for col in columns
            if col.get("role") == "feature"
            and col["name"] in df.columns
            and col.get("role") != "timestamp"  # Exclude timestamps
        ]
        target_cols = [
            col["name"]
            for col in columns
            if col.get("role") == "target" and col["name"] in df.columns
        ]

        if not feature_cols:
            available_roles = {col.get("role", "feature") for col in columns}
            raise ValueError(
                f"No feature columns found in dataset. "
                f"Available column roles: {available_roles}. "
                f"Please set at least one column role to 'feature' in the dataset schema."
            )
        if not target_cols:
            available_roles = {col.get("role", "feature") for col in columns}
            raise ValueError(
                f"No target columns found in dataset. "
                f"Available column roles: {available_roles}. "
                f"Please set at least one column role to 'target' in the dataset schema. "
                f"You can do this in the dataset detail page."
            )

        # Use first target column if multiple
        target_col = target_cols[0]

        # Extract features and target
        X_df = df[feature_cols].copy()
        y_series = df[target_col].copy()

        # Filter out non-numeric columns from features
        numeric_feature_cols = []
        for col in feature_cols:
            if pd.api.types.is_numeric_dtype(X_df[col]):
                numeric_feature_cols.append(col)
            else:
                logger.warning(
                    f"Skipping non-numeric feature column '{col}' (dtype: {X_df[col].dtype})"
                )

        if not numeric_feature_cols:
            raise ValueError(
                "No numeric feature columns found. All feature columns must be numeric (int64, float64)."
            )

        X_df = X_df[numeric_feature_cols]
        X = X_df.values

        # Ensure target is numeric
        if not pd.api.types.is_numeric_dtype(y_series):
            raise ValueError(
                f"Target column '{target_col}' must be numeric (int64, float64), got {y_series.dtype}"
            )

        y = y_series.values

        # Handle missing values - use infer_objects to avoid FutureWarning
        X_df_clean = pd.DataFrame(X).ffill().bfill()
        X = X_df_clean.infer_objects(copy=False).values
        y_series_clean = pd.Series(y).ffill().bfill()
        y = y_series_clean.infer_objects(copy=False).values

        # Normalize features
        feature_scaler = StandardScaler()
        X_scaled = feature_scaler.fit_transform(X)

        # Normalize target
        target_scaler = StandardScaler()
        y_scaled = target_scaler.fit_transform(y.reshape(-1, 1)).flatten()

        # Split data
        n_total = len(X_scaled)
        n_train = int(n_total * self.train_ratio)
        n_val = int(n_total * self.val_ratio)

        X_train = X_scaled[:n_train]
        y_train = y_scaled[:n_train]
        X_val = X_scaled[n_train : n_train + n_val]
        y_val = y_scaled[n_train : n_train + n_val]
        X_test = X_scaled[n_train + n_val :]
        y_test = y_scaled[n_train + n_val :]

        logger.info(
            f"Data split: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}"
        )

        return (
            X_train,
            y_train,
            X_val,
            y_val,
            X_test,
            y_test,
            feature_scaler,
            target_scaler,
        )

    def _build_model(self, input_size: int) -> TCN:
        """Build TCN model from hyperparameters."""
        levels = self.hparams.get("levels", 4)
        kernel_size = self.hparams.get("kernel_size", 3)
        dropout = self.hparams.get("dropout", 0.1)
        output_size = self.hparams.get("output_size", 1)

        # Create channel sizes (doubling each level)
        num_channels = [32 * (2 ** i) for i in range(levels)]
        # Cap at 256 to avoid excessive memory
        num_channels = [min(c, 256) for c in num_channels]

        model = TCN(
            input_size=input_size,
            output_size=output_size,
            num_channels=num_channels,
            kernel_size=kernel_size,
            dropout=dropout,
        ).to(self.device)

        logger.info(f"Built TCN model: {levels} levels, {num_channels} channels")
        return model

    def _train_epoch(
        self,
        model: TCN,
        train_loader: DataLoader,
        optimizer: optim.Optimizer,
        criterion: nn.Module,
    ) -> float:
        """Train for one epoch."""
        model.train()
        total_loss = 0.0
        n_batches = 0

        for batch_features, batch_targets in train_loader:
            batch_features = batch_features.to(self.device)
            batch_targets = batch_targets.to(self.device)

            optimizer.zero_grad()
            outputs = model(batch_features)
            loss = criterion(outputs, batch_targets)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            n_batches += 1

        return total_loss / n_batches if n_batches > 0 else 0.0

    def _validate(
        self, model: TCN, val_loader: DataLoader, criterion: nn.Module
    ) -> float:
        """Validate model."""
        model.eval()
        total_loss = 0.0
        n_batches = 0

        with torch.no_grad():
            for batch_features, batch_targets in val_loader:
                batch_features = batch_features.to(self.device)
                batch_targets = batch_targets.to(self.device)

                outputs = model(batch_features)
                loss = criterion(outputs, batch_targets)

                total_loss += loss.item()
                n_batches += 1

        return total_loss / n_batches if n_batches > 0 else 0.0

    def _evaluate_test(
        self, model: TCN, test_loader: DataLoader, target_scaler: StandardScaler
    ) -> Dict[str, float]:
        """Evaluate on test set and return metrics."""
        model.eval()
        predictions = []
        targets = []

        with torch.no_grad():
            for batch_features, batch_targets in test_loader:
                batch_features = batch_features.to(self.device)
                outputs = model(batch_features)
                predictions.extend(outputs.cpu().numpy())
                targets.extend(batch_targets.cpu().numpy())

        predictions = np.array(predictions).flatten()
        targets = np.array(targets).flatten()

        # Inverse transform
        predictions = target_scaler.inverse_transform(predictions.reshape(-1, 1)).flatten()
        targets = target_scaler.inverse_transform(targets.reshape(-1, 1)).flatten()

        # Calculate metrics
        mse = np.mean((predictions - targets) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions - targets))
        mape = np.mean(np.abs((targets - predictions) / (targets + 1e-8))) * 100

        return {
            "test_rmse": float(rmse),
            "test_mse": float(mse),
            "test_mae": float(mae),
            "test_mape": float(mape),
        }

    def run(self) -> None:
        """Execute the training routine."""
        logger.info(f"Starting TCN training for run {self.run_id}")

        try:
            # Load data
            (
                X_train,
                y_train,
                X_val,
                y_val,
                X_test,
                y_test,
                feature_scaler,
                target_scaler,
            ) = self._load_data()

            input_size = X_train.shape[1]

            # Create datasets
            train_dataset = TimeSeriesDataset(
                X_train, y_train, sequence_length=self.sequence_length
            )
            val_dataset = TimeSeriesDataset(
                X_val, y_val, sequence_length=self.sequence_length
            )
            test_dataset = TimeSeriesDataset(
                X_test, y_test, sequence_length=self.sequence_length
            )

            batch_size = self.hparams.get("batch_size", 64)
            train_loader = DataLoader(
                train_dataset, batch_size=batch_size, shuffle=True
            )
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
            test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

            # Build model
            model = self._build_model(input_size)

            # Setup training
            learning_rate = self.hparams.get("learning_rate", 0.001)
            optimizer = optim.Adam(model.parameters(), lr=learning_rate)
            criterion = nn.MSELoss()

            # Training loop
            epochs = self.hparams.get("epochs", 50)
            best_val_loss = float("inf")
            best_model_path = self.work_dir / "best_model.pt"
            logs_path = self.work_dir / "training_log.csv"

            # Initialize CSV log
            with open(logs_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["epoch", "train_loss", "val_loss", "lr"])

            # Get run object for updating progress
            from ..db import models
            run = (
                self.db_session.query(models.TrainingRun)
                .filter(models.TrainingRun.id == self.run_id)
                .first()
            )
            if run:
                run.device = self.device
                run.total_epochs = epochs
                self.db_session.commit()

            logger.info(f"Training for {epochs} epochs on {self.device}")

            for epoch in range(epochs):
                train_loss = self._train_epoch(model, train_loader, optimizer, criterion)
                val_loss = self._validate(model, val_loader, criterion)

                # Learning rate (current)
                current_lr = optimizer.param_groups[0]["lr"]

                # Log to CSV
                with open(logs_path, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([epoch + 1, train_loss, val_loss, current_lr])

                # Save best model
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    torch.save(
                        {
                            "epoch": epoch + 1,
                            "model_state_dict": model.state_dict(),
                            "optimizer_state_dict": optimizer.state_dict(),
                            "val_loss": val_loss,
                        },
                        best_model_path,
                    )

                # Update current epoch in database every epoch
                if run:
                    run.current_epoch = epoch + 1
                    self.db_session.commit()

                if (epoch + 1) % 10 == 0:
                    logger.info(
                        f"Epoch {epoch + 1}/{epochs}: train_loss={train_loss:.4f}, "
                        f"val_loss={val_loss:.4f}, lr={current_lr:.6f}"
                    )

            # Load best model and evaluate on test set
            checkpoint = torch.load(best_model_path)
            model.load_state_dict(checkpoint["model_state_dict"])
            test_metrics = self._evaluate_test(model, test_loader, target_scaler)

            logger.info(f"Test metrics: {test_metrics}")

            # Update database
            from ..db import models
            from datetime import datetime, timezone

            run = (
                self.db_session.query(models.TrainingRun)
                .filter(models.TrainingRun.id == self.run_id)
                .first()
            )

            if run:
                run.status = "completed"
                run.best_metric_name = "val_loss"
                run.best_metric_value = float(best_val_loss)
                run.model_checkpoint_path = str(best_model_path)
                run.logs_path = str(logs_path)
                run.metrics_summary = test_metrics
                run.device = self.device
                run.current_epoch = epochs
                run.total_epochs = epochs
                run.finished_at = datetime.now(timezone.utc)
                self.db_session.commit()
                logger.info(f"Updated training run {self.run_id} in database")

        except Exception as e:
            logger.error(f"Training failed for run {self.run_id}: {e}", exc_info=True)
            # Update database with error
            from ..db import models
            from datetime import datetime, timezone

            run = (
                self.db_session.query(models.TrainingRun)
                .filter(models.TrainingRun.id == self.run_id)
                .first()
            )
            if run:
                run.status = "failed"
                run.error_message = str(e)
                run.finished_at = datetime.now(timezone.utc)
                self.db_session.commit()
            raise
