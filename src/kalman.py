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
        Q = L_Q @ L_Q.T # uncertainity in z_k?
        R = L_R @ L_R.T # How nosiy do I assume y_k (x_hat_k this is koopmans rollout) is
        return Q, R
    
    def step(self, z_prev, P_prev, u_k, x_hat_H_k):
        # Batch - B
        # state_dim - d
        # Most matrixs like A, B etc only have two dimensions so can use .T for transpose
        # K_k however can have more and thus we use the .transpose(-1, -2)
        """
        Performs a single Kalman filter step.

        Args:
            z_prev (torch.Tensor): The previous state estimate. Shape: (Batch, state_dim)
            P_prev (torch.Tensor): The previous estimate covariance. Shape: (Batch, state_dim, state_dim)
            u_k (torch.Tensor): The control input. Shape: (Batch, state_dim)
            x_hat_H_k (torch.Tensor): The predicted state estimate. Shape: (Batch, state_dim)

        Returns:
            z_k (torch.Tensor): The updated state estimate. Shape: (Batch, state_dim)
            P_k (torch.Tensor): The updated estimate covariance. Shape: (Batch, state_dim, state_dim)
        """
        Q, R = self.covariance_matrices()
        batch_size = z_prev.shape[0]
        # Might need to add somehting here to train on GPU?
        # The -1s here mean dotn change that dimension, so the resulting tensor will have shape (B, d, d)
        I = torch.eye(self.state_dim, device=z_prev.device).expand(batch_size, -1, -1) # Identity matrix with dims d, d
        
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
        # Cant just do a normal @ multiply here as it was outputting a B, d, d creating a new dimension owing to
        # a 2D matrix being multiplied by a 3D one thus we add on an extra 1 to enforce the correct shape and then squeeze it back down to B, d
        residual = (x_hat_H_k - y_hat).unsqueeze(-1)          # (B, d, 1)
        # We use bmn because we want to multiply multiple samples in parallel, and the last two dimensions are the ones we want to multiply (d, d) @ (d, 1)
        correction = torch.bmm(K_k, residual).squeeze(-1)     # (B, d)
        z_k = z_hat + correction # Next prediction
        
        # Joseph-stabilized covariance update (Theorem 3.1, eq. 30-31):
        # P_dual_k = (I - K_k H) P_hat_k (I - K_k H)^T + K_k R K_k^T
        I_minus_KH = I - K_k @ self.H
        # Used to keep floating point errors from causing P_k to become non-symmetric or non-positive definite.
        # look eqn 30-31 in paper
        P_dual = (
            I_minus_KH @ P_hat @ I_minus_KH.transpose(-1, -2)
            + K_k @ R @ K_k.transpose(-1, -2)
        )
        # P_k = 1/2 (P_dual_k + P_dual_k^T), enforcing exact symmetry
        P_k = 0.5 * (P_dual + P_dual.transpose(-1, -2)) # next uncertainity estimate
        
        return z_k, P_k
    
    # P_0 not defined in the paper, but it is the initial estimate covariance. I
    # t is a hyperparameter that can be tuned based on the specific problem and data characteristics. 
    # If not provided, it defaults to an identity matrix, indicating equal uncertainty across all state dimensions at the start.
    def forward(self, z_0, U, x_hat_H, P_0=None):
        """
        Performs a sequence of Kalman filter steps.

        Args:
            z_0 (torch.Tensor): The initial state estimate. Shape: (Batch, state_dim)
            P_0 (torch.Tensor): The initial estimate covariance. Shape: (Batch, state_dim, state_dim)
            U (torch.Tensor): The control inputs for each time step. Shape: (Batch, state_dim, time_steps)
            x_hat_H (torch.Tensor): The predicted state estimates for each time step. Shape: (Batch, state_dim, time_steps)

        Returns:
            Z_prime: (B, d, m) mean of Q(Z|X) = N(Z', P)
            P: (B, m, d, d) covariance of Q(Z|X) = N(Z', P)
        """
        
        batch_size = z_0.shape[0]
        m = U.shape[-1]
        
        if P_0 is None:
            # The -1s here mean dotn change that dimension, so the resulting tensor will have shape (B, d, d)
            P_0 = torch.eye(self.state_dim, device=z_0.device).expand(batch_size, -1, -1)

        z_prev, P_prev = z_0, P_0
        z_list, P_list = [], []
        
        # The loop iterates over the time steps, applying the Kalman filter step
        for k in range(m):
            u_k = U[..., k]
            x_hat_H_k = x_hat_H[..., k]
            z_k, P_k = self.step(z_prev, P_prev, u_k, x_hat_H_k)
            z_list.append(z_k)
            P_list.append(P_k)
            z_prev, P_prev = z_k, P_k

        # torch.stack is used to combine the list of tensors into a single tensor along a new dimension, 
        # effectively creating a time series of the state estimates and their covariances.
        Z = torch.stack(z_list, dim=-1)   # (B, d, m)
        P = torch.stack(P_list, dim=1)    # (B, m, d, d)

        # Skip connection (eq. 22): Z' = Z + U
        # Happens to ensure that the non linear dynamics captured in U that koopman missed are not neglected
        # by the model and thus still contribute to the final prediction to help koopman net learn the non linear dynamics better.
        # It is added after the loop to ensure that the U's dont affect the covariance matrices P, 
        # which are meant to capture the uncertainty in the state estimates Z.
        # Over tiem as koopman net gets better X_res tends to 0 and thus so does U.
        # Adding it bakc here stops the kalman gain from eroding the non linearity. 
        # (as  kalman gain eahc step actiuve pulls us towards the prediction pulling us away from the non linearity not captured)
        Z_prime = Z + U

        return Z_prime, P
    