from __future__ import annotations

import torch
from torch import nn
from torch.distributions import Normal

from baselines.patchtst_backbone import PatchTST_backbone


class ProbabilisticPatchTST(nn.Module):
    """Probabilistic PatchTST wrapper using the project's raw tensor contract.

    Inputs are ``(batch, context time, variables)`` and returned distributions
    expose ``(batch, horizon time, variables)`` event-shaped tensors.
    """

    def __init__(
        self,
        c_in: int,
        context_window: int,
        target_window: int,
        patch_len: int = 16,
        stride: int = 8,
        dropout: float = 0.1,
        sigma_floor: float = 0.05,
        **kwargs,
    ):
        super().__init__()
        self.backbone = PatchTST_backbone(
            c_in=c_in,
            context_window=context_window,
            target_window=target_window,
            patch_len=patch_len,
            stride=stride,
            dropout=dropout,
            revin=True,
            sigma_floor=sigma_floor,
            **kwargs,
        )

    def forward(self, x: torch.Tensor) -> Normal:
        """Return a Normal distribution for a raw ``(B, T, N)`` context."""
        if x.ndim != 3:
            raise ValueError(f"Expected (B, time, variables), got {tuple(x.shape)}")
        mu, sigma_logits = self.backbone(x.transpose(1, 2))
        mu, sigma = self.backbone.denormalize_outputs(mu, sigma_logits)
        return Normal(mu.transpose(1, 2), sigma.transpose(1, 2))

    def sample_predictive(self, x: torch.Tensor, n_samples: int = 100) -> torch.Tensor:
        """Return ``n_samples`` predictive draws as ``(S, B, H, N)``."""
        if n_samples <= 0:
            raise ValueError("n_samples must be positive")
        return self.forward(x).rsample((n_samples,))
