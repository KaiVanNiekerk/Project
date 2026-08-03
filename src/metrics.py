import torch


def nmae(x: torch.Tensor, x_hat: torch.Tensor) -> torch.Tensor:
    """
    Normalized Mean Absolute Error, per paper eq. (37):

        NMAE = sum_{k,t} |x_t^k - x_hat_t^k| / sum_{k,t} |x_t^k|

    x, x_hat: any shape, as long as they match (e.g. [K, T] or [B, K, T]).
    Summation is global (paper doesn't average per-variable/per-timestep
    separately -- it's a single ratio over the whole tensor).
    """
    return (x - x_hat).abs().sum() / x.abs().sum()


def crps(samples: torch.Tensor, x: torch.Tensor, sample_dim: int = 0) -> torch.Tensor:
    """
    Continuous Ranked Probability Score, per paper eq. (38):

        CRPS = \int_R (F(z) - I{x <= z})^2 dz

    estimated from the empirical CDF of n samples X_1, ..., X_n ~ F
    (paper uses n = 100).

    Rather than numerically integrating F_hat against the indicator function,
    this uses the standard closed-form identity for CRPS of an empirical
    distribution (this is algebraically exact for the empirical CDF -- not
    an approximation, and not the quantile-loss discretization ProbTS uses):

        CRPS(F_n, x) = E|X - x| - 0.5 * E|X - X'|

    where X, X' are drawn iid from the n samples. Estimated as:

        (1/n) sum_i |X_i - x|  -  (1/(2n^2)) sum_i sum_j |X_i - X_j|

    Parameters
    ----------
    samples : torch.Tensor
        Samples from the predictive distribution, e.g. rsample()'d from
        post_dist. Shape [n, ...] with the sample dimension at `sample_dim`.
    x : torch.Tensor
        Ground truth, same shape as `samples` minus the sample dimension.
    sample_dim : int
        Which dimension of `samples` indexes the n draws.

    Returns
    -------
    torch.Tensor (scalar)
        Mean CRPS over all remaining dimensions (variables, timesteps, batch).
    """
    samples = samples.movedim(sample_dim, 0)  # -> [n, ...]
    n = samples.shape[0]

    # E|X - x|, estimated per-point
    term1 = (samples - x.unsqueeze(0)).abs().mean(dim=0)  # [...]

    # 0.5 * E|X - X'|, estimated per-point via all pairs (i, j)
    diff = samples.unsqueeze(0) - samples.unsqueeze(1)  # [n, n, ...]
    term2 = 0.5 * diff.abs().mean(dim=(0, 1))            # [...]

    point_crps = term1 - term2                          # [...]
    return point_crps.mean()