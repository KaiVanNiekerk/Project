# K²VAE Replication Roadmap

Architecture: **Input Token Embedding → KoopmanNet → KalmanNet → Decoder**,
trained jointly via $\mathcal{L}_{ELBO} + \mathcal{L}_{Rec}$.

---

## Phase 0 — Scaffolding & Data Pipeline

- Patching: $X \in \mathbb{R}^{N\times T} \to X^P \in \mathbb{R}^{N\times s\times n}$, non-overlapping patches, $s = T/n$.
- Input Token Embedding:

$$
X^{P'} = \mathrm{Projection}(\mathrm{Flatten}(X^P)) \in \mathbb{R}^{d\times n}
$$

- Get one small dataset loading cleanly (start with ETTh1 or Exchange).

**Checkpoint:** shapes check out end-to-end from raw series to embedded tokens, no model logic yet.

---

## Phase 1 — KoopmanNet (Linearisation)

- Measurement function $\psi$ (MLP):

$$
X^{P^*} = \psi(X^{P'}) = \left[x_1^{P^*}, x_2^{P^*}, \dots, x_n^{P^*}\right]
$$

- One-step eDMD for the local Koopman operator:

$$
X^{P^*}_{back} = \left[x_1^{P^*}, \dots, x_{n-1}^{P^*}\right], \qquad
X^{P^*}_{fore} = \left[x_2^{P^*}, \dots, x_n^{P^*}\right]
$$

$$
K_{loc} = X^{P^*}_{fore} \left(X^{P^*}_{back}\right)^{\dagger}
$$

- Learnable global part $K_{glo}$, combined operator:

$$
K = K_{loc} + K_{glo}
$$

- Rollout via matrix powers:

$$
\hat x_i^{C} = (K)^{i-1} x_1^{P^*}, \qquad \hat x_i^{H} = (K)^{i+n-1} x_1^{P^*}
$$

giving $\hat X^C \in \mathbb{R}^{d\times n}$ (context reconstruction) and $\hat X^H \in \mathbb{R}^{d\times m}$ (predicted horizon in measurement space).

**Checkpoint:** train KoopmanNet alone with

$$
\mathcal{L}_{Rec} = \left\lVert X - \psi^{-1}(\hat X^C) \right\rVert_2^2
$$

using a placeholder decoder, and confirm reasonable context reconstruction. Test the **mixed** $K = K_{loc}+K_{glo}$ from the start — $K_{loc}$ alone is numerically unstable on some datasets (see ablation results).

---

## Phase 2 — KalmanNet

- Residual and control input via Integrator (Transformer encoder):

$$
X^{Res} = X^{P^*} - \hat X^{C}, \qquad U = \mathrm{Integrator}(X^{Res}) = [u_1, \dots, u_m]
$$

- Process model:

$$
z_k = Az_{k-1} + Bu_k + w_k, \qquad w_k \sim \mathcal{N}(0, Q), \qquad z_0 = x_n^{P^*}
$$

- Observation model (note: $\hat X^H$ from KoopmanNet is treated as the *prior observation*):

$$
o_k = Hz_k + v_k, \qquad v_k \sim \mathcal{N}(0, R)
$$

- Prediction step:

$$
\hat z_k = Az_{k-1} + Bu_k, \qquad \hat P_k = AP_{k-1}A^T + Q
$$

- Update step:

$$
K_k = \hat P_k H^T \left(H\hat P_k H^T + R\right)^{-1}
$$

$$
z_k = \hat z_k + K_k\left(\hat x_k^H - H\hat z_k\right)
$$

$$
P_k = (I - K_kH)\hat P_k
$$

- Numerically stable covariance update (Theorem 3.1):

$$
P_k = \tfrac{1}{2}\left(P_k + P_k^T\right)
$$

$$
P_k^{dual} = (I-K_kH)\hat P_k(I-K_kH)^T + K_kRK_k^T
$$

- Skip connection:

$$
Z' = Z + U
$$

- Positive-definiteness of $Q, R$ via Cholesky-style parameterisation: $Q = L_QL_Q^T$, $R = L_RL_R^T$.

**Checkpoint:** with KoopmanNet frozen (or jointly), confirm the Kalman recursion runs stably over the full horizon $m$ without covariance blowup.

---

## Phase 3 — Decoder & Full ELBO

- Variational distribution:

$$
Q(Z\mid X) = \mathcal{N}(Z', P)
$$

- Reparameterised sampling, then two decoder heads:

$$
Z^{sample} = \mathrm{Resample}(Q(Z\mid X)), \qquad
\mu = \psi_\mu^{-1}(Z^{sample}), \qquad \sigma = \psi_\sigma^{-1}(Z^{sample})
$$

$$
X^{Rec} = \psi_\mu^{-1}(\hat X^C), \qquad P(Y\mid Z) = \mathcal{N}(\mu, \sigma)
$$

- Full learning objective:

$$
\mathcal{L}_{ELBO} = -\mathbb{E}[\log P(Y\mid Z,X)] + D_{KL}\big(Q(Z\mid X)\,\|\,P(Z\mid X)\big), \qquad P(Z\mid X) = \mathcal{N}(0,I)
$$

$$
\mathcal{L}_{Rec} = \left\lVert X - X^{Rec} \right\rVert_2^2
$$

**Checkpoint:** full forward/backward pass, loss decreasing, no NaNs — first real end-to-end training run on ETTh1 short-term.

---

## Phase 4 — Metrics & Sanity vs. Paper

- **NMAE:**

$$
\mathrm{NMAE} = \frac{\sum_{k=1}^{K}\sum_{t=1}^{T} \left|x_t^k - \hat x_t^k\right|}{\sum_{k=1}^{K}\sum_{t=1}^{T} \left|x_t^k\right|}
$$

- **CRPS** (empirical CDF, 100 samples):

$$
\mathrm{CRPS} = \int_{\mathbb{R}} \big(F(z) - \mathbb{I}\{x \le z\}\big)^2\, dz
$$

- Reproduce 1–2 of the paper's own numbers (e.g. Exchange-S, ETTh1-S) before scaling to the full benchmark suite.

---

## Phase 5 — Ablations (optional)

- $K_{loc}$ only vs. $K_{glo}$ only vs. mixed $K$.
- w/o Integrator, w/o skip connection, w/o control input.
- w/o KoopmanNet, w/o KalmanNet.

---

## Open Fork Point: Partial Observations

This roadmap replicates K²VAE as specified (fully-observed inputs). If the
extension to partial observations is greenlit, the seam is primarily at the
**Observation Model** stage:

$$
o_k = Hz_k + v_k
$$

which would need to become a genuine observation-to-state mapping rather
than treating $\hat X^H$ as a pseudo-observation.

# Libraries

## Libraries to use

| Library | Role |
|---|---|
| **PyTorch** | Core tensor ops, autograd, `nn.Module` for KoopmanNet/KalmanNet/Decoder. |
| **NumPy** | Vectorised array ops outside the autograd graph; sanity-checking eDMD pseudoinverse on toy data. |
| **einops** | Clean, readable reshape/rearrange for patching ($X\in\mathbb{R}^{N\times T}\to X^P\in\mathbb{R}^{N\times s\times n}$); self-documenting tensor shape contracts. |
| **pandas** | Loading/preprocessing raw time series CSVs, resampling, train/val/test splitting — done independently rather than via ProbTS's `DataManager`. |
| **scikit-learn** | `StandardScaler`/`MinMaxScaler` for normalisation; `LinearRegression` for the $R^2$ system-identification metric. |
| **matplotlib / seaborn** | State-space visualisations, training curves, ablation bar charts. |
| **plotly** | Interactive 3D latent-space scatter plots for exploring barrel/circle structure. |
| **properscoring** (or hand-written) | CRPS computation, written from the empirical-CDF definition rather than borrowed. |
| **wandb** | Experiment tracking across ablation runs. |
| **tqdm** | Progress bars for training loops. |
| **PyTorch Lightning** *(optional)* | Generic trainer utility only — not adopting their `LightningModule`/config-YAML structure. |

## Libraries deliberately NOT used

| Library | Reason to avoid |
|---|---|
| **ProbTS** | The official K²VAE benchmark harness; reimplementing dataset classes independently (using only publicly documented context/prediction lengths and frequencies) is both more defensible academically and avoids mirroring undocumented preprocessing quirks. |
| **pydmd** | The one-step eDMD used (`X_fore @ pinv(X_back)`) is trivial; a full DMD library is unnecessary and writing it by hand ensures understanding of the local Koopman operator. |
| **filterpy** | Does not support the *learned* gain/matrices structure EKVAE/K²VAE require; the predict/update recursion is implemented by hand regardless. |
| **JAX / Pyro** | Native PyTorch stack preferred for consistency across the project. |