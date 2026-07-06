## Why does K² only use KalmanNet and not a normal Kalman filter?

The classical KF is optimal only under a linear-Gaussian model with known
$F, B, H, Q, R$:

$$z_{t+1} = Fz_t + Bu_t + w_t,\quad w_t\sim\mathcal N(0,Q)$$
$$x_t = Hz_t + v_t,\quad v_t\sim\mathcal N(0,R)$$

The gain $K_t = P_t^-H^\top(HP_t^-H^\top+R)^{-1}$ is derived from $Q,R$, so it's
only trustworthy if those actually describe the true noise.

Koopman theory guarantees exact linearity only in an infinite-dimensional
observable space. A finite-dimensional KoopmanNet gives
$\tilde z_{t+1} = F\tilde z_t + \varepsilon_t$, where $\varepsilon_t$ is
state-dependent truncation error, not clean Gaussian noise. Feeding this into
the analytic KF gain would miscalibrate trust between prediction and
observation.

KalmanNet keeps the recursive predict-correct structure but learns the
correction instead of deriving it analytically:

$$m_t = m_t^- + \mathcal K_\phi(m_t^-, x_t)(x_t - Hm_t^-)$$

This lets training calibrate the gain to the actual residual statistics of
the Koopman approximation, rather than assuming a fixed noise model that
doesn't hold.