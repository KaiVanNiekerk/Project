from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import torch

from src.elbo import gaussian_nll
from src.metrics import crps


@dataclass
class BaselineHistory:
    """Per-epoch NLL history for a probabilistic baseline."""

    epoch: list[int] = field(default_factory=list)
    train_nll: list[float] = field(default_factory=list)
    val_nll: list[float] = field(default_factory=list)


class BaselineTrainer:
    """Train and evaluate a probabilistic baseline on the shared data loaders."""

    def __init__(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        train_loader,
        val_loader,
        device: str = "cpu",
        checkpoint_dir: str = "checkpoints/baselines",
        checkpoint_name: str = "patchtst_best.pt",
        grad_clip_norm: float = 1.0,
        patience: int = 10,
    ):
        self.model = model.to(device)
        self.optimizer = optimizer
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.grad_clip_norm = grad_clip_norm
        self.patience = patience
        self.checkpoint_path = os.path.join(checkpoint_dir, checkpoint_name)
        os.makedirs(checkpoint_dir, exist_ok=True)
        self.history = BaselineHistory()
        self.best_val_loss = float("inf")
        self.best_epoch = -1
        self.epochs_since_improvement = 0
        self.skipped_batches = 0

    def _run_batch(self, x_context: torch.Tensor, x_horizon: torch.Tensor) -> torch.Tensor:
        """Compute the shared Gaussian NLL for one raw tensor batch."""
        distribution = self.model(x_context)
        return gaussian_nll(x_horizon, distribution.loc, distribution.scale)

    def fit(self, max_epochs: int) -> dict[str, Any]:
        """Train for at most ``max_epochs`` and checkpoint the best validation NLL."""
        for epoch in range(1, max_epochs + 1):
            train_nll = self._train_epoch()
            val_nll = self._validate()
            self.history.epoch.append(epoch)
            self.history.train_nll.append(train_nll)
            self.history.val_nll.append(val_nll)
            print(f"epoch {epoch}: train_nll={train_nll:.4f}, val_nll={val_nll:.4f}")

            if val_nll < self.best_val_loss:
                self.best_val_loss = val_nll
                self.best_epoch = epoch
                torch.save(
                    {
                        "epoch": epoch,
                        "model_state_dict": self.model.state_dict(),
                        "optimizer_state_dict": self.optimizer.state_dict(),
                        "val_nll": val_nll,
                    },
                    self.checkpoint_path,
                )
                self.epochs_since_improvement = 0
            else:
                self.epochs_since_improvement += 1
                if self.epochs_since_improvement > self.patience:
                    break

        return {
            "best_epoch": self.best_epoch,
            "best_val_nll": self.best_val_loss,
            "skipped_batches": self.skipped_batches,
        }

    def _train_epoch(self) -> float:
        self.model.train()
        total = 0.0
        batches = 0
        for x_context, x_horizon in self.train_loader:
            x_context = x_context.to(self.device)
            x_horizon = x_horizon.to(self.device)
            try:
                loss = self._run_batch(x_context, x_horizon)
            except RuntimeError as exc:
                self.skipped_batches += 1
                print(f"[baseline train] skipped batch: {type(exc).__name__}: {exc}")
                continue
            if not torch.isfinite(loss):
                self.skipped_batches += 1
                continue
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip_norm)
            self.optimizer.step()
            total += float(loss.detach())
            batches += 1
        return total / max(batches, 1)

    @torch.no_grad()
    def _validate(self) -> float:
        self.model.eval()
        total = 0.0
        batches = 0
        for x_context, x_horizon in self.val_loader:
            x_context = x_context.to(self.device)
            x_horizon = x_horizon.to(self.device)
            try:
                loss = self._run_batch(x_context, x_horizon)
            except RuntimeError:
                continue
            if torch.isfinite(loss):
                total += float(loss)
                batches += 1
        return total / max(batches, 1)

    def load_checkpoint(self, path: str | None = None) -> dict[str, Any]:
        """Load the best saved baseline state."""
        checkpoint = torch.load(path or self.checkpoint_path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        return checkpoint

    @torch.no_grad()
    def evaluate(self, loader, compute_crps: bool = True, crps_samples: int = 100) -> dict[str, Any]:
        """Evaluate NLL, CRPS, and return raw tensors for shared plotting."""
        self.model.eval()
        losses = []
        crps_values = []
        contexts, targets, means, sigmas = [], [], [], []
        skipped = 0
        for x_context, x_horizon in loader:
            x_context = x_context.to(self.device)
            x_horizon = x_horizon.to(self.device)
            try:
                distribution = self.model(x_context)
                loss = gaussian_nll(x_horizon, distribution.loc, distribution.scale)
                if not torch.isfinite(loss):
                    skipped += 1
                    continue
                losses.append(float(loss))
                if compute_crps:
                    samples = self.model.sample_predictive(x_context, crps_samples)
                    crps_values.append(float(crps(samples, x_horizon)))
                contexts.append(x_context.cpu())
                targets.append(x_horizon.cpu())
                means.append(distribution.loc.cpu())
                sigmas.append(distribution.scale.cpu())
            except RuntimeError:
                skipped += 1

        return {
            "losses": {
                "total": float(np.mean(losses)) if losses else float("nan"),
                "nll": float(np.mean(losses)) if losses else float("nan"),
                "elbo": float(np.mean(losses)) if losses else float("nan"),
                "kl": 0.0,
                "rec": 0.0,
                "crps": float(np.mean(crps_values)) if crps_values else float("nan"),
            },
            "n_batches": len(losses),
            "n_skipped": skipped,
            "X_C": torch.cat(contexts) if contexts else None,
            "X_H": torch.cat(targets) if targets else None,
            "X_Rec": None,
            "mu": torch.cat(means) if means else None,
            "sigma": torch.cat(sigmas) if sigmas else None,
        }
