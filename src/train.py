import os
import random
import numpy as np
import torch
import wandb
 
from elbo import total_loss
from metrics import crps
from plotting import EpochHistory

class Trainer:
    """
    Orchestrates training for K2VAE.
 
    Owns: model, optimizer, dataloaders, lambda_rec, early-stop state,
    checkpoint policy. Does NOT own loss math (elbo.py) or the forward
    pass (K2VAE), those stay independent so they can be tested in
    isolation.
 
    Expects each batch from train_loader / val_loader to be a tuple
    (X_C, X_H) where:
    NEED TO HANDLE DIMENSIONS HERE as preprocessing spits out b n d currently:
        X_C : (Batch, input_dim, n) -> raw, patched+flattened context window
        X_H : (Batch, input_dim, m) -> raw, patched+flattened horizon window
              (same flattening as X_C, since mu/sigma from decoder_mu /
              decoder_sigma live in that same input_dim space, NOT
              X_H_hat, which is Koopman's measurement-space rollout)
    """
    def __init__(self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        train_loader,
        val_loader,
        lambda_rec: float = 1.0,
        kl_weight: float = 0.01, # matches reference weight_beta; fixed, not annealed
        device: str = "cpu",
        patience: int = 5,
        min_delta: float = 0.001,
        checkpoint_dir: str = "checkpoints",
        checkpoint_name: str = "k2vae_best.pt",
        grad_clip_norm: float = 1.0,
        use_wandb: bool = True,
        seed: int = 0):
        
        self.model = model.to(device)
        self.optimizer = optimizer
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.lambda_rec = lambda_rec
        self.device = device
        self.patience = patience
        self.min_delta = min_delta
        self.grad_clip_norm = grad_clip_norm
        self.use_wandb = use_wandb
        self.seed = seed
        self.kl_weight = kl_weight
        
        os.makedirs(checkpoint_dir, exist_ok=True)
        self.checkpoint_path = os.path.join(checkpoint_dir, checkpoint_name)
 
        # Early stopping / checkpoint state, both driven off the same
        # criterion (val total loss) so "best model saved" and "reason we
        # stopped" can never disagree with each other.
        self.best_val_loss = float("inf")
        self.best_epoch = -1
        self.epochs_since_improvement = 0
        self.nan_batches_skipped = 0 # Diagnostic
        
        # Per-epoch metric history, for plotting.py's plot_loss_curves().
        self.history = EpochHistory(
            epoch=[],
            train_total=[], val_total=[],
            train_elbo=[], val_elbo=[],
            train_nll=[], val_nll=[],
            train_kl=[], val_kl=[],
            train_rec=[], val_rec=[],
            skipped_batches=[],
        )   

    def _reconstruction_scale(self, X_C: torch.Tensor) -> torch.Tensor:
        """Return the RevIN scale used to stabilize reconstruction MSE.

        Models used for no-RevIN ablations receive unit scale so this helper
        preserves the trainer's loss contract without requiring RevIN.
        """
        revin = getattr(self.model, "revin", None)
        std = getattr(revin, "std", None)
        if std is None:
            return torch.ones(
                X_C.shape[0], 1, X_C.shape[2], device=X_C.device, dtype=X_C.dtype
            )
        return std
             
        # Actual training loop
    def fit(self, maxEpochs: int):
        for epoch in range(1, maxEpochs + 1):
            train_metrics = self._train_epoch(epoch)
            val_metrics = self._validate(epoch)
            #Logging
            print(f"epoch {epoch}: train_loss={train_metrics['total']:.4f}, val_loss={val_metrics['total']:.4f}")
            
            # Record this epoch's metrics for plot_loss_curves()
            self.history.epoch.append(epoch)
            self.history.train_total.append(train_metrics["total"])
            self.history.val_total.append(val_metrics["total"])
            self.history.train_elbo.append(train_metrics["elbo"])
            self.history.val_elbo.append(val_metrics["elbo"])
            self.history.train_nll.append(train_metrics["nll"])
            self.history.val_nll.append(val_metrics["nll"])
            self.history.train_kl.append(train_metrics["kl"])
            self.history.val_kl.append(val_metrics["kl"])
            self.history.train_rec.append(train_metrics["rec"])
            self.history.val_rec.append(val_metrics["rec"])
            self.history.skipped_batches.append(self.nan_batches_skipped)
            
            if self.use_wandb:
                wandb.log(
                    {
                         #  Track what is happening in the training loop, including epoch number and metrics for both train and validation sets
                        "epoch": epoch,
                        **{f"train_{k}": v for k, v in train_metrics.items()},
                        **{f"val_{k}": v for k, v in val_metrics.items()},
                        "nan_batches_skipped_total": self.nan_batches_skipped,
                    }
                )
                
            # Checks this epochs validation loss against best so far, and updates the best model if this epoch is an improvement. 
            # Also checks for early stopping conditions based on the number of epochs since the last improvement.
            improved = self._checkpoint_step(val_metrics["total"], epoch)
            stop = self._early_stop_step(improved)
    
            if stop:
                print(
                    f"Early stopping at epoch {epoch} "
                    f"(best epoch {self.best_epoch}, "
                    f"best val loss {self.best_val_loss:.6f})"
                )
                break
    
        return {                
            "best_epoch": self.best_epoch,
            "best_val_loss": self.best_val_loss,
            "nan_batches_skipped": self.nan_batches_skipped,
        }
            
    # training loop for a single epoch, returns the average metrics for the epoch
    def _train_epoch(self, epoch: int) -> dict:
        self.model.train()
        running = {"total": 0.0, "elbo": 0.0, "nll": 0.0, "kl": 0.0, "rec": 0.0}
        n_batches = 0
        
        for X_C, X_H in self.train_loader:
            X_C = X_C.to(self.device)
            X_H = X_H.to(self.device)
 
            # Wrapped because MultivariateNormal's Cholesky decomposition
            # (used inside kl_divergence_gaussian and K2VAE.reparameterize)
            # raises RuntimeError rather than returning NaN when P loses
            # positive-definiteness, an isfinite() check alone never
            # sees this, it just crashes the run.
            try:
                X_Rec, mu, sigma, Z_prime, P = self.model(X_C)
                std = self._reconstruction_scale(X_C)
                # The model returns RevIN-denormalized reconstructions, while
                # NLL remains in output space. Normalize only the MSE inputs so
                # large per-variable scales do not dominate its gradients.
                X_C_scaled = X_C / std
                X_Rec_scaled = X_Rec / std
 
                losses = total_loss(
                    X_H=X_H,
                    mu=mu,
                    sigma=sigma,
                    Z_prime=Z_prime,
                    P=P,
                    X_C=X_C_scaled,
                    X_Rec=X_Rec_scaled,
                    lambda_rec=self.lambda_rec,
                    beta=self.kl_weight,
                )
                loss = losses["total"]
            except RuntimeError as e:
                self.nan_batches_skipped += 1
                print(f"[train] skipped batch: {type(e).__name__}: {e}")
                continue
 
            if not torch.isfinite(loss):
                # Skip the optimizer step, not the whole epoch. A handful
                # of bad batches shouldn't corrupt the run, but repeated
                # occurrences should stay visible via the counter.
                self.nan_batches_skipped += 1
                continue
 
            self.optimizer.zero_grad() # ensures that each epoch gradient is computed independently, preventing accumulation from previous epochs
            loss.backward() # Computes gradients
            # Caps gradient spikes for stability, preventing exploding gradients that can destabilize training.
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), max_norm=self.grad_clip_norm
            )
            self.optimizer.step() # step forward
    
            # Bookkeeping
            for k in running:
                running[k] += losses[k].item()
            n_batches += 1
            
        # Guard to not crash model if all 0s within a batch
        n_batches = max(n_batches, 1)  # guard against an all-NaN epoch (Xero div)
        return {k: v / n_batches for k, v in running.items()} # returns the average metrics for the epoch
    
    # Validation loop for a single epoch, returns the average metrics for the epoch
    @torch.no_grad() # disables gradient computation for the validation loop, reducing memory usage and speeding up inference since gradients are not needed during evaluation.
    def _validate(self, epoch: int) -> dict:
        self.model.eval()
        running = {"total": 0.0, "elbo": 0.0, "nll": 0.0, "kl": 0.0, "rec": 0.0}
        n_batches = 0
 
        for X_C, X_H in self.val_loader:
            X_C = X_C.to(self.device)
            X_H = X_H.to(self.device)
 
            try:
                X_Rec, mu, sigma, Z_prime, P = self.model(X_C)
                std = self._reconstruction_scale(X_C)
                # Use the same reconstruction scale during validation as during
                # training so the checkpoint criterion has the same objective.
                X_C_scaled = X_C / std
                X_Rec_scaled = X_Rec / std

                #can be removed later 
                if n_batches == 0: # Just print for the first batch to avoid spam
                    print(f"[Epoch {epoch} Val] Sigma Mean: {sigma.mean().item():.6f}, Sigma Min: {sigma.min().item():.6f}")
 
                losses = total_loss(
                    X_H=X_H,
                    mu=mu,
                    sigma=sigma,
                    Z_prime=Z_prime,
                    P=P,
                    X_C=X_C_scaled,
                    X_Rec=X_Rec_scaled,
                    lambda_rec=self.lambda_rec,
                    beta=self.kl_weight, # Check to see if should be in val
                )
            except RuntimeError as e:
                print(f"[val] skipped batch: {type(e).__name__}: {e}")
                continue
 
            if not torch.isfinite(losses["total"]):
                continue
 
            for k in running:
                running[k] += losses[k].item()
            n_batches += 1
 
        # Guard to not crash model if all 0s within a batch
        n_batches = max(n_batches, 1)
        return {k: v / n_batches for k, v in running.items()}
    
    # Checkpoints
    def _checkpoint_step(self, val_total_loss: float, epoch: int) -> bool:
        improved = val_total_loss < (self.best_val_loss - self.min_delta)
        if improved:
            self.best_val_loss = val_total_loss
            self.best_epoch = epoch
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": self.model.state_dict(),
                    "optimizer_state_dict": self.optimizer.state_dict(),
                    "lambda_rec": self.lambda_rec,
                    "val_total_loss": val_total_loss,
                    "torch_rng_state": torch.get_rng_state(),
                    "numpy_rng_state": np.random.get_state(),
                    "python_rng_state": random.getstate(),
                    "seed": self.seed,
                },
                self.checkpoint_path,
            )
        return improved
 
    def _early_stop_step(self, improved: bool) -> bool:
        if improved:
            self.epochs_since_improvement = 0
        else:
            self.epochs_since_improvement += 1
        return self.epochs_since_improvement > self.patience
    
    
    def load_checkpoint(self, path: str = None) -> dict:
        """
            Loads a checkpoint saved by _checkpoint_step into self.model and
            self.optimizer. Defaults to this Trainer's own checkpoint_path (the
            best-val-loss checkpoint), but accepts an explicit path if loading
            a checkpoint saved by a different run.
            """
        ckpt_path = path or self.checkpoint_path
        checkpoint = torch.load(ckpt_path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        return checkpoint
    
    # Note the compute_crps flag is just used so we can run eval and test it w/o having to do the 
    # sampling process needed for crps
    @torch.no_grad()
    def evaluate(self, loader, compute_crps: bool = False, crps_samples: int = 100) -> dict:
        """
        Runs the model in eval mode over `loader`, intended for test_loader
        called once after training. Returns both the averaged loss
        components (same shape as _validate) and the raw per-batch tensors
        concatenated over the batch dim, for metrics.py and
        plot_data.PlotDataCollector to consume.

        Unlike _train_epoch and _validate, skipped batches here are NOT
        silently absorbed into a running average, since dropping test data
        changes what the reported metrics measure. They are counted and
        the count is returned.
        """
        self.model.eval()
        running = {"total": 0.0, "elbo": 0.0, "nll": 0.0, "kl": 0.0, "rec": 0.0, "crps": 0.0}
        n_batches = 0
        skipped = 0

        X_C_all, X_H_all, X_Rec_all, mu_all, sigma_all = [], [], [], [], []

        for X_C, X_H in loader:
            X_C = X_C.to(self.device)
            X_H = X_H.to(self.device)

            try:
                X_Rec, mu, sigma, Z_prime, P = self.model(X_C)
                std = self._reconstruction_scale(X_C)
                # Keep reported test loss consistent with the training and
                # validation reconstruction objective.
                X_C_scaled = X_C / std
                X_Rec_scaled = X_Rec / std

                losses = total_loss(
                    X_H=X_H,
                    mu=mu,
                    sigma=sigma,
                    Z_prime=Z_prime,
                    P=P,
                    X_C=X_C_scaled,
                    X_Rec=X_Rec_scaled,
                    lambda_rec=self.lambda_rec,
                    beta=self.kl_weight, # Check if should be in test
                )
            except RuntimeError as e:
                skipped += 1
                print(f"[test] skipped batch: {type(e).__name__}: {e}")
                continue

            if not torch.isfinite(losses["total"]):
                skipped += 1
                continue

            for k in running:
                if k != "crps":
                    running[k] += losses[k].item()
            n_batches += 1
            
            if compute_crps:                          
                pred_samples = self.model.sample_predictive(X_C, n_samples=crps_samples)
                running["crps"] += crps(pred_samples, X_H, sample_dim=0).item()

            # Moved to CPU immediately so this doesn't hold a growing GPU
            # buffer for the whole test set.
            X_C_all.append(X_C.cpu())
            X_H_all.append(X_H.cpu())
            X_Rec_all.append(X_Rec.cpu())
            mu_all.append(mu.cpu())
            sigma_all.append(sigma.cpu())

        if skipped:
            print(f"[test] {skipped} batch(es) skipped out of {skipped + n_batches}")

        # Guard to not crash model if all 0s within a batch
        n_batches_safe = max(n_batches, 1)
        avg_losses = {k: v / n_batches_safe for k, v in running.items()}

        return {
            "losses": avg_losses,
            "n_batches": n_batches,
            "n_skipped": skipped,
            "X_C": torch.cat(X_C_all, dim=0) if X_C_all else None,
            "X_H": torch.cat(X_H_all, dim=0) if X_H_all else None,
            "X_Rec": torch.cat(X_Rec_all, dim=0) if X_Rec_all else None,
            "mu": torch.cat(mu_all, dim=0) if mu_all else None,
            "sigma": torch.cat(sigma_all, dim=0) if sigma_all else None,
        }


# wandb sweep entry point lives in sweep.py (kept out of this file so it
# doesn't share a code path with normal single-config runs via run.py).
# Two-phase sweep: configs/sweep_continuous.yaml then configs/sweep_architecture.yaml
# (see the usage docstring at the top of sweep.py for the full chained workflow).