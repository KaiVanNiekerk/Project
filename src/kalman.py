import torch
import torch.nn as nn
import torch.nn.functional as F

class KalmanNet(nn.Module):
    def __init__(self, state_dim: int):
        super().__init__()
        self.state_dim = state_dim
        
        # The following matrices are all learnable and initialised as identity matrices 
        # and are trained to adapt to the specific dynamics of the system.
        # A - transition matrix (How does the state naturally evolve)
        # B - control matrix (Used to amplify u_k which corrects for the koopman operator's linearity assumption) LOOK AT THIS
        # H - observation matrix ()
        # Need to look at and udnerstand B and H properly.
        self.A = nn.Parameter(torch.eye(state_dim))
        self.B = nn.Parameter(torch.eye(state_dim))
        self.H = nn.Parameter(torch.eye(state_dim))
        
        # "we initialize the covariance matrices Q and R as identity
        # matrices and use lower triangular matrices L_Q and L_R to keep
        # the positive definiteness: Q = L_Q L_Q^T, R = L_R L_R^T."
        self.L_Q_raw = nn.Parameter(torch.eye(state_dim))
        self.L_R_raw = nn.Parameter(torch.eye(state_dim))
    
    # Q is the covariance matrix that represents how much we trust our model's predictions
    # R is the covariance matrix that represents how much we trust our observations (measurements)
    def covariance_matrices(self):
        # torch.tril 0s out all the elements above the diagonal, ensuring the matrices are in lower triangular form.
        L_Q = torch.tril(self.L_Q_raw)
        L_R = torch.tril(self.L_R_raw)
        # Ensure positive definiteness of Q and R by constructing them from lower triangular matrices
        Q = L_Q @ L_Q.T
        R = L_R @ L_R.T
        return Q, R
    
    def step(self, z_prev, P_prev, u_k, x_hat_H_k):
        # Batch - B
        # state_dim - d
        """
        Performs a single Kalman filter step.

        Args:
            z_prev (torch.Tensor): The previous observation. Shape: (Batch, state_dim)
            P_prev (torch.Tensor): The previous estimate covariance. Shape: (Batch, state_dim, state_dim)
            u_k (torch.Tensor): The control input. Shape: (Batch, state_dim)
            x_hat_H_k (torch.Tensor): The predicted state estimate. Shape: (Batch, state_dim)

        Returns:
            x_k (torch.Tensor): The updated state estimate. Shape: (Batch, state_dim)
            P_k (torch.Tensor): The updated estimate covariance. Shape: (Batch, state_dim, state_dim)
        """
        Q, R = self.covariance_matrices()
        
        # Prediction step
        # z_hat_k = A z_{k-1} + B u_k
        z_hat = z_prev @ self.A.T + u_k @ self.B.T
        # P_hat_k = A P_{k-1} A^T + Q
        P_hat = self.A @ P_prev @ self.A.T + Q
        
        # Update step
        # K_k = P_hat_k H^T (H P_hat_k H^T + R)^-1
        # Solved via linear solve rather than explicit inverse, for
        # numerical stability (S is symmetric so this is well-posed).
        S = self.H @ P_hat @ self.H.T + R
        rhs = self.H @ P_hat  # = (P_hat @ H^T)^T since P_hat is symmetric
        K_T = torch.linalg.solve(S, rhs)  # S @ K^T = rhs
        K_k = K_T.transpose(-1, -2) # Kalman gain which determines how much we trust the new measurement versus our prediction
        
        # z_k = z_hat_k + K_k (x_hat_H_k - H z_hat_k)
        # take my prediction and correct it with the new measurement, weighted by how much we trust the measurement (K_k)
        y_hat = z_hat @ self.H.T
        z_k = z_hat + (x_hat_H_k - y_hat) @ K_k.transpose(-1, -2) # Next prediction
        
        # Joseph-stabilized covariance update (Theorem 3.1, eq. 30-31):
        # P_dual_k = (I - K_k H) P_hat_k (I - K_k H)^T + K_k R K_k^T
        I_minus_KH = I - K @ self.H
        # Used to keep floating point errors from causing P_k to become non-symmetric or non-positive definite.
        # look eqn 30-31 in paper
        P_dual = (
            I_minus_KH @ P_hat @ I_minus_KH.transpose(-1, -2)
            + K_k @ R @ K_k.transpose(-1, -2)
        )
        # P_k = 1/2 (P_dual_k + P_dual_k^T), enforcing exact symmetry
        P_k = 0.5 * (P_dual + P_dual.transpose(-1, -2)) # next uncertainity estimate
        
        return z_k, P_k
    
    # Next implementation is Forward pass 
    
    