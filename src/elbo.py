import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal, MultivariateNormal, kl_divergence

# Reduction is used to determine how we set the tensor to a single value. 
# "mean" means we take the mean of all the values in the tensor, 
# "sum" means we sum all the values in the tensor, 
# and "none" means we don't reduce the tensor at all and keep it as is.
"""
    This function is used to generate the negative log likelihood and reduce it to a single value to be used in backprop
    Args:
        Y (torch.Tensor) : The observed data (ground truth) for the prediction horizon. Shape: (Batch, d)
        mu (torch.Tensor) : The predicted mean of the Gaussian distribution for the prediction horizon. Shape: (Batch, d)
        sigma (torch.Tensor) : The predicted standard deviation of the Gaussian distribution for the prediction horizon
        Reduction (str) : Specifies the reduction method to apply to the loss. Options are "mean", "sum", or "none". Default is "mean".
    
    Returns:
        torch.Tensor : The computed loss value, reduced according to the specified method.
"""
def gaussian_nll(Y: torch.Tensor, mu: torch.Tensor, sigma: torch.Tensor, reduction: str = "mean") -> torch.Tensor:
    """-log P(Y|Z,X), where P(Y|Z,X) = N(mu, sigma)  (eq. 24-25)"""
    dist = Normal(mu, sigma)
    nll = -dist.log_prob(Y)
    
    if reduction == "mean":
        return nll.mean()
    elif reduction == "sum":
        return nll.sum()
    elif reduction == "none":
        return nll
    else:
        raise ValueError(f"Unknown reduction: {reduction}")

"""
    This function is used to compute the Kullback-Leibler divergence between two Gaussian distributions and reduce it to a single value.
    Args:
        Z_prime (torch.Tensor) : The predicted mean of the latent variable Z. Shape: (Batch, d, m)
        P (torch.Tensor) : The predicted covariance matrix of the latent variable Z. Shape: (Batch, m, d, d)
        Reduction (str) : Specifies the reduction method to apply to the loss. Options are "mean", "sum", or "none". Default is "mean".
    
    Returns:
        torch.Tensor : The computed loss value, reduced according to the specified method.
"""
def kl_divergence_gaussian(Z_prime: torch.Tensor, P: torch.Tensor, reduction: str = "mean") -> torch.Tensor:
    """D_KL(Q(Z|X) || P(Z|X)), Q(Z|X) = N(Z', P), P(Z|X) = N(0, I)  (eq. 26)"""
    B, d, m = Z_prime.shape
    Z_prime_T = Z_prime.transpose(1, 2)  # (B, m, d)
    jitter = torch.eye(d, device=P.device).expand_as(P) * 1e-6 # Ensure it remains differentiable and numerically stable
    Q = MultivariateNormal(loc=Z_prime_T, covariance_matrix=P + jitter)
    
    prior_mean = torch.zeros_like(Z_prime_T)
    prior_cov = torch.eye(d, device=P.device).expand(B, m, d, d)
    prior = MultivariateNormal(loc=prior_mean, covariance_matrix=prior_cov)

    kl_per_step = kl_divergence(Q, prior)   # (B, m)
    kl_per_batch = kl_per_step.sum(dim=1)   # sum over the m horizon steps -> (B,)

    if reduction == "mean":
        return kl_per_batch.mean()
    elif reduction == "sum":
        return kl_per_batch.sum()
    elif reduction == "none":
        return kl_per_batch
    else:
        raise ValueError(f"Unknown reduction: {reduction}")


"""
    This function is used to compute the reconstruction loss and reduce it to a single value.
    Args:
        X_C (torch.Tensor) : The observed data (ground truth) for the reconstruction horizon. Shape: (Batch, d)
        X_Rec (torch.Tensor) : The reconstructed data. Shape: (Batch, d)
        Reduction (str) : Specifies the reduction method to apply to the loss. Options are "mean", "sum", or "none". Default is "mean".

    Returns:
        torch.Tensor : The computed loss value, reduced according to the specified method.
"""
def reconstruction_loss(X_C: torch.Tensor, X_Rec: torch.Tensor, reduction: str = "mean") -> torch.Tensor:
    """L_Rec = ||X - X_Rec||_2^2  (eq. 27)"""
    loss = F.mse_loss(X_Rec, X_C, reduction=reduction)
    return loss

"""
    This function computes the Evidence Lower Bound (ELBO) loss, which is a combination of the negative log likelihood and the Kullback-Leibler divergence.
    Args:
        X_H (torch.Tensor): The observed data (ground truth) for the prediction horizon. Shape: (Batch, d)
        mu (torch.Tensor): The predicted mean of the Gaussian distribution for the prediction horizon. Shape: (Batch, d)
        sigma (torch.Tensor): The predicted standard deviation of the Gaussian distribution for the prediction horizon. Shape: (Batch, d)
        Z_prime (torch.Tensor): The predicted mean of the latent variable Z. Shape: (Batch, d, m)
        P (torch.Tensor): The predicted covariance matrix of the latent variable Z. Shape: (Batch, m, d, d)
    Returns:
        torch.Tensor : The computed ELBO loss value.
"""
def elbo_loss(X_H: torch.Tensor, mu: torch.Tensor, sigma: torch.Tensor, Z_prime: torch.Tensor, P: torch.Tensor) -> torch.Tensor:
    """L_ELBO = gaussian_nll(...) + kl_divergence_gaussian(...)  (eq. 26)"""
    nll = gaussian_nll(X_H, mu, sigma)
    kl = kl_divergence_gaussian(Z_prime, P)
    return nll + kl

"""

    Args:
        X_H (torch.Tensor): The observed data (ground truth) for the prediction horizon. Shape: (Batch, d)
        mu (torch.Tensor): The predicted mean of the Gaussian distribution for the prediction horizon. Shape: (Batch, d)
        sigma (torch.Tensor): The predicted standard deviation of the Gaussian distribution for the prediction horizon. Shape: (Batch, d)
        Z_prime (torch.Tensor): The predicted mean of the latent variable Z. Shape: (Batch, d, m)
        P (torch.Tensor): The predicted covariance matrix of the latent variable Z. Shape: (Batch, m, d, d)
        X_C (torch.Tensor): The observed data (ground truth) for the reconstruction horizon. Shape: (Batch, d)
        X_Rec (torch.Tensor): The reconstructed data. Shape: (Batch, d)
    Returns:
        dict : A dictionary containing the total loss, ELBO loss, negative log likelihood, KL divergence, and reconstruction loss.
    
"""
def total_loss(X_H: torch.Tensor, mu: torch.Tensor, sigma: torch.Tensor, Z_prime: torch.Tensor, P: torch.Tensor, X_C: torch.Tensor, X_Rec: torch.Tensor, lambda_rec: float = 1.0) -> dict:
    """L = L_ELBO + lambda_rec * L_Rec"""
    nll = gaussian_nll(X_H, mu, sigma)
    kl = kl_divergence_gaussian(Z_prime, P)
    elbo = nll + kl
    rec = reconstruction_loss(X_C, X_Rec)
    total = elbo + lambda_rec * rec

    return {
        "total": total,
        "elbo": elbo,
        "nll": nll,
        "kl": kl,
        "rec": rec,
    }