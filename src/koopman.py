import torch
import torch.nn as nn
from einops import rearrange
import math

class KoopmanNet(nn.Module):
    def __init__(self, d: int, hidden_dim: int = 128):
        super().__init__()
        self.d = d

        # Measurement function as structured in their koopman configuration 
        self.measurement_function = nn.Sequential(
            nn.Linear(d, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.05),
            nn.Linear(hidden_dim, d)
        )

        # Defining the global operator, a global safety net that captures shared dynamics across
        # the dataset and prevents the math from exploding early in training
        K_init = torch.randn(d, d) # d x d matrix that is randomly initialized from a normal distribution
        U, _, V = torch.svd(K_init) 
        self.K_glo = nn.Parameter(torch.mm(U, V.t()))  # performs matrix multiplication of U and V^T to ensure K_glo is orthogonal providing stability

    def forward(self, X_p_prime: torch.Tensor, m: int):
        """
        Maps tokens to a linear measurement space, calculates the Koopman Operator via eDMD, 
        and predicts future states.

        Args:
            X_p_prime (torch.Tensor): Embedded tokens from TokenEmbedding. Shape: (Batch, d, n)
            m (int): The number of patches to predict into the future (Horizon / patch_size).

        Returns:
            X_p_star (torch.Tensor): The true mapped history. Shape: (Batch, d, n)
            X_C_hat (torch.Tensor): The linear reconstruction of the past. Shape: (Batch, d, n)
            X_H_hat (torch.Tensor): The linear prediction of the future. Shape: (Batch, d, m)
        """
        B, d, n = X_p_prime.shape 

        # Map to measurement space
        X_p_mapped = rearrange(X_p_prime, 'b d n -> b n d') # rearrange to (B, n, d) as the MLP expects the last dimension to be the feature dimension
        X_p_star = self.measurement_function(X_p_mapped) # pass the reshaped data through the measurement function to map to the linear measurement space

        # Restore the column-vector convention required for the upcoming eDMD matrix algebra
        X_p_star = rearrange(X_p_star, 'b n d -> b d n')

        # Get local operator, uses one-step extended Dynamic Mode Decomposition (eDMD) 
        # to find the line of best fit representing the system's dynamics for this specific batch
        X_back = X_p_star[:, :, :-1]  # (B, d, n-1), the past, all patches except the last one
        X_forward = X_p_star[:, :, 1:]  # (B, d, n-1), the future, all patches except the first one

        # Solve X_back^T * K^T = X_fore^T, then transpose the result (this is to follow the conventiion of the original paper)
        X_back_T = X_back.transpose(1, 2)  # (B, n-1, d)
        X_forward_T = X_forward.transpose(1, 2)  # (B, n-1, d)
        K_loc_T = torch.linalg.lstsq(X_back_T, X_forward_T).solution # (B, d, d), this is faster and more numerically stable than using the pseudo-inverse
        K_loc = K_loc_T.transpose(1, 2)  # (B, d, d), returning to the original shape of the local operator

        # Creating the final operator as a combination of the global and local operators
        K = K_loc + self.K_glo.unsqueeze(0).repeat(B, 1, 1)  # (B, d, d), adds batch dimension to the global operator and combines it with the local operator

        # NaN error handling: If K has NaN values, replace it with the identity matrix 
        # to avoid propagation of errors in the reconstruction and prediction steps.
        if torch.isnan(K).any():
            K = torch.eye(d, device=K.device).unsqueeze(0).repeat(B, 1, 1)

        # Reconstruction and prediction of state transitions 
        current_state = X_p_star[:, :, 0].unsqueeze(-1) # first token, shape (B, d, 1) adjusted to have the correct shape for matrix multiplication with K
        reconstruction = []

        # Reconstruct context window 
        for _ in range(n):
            reconstruction.append(current_state.squeeze(-1)) # saving the current state for reconstruction, shape (B, d)
            current_state = torch.bmm(K, current_state)  # matrix multiplication of K and current_state to get the next state in the sequence

        # Extracts the true last token from the mapped space 
        # to prevent errors from accumulating in the prediction step, shape (B, d, 1)
        current_state = X_p_star[:, :, -1].unsqueeze(-1)
        prediction = []

        for _ in range(m):
            current_state = torch.bmm(K, current_state)
            prediction.append(current_state.squeeze(-1)) 
            
        # Stack lists back along the time dimension
        X_C_hat = torch.stack(reconstruction, dim=-1) # shape (B, d, n)
        X_H_hat = torch.stack(prediction, dim=-1)     # shape (B, d, m)

        # Return the true mapped space, the reconstruction, and the prediction
        return X_p_star, X_C_hat, X_H_hat