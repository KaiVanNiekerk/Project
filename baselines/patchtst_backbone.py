from __future__ import annotations

import math
from typing import Optional

import torch
from torch import Tensor, nn
import torch.nn.functional as F

from src.revIN import RevIN


class PatchTST_backbone(nn.Module):
    """Compact PatchTST-style backbone with probabilistic dual forecast heads.

    The project does not currently contain the external PatchTST ``TSTiEncoder``
    implementation, so this class provides the same core contract locally:
    channel-independent patch embeddings, Transformer encoding over patches, and
    separate mean and uncertainty heads.
    """

    def __init__(
        self,
        c_in: int,
        context_window: int,
        target_window: int,
        patch_len: int = 16,
        stride: int = 8,
        max_seq_len: int = 1024,
        n_layers: int = 3,
        d_model: int = 128,
        n_heads: int = 8,
        d_ff: int = 256,
        dropout: float = 0.1,
        head_dropout: float = 0.0,
        revin: bool = True,
        affine: bool = True,
        sigma_floor: float = 0.05,
        **kwargs,
    ):
        super().__init__()
        if patch_len <= 0 or stride <= 0:
            raise ValueError("patch_len and stride must be positive")
        if patch_len > context_window:
            raise ValueError("patch_len cannot exceed context_window")
        if d_model % n_heads != 0:
            raise ValueError("d_model must be divisible by n_heads")

        self.c_in = c_in
        self.context_window = context_window
        self.target_window = target_window
        self.patch_len = patch_len
        self.stride = stride
        self.sigma_floor = sigma_floor
        self.revin = revin
        self.revin_layer = RevIN(c_in, affine=affine) if revin else None

        self.patch_count = 1 + (context_window - patch_len) // stride
        self.patch_projection = nn.Linear(patch_len, d_model)
        self.position_embedding = nn.Parameter(
            torch.zeros(1, self.patch_count, d_model)
        )
        nn.init.normal_(self.position_embedding, std=0.02)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_ff,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=False,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.encoder_norm = nn.LayerNorm(d_model)
        flattened_dim = self.patch_count * d_model
        self.head = Dual_Flatten_Head(
            c_in=c_in,
            flattened_dim=flattened_dim,
            target_window=target_window,
            head_dropout=head_dropout,
        )

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        """Return mean and raw sigma-head outputs in ``(B, variables, horizon)``."""
        if x.ndim != 3 or x.shape[1] != self.c_in or x.shape[2] != self.context_window:
            raise ValueError(
                f"Expected (B, {self.c_in}, {self.context_window}), got {tuple(x.shape)}"
            )

        if self.revin_layer is not None:
            # RevIN owns context statistics so forecast outputs use the same
            # instance-specific location and scale as K2VAE.
            x_time = self.revin_layer(x.transpose(1, 2), mode="norm")
            x = x_time.transpose(1, 2)

        patches = x.unfold(dimension=-1, size=self.patch_len, step=self.stride)
        # (B, variables, patch_count, patch_len) -> one patch sequence per variable.
        encoded = self.patch_projection(patches)
        encoded = encoded + self.position_embedding[:, : encoded.shape[2]]
        batch, variables, patch_count, _ = encoded.shape
        encoded = encoded.reshape(batch * variables, patch_count, -1)
        encoded = self.encoder_norm(self.encoder(encoded))
        encoded = encoded.reshape(batch, variables, patch_count, -1)
        return self.head(encoded)

    def denormalize_outputs(self, mu: Tensor, sigma_logits: Tensor) -> tuple[Tensor, Tensor]:
        """Restore mean and standard deviation to the input data scale."""
        sigma_norm = F.softplus(sigma_logits) + 1e-6
        if self.revin_layer is not None:
            mu_time = self.revin_layer(mu.transpose(1, 2), mode="denorm")
            sigma_time = self.revin_layer.denormalize_sigma(
                sigma_norm.transpose(1, 2)
            )
            mu = mu_time.transpose(1, 2)
            sigma_norm = sigma_time.transpose(1, 2)
        sigma = sigma_norm + self.sigma_floor
        return mu, sigma


class Dual_Flatten_Head(nn.Module):
    """Map encoded patch sequences to separate mean and sigma forecasts."""

    def __init__(self, c_in: int, flattened_dim: int, target_window: int, head_dropout: float):
        super().__init__()
        self.flatten = nn.Flatten(start_dim=2)
        self.dropout = nn.Dropout(head_dropout)
        self.linear_mu = nn.Linear(flattened_dim, target_window)
        self.linear_sigma = nn.Linear(flattened_dim, target_window)

    def forward(self, encoded: Tensor) -> tuple[Tensor, Tensor]:
        """Return ``(mu, sigma_logits)`` with shape ``(B, variables, horizon)``."""
        flattened = self.dropout(self.flatten(encoded))
        return self.linear_mu(flattened), self.linear_sigma(flattened)
