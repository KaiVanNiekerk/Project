# EKVAE Research Analysis

## Review Takeaways

From the reviews and rebuttal, the main points are:

1. The strongest support is for how well the model tracks dynamics in practice.
2. It is harder to separate what each part contributes because CO, EKVAE, and VHP are used together.
3. Reproducing the results may be harder because there is no official repository to follow.

### Practical Note

- Prioritize controlled experiments that test one part at a time rather than broad extension work.

### Method Notes and Watch-Outs

- Keep the first pass focused on the main trend, not every table entry.
- Do not let the combined setup hide what CO, EKVAE, and VHP each contribute.

### Toy-Data / Short-Sequence Caveat

- If the paper mostly used toy data or very short sequences, the reported gains may be easier to achieve than on longer, messier time series.
- Short sequences can make forecasting, filtering, and reconstruction look cleaner than they will on real datasets with longer temporal dependence.
- For our project, we should expect more difficulty on longer-horizon data and avoid treating toy-data performance as proof of broad generalization.

## Core Concepts

Use this order for implementation: ELBO/DSSM first, then CO, then EKVAE, then VHP.

### How to Read the Paper Background

The background section of the paper is setting up a simple idea: we want to model a sequence of observations while also keeping track of a hidden state that explains how the sequence evolves.

In the notation used there:

- $x_{1:T}$ is the observed sequence.
- $z_{1:T}$ is the hidden latent state sequence.
- $u_{1:T}$ is an optional control input sequence, such as actions.

The main assumption is the Markov assumption. In simple terms, this means the next hidden state is assumed to depend only on the current hidden state, not on the whole past. That is why the model is written as a product of step-by-step transition and observation terms. The latent state acts like the model's internal memory of the system.

The factorization in the paper says two things:

1. The hidden state evolves over time according to a transition model.
2. Each observation is generated from the current hidden state.

This is useful because it separates the dynamics from the observations. The dynamics describe how the system changes; the observation model describes how we see that system through noisy measurements.

The ELBO then gives the training objective for this setup. It can be read as a balance between two parts:

- reconstruction quality, which asks whether the model can explain the observed sequence well;
- compression or regularisation, which asks whether the latent representation stays compact and does not store unnecessary detail.

In the paper's notation, this is often described as distortion and rate. Distortion is the part that rewards good reconstruction. Rate is the part that measures how far the learned posterior is from the prior, which is another way of measuring how much information the latent state is using.

So the background section is really establishing the core trade-off of the whole method: a model should both reconstruct the sequence well and keep a sensible hidden state representation that explains the dynamics rather than memorising the data.

### Evidence Lower Bound (ELBO)

**What It Is:**
The ELBO is the core objective function in variational inference. It provides a lower bound on the log-likelihood of the data, which we maximize during training instead of directly maximizing the intractable likelihood.

**Formula:**
$$
   ext{ELBO} = \mathbb{E}_{q(z|x)}[\log p(x|z)] - \text{KL}(q(z|x) \| p(z))
$$

What this means:

- The expectation term measures how well the model can reconstruct the observed data from the latent variable.
- The KL term measures how far the learned latent distribution is from the prior.
- The model tries to make reconstruction strong while keeping the latent space well behaved.

**Detailed Explanation:**

- The first term, $\mathbb{E}_{q(z|x)}[\log p(x|z)]$, is the **distortion** term. It measures how well the model reconstructs the observed data from the latent variable $z$. Low distortion means the reconstruction is close to the input; high distortion means more information was lost in compression. In EKVAE, distortion checks whether the latent state still preserves the underlying system behaviour over time.

- The second term, $\text{KL}(q(z|x) \| p(z))$, is the **rate** term. It measures how much information the encoder stores in the latent code compared with the prior. A large KL means the model is using more latent capacity; a small KL means the code is more compressed. CO controls this term directly through the threshold $D_0$.

The trade-off is simple: too much distortion focus can lead to overfitting, while too much rate pressure can make the latent code too compressed to be useful.

**In This Project:**
The constrained optimization (CO) framework modifies this standard ELBO by introducing a constraint on the rate term. Instead of freely balancing reconstruction vs regularization, CO enforces that the KL divergence stays below a target threshold $D_0$. This allows us to explicitly control the trade-off between model complexity and reconstruction quality.

**Notes and Watch-Outs:**

- The distortion-rate balance is easy to overstate; the practical goal is useful reconstruction, not perfect compression.
- If the ELBO baseline is weak, later comparisons become harder to interpret.

### Deep State-Space Model (DSSM)

**What It Is:**
A DSSM is a neural generative model for sequences that combines a Markov state-space structure with deep neural networks for the dynamics and observation process.

**Structure:**
 A DSSM has two key parts:

1. **State transition model (dynamics):**
   $$
   z_t \sim p(z_t | z_{t-1})
   $$
   This describes how the hidden state evolves over time. It takes the previous state $z_{t-1}$ and generates the next state $z_t$. For EKVAE, this uses a neural network parameterized by $\theta$.

2. **Observation model (decoder):**
   $$
   x_t \sim p(x_t | z_t)
   $$
   This describes how observations are generated from the current state. It takes the state $z_t$ and generates the observation $x_t$. In practice, this is often a Gaussian with mean and variance predicted by a neural network.

**Joint Model:**
$$
p(x_{1:T}, z_{1:T}) = p(z_1) \prod_{t=2}^{T} p(z_t | z_{t-1}) \prod_{t=1}^{T} p(x_t | z_t)
$$

This factorization says: the full sequence likelihood breaks down into a prior on the initial state, a product of transition probabilities, and a product of observation probabilities.

What this means:

- $p(z_1)$ gives the starting hidden state.
- $p(z_t | z_{t-1})$ gives the rule for how the hidden state evolves from one step to the next.
- $p(x_t | z_t)$ gives the rule for how each observation is produced from the hidden state.
- The product notation means the same kind of step is repeated across the whole sequence.

**Why DSSM Is Useful for Dynamics:**

- the latent state is an explicit estimate of the system state;
- the next state depends on the current state, which fits many physical systems;
- it is often a cleaner fit than an unconstrained RNN.

**Inference in DSSM:**
During inference, we need to estimate the state sequence $z_{1:T}$ given observations $x_{1:T}$. The posterior is:
$$
q(z_{1:T} | x_{1:T}) = q(z_1 | x_{1:T}) \prod_{t=2}^{T} q(z_t | z_{t-1}, x_{1:T})
$$

This is tractable only under certain assumptions (like linearity or Gaussian transitions), which is where the Kalman filter/smoother comes in for the standard KVAE, and the Extended Kalman Filter for EKVAE.

**Notes and Watch-Outs:**

- DSSM assumptions are clean mathematically, but real sequence data may not follow the Markov assumption exactly.
- If the state transition is too weak, the model can collapse into a decoder-heavy solution.

### Constrained Optimization (CO) Framework

**What It Is:**
Constrained Optimization is a version of ELBO training that puts an explicit limit on the KL divergence instead of relying on a hand-tuned $\beta$.

**Problem with Standard ELBO Training:**
In weighted ELBO training, we optimize:
$$
	ext{ELBO} = \mathbb{E}_{q(z|x)}[\log p(x|z)] - \beta \cdot \text{KL}(q(z|x) \| p(z))
$$

What this means:

- $\beta$ is a hand-chosen weight on the KL term.
- A larger $\beta$ pushes the model to keep the latent space smaller.
- A smaller $\beta$ lets the model focus more on reconstruction.

The weight $\beta$ controls the trade-off, but:

- too small, and the model overfits;
- too large, and the model under-fits;
- the right value usually needs tuning for each dataset.

**CO Solution:**
Instead of balancing with a weight, CO enforces a hard constraint:

$$
\max_{q, p} \mathbb{E}_{q(z|x)}[\log p(x|z)] \quad \text{subject to} \quad \text{KL}(q(z|x) \| p(z)) \leq D_0
$$

This is solved using the Lagrangian formulation:
$$
\mathcal{L} = \mathbb{E}_{q(z|x)}[\log p(x|z)] - \lambda \cdot (\text{KL}(q(z|x) \| p(z)) - D_0)
$$

where $\lambda$ is a Lagrange multiplier updated during training.

**Connection to the ELBO:**
Recall that the ELBO splits into two terms: $\mathbb{E}_{q(z|x)}[\log p(x|z)] - \text{KL}(q(z|x) \| p(z))$. In the CO Lagrangian above, if we rearrange and expand, we recover exactly these terms:
$$
\mathcal{L} = \mathbb{E}_{q(z|x)}[\log p(x|z)] - \lambda \cdot \text{KL}(q(z|x) \| p(z)) + \text{constant}
$$

The first term $\mathbb{E}_{q(z|x)}[\log p(x|z)]$ is reconstruction (distortion), and the second term $\text{KL}(q(z|x) \| p(z))$ is rate. The multiplier $\lambda$ acts like a learned $\beta$ that adjusts during training, rather than being hand-chosen, to keep the rate near the target $D_0$.

What this means:

- $D_0$ is the target rate (KL) level.
- $\lambda$ is adjusted during training to keep the KL near that target.
- The model is no longer balancing the terms with a fixed weight; it is enforcing a limit.

**Why the Term Order Is Reversed:**
Notice that the ELBO puts reconstruction first: $\text{ELBO} = \text{distortion} - \text{rate}$, while the CO Lagrangian puts rate first: $\mathcal{L} = \text{rate} + \lambda(\text{distortion} - D_0)$. This is not accidental—it reflects a fundamental shift in perspective.

In the ELBO, we **maximize** a weighted trade-off. In the constrained form, we **minimize** rate while keeping distortion under a threshold, so the constrained quantity moves inside the multiplier term. This is the same objective/constraint flip summarized later in the "Constraint Flip" subsection.

**Why Minimize Rate at All:**

Rate is precisely the KL divergence term $\text{KL}(q(z|x) \| p(z))$, which measures how different the encoder's learned posterior $q(z|x)$ is from the prior $p(z)$. Intuitively:

- If KL is small, the encoder outputs are close to the prior, meaning the latent code carries little information about the input.
- If KL is large, the encoder diverges significantly from the prior, meaning the latent code is storing substantial information.

Minimizing this term encourages compact, structured latent codes. If rate is too high, the model can memorize observations instead of learning stable dynamics. The $D_0$ constraint keeps reconstruction quality acceptable while rate is pushed down.

**How It Works in Practice:**

In practice, this is implemented with a primal-dual update: model parameters optimize the Lagrangian while $\lambda$ is adapted to keep the chosen constraint near its threshold. The concrete update rule is given in the optimization subsection below.

**Why CO Is Useful:**

- $D_0$ has a clear information meaning.
- the weight is adapted during training instead of chosen by hand;
- it is a structured rate-distortion setup.

**How CO Relates to This Project:**
Your staged experiments include:

1. **Stage A:** ELBO baseline (standard $\beta$-weighted training)
2. **Stage B:** +CO (same model, but with constrained optimization)

This tests whether CO improves the same model under the same data.

**Practical Implications for Implementation:**

- Keep $\lambda$ updates stable and choose a realistic $D_0$ for each dataset.

**Risk to Watch (from Plausible Issues):**
The sensitivity to $D_0$ is real. If you set it too high, the constraint is meaningless. If you set it too low, the optimizer might fail to find a feasible solution. This is why the authors note that finding the "sweet spot" is important but not straightforward.

**Limitation: Multimodal Posteriors:**

CO operates at the rate level—it constrains the KL divergence between the encoder's posterior and the prior. However, this constraint does not address the fundamental representational limitation when the true posterior is multimodal.

The issue is this: if the true posterior $p(z_t | x_{1:T})$ has multiple well-separated modes, the encoder still outputs a single Gaussian $q(z_t | x_{1:T})$. The KL divergence between that Gaussian and the prior $p(z_t)$ is still well-defined and constrainable. But constraining KL does not make the single Gaussian a better approximation of the multimodal true posterior. You can satisfy $\text{KL}(q \| p(z)) \le D_0$ while still failing to capture the multiple modes.

In other words: CO helps keep the latent code compact and efficient, but it does not change the fact that the inference algorithm (the EKF/smoother in EKVAE) can only represent a single Gaussian belief at each time step. A multimodal true posterior requires a fundamentally different inference mechanism, like particle filters or mixture models, not just better rate/distortion trade-off tuning.

So if your data has multimodal posteriors, CO will not fix that problem. It may still improve over a poorly-tuned ELBO, but the ceiling on performance is set by the unimodal Gaussian assumption in the smoother itself.

**Notes and Watch-Outs:**

- CO should be treated as a controlled experiment, not an automatic improvement.
- The main implementation risk is unstable tuning of $D_0$ and $\lambda$.

**Toy-Data / Short-Sequence Caveat:**

- See the main caveat in `Review Takeaways`. The same short-sequence concern applies here when interpreting CO gains.

**Why This Matters in the Paper:**
Section 3 makes one main point: a high ELBO does not automatically mean the model has learned real dynamics. CO addresses this by keeping rate small while requiring distortion to stay below $D_0$. The optimization rule below implements that idea directly.

**Where CO Is Expected to Work Best (Initial Hypothesis):**

CO should perform strongest on systems and datasets with the following characteristics:

- **Smooth, low-noise dynamics:** Systems with predictable, continuous state evolution (e.g., simulated pendulums, robotic arms, smooth video) where trajectories don't have sudden jumps or stochasticity.
- **Approximately unimodal posteriors:** Observations should constrain the state well enough that the true posterior is mostly single-peaked. This happens when:
  - The measurement/rendering breaks symmetries (different states look visibly different),
  - Temporal context is rich (long enough sequences or high frame rate so direction/velocity is quickly disambiguated),
  - Noise is low enough that ambiguity resolves quickly.
- **Moderate sequence length:** Long enough that the dynamics matter (not single-frame prediction), but short enough that the latent budget remains tractable. Very long sequences may require tuning $D_0$ differently.
- **Sufficient observability:** The observed data should contain enough information to pin down most state variables. Partial or severely occluded observations are harder.

Conversely, CO is likely to struggle or provide less benefit on:

- Stochastic or chaotic systems where the posterior is inherently spread and multimodal.
- Data with symmetries (e.g., a pendulum viewed from the side: +45° and -45° look identical).
- Very short sequences where direction/velocity cannot be resolved from one frame.
- Sparse or highly corrupted observations.

On such data, the bottleneck is representational (unimodal inference), not just rate tuning, so CO alone cannot fix it.

### Constraint Flip: Rate-Constrained vs Distortion-Constrained

This project note uses both constrained forms in different places. They are related, but the constrained quantity and optimization priority are flipped.

**A) Rate-Constrained Form (as introduced earlier):**

$$
\max_{\theta,\phi}\; D(\theta,\phi)
\quad \text{subject to} \quad
R(\phi) \le R_0
$$

with Lagrangian

$$
\mathcal{L}_{\text{rate-const}} = D(\theta,\phi) - \lambda\big(R(\phi)-R_0\big).
$$

Interpretation: maximize reconstruction quality while enforcing an information budget.

**B) Distortion-Constrained Form (used in the optimization subsection):**

$$
\min_{\theta,\psi,\phi}\; R(\psi,\phi)
\quad \text{subject to} \quad
D(\theta,\phi) \le D_0
$$

with Lagrangian

$$
\mathcal{L}_{\text{dist-const}} = R(\psi,\phi) + \lambda\big(D(\theta,\phi)-D_0\big).
$$

Interpretation: minimize latent information usage while enforcing a reconstruction-quality floor.

**How to Identify the Flip in Formulae:**

- The unconstrained objective is the term outside the multiplier and appears first in the Lagrangian.
- The constrained quantity appears inside $\lambda(\cdot - \text{threshold})$.
- If the constraint is $R \le R_0$, you are in rate-constrained mode.
- If the constraint is $D \le D_0$, you are in distortion-constrained mode.

Both are valid rate-distortion formulations; they just choose opposite sides as the primary optimization target.

**Why This Flip Occurs and Why It Matters:**

The flip occurs because constrained optimization lets you choose either side of the rate-distortion trade-off as the primary objective and place the other side as a hard feasibility condition. Mathematically, this is a primal-design choice: optimize $D$ under a rate budget, or optimize $R$ under a distortion budget. The Lagrangian then reflects that choice automatically, with the constrained term appearing inside the multiplier.

This matters because it changes what training guarantees and how results should be interpreted. In rate-constrained form, the guarantee is bounded information usage, so reconstruction gains are read as "best quality under a fixed code budget." In distortion-constrained form, the guarantee is bounded reconstruction error, so compression gains are read as "smallest code that still meets quality." For this project, that distinction affects threshold selection ($R_0$ vs $D_0$), failure diagnosis (constraint violation indicates different bottlenecks), and fair comparison across stages.

**Short note on the apparent paper switch:**
If the paper first writes a distortion-constrained objective and later discusses a rate-constrained one, this is usually a change in parameterization and emphasis, not a contradiction. The authors are describing the same rate-distortion trade-off from two sides: one form fixes quality and optimizes compression, while the other fixes compression budget and discusses achievable quality.

### Optimization Algorithm for CO

This subsection describes the training procedure for the constrained objective. The architecture stays the same; what changes is how the encoder, decoder, and latent dynamics are updated during training.

The constrained problem is:

$$
\min_{\theta,\psi,\phi} R(\psi,\phi) \quad \text{subject to} \quad D(\theta,\phi) \le D_0
$$

Here:

- $\theta$ are the generative model parameters, usually the decoder and dynamics parameters.
- $\psi$ are the prior or transition parameters.
- $\phi$ are the inference or encoder parameters.
- $D(\theta,\phi)$ is the reconstruction distortion.
- $R(\psi,\phi)$ is the rate term.
- $D_0$ is the target distortion level.

The Lagrangian form is:

$$
\mathcal{L}(\theta,\psi,\phi;\lambda) = R(\psi,\phi) + \lambda\big(D(\theta,\phi) - D_0\big)
$$

This is a saddle-point problem: the model parameters are updated to reduce the Lagrangian, while the multiplier $\lambda$ is updated to keep the distortion constraint active.

In practice, training follows a primal-dual pattern:

1. Compute the current reconstruction error $D$ and rate $R$ on a batch.
2. Update the model parameters $\theta, \psi, \phi$ to reduce the Lagrangian.
3. Update $\lambda$ so the constraint stays near the target distortion.

The dual update is typically written as:

$$
\lambda \leftarrow \max\big(0,\, \lambda + \eta(D - D_0)\big)
$$

where $\eta$ is the dual learning rate.

This update has a simple interpretation:

- if distortion is too high, $\lambda$ increases and reconstruction is penalized more strongly;
- if distortion is already low enough, $\lambda$ decreases or stays small, letting the model spend more capacity on lowering rate;
- the non-negativity projection $\max(0, \cdot)$ keeps the multiplier valid.

This is the part that makes CO more than a fixed-weight ELBO. Instead of choosing one static $\beta$, the optimization adapts the penalty during training so the model stays near the desired distortion level.

To implement it, we need:

- a reconstruction term $D$;
- a rate term $R$;
- a target distortion $D_0$;
- a Lagrange multiplier $\lambda$;
- a learning rate for both the model parameters and the dual update.

The main practical risk is tuning $D_0$ and $\eta$ so that the constraint is enforced without making training unstable.

### REWO-Style Multiplier Update

The paper does not use a fixed multiplier update. Instead, it adopts a REWO (Reconstruction-based Weighting for Optimization) style rule that adapts $\lambda$ multiplicatively. The stated goal is to keep a lower bound on $\log p(x_{1:T} \mid u_{1:T})$ during training, which the paper says holds when $\lambda$ remains in the valid range.

The REWO-style update is:

$$
\lambda^{(i)} = \lambda^{(i-1)} \cdot \exp\left[-\nu \cdot f_\lambda\big(\lambda^{(i-1)}, D^{(i)}(\theta,\phi) - D_0; \tau_1, \tau_2\big) \cdot \big(D^{(i)}(\theta,\phi) - D_0\big)\right]
$$

This update means:

- if the distortion is above the target, the exponent pushes $\lambda$ upward so the reconstruction penalty becomes stronger;
- if the distortion is below the target, the update relaxes $\lambda$ so the model can focus more on rate reduction;
- the exponential form keeps $\lambda$ positive without needing a separate projection step.

The helper function is

$$
f_\lambda(\lambda, \delta; \tau_1, \tau_2) = 1 - H(\delta)\tanh\big(\tau_1(1/\lambda - 1)\big) - \tau_2 H(\delta)
$$

where $\delta = D^{(i)}(\theta,\phi) - D_0$ and $H$ is the Heaviside step function. Its role is to change the slope of the multiplier update depending on whether the constraint is currently violated.

In plain terms:

- when $\delta \le 0$, the constraint is already satisfied, so the update behaves more gently;
- when $\delta > 0$, the update becomes more aggressive and increases pressure on reconstruction;
- $\tau_1$ and $\tau_2$ control how sharp that switch is.

The paper also smooths the batch distortion before updating the multiplier:

$$
\hat{D}^{(i)} = (1-\alpha)\hat{D}_{ba} + \alpha\hat{D}^{(i-1)}
$$

This moving average matters because the raw batch distortion can fluctuate a lot from step to step. Smoothing makes the constraint update more stable and reduces the chance that $\lambda$ reacts to a noisy batch.

The smoothing weight $\alpha$ controls how much memory the update has: larger values make the distortion estimate react more slowly, while smaller values make it respond more quickly to the current batch.

### Two-Phase Training

The algorithm is split into two phases.

In the initial phase, the model updates only $\theta$ and $\phi$. The aim is to reduce reconstruction error first by learning the features of individual observations $x_t$. In this stage, the model is not yet updating the transition parameters.

Once the inequality $D(\theta,\phi) \le D_0$ is satisfied, the algorithm switches to the main phase. At that point it updates $\theta, \psi, \phi, \psi_0,$ and $\phi_0$ together, so the model can start learning the system dynamics and the VHP at the same time.

This phase split is important because it prevents the dynamics model from being learned before the reconstructions are already good enough. In other words, the method first learns to explain observations, then uses that stable reconstruction regime to learn latent dynamics.

What this adds beyond the basic Lagrangian view:

- the constraint is not enforced with a fixed step size;
- the multiplier is adapted using a smoothed distortion signal;
- the method uses a warm-up stage before learning the full dynamics model;
- this is the part that makes the algorithm practical, not just theoretical.

### Extended Kalman VAE (EKVAE)

**What It Is:**
EKVAE is the main model studied here. It uses an Extended Kalman Filter style update to handle nonlinear latent dynamics while still tracking a latent state over time.

**Why It Exists:**
Plain Kalman models work well when the dynamics are linear and Gaussian, but that is too restrictive for many real sequence problems. EKVAE keeps the state-space structure, but lets the transition function be nonlinear through a neural network. The Kalman part then makes approximate filtering and smoothing possible.

**Core Idea:**
The latent dynamics follow a nonlinear transition such as:
$$z_t = f_\theta(z_{t-1}) + \epsilon_t$$

What this means:

- $f_\theta$ is the learned transition model.
- It predicts the next hidden state from the current hidden state.
- $\epsilon_t$ represents random variation or modelling error.

and the observations are generated from the latent state through a decoder such as:
$$x_t = g_\phi(z_t) + \eta_t$$

What this means:

- $g_\phi$ is the observation or decoder model.
- It turns the hidden state into the visible observation.
- $\eta_t$ represents observation noise.
**How the Extended Kalman Part Works:**
EKVAE handles nonlinear transitions by using a learned, time-dependent local linearization. At each step the model emits a matrix $F_t$ that serves as a surrogate Jacobian for the transition map around the current latent state; this surrogate enables Kalman-style prediction and update for nonlinear dynamics.

Key points:

- $F_t$ is a task-driven, learned approximation (a surrogate Jacobian), not necessarily the exact analytic Taylor Jacobian of the true system.
- The EKF-style prediction and correction use $F_t$; its fidelity directly affects filtering and smoothing accuracy.
- Because $F_t$ is learned jointly with dynamics and inference networks, linearization errors can occur. If you intend to claim recovery of true system derivatives, include diagnostics (finite-difference Jacobian checks, prediction residual analysis, or sensitivity tests) comparing learned $F_t$ to numerical Jacobians.

Practical takeaway: treat $F_t$ as an inference-friendly surrogate and report predictive/system-ID performance as the primary evidence; include explicit validation when making claims about physical Jacobians.

**Why EKVAE Matters for This Project:**
It is where ELBO, DSSM, CO, and VHP come together, so it is the main model we want to test and reproduce.

**How It Connects to the Paper's Claims:**
The paper's claim is that EKVAE should capture temporal structure better than a plain VAE or a generic recurrent model.

**Why It Can Be Tricky in Practice:**

- The EKF approximation depends on the quality of the learned local linearisation, so linearization errors can affect performance.
- Training can be sensitive because the model has multiple moving parts: encoder, decoder, transition model, and filtering logic.
- If the latent dynamics are too nonlinear or the observations too noisy, the approximate linearization may struggle.

**What This Means for Our Implementation:**
We do not need every proof; we need the latent transition, observation model, and EKF-style inference implemented consistently.

**Notes and Watch-Outs:**

- EKVAE is more fragile than a simple VAE because transition, decoder, and filtering all need to work together.
- Linearization errors can matter more than they do in simpler models.

**Toy-Data / Short-Sequence Caveat:**

- See the main caveat in `Review Takeaways`. The same short-sequence concern applies when assessing EKVAE robustness.

### Variational Hierarchical Prior (VHP)

**What It Is:**
The Variational Hierarchical Prior is a more flexible latent prior than a single fixed Gaussian prior. It uses a hierarchy so the prior can adapt to more complex sequence structure.

**Why It Exists:**
A simple prior can be too rigid for sequential data, so VHP gives the model more freedom to represent uncertainty and multi-scale patterns.

**General Idea of the Hierarchy:**
At a high level, the prior is not just:
$$p(z_t)$$

but something closer to a layered prior such as:
$$p(z_t, h_t) = p(z_t \mid h_t) p(h_t)$$

What this means:

- $h_t$ is a higher-level latent variable.
- $p(h_t)$ gives the distribution of that higher-level variable.
- $p(z_t \mid h_t)$ says the actual latent state depends on that higher-level structure.
- This makes the prior more flexible than a single Gaussian.

**How This Is Achieved in Practice:**

Instead of forcing one global Gaussian shape for all sequences, VHP adds a second latent level that can adapt the prior shape for different sequence contexts.

1. Sample a higher-level variable (e.g., $\zeta$ or $h$) from a simple base prior.
2. Use that variable to parameterize the lower-level prior over $z$ (for example, by changing mean/covariance of $p(z\mid \zeta)$).
3. Marginalize over the higher-level variable:
   $$p(z)=\int p(z\mid \zeta)p(\zeta)\,d\zeta$$

In many implementations, the higher-level prior is kept simple (often $p(\zeta)=\mathcal{N}(0,I)$) for stable and tractable optimization. The flexibility comes from the conditional mapping $p(z\mid \zeta)$: even with a Gaussian $p(\zeta)$, marginalizing through a nonlinear or parameterized conditional produces a much richer effective prior over $z$ than a single fixed Gaussian.

So the hierarchy separates roles: $\zeta$ is the simple "global selector" latent, while $z$ is the task/dynamics latent whose prior shape is adapted through $\zeta$.

This integral creates a mixture-like effective prior, which can represent curved or multi-region latent manifolds that a single $\mathcal{N}(0,I)$ cannot.

During training, a variational posterior (like $q_{\phi_0}(\zeta\mid z)$) is learned so this hierarchy stays tractable. The result is that the learned prior better matches the aggregate posterior from data, which typically reduces over-regularization pressure from the KL term.

**How to Interpret It:**

- $z_t$ still represents the actual dynamics.
- $h_t$ shapes how $z_t$ is distributed over time.
- Together, they make the prior more expressive than a plain Gaussian.

**Why This Matters Mathematically:**
Simple priors are easier to infer with, but they can be a poor fit for real sequential data. VHP gives the model a richer prior family that can improve the latent representation when the data is complex.

**How It Relates to This Project:**
VHP is the final later stage in our staged comparison:

1. ELBO baseline
2. +CO
3. +EKVAE
4. +VHP

It lets us test whether the richer prior improves prediction or system identification beyond the earlier stages.

**Practical Trade-Off:**

- **Benefit:** a more flexible prior that may fit complex dynamics better.
- **Cost:** more parameters, more computation, and more overfitting risk on small datasets.
- **Interpretation:** if it does not clearly improve over +EKVAE, the extra complexity may not be worth it.

**What to Watch for in Implementation:**

- training may become less stable;
- the prior may be harder to tune;
- gains may depend on the dataset, so VHP should stay a later comparison step.

**Notes and Watch-Outs:**

- VHP is the most likely place for diminishing returns if the dataset is small or simple.
- Keep it as a later stage, not the first thing to debug.

**Toy-Data / Short-Sequence Caveat:**

- See the main caveat in `Review Takeaways`. The same short-sequence concern applies when attributing gains to VHP.

### Learning the Initial Distribution

This section of the paper is about the prior for the first latent state, $z_1$. The key idea is simple: a fixed standard normal prior can be too restrictive, so the model should learn a better starting distribution from the data.

The formulas to remember are:

- $p(z_1) = \mathcal{N}(0, I)$ is the simple default prior the paper wants to improve on.
- $p^*(z_1) = \mathbb{E}_{p_D}[q_\phi(z_1 \mid x, u)]$ is the empirical Bayes target: the prior should match the average posterior initial state from the data.
- $p_{\psi_0}(z_1) = \int p_{\psi_0}(z_1 \mid \zeta)p(\zeta)\,d\zeta$ is the hierarchical prior used to approximate that target.
- $q_{\phi_0}(\zeta \mid z_1)$ is the variational posterior used to learn the hierarchical prior.

Together, these equations say: the standard normal prior is often too simple; the empirical Bayes target gives a data-matched prior; and the hierarchical prior plus variational posterior is the tractable way to learn that richer shape in practice.

**Why This Matters:**

The key insight is that $z_1$ is not just a starting point—it affects the entire sequence because each $z_t$ depends on $z_{t-1}$. If you start with an unrealistic prior for $z_1$, the model has to fight to explain the data from an incorrect starting position. This wastes capacity in the latent representation.

More concretely: if $p(z_1)$ is too narrow (like the standard normal), the inference network $q_\phi(z_1 \mid x, u)$ will be penalized in the KL term for deviating from it. But the data may naturally lead to very different initial latent states. The model then either:

1. Accepts a high KL penalty (increasing the rate term), which reduces the budget for reconstruction quality, or
2. Stays close to the prior despite it being wrong, which forces the transition model to compensate and weakens the dynamics learning.

Either way, a poor prior on $z_1$ undermines what the model is trying to learn.

The solution is to learn the prior from the data itself. The empirical Bayes target $p^*(z_1) = \mathbb{E}_{p_D}[q_\phi(z_1 \mid x, u)]$ says: look at what the inference network learns as the initial state across your entire dataset, and use that as your prior. This way, the prior and the inferred initial states are naturally aligned, the KL term is reduced, and the model has more capacity to capture both reconstruction quality and meaningful dynamics.

**Practical Consequence for This Project:**

In the CO framework, the trade-off is between rate (KL) and distortion (reconstruction). A better prior on $z_1$ directly reduces the rate term without sacrificing distortion. The empirical Bayes target is ideal but not directly learnable during minibatch training, so the hierarchical prior is used as the practical approximation:

- The latent variable $\zeta$ acts as a "hyper-parameter" for the $z_1$ distribution.
- Marginalizing over $\zeta$ gives a more flexible family of distributions than a simple Gaussian.
- The variational posterior $q_{\phi_0}(\zeta \mid z_1)$ lets you fit this richer prior to match the empirical distribution across your data.

This two-level structure approximates the empirical Bayes target without computing a full-dataset expectation at every step.

### Evaluation Metrics

Two simple formulas are used to judge the model's performance:

**MSE (Mean Squared Error):**
$$
\mathrm{MSE} = \frac{1}{NT}\sum_{n=1}^{N}\sum_{t=1}^{T} \lVert \hat{x}_t^{(n)} - x_t^{(n)} \rVert_2^2
$$

What this means:

- $\hat{x}_t^{(n)}$ is the model's predicted value.
- $x_t^{(n)}$ is the true value.
- The squared difference measures how far the prediction is from the truth.
- Averaging over all sequences and time steps gives one overall error score.

Lower MSE means the model is reconstructing or forecasting more accurately.

**$R^2$ (Coefficient of Determination):**
$$
R^2 = 1 - \frac{\sum_i (y_i - \hat{y}_i)^2}{\sum_i (y_i - \bar{y})^2}
$$

What this means:

- $y_i$ is the true target value.
- $\hat{y}_i$ is the predicted target value.
- $\bar{y}$ is the average of the true target values.
- The numerator measures prediction error.
- The denominator measures the total variation in the true values.

An $R^2$ value near 1 means the latent variables explain the target state well. A value near 0 means the model is doing about as well as just predicting the mean. Negative values mean the model is doing worse than that simple baseline.

These metrics close the method section and define how we will judge each stage in the comparison. The next section translates this into concrete scope decisions for execution.

## Scope Plan

Based on the review feedback and the no-code constraint, this is what should stay, be deferred, or be removed.

### Keep in Immediate Scope

1. Keep all three paper datasets for the core study.
   Why: this stays faithful to the benchmark setup while avoiding new dataset confounders.
   Included: pendulum, reacher-angle, reacher-RGB.

2. Keep staged comparison experiments.
   Why: this directly addresses the review criticism that the contributions are not clearly separated.
   Order: ELBO baseline -> +CO -> +EKVAE -> +VHP.

3. Keep a reduced but representative baseline set.
   Why: provides meaningful comparison without rebuilding an entire model zoo.
   Suggested minimum: one standard DSSM baseline, one KVAE-family baseline, EKVAE target model.

4. Keep trend-level replication as the primary endpoint.
   Why: exact metric matching is fragile without official implementation details.
   Standard: match trends and component effects first; do not treat exact number matching as required.

### Defer to a Later Phase

1. New transfer datasets (finance, health, or other non-paper datasets).
   Why: valuable, but not required to answer the first core research question.

2. Full baseline-family recreation.
   Why: high engineering cost and high risk of shallow comparisons.

3. Deep hyperparameter tuning sweeps.
   Why: useful later, but not vital for first-pass evidence.

### Remove from Immediate Scope

1. RL/disentanglement extensions and side claims.
   Why: not central to the immediate supervisor-critical objective.

2. Exact numeric replication as a hard milestone.
   Why: too brittle in an independent reimplementation setting.

**Notes and Watch-Outs:**

- The safest reduction is to preserve the paper datasets and core model stages, then only expand if the first results are stable.
- Extra datasets and heavy sweeps should wait until the baseline chain is working.

## Method Watch-outs

These are known limitations or practical challenges with the EKVAE approach itself, not just the paper.

1. **Distortion Baseline Sensitivity ($D_0$)**
   The constrained optimization requires picking a baseline distortion $D_0$. If this hyperparameter is set too high, the optimization can fail abruptly. The authors assume we can find the "sweet spot" through heuristics, but this is a practical tuning problem that may not generalize well across datasets.

2. **Markov Assumption vs Hidden Dynamics**
   The core argument for state-space models is that RNNs do not follow a strict Markov form. However, real-world systems often have unmeasured dynamics such as small disturbances, sensor noise, or hidden states. In those cases, an RNN's implicit memory may be more robust than a model that only uses the current state when observations are incomplete.

3. **Computational Cost of VHP**
   The Variational Hierarchical Prior adds flexibility but also computational overhead and more parameters. On smaller datasets or simpler tasks, this can lead to overfitting rather than better generalization. It may be overkill for some problems.

4. **Neural Linearization as Approximation**
   The EKF uses a neural network to approximate the Jacobian rather than computing exact derivatives by hand. This is efficient but approximate, so the learned linearization may be useful for training without perfectly matching the true system Jacobian.

### Notes and Watch-Outs

- These are not reasons to drop the method outright; they are reasons to keep expectations realistic.
- In practice, they mostly argue for careful component checks, clear reporting, and not overclaiming exact reproduction.
