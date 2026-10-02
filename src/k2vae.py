import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange
from torch.distributions.normal import Normal
from torch.distributions.multivariate_normal import MultivariateNormal
from koopman import KoopmanNet
from integrator import Integrator
from kalman import KalmanNet
from preprocessing import k2vae_integration
from revIN import RevIN

class K2VAE(nn.Module):
    def __init__(self, input_dim: int, d: int, m: int, n: int, integrator_args: dict, num_vars: int, patch_size: int, hidden_dim: int = 128, hidden_layers: int = 3, sigma_floor: float = 5e-2, use_revin: bool = True, koopman_mode: str = "mixed"):
        """
        Args:
            input_dim (int): The size of a flattened multivariate patch (Variables * Patch Size).
            d (int): The dimension of the latent measurement space.
            m (int): The number of patches in the future prediction horizon.
            n (int): The number of patches in the past context window.
            integrator_args (dict): Hyperparameters for the Integrator Transformer network.
            hidden_dim (int, optional): Number of neurons in the hidden layers of the MLPs. Defaults to 128.
            hidden_layers (int, optional): Number of hidden layers in the decoder MLPs. Defaults to 3.
            sigma_floor (float, optional): Minimum output standard deviation in
                standardized data space. Defaults to 0.05.
            use_revin (bool, optional): Whether to apply instance normalization.
                Defaults to True.
            koopman_mode (str, optional): Local/global Koopman combination:
                ``static``, ``dynamic``, or ``mixed``. Defaults to ``mixed``.
        """
        super().__init__()
        self.d = d
        self.m = m
        self.n = n
        self.num_vars = num_vars
        self.patch_size = patch_size
        self.sigma_floor = sigma_floor
        self.use_revin = use_revin
        self.revin = RevIN(num_vars=num_vars, affine=True) if use_revin else None

        self.patch_embedding = nn.Linear(input_dim, d) # Projects the input patches to the latent measurement space 
        self.koopman = KoopmanNet(d=d, hidden_dim=hidden_dim, koopman_mode=koopman_mode)  # Evaluates the measurement function and Koopman operator
        self.integrator = Integrator(**integrator_args)  # Maps the Koopman residual to a control-input sequence over the prediction horizon 
        self.kalman = KalmanNet(state_dim = d) # # Refines linear state predictions and outputs process uncertainty (covariance)

        # Decodes latent states back into the mean of the original input dimensions
        # make decoder allows for multipel hidden layers.
        def _make_decoder(hidden_layers: int) -> nn.Sequential:
            layers = [nn.Linear(d, hidden_dim), nn.ReLU()]
            for _ in range(hidden_layers - 1):
                layers += [nn.Linear(hidden_dim, hidden_dim), nn.ReLU()]
            layers.append(nn.Linear(hidden_dim, input_dim))
            return nn.Sequential(*layers)
        
        self.decoder_mu = _make_decoder(hidden_layers=hidden_layers)
        self.decoder_sigma = _make_decoder(hidden_layers=hidden_layers)

    def reparameterize(self, Z_prime: torch.Tensor, P: torch.Tensor) -> torch.Tensor:
        """
        Samples a latent state from the KalmanNet's predicted distribution Q(Z|X) = N(Z', P)
        using the reparameterization trick to maintain gradient flow.

        Args:
            Z_prime (torch.Tensor): The Kalman-refined future latent mean. Shape: (Batch, d, m)
            P (torch.Tensor): The Kalman process covariance matrices. Shape: (Batch, m, d, d)

        Returns:
            torch.Tensor: The sampled latent state. Shape: (Batch, d, m)
        """
        if self.training: # During training, we sample from the distribution to allow for stochasticity and gradient flow

            Z_prime_T = Z_prime.transpose(1, 2)  # (B, m, d)

            # Create a MVN distribution using the Kalman covariance P
            jitter = torch.eye(self.d, device=P.device).expand_as(P) * 1e-5 # Add minor variance to the diagonal of P for positive definiteness
            dist = MultivariateNormal(loc=Z_prime_T, covariance_matrix=P + jitter) 

            Z_sample_T = dist.rsample()  # (B, m, d), this uses the reparameterization trick to allow gradients to flow through the sampling process
            return Z_sample_T.transpose(1, 2)  # (B, d, m)

        return Z_prime # During evaluation, return the deterministic mean 
    
    def _encode(self, x: torch.Tensor):
        """
        Runs the deterministic upstream stages shared by forward() and
        sample_predictive(): patch embedding, KoopmanNet, Integrator,
        KalmanNet. Everything past this point (reparameterize + decode)
        differs between "one training sample" and "n_samples for CRPS",
        so this is where the two paths split off from shared code.

        Returns:
            Z_prime (torch.Tensor): (Batch, d, m)
            P (torch.Tensor): (Batch, m, d, d)
            X_C_hat (torch.Tensor): (Batch, d, n), needed by forward() for
                reconstructed_X_C_mu but not by sample_predictive()
        """
        x_norm = self.revin(x, mode="norm") if self.use_revin else x
        x_patched = k2vae_integration(x_norm, self.patch_size)
        X_p_prime_T = self.patch_embedding(x_patched.transpose(1, 2))
        X_p_prime = X_p_prime_T.transpose(1, 2)

        z_star, X_C_hat, X_H_hat = self.koopman(X_p_prime, self.m)

        X_res = z_star - X_C_hat
        X_res_T = X_res.transpose(1, 2)
        U_T = self.integrator(X_res_T)
        U = U_T.transpose(1, 2)

        z_0 = z_star[:, :, -1]
        Z_prime, P = self.kalman(z_0, U, X_H_hat)

        return Z_prime, P, X_C_hat

    def _decode_mean(self, latent: torch.Tensor) -> torch.Tensor:
        """Decode latent patches and restore temporal layout and data scale."""
        decoded = self.decoder_mu(latent.transpose(1, 2)).transpose(1, 2)
        # Decoder outputs are flattened patches; restore time and variables
        # before applying the context statistics saved by RevIN.
        decoded_time = rearrange(
            decoded, "B (N s) p -> B (p s) N", N=self.num_vars, s=self.patch_size
        )
        return self.revin(decoded_time, mode="denorm") if self.use_revin else decoded_time

    def _decode_sigma(self, latent: torch.Tensor) -> torch.Tensor:
        """Decode positive uncertainty and restore it to the input data scale."""
        logits = self.decoder_sigma(latent.transpose(1, 2)).transpose(1, 2)
        # Sigma is a positive spread, so apply softplus before denormalization.
        sigma_norm = F.softplus(
            rearrange(
                logits, "B (N s) p -> B (p s) N", N=self.num_vars, s=self.patch_size
            )
        ) + 1e-6
        # Add the floor rather than hard-clamping so the decoder keeps a useful
        # gradient even when its predicted uncertainty is near the minimum.
        # Keep uncertainty away from zero so the Gaussian NLL cannot become
        # numerically extreme when a forecast error is nonzero.
        sigma = self.revin.denormalize_sigma(sigma_norm) if self.use_revin else sigma_norm
        return sigma + self.sigma_floor

    def forward(self, x: torch.Tensor):
        """
        Args:
            x (torch.Tensor): The patched input context data. Shape: (Batch, input_dim, n)

        Returns:
            tuple:
                - reconstructed_X_C_mu (torch.Tensor): Decoded past context mean for reconstruction loss. Shape: (Batch, input_dim, n)
                - reconstructed_X_H_mu (torch.Tensor): Decoded future horizon mean for ELBO. Shape: (Batch, input_dim, m)
                - reconstructed_X_H_sigma (torch.Tensor): Decoded future horizon standard deviation for ELBO. Shape: (Batch, input_dim, m)
                - Z_prime (torch.Tensor): Refined latent mean for KL Divergence calculation. Shape: (Batch, d, m)
                - P (torch.Tensor): Latent covariance matrices for KL Divergence calculation. Shape: (Batch, m, d, d)
        """
        Z_prime, P, X_C_hat = self._encode(x)
        
        Z_sample = self.reparameterize(Z_prime, P)  # (B, d, m), this is the sampled latent states from Q(Z|X) 

        # Decode the sampled latent states to reconstruct the input data
        reconstructed_X_C_mu = self._decode_mean(X_C_hat)
        reconstructed_X_H_mu = self._decode_mean(Z_sample)
        reconstructed_X_H_sigma = self._decode_sigma(Z_sample)

        return reconstructed_X_C_mu, reconstructed_X_H_mu, reconstructed_X_H_sigma, Z_prime, P

    def sample_predictive(self, x: torch.Tensor, n_samples: int = 100) -> torch.Tensor:
        """
        Draws n_samples from the posterior predictive P(Y|X), for CRPS
        estimation (paper Appendix C.3 uses n=100). Unlike forward(), which
        reparameterizes Z once, this samples Z ~ Q(Z|X) and then Y|Z ~
        N(mu, sigma) independently n_samples times, since CRPS needs draws
        from the full predictive distribution rather than the decoder mean.

        Shares the deterministic upstream stages with forward() via
        _encode(), so those layers are still only defined/run once here,
        not duplicated.

        Args:
            x (torch.Tensor): patched input context. Shape (Batch, input_dim, n)
            n_samples (int): number of posterior predictive draws.

        Returns:
            torch.Tensor: horizon samples. Shape (n_samples, Batch, input_dim, m)
        """
        Z_prime, P, _ = self._encode(x)

        Z_prime_T = Z_prime.transpose(1, 2)  # (B, m, d)
        jitter = torch.eye(self.d, device=P.device).expand_as(P) * 1e-5
        dist_z = MultivariateNormal(loc=Z_prime_T, covariance_matrix=P + jitter)

        samples = []
        for _ in range(n_samples):
            Z_sample_T = dist_z.rsample()  # (B, m, d)
            Z_sample = Z_sample_T.transpose(1, 2)
            mu = self._decode_mean(Z_sample)
            sigma = self._decode_sigma(Z_sample)

            y_sample = Normal(mu, sigma).rsample()
            samples.append(y_sample)

        return torch.stack(samples, dim=0)  # (n_samples, B, input_dim, m)