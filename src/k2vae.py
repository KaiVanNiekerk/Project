import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions.multivariate_normal import MultivariateNormal
from koopman import KoopmanNet
from integrator import Integrator
from kalman import KalmanNet

class K2VAE(nn.Module):
    def __init__(self, input_dim: int, d: int, m: int, n: int, integrator_args: dict, hidden_dim: int = 128):
        """
        Args:
            input_dim (int): The size of a flattened multivariate patch (Variables * Patch Size).
            d (int): The dimension of the latent measurement space.
            m (int): The number of patches in the future prediction horizon.
            n (int): The number of patches in the past context window.
            integrator_args (dict): Hyperparameters for the Integrator Transformer network.
            hidden_dim (int, optional): Number of neurons in the hidden layers of the MLPs. Defaults to 128.
        """
        super().__init__()
        self.d = d
        self.m = m
        self.n = n

        self.patch_embedding = nn.Linear(input_dim, d) # Projects the input patches to the latent measurement space 
        self.koopman = KoopmanNet(d = d, hidden_dim = hidden_dim)  # Evaluates the measurement function and Koopman operator 
        self.integrator = Integrator(**integrator_args)  # Maps the Koopman residual to a control-input sequence over the prediction horizon 
        self.kalman = KalmanNet(state_dim = d) # # Refines linear state predictions and outputs process uncertainty (covariance)

        # Decodes latent states back into the mean of the original input dimensions
        self.decoder_mu = nn.Sequential(
            nn.Linear(d, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim)
        )

        # Decodes latent states back into the variance scale of the original input dimensions
        self.decoder_sigma = nn.Sequential(
            nn.Linear(d, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
        )

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
        # Input token embedding
        x_T = x.transpose(1, 2)  # (B, n, input_dim)
        X_p_prime_T = self.patch_embedding(x_T)  # (B, n, d)
        X_p_prime = X_p_prime_T.transpose(1, 2)  # (B, d, n)

        # KoopmanNet forward pass to get the true mapped history, past reconstruction, and future prediction
        # z_star: true mapped history , X_C_hat: past reconstruction, X_H_hat: future prediction
        z_star, X_C_hat, X_H_hat = self.koopman(X_p_prime, self.m)

        # Integrator forward pass to get the predicted future states based on the residuals between the true mapped history and past reconstruction
        X_res = z_star - X_C_hat  # (B, d, n), residuals between true mapped history and past reconstruction
        X_res_T = X_res.transpose(1, 2)  # (B, n, d)
        U_T = self.integrator(X_res_T)  # (B, m, d)
        U = U_T.transpose(1, 2)  # (B, d, m), the control sequence mapping the Koopman residuals to the future prediction horizon

        # KalmanNet forward pass to get the mean and covariance of Q(Z|X)
        z_0 = z_star[:, :, -1]  # (B, d), last token of the true mapped history as the initial state for KalmanNet

        Z_prime, P = self.kalman(z_0, U, X_H_hat)  # Z_prime: (B, d, m), P: (B, m, d, d)

        Z_sample = self.reparameterize(Z_prime, P)  # (B, d, m), this is the sampled latent states from Q(Z|X) 

        # Decode the sampled latent states to reconstruct the input data
        X_C_hat_T = X_C_hat.transpose(1, 2)  # (B, n, d)
        reconstructed_X_C_mu = self.decoder_mu(X_C_hat_T).transpose(1, 2) # (B, input_dim, n)

        Z_sample_T = Z_sample.transpose(1, 2)  # (B, m, d)
        reconstructed_X_H_mu = self.decoder_mu(Z_sample_T).transpose(1, 2) # (B, input_dim, m)

        reconstructed_X_H_sigma = self.decoder_sigma(Z_sample_T).transpose(1, 2) # (B, input_dim, m)
        reconstructed_X_H_sigma = F.softplus(reconstructed_X_H_sigma) + 1e-5  # Ensure positive variance

        return reconstructed_X_C_mu, reconstructed_X_H_mu, reconstructed_X_H_sigma, Z_prime, P

