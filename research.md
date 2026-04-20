# EKVAE Research Analysis

## Review Takeaways

From the reviews and rebuttal, the main points are:

1. The strongest support is for how well the model tracks dynamics in practice.
2. It is harder to separate what each part contributes because CO, EKVAE, and VHP are used together.
3. Reproducing the results may be harder because there is no official repository to follow.

Practical note:

- Prioritize controlled experiments that test one part at a time rather than broad extension work.

**Notes / watch-outs:**
- Keep the first pass focused on the main trend, not every table entry.
- Do not let the combined setup hide what CO, EKVAE, and VHP each contribute.

**Toy-data / short-sequence caveat:**
- If the paper mostly used toy data or very short sequences, the reported gains may be easier to achieve than on longer, messier time series.
- Short sequences can make forecasting, filtering, and reconstruction look cleaner than they will on real datasets with longer temporal dependence.
- For our project, that means we should expect more difficulty when moving to longer-horizon data, and we should not treat toy-data performance as proof of broad generalization.

## Core Concepts

Use this order for implementation: ELBO/DSSM first, then CO, then EKVAE, then VHP.

### Evidence Lower Bound (ELBO)

**What it is:**
The ELBO is the core objective function in variational inference. It provides a lower bound on the log-likelihood of the data, which we maximize during training instead of directly maximizing the intractable likelihood.

**The formula:**
$$\text{ELBO} = \mathbb{E}_{q(z|x)}[\log p(x|z)] - \text{KL}(q(z|x) \| p(z))$$

**Detailed explanation:**
- The first term, $\mathbb{E}_{q(z|x)}[\log p(x|z)]$, is the **distortion** term. It measures how well the model reconstructs the observed data from the latent variable $z$. Low distortion means the reconstruction is close to the input; high distortion means more information was lost in compression. In EKVAE, distortion checks whether the latent state still preserves the underlying system behaviour over time.

- The second term, $\text{KL}(q(z|x) \| p(z))$, is the **rate** term. It measures how much information the encoder stores in the latent code compared with the prior. A large KL means the model is using more latent capacity; a small KL means the code is more compressed. CO controls this term directly through the threshold $D_0$.

The trade-off is simple: too much distortion focus can lead to overfitting, while too much rate pressure can make the latent code too compressed to be useful.

**In the context of this project:**
The constrained optimization (CO) framework modifies this standard ELBO by introducing a constraint on the rate term. Instead of freely balancing reconstruction vs regularization, CO enforces that the KL divergence stays below a target threshold $D_0$. This allows us to explicitly control the trade-off between model complexity and reconstruction quality.

**Notes / watch-outs:**
- The distortion-rate balance is easy to overstate; the practical goal is useful reconstruction, not perfect compression.
- If the ELBO baseline is weak, later comparisons become harder to interpret.

### Deep State-Space Model (DSSM)

**What it is:**
A DSSM is a neural generative model for sequences that combines a Markov state-space structure with deep neural networks for the dynamics and observation process.

**The structure:**
A DSSM has two key parts:

1. **State transition model (dynamics):**
   $$z_t \sim p(z_t | z_{t-1})$$
   This describes how the hidden state evolves over time. It takes the previous state $z_{t-1}$ and generates the next state $z_t$. For EKVAE, this uses a neural network parameterized by $\theta$.

2. **Observation model (decoder):**
   $$x_t \sim p(x_t | z_t)$$
   This describes how observations are generated from the current state. It takes the state $z_t$ and generates the observation $x_t$. In practice, this is often a Gaussian with mean and variance predicted by a neural network.

**The joint model:**
$$p(x_{1:T}, z_{1:T}) = p(z_1) \prod_{t=2}^{T} p(z_t | z_{t-1}) \prod_{t=1}^{T} p(x_t | z_t)$$

This factorization says: the full sequence likelihood breaks down into a prior on the initial state, a product of transition probabilities, and a product of observation probabilities.

**Why DSSM is useful for dynamics:**
- the latent state is an explicit estimate of the system state;
- the next state depends on the current state, which fits many physical systems;
- it is often a cleaner fit than an unconstrained RNN.

**Inference in DSSM:**
During inference, we need to estimate the state sequence $z_{1:T}$ given observations $x_{1:T}$. The posterior is:
$$q(z_{1:T} | x_{1:T}) = q(z_1 | x_{1:T}) \prod_{t=2}^{T} q(z_t | z_{t-1}, x_{1:T})$$

This is tractable only under certain assumptions (like linearity or Gaussian transitions), which is where the Kalman filter/smoother comes in for the standard KVAE, and the Extended Kalman Filter for EKVAE.

**Notes / watch-outs:**
- DSSM assumptions are clean mathematically, but real sequence data may not follow the Markov assumption exactly.
- If the state transition is too weak, the model can collapse into a decoder-heavy solution.

### Constrained Optimization (CO) Framework

**What it is:**
Constrained Optimization is a version of ELBO training that puts an explicit limit on the KL divergence instead of relying on a hand-tuned $\beta$.

**The problem with standard ELBO training:**
In weighted ELBO training, we optimize:
$$\text{ELBO} = \mathbb{E}_{q(z|x)}[\log p(x|z)] - \beta \cdot \text{KL}(q(z|x) \| p(z))$$

The weight $\beta$ controls the trade-off, but:
- too small, and the model overfits;
- too large, and the model under-fits;
- the right value usually needs tuning for each dataset.

**The CO solution:**
Instead of balancing with a weight, CO enforces a hard constraint:

$$\max_{q, p} \mathbb{E}_{q(z|x)}[\log p(x|z)] \quad \text{subject to} \quad \text{KL}(q(z|x) \| p(z)) \leq D_0$$

This is solved using the Lagrangian formulation:
$$\mathcal{L} = \mathbb{E}_{q(z|x)}[\log p(x|z)] - \lambda \cdot (\text{KL}(q(z|x) \| p(z)) - D_0)$$

where $\lambda$ is a Lagrange multiplier updated during training.

**How it works in practice:**
1. Set a target rate threshold $D_0$.
2. Adjust $\lambda$ during training so the KL stays near that target.
3. Increase the penalty if KL rises too high.
4. Relax it if KL stays too low.

**Why CO is useful:**
- $D_0$ has a clear information meaning.
- the weight is adapted during training instead of chosen by hand;
- it is a structured rate-distortion setup.

**How CO relates to this project:**
Your staged experiments include:
1. **Stage A:** ELBO baseline (standard $\beta$-weighted training)
2. **Stage B:** +CO (same model, but with constrained optimization)

This tests whether CO improves the same model under the same data.

**Practical implications for implementation:**
- update $\lambda$ during training;
- choose a reasonable $D_0$ for each dataset;
- keep the updates stable so training does not oscillate.

**Risk to watch (from Plausible Issues):**
The sensitivity to $D_0$ is real. If you set it too high, the constraint is meaningless. If you set it too low, the optimizer might fail to find a feasible solution. This is why the authors note that finding the "sweet spot" is important but not straightforward.

**Notes / watch-outs:**
- CO should be treated as a controlled experiment, not an automatic improvement.
- The main implementation risk is unstable tuning of $D_0$ and $\lambda$.

**Toy-data / short-sequence caveat:**
- CO may look especially stable on short or simple sequences, because the latent budget is easier to manage.
- On longer sequences, the same $D_0$ may behave differently, so tuning expectations should stay realistic.

### Extended Kalman VAE (EKVAE)

**What it is:**
EKVAE is the main model studied here. It uses an Extended Kalman Filter style update to handle nonlinear latent dynamics while still tracking a latent state over time.

**Why it exists:**
Plain Kalman models work well when the dynamics are linear and Gaussian, but that is too restrictive for many real sequence problems. EKVAE keeps the state-space structure, but lets the transition function be nonlinear through a neural network. The Kalman part then makes approximate filtering and smoothing possible.

**Core idea:**
The latent dynamics follow a nonlinear transition such as:
$$z_t = f_\theta(z_{t-1}) + \epsilon_t$$

and the observations are generated from the latent state through a decoder such as:
$$x_t = g_\phi(z_t) + \eta_t$$

where $f_\theta$ is the learned transition model, $g_\phi$ is the observation/decoder model, and $\epsilon_t, \eta_t$ are noise terms.

**How the Extended Kalman part works:**
Because the transition is nonlinear, EKVAE cannot use a standard linear Kalman update directly. Instead, it linearizes the transition around the current estimate using a Jacobian:
$$F_t = \frac{\partial f_\theta}{\partial z}\bigg|_{z = \hat{z}_{t-1}}$$

This Jacobian gives a local linear approximation of the nonlinear transition. The filter then uses that approximation to predict and correct the latent state.

At a high level, the EKF step does two things:
1. **Prediction:** use the learned dynamics model to predict the next latent state.
2. **Update:** use the new observation to correct that prediction.

This is what lets EKVAE keep the sequential structure of a state-space model while still handling nonlinear dynamics.

**Why EKVAE matters for this project:**
It is where ELBO, DSSM, CO, and VHP come together, so it is the main model we want to test and reproduce.

**How it connects to the paper's claims:**
The paper's claim is that EKVAE should capture temporal structure better than a plain VAE or a generic recurrent model.

**Why it can be tricky in practice:**
- The EKF approximation depends on the local Jacobian, so errors in linearization can affect performance.
- Training can be sensitive because the model has multiple moving parts: encoder, decoder, transition model, and filtering logic.
- If the latent dynamics are too nonlinear or the observations too noisy, the approximate linearization may struggle.

**What this means for our implementation:**
We do not need every proof; we need the latent transition, observation model, and EKF-style inference implemented consistently.

**Notes / watch-outs:**
- EKVAE is more fragile than a simple VAE because transition, decoder, and filtering all need to work together.
- Linearization errors can matter more than they do in simpler models.

**Toy-data / short-sequence caveat:**
- EKVAE can look strong on short toy sequences because the nonlinear dynamics are easier to track.
- Longer sequences or noisier datasets may expose filtering errors more clearly, so we should expect performance to drop if the paper mostly used short horizons.

### Variational Hierarchical Prior (VHP)

**What it is:**
The Variational Hierarchical Prior is a more flexible latent prior than a single fixed Gaussian prior. It uses a hierarchy so the prior can adapt to more complex sequence structure.

**Why it exists:**
A simple prior can be too rigid for sequential data, so VHP gives the model more freedom to represent uncertainty and multi-scale patterns.

**General idea of the hierarchy:**
At a high level, the prior is not just:
$$p(z_t)$$

but something closer to a layered prior such as:
$$p(z_t, h_t) = p(z_t \mid h_t) p(h_t)$$

where $h_t$ is a higher-level latent variable that shapes the distribution of $z_t$. This lets the model express latent structure at more than one level.

**How to interpret it:**
- $z_t$ still represents the actual dynamics.
- $h_t$ shapes how $z_t$ is distributed over time.
- Together, they make the prior more expressive than a plain Gaussian.

**Why this matters mathematically:**
Simple priors are easier to infer with, but they can be a poor fit for real sequential data. VHP gives the model a richer prior family that can improve the latent representation when the data is complex.

**How it relates to this project:**
VHP is the final later stage in our staged comparison:
1. ELBO baseline
2. +CO
3. +EKVAE
4. +VHP

It lets us test whether the richer prior improves prediction or system identification beyond the earlier stages.

**Practical trade-off:**
- **Benefit:** a more flexible prior that may fit complex dynamics better.
- **Cost:** more parameters, more computation, and more overfitting risk on small datasets.
- **Interpretation:** if it does not clearly improve over +EKVAE, the extra complexity may not be worth it.

**What to watch for in implementation:**
- training may become less stable;
- the prior may be harder to tune;
- gains may depend on the dataset, so VHP should stay a later comparison step.

**Notes / watch-outs:**
- VHP is the most likely place for diminishing returns if the dataset is small or simple.
- Keep it as a later stage, not the first thing to debug.

**Toy-data / short-sequence caveat:**
- A richer prior can look helpful on small toy data but add less value on larger datasets if the extra complexity is not needed.
- If the source paper relied on short sequences, VHP may be over-credited relative to how it would behave on longer time horizons.

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

**Notes / watch-outs:**
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

**Notes / watch-outs:**
- These are not reasons to drop the method outright; they are reasons to keep expectations realistic.
- In practice, they mostly argue for careful component checks, clear reporting, and not overclaiming exact reproduction.
