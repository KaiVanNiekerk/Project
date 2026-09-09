import torch
import torch.nn as nn

class RevIN(nn.Module):
    """
    Reversible Instance Normalization (RevIN).
    
    Dynamically normalizes each time-series context window to have a mean of 0 
    and a standard deviation of 1, minimizing the effect of distribution 
    shifts/drift in long-term forecasting.
    """

    def __init__(self, num_vars: int, eps: float = 1e-5, affine: bool = True, affine_min_scale: float = 0.1):
        """
        Args:
            num_vars (int): Number of variables in the input time series.
            eps (float): A small value added to the variance for numerical stability.
            affine (bool): If True, applies learnable affine parameters after normalization.
            affine_min_scale (float): Minimum magnitude allowed for a learned affine
                scale during normalization and denormalization. Defaults to 0.1.
        """
        super().__init__()
        self.num_vars = num_vars
        self.eps = eps
        self.affine = affine 
        self.affine_min_scale = affine_min_scale

        # Allows the model to learn scaling and shifting parameters instead of just 
        # normalizing to zero mean and unit variance which may not be optimal for all datasets
        if self.affine:
            
            # Torch.ones initializes the weight to 1 for each variable
            self.weight = nn.Parameter(torch.ones(num_vars)) 
            # Torch.zeros initializes the bias to 0 for each variable
            self.bias = nn.Parameter(torch.zeros(num_vars))

    def forward(self, x: torch.Tensor, mode: str) -> torch.Tensor:
        """
        Args:
            x (torch.Tensor): The input time series data. Expected shape: (Batch, Time, Variables).
            mode (str): Either 'norm' (to normalize) or 'denorm' (to restore the original scale).
            
        Returns:
            torch.Tensor: The transformed tensor of the same shape.
        """
        if mode == 'norm':
            self._get_statistics(x)
            return self._normalize(x)
        elif mode == 'denorm':
            return self._denormalize(x)
        else:
            raise ValueError(f"Invalid Mode ({mode}): Mode must be either 'norm' or 'denorm'.")

    def _get_statistics(self, x: torch.Tensor):
        """
        Computes the mean and standard deviation for each variable in the input tensor.
        
        Args:
            x (torch.Tensor): The input time series data. Expected shape: (Batch, Time, Variables).
        """
        # Compute mean and stddev along the time dimension (dim=1), dim 0 is the batch dimension, and dim 2 is the variable dimension

        # keepdim=True ensures the output has the same number of dimensions as the input
        self.mean = torch.mean(x,dim=1, keepdim=True).detach()  
        # Detaching ensures that these statistics are not part of the backpropagation gradient computations
        self.std = torch.sqrt(torch.var(x, dim=1, unbiased=False, keepdim=True) + self.eps).detach() 

    def _normalize(self, x: torch.Tensor) -> torch.Tensor:
        """
        Normalizes the input tensor using the computed mean and standard deviation.
        
        Args:
            x (torch.Tensor): The input time series data. Expected shape: (Batch, Time, Variables).
        """
        x = (x - self.mean) / self.std  # Since x is of shape (Batch, Time, Variables), mean and std are computed across the time dimension

        if self.affine:
            # Apply learnable affine transformation
            x = x * self._safe_weight() + self.bias  # Shape: (Batch, Time, Variables)

        return x

    def _denormalize(self, x: torch.Tensor) -> torch.Tensor:
        """
        Restores the original scale of the input tensor using the stored mean and standard deviation.
        
        Args:
            x (torch.Tensor): The normalized time series data. Expected shape: (Batch, Time, Variables).
        """
        if self.affine:
            # Reverse the affine transformation without allowing a learned scale
            # near zero to make denormalized outputs numerically unbounded.
            x = (x - self.bias) / self._safe_weight()  # Shape: (Batch, Time, Variables)

        # Restore original scale
        x = x * self.std + self.mean  # Shape: (Batch, Time, Variables)

        return x

    def denormalize_sigma(self, sigma: torch.Tensor) -> torch.Tensor:
        """Map positive standard deviations back to the input scale.

        Standard deviations use the absolute affine scale and never the affine
        bias because spread has no location component.
        """
        if self.affine:
            sigma = sigma / self._safe_weight().abs()
        return sigma * self.std

    def _safe_weight(self) -> torch.Tensor:
        """Keep the learned affine scale away from the singular zero point."""
        safe_abs_weight = self.weight.abs().clamp_min(self.affine_min_scale)
        return torch.where(self.weight >= 0, safe_abs_weight, -safe_abs_weight)



