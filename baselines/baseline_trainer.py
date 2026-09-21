import os
import random
import numpy as np
import torch
import wandb

from metrics import crps
from plotting import EpochHistory

class BaselineTrainer:
    """
    Orchestrates training for direct probabilistic baselines (PatchTST, Koopa)
    that optimize Gaussian Negative Log-Likelihood (NLL) directly on the horizon.
    """
    def __init__(self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        train_loader,
        val_loader,
        device: str = "cpu",
        patience: int = 5,
        min_delta: float = 0.001,
        checkpoint_dir: str = "checkpoints",
        checkpoint_name: str = "patchtst_best.pt",
        grad_clip_norm: float = 1.0,
        use_wandb: bool = True,
        seed: int = 0):
        
        self.model = model.to(device)
        self.optimizer = optimizer
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.patience = patience
        self.min_delta = min_delta
        self.grad_clip_norm = grad_clip_norm
        self.use_wandb = use_wandb
        self.seed = seed
        
        os.makedirs(checkpoint_dir, exist_ok=True)
        self.checkpoint_path = os.path.join(checkpoint_dir, checkpoint_name)
 
        self.best_val_loss = float("inf")
        self.best_epoch = -1
        self.epochs_since_improvement = 0
        self.nan_batches_skipped = 0
        
        self.history = EpochHistory(
            epoch=[],
            train_total=[], val_total=[],
            train_elbo=[], val_elbo=[],
            train_nll=[], val_nll=[],
            train_kl=[], val_kl=[],
            train_rec=[], val_rec=[],
            skipped_batches=[],
        )

    def fit(self, maxEpochs: int):
        for epoch in range(1, maxEpochs + 1):
            train_metrics = self._train_epoch(epoch)
            val_metrics = self._validate(epoch)
            
            print(f"[Baseline] Epoch {epoch}: train_nll={train_metrics['nll']:.4f}, val_nll={val_metrics['nll']:.4f}")
            
            self.history.epoch.append(epoch)
            for k in ["total", "elbo", "nll", "kl", "rec"]:
                getattr(self.history, f"train_{k}").append(train_metrics[k])
                getattr(self.history, f"val_{k}").append(val_metrics[k])
            self.history.skipped_batches.append(self.nan_batches_skipped)
            
            if self.use_wandb and wandb.run is not None:
                wandb.log({
                    "epoch": epoch,
                    **{f"train_{k}": v for k, v in train_metrics.items()},
                    **{f"val_{k}": v for k, v in val_metrics.items()},
                })
                
            improved = self._checkpoint_step(val_metrics["total"], epoch)
            if self._early_stop_step(improved):
                print(f"Early stopping at epoch {epoch} (best val loss {self.best_val_loss:.6f})")
                break
    
        return {
            "best_epoch": self.best_epoch, 
            "best_val_loss": self.best_val_loss,
            "best_val_nll": self.best_val_loss
        }

    def _train_epoch(self, epoch: int) -> dict:
        self.model.train()
        running_nll = 0.0
        n_batches = 0
        
        for X_C, X_H in self.train_loader:
            X_C = X_C.to(self.device)
            X_H = X_H.to(self.device)
 
            try:
                dist = self.model(X_C)
                loss = -dist.log_prob(X_H).mean()
            except Exception:
                self.nan_batches_skipped += 1
                continue
 
            if not torch.isfinite(loss):
                self.nan_batches_skipped += 1
                continue
 
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=self.grad_clip_norm)
            self.optimizer.step()
    
            running_nll += loss.item()
            n_batches += 1
            
        n_batches = max(n_batches, 1)
        avg_nll = running_nll / n_batches
        return {"total": avg_nll, "elbo": 0.0, "nll": avg_nll, "kl": 0.0, "rec": 0.0}
    
    @torch.no_grad()
    def _validate(self, epoch: int) -> dict:
        self.model.eval()
        running_nll = 0.0
        n_batches = 0
 
        for X_C, X_H in self.val_loader:
            X_C = X_C.to(self.device)
            X_H = X_H.to(self.device)
 
            try:
                dist = self.model(X_C)
                loss = -dist.log_prob(X_H).mean()
            except Exception:
                continue
 
            if not torch.isfinite(loss):
                continue
 
            running_nll += loss.item()
            n_batches += 1
 
        n_batches = max(n_batches, 1)
        avg_nll = running_nll / n_batches
        return {"total": avg_nll, "elbo": 0.0, "nll": avg_nll, "kl": 0.0, "rec": 0.0}
    
    def _checkpoint_step(self, val_loss: float, epoch: int) -> bool:
        improved = val_loss < (self.best_val_loss - self.min_delta)
        if improved:
            self.best_val_loss = val_loss
            self.best_epoch = epoch
            torch.save({
                "epoch": epoch,
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "val_total_loss": val_loss,
                "torch_rng_state": torch.get_rng_state(),
                "seed": self.seed,
            }, self.checkpoint_path)
        return improved
 
    def _early_stop_step(self, improved: bool) -> bool:
        if improved:
            self.epochs_since_improvement = 0
        else:
            self.epochs_since_improvement += 1
        return self.epochs_since_improvement > self.patience

    def load_checkpoint(self, path: str = None) -> dict:
        ckpt_path = path or self.checkpoint_path
        checkpoint = torch.load(ckpt_path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        return checkpoint

    @torch.no_grad()
    def evaluate(self, loader, compute_crps: bool = True, crps_samples: int = 100) -> dict:
        self.model.eval()
        running_nll, running_crps = 0.0, 0.0
        n_batches, skipped = 0, 0
        
        X_C_all, X_H_all, mu_all, sigma_all = [], [], [], []

        for X_C, X_H in loader:
            X_C = X_C.to(self.device)
            X_H = X_H.to(self.device)

            try:
                dist = self.model(X_C)
                loss = -dist.log_prob(X_H).mean()
            except Exception:
                skipped += 1
                continue

            if not torch.isfinite(loss):
                skipped += 1
                continue

            running_nll += loss.item()
            n_batches += 1
            
            if compute_crps:
                # Chunk CRPS along the batch dimension to avoid OOM from 100x100 broadcasting
                batch_crps = 0.0
                eval_chunk = 32
                for start_i in range(0, X_C.shape[0], eval_chunk):
                    end_i = min(start_i + eval_chunk, X_C.shape[0])
                    sub_xc = X_C[start_i:end_i]
                    sub_xh = X_H[start_i:end_i]
                    sub_samples = self.model.sample_predictive(sub_xc, n_samples=crps_samples)
                    batch_crps += crps(sub_samples, sub_xh, sample_dim=0).item() * (end_i - start_i)
                running_crps += batch_crps / X_C.shape[0]
                
            X_C_all.append(X_C.cpu())
            X_H_all.append(X_H.cpu())
            mu_all.append(dist.loc.cpu())
            sigma_all.append(dist.scale.cpu())

        n_batches_safe = max(n_batches, 1)
        return {
            "losses": {"total": running_nll / n_batches_safe, "nll": running_nll / n_batches_safe, "crps": running_crps / n_batches_safe, "elbo": 0.0, "kl": 0.0, "rec": 0.0},
            "n_batches": n_batches,
            "n_skipped": skipped,
            "X_C": torch.cat(X_C_all, dim=0) if X_C_all else None,
            "X_H": torch.cat(X_H_all, dim=0) if X_H_all else None,
            "mu": torch.cat(mu_all, dim=0) if mu_all else None,
            "sigma": torch.cat(sigma_all, dim=0) if sigma_all else None,
        }