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

# def kl_divergence_gaussian(Z_prime: torch.Tensor, P: torch.Tensor, reduction: str = "mean") -> torch.Tensor:
#     """D_KL(Q(Z|X) || P(Z|X)), Q(Z|X) = N(Z', P), P(Z|X) = N(0, I)  (eq. 26)"""
#     B, d, m = Z_prime.shape
#     Z_prime_T = Z_prime.transpose(1, 2)  # (B, m, d)
#     jitter = torch.eye(d, device=P.device).expand_as(P) * 1e-6 # Ensure it remains differentiable and numerically stable
#     Q = MultivariateNormal(loc=Z_prime_T, covariance_matrix=P + jitter)
    
#     prior_mean = torch.zeros_like(Z_prime_T)
#     prior_cov = torch.eye(d, device=P.device).expand(B, m, d, d)
#     prior = MultivariateNormal(loc=prior_mean, covariance_matrix=prior_cov)

#     kl_per_step = kl_divergence(Q, prior)   # (B, m)
#     kl_per_batch = kl_per_step.sum(dim=1)   # sum over the m horizon steps -> (B,)

#     if reduction == "mean":
#         return kl_per_batch.mean()
#     elif reduction == "sum":
#         return kl_per_batch.sum()
#     elif reduction == "none":
#         return kl_per_batch
#     else:
#         raise ValueError(f"Unknown reduction: {reduction}") 

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
    
    # Average across the horizon dimension (m) instead of summing.
    # This aligns the KL scale with the NLL and MSE 'mean' reductions.
    kl_per_batch = kl_per_step.mean(dim=1)   # -> (B,)

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

#def elbo_loss(X_H: torch.Tensor, mu: torch.Tensor, sigma: torch.Tensor, Z_prime: torch.Tensor, P: torch.Tensor) -> torch.Tensor:
#    """L_ELBO = gaussian_nll(...) + kl_divergence_gaussian(...)  (eq. 26)"""
#    nll = gaussian_nll(X_H, mu, sigma)
#    kl = kl_divergence_gaussian(Z_prime, P)
#    return nll + kl

# DEVIATION FROM PAPER (eq. 26): beta-weighted KL instead of an unweighted sum.
#
# With beta=1 from epoch 1, D_KL(Z') has a trivial one-line gradient (dKL/dZ' = Z'),
# available from the first batch, while NLL only improves once Koopman + Kalman +
# the Integrator jointly learn real structure, which takes many epochs. Gradient
# descent found the cheap fix first: R inflated to starve the Kalman gain, and the
# Integrator learned U = -Z, driving Z' = Z + U toward 0 to satisfy KL before mu
# ever had a chance to become genuinely informative. Confirmed via checkpoint
# diagnostics (see posterior_collapse_diagnostic.html): rho(K) and Koopman's own
# forecast were healthy, but ||Z'|| ~0 and diag(P) == I identically, with
# ||Z|| ~ ||U|| anti-correlated.
#
# Ramping beta 0 -> 1 over warmup removes that shortcut early on, so the only
# way to reduce the loss during warmup is to actually improve mu. beta_warmup_epochs=0
# reproduces the exact paper objective for baseline/ablation comparison.

# DEVIATION FROM PAPER (eq. 26): fixed KL weight, not the literal unweighted sum.
# The paper's own reference implementation (config/*/k2vae.yaml, all datasets)
# trains with weight_beta=0.01 throughout, despite eq. 26 showing an unweighted
# D_KL. This is a paper-text-vs-code mismatch, not something we invented:
# beta-annealing toward 1.0 was tried first and still collapsed once the ramp
# finished (test_kl matched the unweighted baseline to 4 sig figs); the
# reference's fixed small weight is what actually produced the paper's results.

def elbo_loss(X_H: torch.Tensor, mu: torch.Tensor, sigma: torch.Tensor, Z_prime: torch.Tensor, P: torch.Tensor, beta: float = 0.01) -> torch.Tensor:
    """L_ELBO = gaussian_nll(...) + beta * kl_divergence_gaussian(...)  (eq. 26, beta-annealed deviation)"""
    nll = gaussian_nll(X_H, mu, sigma)
    kl = kl_divergence_gaussian(Z_prime, P)
    return nll + beta * kl

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
#def total_loss(X_H: torch.Tensor, mu: torch.Tensor, sigma: torch.Tensor, Z_prime: torch.Tensor, P: torch.Tensor, X_C: torch.Tensor, X_Rec: torch.Tensor, lambda_rec: float = 1.0) -> dict:
#    """L = L_ELBO + lambda_rec * L_Rec"""
#    nll = gaussian_nll(X_H, mu, sigma)
#    kl = kl_divergence_gaussian(Z_prime, P)
#    elbo = nll + kl
#    rec = reconstruction_loss(X_C, X_Rec)
#    total = elbo + lambda_rec * rec
#
#    return {
#        "total": total,
#        "elbo": elbo,
#        "nll": nll,
#        "kl": kl,
#        "rec": rec,
#    }
    
def total_loss(X_H: torch.Tensor, mu: torch.Tensor, sigma: torch.Tensor, Z_prime: torch.Tensor, P: torch.Tensor, X_C: torch.Tensor, X_Rec: torch.Tensor, lambda_rec: float = 1.0, beta: float = 0.01) -> dict:
    """L = L_ELBO(beta) + lambda_rec * L_Rec. kl returned unweighted (raw D_KL) so
    the true elbo (nll + kl) can always be reconstructed regardless of beta."""
    nll = gaussian_nll(X_H, mu, sigma)
    kl = kl_divergence_gaussian(Z_prime, P)
    elbo = nll + beta * kl
    rec = reconstruction_loss(X_C, X_Rec)
    total = elbo + lambda_rec * rec

    return {
        "total": total,
        "elbo": elbo,
        "nll": nll,
        "kl": kl,
        "rec": rec,
        "beta": beta,
    }