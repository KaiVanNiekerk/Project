from __future__ import annotations

import math

import torch
import torch.nn.functional as F
from torch import Tensor, nn
from torch.distributions import Normal

from src.revIN import RevIN

class MLP(nn.Module):
    """Per-time-step MLP used by the time-invariant and time-varying paths."""
    def __init__(self, f_in: int, f_out: int, hidden_dim: int = 128, hidden_layers: int = 2, dropout: float = 0.05, activation: str = "tanh"):
        super().__init__()
        if hidden_layers < 1:
            raise ValueError("hidden_layers must be at least 1")
        activation_layer = {"relu": nn.ReLU, "tanh": nn.Tanh}.get(activation)
        if activation_layer is None:
            raise ValueError(f"Unsupported activation: {activation}")
        
        layers: list[nn.Module] = [nn.Linear(f_in, hidden_dim), activation_layer(), nn.Dropout(dropout)]
        for _ in range(hidden_layers - 2):
            layers.extend([nn.Linear(hidden_dim, hidden_dim), activation_layer(), nn.Dropout(dropout)])
        
        if hidden_layers == 1:
            layers = [nn.Linear(f_in, f_out)]
        else:
            layers.append(nn.Linear(hidden_dim, f_out))
            
        self.layers = nn.Sequential(*layers)

    def forward(self, x: Tensor) -> Tensor:
        """Apply the MLP independently to the final feature dimension."""
        return self.layers(x)


class RidgeDMD(nn.Module):
    """Batched ridge DMD with bounded rollout operators."""
    def __init__(self, ridge_lambda: float = 1e-3, max_operator_norm: float = 1.0):
        super().__init__()
        self.ridge_lambda = ridge_lambda
        self.max_operator_norm = max_operator_norm

    def fit(self, z: Tensor) -> Tensor:
        """Fit ``z[t+1] ~= z[t] @ K`` using Normal Equations and return the regularized operator."""
        batch, steps, dimension = z.shape
        if steps < 2:
            raise ValueError("DMD requires at least two snapshots")
        x, y = z[:, :-1], z[:, 1:]
        
        # 1. NORMAL EQUATIONS (Replaces slow lstsq SVD)
        xtx = torch.bmm(x.transpose(1, 2), x)
        xty = torch.bmm(x.transpose(1, 2), y)
        
        identity = torch.eye(dimension, device=z.device, dtype=z.dtype).expand(batch, -1, -1)
        system = xtx + self.ridge_lambda * identity
        
        # Analytical, fully vectorized backward pass
        operator = torch.linalg.solve(system, xty)
        
        # 2. FROBENIUS NORM (Replaces slow ord=2 spectral norm SVD)
        norm = torch.linalg.matrix_norm(operator, ord='fro', dim=(1, 2), keepdim=True)
        operator = operator * torch.clamp(self.max_operator_norm / norm.clamp_min(1e-12), max=1.0)
        
        return operator

    def forward(self, z: Tensor, pred_len: int) -> tuple[Tensor, Tensor]:
        """Return one-step reconstruction and bounded multi-step forecasts."""
        operator = self.fit(z)
        reconstruction = torch.cat((z[:, :1], torch.bmm(z[:, :-1], operator)), dim=1)
        current = z[:, -1:]
        forecasts = []
        for _ in range(pred_len):
            current = torch.bmm(current, operator)
            forecasts.append(current)
        return reconstruction, torch.cat(forecasts, dim=1)


class TimeInvariantKoopman(nn.Module):
    """Learnable time-invariant latent transition path."""
    def __init__(self, dynamic_dim: int, encoder: nn.Module, decoder: nn.Module, target_window: int):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.operator = nn.Linear(dynamic_dim, dynamic_dim, bias=False)
        nn.init.orthogonal_(self.operator.weight)
        self.target_window = target_window

    def forward(self, x: Tensor) -> Tensor:
        """Encode, apply the global operator, decode, and return forecast layout."""
        latent = self.operator(self.encoder(x.transpose(1, 2)))
        return self.decoder(latent).transpose(1, 2)


class TimeVaryingKoopman(nn.Module):
    """Segment a sequence and forecast with a locally fitted DMD operator."""
    def __init__(self, enc_in: int, input_len: int, target_window: int, seg_len: int, dynamic_dim: int, encoder: nn.Module, decoder: nn.Module, multistep: bool, ridge_lambda: float, max_operator_norm: float):
        super().__init__()
        self.enc_in = enc_in
        self.input_len = input_len
        self.target_window = target_window
        self.seg_len = seg_len
        self.frequency = math.ceil(input_len / seg_len)
        self.steps = math.ceil(target_window / seg_len)
        self.padding_len = self.frequency * seg_len - input_len
        self.encoder = encoder
        self.decoder = decoder
        self.dynamics = RidgeDMD(ridge_lambda, max_operator_norm)
        self.multistep = multistep

    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]:
        """Return backcast and forecast in ``(B,time,variables)`` layout."""
        if self.padding_len:
            prefix = x[:, -self.padding_len:, :]
            padded = torch.cat((prefix, x), dim=1)
        else:
            padded = x
        segments = padded.reshape(x.shape[0], self.frequency, self.seg_len, self.enc_in)
        encoded = self.encoder(segments.reshape(x.shape[0], self.frequency, -1))
        
        reconstructed, predicted = self.dynamics(encoded, self.steps)
        
        backcast = self.decoder(reconstructed).reshape(x.shape[0], self.frequency, self.seg_len, self.enc_in)
        forecast = self.decoder(predicted).reshape(x.shape[0], self.steps, self.seg_len, self.enc_in)
        
        backcast = backcast.reshape(x.shape[0], -1, self.enc_in)[:, -self.input_len:, :]
        forecast = forecast.reshape(x.shape[0], -1, self.enc_in)[:, :self.target_window, :]
        return backcast, forecast


class ProbabilisticKoopa(nn.Module):
    """Standalone probabilistic Koopa baseline for the shared raw-window API."""
    def __init__(self, c_in: int, context_window: int, target_window: int, seg_len: int = 8, dynamic_dim: int = 64, hidden_dim: int = 64, hidden_layers: int = 2, num_blocks: int = 2, multistep: bool = False, sigma_floor: float = 0.05, ridge_lambda: float = 1e-3, max_operator_norm: float = 1.0):
        super().__init__()
        if context_window % seg_len != 0:
            raise ValueError("context_window must be divisible by seg_len")
            
        self.context_window = context_window
        self.target_window = target_window
        self.c_in = c_in
        self.alpha = 0.2
        self.sigma_floor = sigma_floor
        self.revin = RevIN(c_in, affine=False)
        
        self.time_inv_encoder = MLP(context_window, dynamic_dim, hidden_dim, hidden_layers, activation="relu")
        self.time_inv_decoder = MLP(dynamic_dim, target_window, hidden_dim, hidden_layers, activation="relu")
        
        self.time_var_encoder = MLP(seg_len * c_in, dynamic_dim, hidden_dim, hidden_layers, activation="tanh")
        self.time_var_decoder = MLP(dynamic_dim, seg_len * c_in, hidden_dim, hidden_layers, activation="tanh")
        
        self.time_inv_paths = nn.ModuleList([
            TimeInvariantKoopman(dynamic_dim, self.time_inv_encoder, self.time_inv_decoder, target_window)
            for _ in range(num_blocks)
        ])
        self.time_var_paths = nn.ModuleList([
            TimeVaryingKoopman(c_in, context_window, target_window, seg_len, dynamic_dim, self.time_var_encoder, self.time_var_decoder, multistep, ridge_lambda, max_operator_norm)
            for _ in range(num_blocks)
        ])
        
        self.projector_mu = nn.Linear(target_window, target_window)
        self.projector_sigma = nn.Linear(target_window, target_window)

    def _frequency_filter(self, x: Tensor) -> Tensor:
        """Select the highest-energy frequency bins for the time-invariant path."""
        amplitudes = torch.fft.rfft(x, dim=1).abs().mean(dim=(0, 2))
        count = min(int(amplitudes.numel() * self.alpha), amplitudes.numel())
        if count > 0:
            return amplitudes.topk(count).indices
        return amplitudes.new_empty((0,), dtype=torch.long)

    def forward(self, x_enc: Tensor) -> Normal:
        """Return a Gaussian forecast for raw ``(B, context, variables)`` input."""
        if x_enc.ndim != 3 or x_enc.shape[1] != self.context_window or x_enc.shape[2] != self.c_in:
            raise ValueError(f"Expected (B, {self.context_window}, {self.c_in}), got {tuple(x_enc.shape)}")
            
        normalized = self.revin(x_enc, mode="norm")
        residual = normalized
        forecast = None
        
        mask_spectrum = self._frequency_filter(residual)
        
        for time_inv_path, time_var_path in zip(self.time_inv_paths, self.time_var_paths):
            
            # Inline Fourier splitting logic to prevent module instantiation in forward pass
            spectrum = torch.fft.rfft(residual, dim=1)
            mask = torch.ones_like(spectrum)
            if mask_spectrum.numel() > 0:
                mask[:, mask_spectrum, :] = 0
                
            time_varying = torch.fft.irfft(spectrum * mask, n=residual.shape[1], dim=1)
            time_invariant = residual - time_varying
            
            invariant_forecast = time_inv_path(time_invariant)
            time_var_backcast, time_var_forecast = time_var_path(time_varying)
            
            residual = residual - time_var_backcast
            
            if forecast is None:
                forecast = time_var_forecast + invariant_forecast
            else:
                forecast = forecast + time_var_forecast + invariant_forecast
                
        mu_norm = self.projector_mu(forecast.transpose(1, 2)).transpose(1, 2)
        sigma_logits = self.projector_sigma(forecast.transpose(1, 2)).transpose(1, 2)
        
        mu = self.revin(mu_norm, mode="denorm")
        sigma_norm = F.softplus(sigma_logits) + 1e-6
        sigma = self.revin.denormalize_sigma(sigma_norm) + self.sigma_floor
        
        return Normal(mu, sigma)

    def sample_predictive(self, x: Tensor, n_samples: int = 100) -> Tensor:
        """Return predictive draws with shape ``(samples, batch, horizon, variables)``."""
        if n_samples <= 0:
            raise ValueError("n_samples must be positive")
        return self.forward(x).rsample((n_samples,))