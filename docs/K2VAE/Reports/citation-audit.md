# Citation audit: Preliminaries and K²VAE chapters

Scope: `thesis.qmd` lines 63–448 (Chapter 2 Preliminaries, Chapter 3 K²VAE). Line numbers refer to the version as of 14 Oct 2026.
Nothing has been changed in the thesis or in `references.bib`.

Source PDFs and text extracts are in `Thesis/Sources/` (outside the repo, so they are never pushed).
**Page numbers are PDF page numbers of those files**, not journal page numbers.

**Status labels**

| Label | Meaning |
|---|---|
| ✅ OK | The source says this. The location is given. |
| ⚠️ PARTIAL | The source supports part of the sentence, or supports it with a caveat. |
| 🚩 FLAG | No source in the search chain backs it, or a source contradicts it. Needs a decision or a new source. |
| 🛠 OWN | Describes our implementation or our own reasoning. No literature citation is needed. The code location is given where useful. |

---

## 1. Headline flags (read these first)

1. **Markov / non-Markov argument (L75).** Nothing in the chain supports "real-world data is non-Markovian" or "Koopman lifting implicitly encodes historical dependencies". Brunton §5.2 (p. 58) only links Koopman to hidden variables through *time-delay coordinates*, which K²VAE does not use. The sentence is cited to Brunton, but Brunton does not back that part.
2. **"Linear techniques give more stable and accurate forecasts over longer horizons" (L81, L111).** Brunton only says linear representations *enable* prediction with standard linear methods. The long-horizon stability claim is K²VAE's claim about its own model, and Koopa (App. D.4) warns that Koopman operators with eigenvalues off the unit circle explode over long horizons.
3. **K_glo "initialised as an orthogonal matrix via SVD" (L105, L354).** L105 cites `[@k2vae2025]`, but the paper never mentions the initialisation. It is our code (`src/koopman.py:32-33`), so it should be marked as our choice and not cited to K²VAE.
4. **"The Koopman network bypasses the autoregressive feedback loop entirely" (L344, L356).** The K²VAE paper describes itself the other way: "K2VAE also works like an autoregressive dynamic system" (§3.1.1, p. 3) and "K2VAE also autoregressively models the time series in a linear dynamical system" (§5.1, p. 9). Also, "diffusion and flow models predict step t+1 then t+2" is not true of CSDI, which is non-autoregressive. K²VAE criticises diffusion and flow models for long *denoising* paths, not for time-step autoregression. "Errors compound exponentially" has no source.
5. **Forecast start state (L356).** The thesis says the forecast starts from the final context state z₀ = x_n*. K²VAE Eq. (11), p. 4, iterates from the *first* token: x̂ᴴ_i = 𝒦^(i+n−1) x₁*. This is an implementation difference. Do not cite K²VAE for it.
6. **Decoder description (L424).** The thesis says "the original theoretical framework" describes the decoder "simply as an inverse measurement function", and that the implementation needs more. But K²VAE §3.1.3, Eq. (24), p. 5, already specifies two MLPs, μ⁻¹ and σ⁻¹. As written, this misrepresents the paper.
7. **"Standard implementations apply patchification during data loading" (L336).** PatchTST, the main patching reference, does the opposite: "we normalize each x(i) before patching" (PatchTST §3.1, p. 5). This may be true of the official K²VAE/ProbTS code, but then say that rather than "standard implementations".
8. **"Joseph stabilised form" (L396) and "Cholesky decomposition" (L394, L420).** No source in the chain uses either name. K²VAE gives the equations (Eq. 29; Q = L_Q L_Qᵀ) without naming them. A Kalman-filter textbook is needed for "Joseph form" and a linear-algebra text for "Cholesky". Neither is in the chain. Also, L394 says Q and R are "built directly from a single learnable matrix at each time step", but they are global parameters, not per-step ones.
9. **AE latent space has "disjoint clusters / empty regions" (L205) and "KL keeps encodings overlapping" (L231).** Not in Hinton, Kingma or Doersch.
10. ~~**Positional encoding (L143).**~~ **Resolved 14 Oct:** L143 now describes sinusoidal vs. learned encodings without saying "typically", and L375 states that the Integrator uses no positional encoding and that the head recovers order. Original note: Vaswani says sinusoidal and learned encodings performed "nearly identically" (§3.5, p. 6), and PatchTST uses a learned one, so "typically fixed" overstates it. More important: **our Integrator has no positional encoding at all** (`src/integrator.py`), yet the text implies the encoder-only variant we use includes one. This is a content issue, not only a citation one.
11. **RevIN is named ("Kim et al.") but never cited and has no bib entry.** It is not in K²VAE's reference list. I found it through PatchTST and Koopa. **I could not open the paper PDF** because OpenReview blocks automated downloads. I verified the abstract and the equations against the authors' official code instead. Please download https://openreview.net/pdf?id=cGDAkQo1C0p into `Sources/` so I can check equation numbers and the intro claims.
12. **β-weighted KL (L443–446).** The natural source is Higgins et al. 2017 (β-VAE), which is in K²VAE's reference list. **I could not download it** (OpenReview again). Please fetch https://openreview.net/pdf?id=Sy2fzU9gl. K²VAE itself only says the objective is "weightsumed by L_ELBO and L_Rec" (§3.1.4, p. 5). It never weights the KL inside the ELBO.
13. **Do not copy K²VAE's Schmid (2010) citation for eDMD.** Schmid introduced DMD, not eDMD. eDMD is Williams et al. (2015), as cited in Brunton §5.1 and Koopa. Brunton §5.1 already covers it.

---

## 2. Sources used

| Key (proposed) | Source | How found | Status |
|---|---|---|---|
| `k2vae2025` | Wu et al. 2025, K²VAE (arXiv v3) | existing | ✔ read |
| `koopman2021modern` | Brunton et al. 2021, Modern Koopman Theory (arXiv) | existing | ✔ read |
| `vaswani2017attention` | Vaswani et al. 2017 | existing + K²VAE ref | ✔ read |
| `nie2023patchtst` | Nie et al. 2023, PatchTST | existing + K²VAE ref | ✔ read |
| `kalman1960new` | Kalman 1960 | existing | ✔ read |
| `kalmannet2021` | Revach et al. 2022, KalmanNet | existing | ✔ read |
| `hinton2006reducing` | Hinton & Salakhutdinov 2006 | existing | ✔ read |
| `kingma2014vae` | Kingma & Welling 2014 | existing + K²VAE ref | ✔ read |
| `doersch2016tutorial` | Doersch 2016 | existing | ✔ read |
| `jazwinski2007stochastic` | Jazwinski (book) | existing | ✗ not accessible. Only cited in the Lit Review, so out of scope. |
| **`welch1995`** *(new)* | Welch & Bishop, *An Introduction to the Kalman Filter*, UNC TR 95-041 | K²VAE ref | ✔ read |
| **`liu2023koopa`** *(new)* | Liu et al. 2023, Koopa (NeurIPS) | K²VAE ref | ✔ read. Already a baseline in Ch. 4, so it may already be planned for the bib. |
| **`cirstea2022triformer`** *(new, optional)* | Cirstea et al. 2022, Triformer | K²VAE ref | ✔ read |
| **`higgins2017betavae`** *(new)* | Higgins et al. 2017, β-VAE | K²VAE ref | ✗ download blocked. Needs a manual download. |
| `simon2001`, `koopman1931`, `schmid2010` | K²VAE refs | K²VAE ref | ✗ not obtained. Not needed: Welch and Brunton cover the same ground. |
| `lan2013linearization` | Lan & Mezić 2013 | K²VAE ref | ✔ obtained. Not needed: Brunton covers it. |
| **`kim2022revin`** *(new)* | Kim et al. 2022, RevIN (ICLR) | inside PatchTST (§3.1, p. 5) and Koopa (ref [16]) | ⚠️ paper blocked. Abstract and code verified from the official repo `ts-kim/RevIN`. |
| **`sohn2015cvae`** *(new)* | Sohn, Lee & Yan 2015, CVAE (NeurIPS) | inside Doersch (ref 7). Already verified in an earlier session. | ✔ read |
| **`ba2016layernorm`** *(new, optional)* | Ba, Kiros & Hinton 2016, Layer Normalization | inside Vaswani (ref [1]) | ✔ read |
| **`he2016resnet`** *(new, optional)* | He et al. 2016, ResNet | inside Vaswani (ref [11]) | ✔ read |

---

## 3. Preliminaries

### 3.1 Koopman Theory (L67–111)

| Line | Claim | Current cite | Proposed source → location | Status / notes |
|---|---|---|---|---|
| 69–73 | Nonlinear discrete dynamics x_{k+1} = f(x_k) | none | Brunton §1, Eq. (1.4), p. 4. K²VAE §2, p. 2 (same notation). | ✅ |
| 75 | Strictly Markovian assumption; real data non-Markovian; missing context shows up as noise; compounding error and drift | none (paragraph ends with Brunton) | — | 🚩 No source. See headline flag 1. |
| 75 | Koopman maps the state into a higher (infinite-dimensional) space where the evolution is linear | Brunton | Brunton abstract and §1, p. 2 ("infinite-dimensional, but linear, Koopman operator"). Fig. 5.2(b), p. 62 ("lifted to a higher dimension where … approximately linear"). | ✅ |
| 75 | "Expanding the dimensionality … implicitly encodes historical dependencies … bridging non-Markovian reality and Markovian linear algebra" | Brunton | Brunton §5.2, p. 58, only via time-delay coordinates | 🚩 Not what Brunton says for a lifted state without delays. |
| 75–79 | Operator acts on observables; ψ(x_{k+1}) = 𝒦 ψ(x_k) | Brunton | Brunton §1, Eq. (1.5), p. 4 ("Kg(x_k) := g(F(x_k)) = g(x_{k+1})"). §2.1, p. 10 ("advances measurement functions of the state"). K²VAE Eq. (1), p. 2. | ✅ |
| 81 | Linear evolution lets us use linear techniques | none | Brunton abstract, p. 1 ("enable the prediction, estimation, and control … with standard textbook methods developed for linear systems") | ✅ for this half |
| 81 | "… more stable and accurate forecasts over longer horizons" | none | K²VAE abstract (claim about the whole model) | 🚩 See headline flag 2. |
| 83 | True operator is infinite-dimensional, so a finite approximation is needed | Brunton | Brunton §2.3.1, p. 18 (finite-dimensional matrix representation on an invariant subspace) | ✅ |
| 83 | Hand-picking observables is hard | Brunton | Brunton §5 intro, p. 55 ("Finding, approximating, and representing these observables … is still a central challenge"). Koopa §3.2, p. 3 ("eDMD … proposed to avoid handcrafting measurement functions"). | ✅ |
| 83 | Learn ψ and 𝒦 jointly with a neural network | Brunton | Brunton §5.4, pp. 61–62 and Fig. 5.2 (encoder φ, matrix K, linearity loss ‖φ(x_{k+1}) − Kφ(x_k)‖) | ✅ |
| 83–87 | Apply ψ to the patches to get X^{P*} | none | K²VAE §3.1.2, Eq. (5), p. 4 | ✅ Missing cite. |
| 89–97 | eDMD with past and future (shifted) matrices | Brunton | Brunton §5.1, Eq. (5.2a), p. 56. K²VAE Eqs. (6–7), p. 4. Koopa Eq. (10), p. 6 (the same X_back/X_fore construction, "one-step operator approximation"). | ✅ Koopa is the closest match to our notation. |
| 99–103 | 𝒦_loc = X_fore X_back† via the Moore–Penrose pseudoinverse, equivalent to least squares | none | Brunton §3.1, Eq. (3.4), p. 22 (argmin of the Frobenius norm, "† denotes the pseudo-inverse"). Brunton Eq. (5.3), p. 56 (eDMD version). K²VAE Eq. (8), p. 4. | ✅ Missing cite. |
| 105 | Relying only on 𝒦_loc causes numerical instability or wrong convergence | K²VAE (end of paragraph) | K²VAE §3.1.2, p. 4 ("may cause numerical instability or guide the model to converge in a wrong direction"). §4.3.1, p. 8. | ✅ |
| 105 | 𝒦_glo learnable and shared; captures global dynamics | K²VAE | K²VAE §3.1.2, p. 4 ("capture the global-shared dynamics, we introduce a learnable part") | ✅ |
| 105 | 𝒦_glo initialised orthogonal via SVD | K²VAE | — (`src/koopman.py:32-33`) | 🚩 / 🛠 Not in the paper. See headline flag 3. |
| 107–109 | 𝒦 = 𝒦_loc + 𝒦_glo | K²VAE | K²VAE §3.1.2, p. 4 | ✅ |
| 111 | 𝒦 forecasts "without the compounding error that arises from nonlinear dynamics" | none | — | 🚩 No source. See headline flag 2. |
| 111 | Residual between predicted and actual states leaves a bias, so the Integrator and KalmanNet are added | none | K²VAE §1, p. 2 and §3.1.2, p. 4 ("biased linear system") | ✅ Missing cite. |

### 3.2 Transformer Encoder (L113–143)

| Line | Claim | Current cite | Proposed source → location | Status / notes |
|---|---|---|---|---|
| 115 | Transformers have become widely used in NLP | Vaswani | PatchTST §1, p. 1 ("great success on … natural language processing", citing the Kalyan 2021 survey) | ⚠️ Vaswani introduced it for machine translation (abstract, p. 1). It cannot show later wide use. Keep Vaswani for the architecture and add PatchTST, or rephrase. |
| 115 | Applied to time-series forecasting | PatchTST | PatchTST abstract and §1, p. 1 | ✅ |
| 115 | Self-attention weighs the importance of different parts of the sequence | none | Vaswani §2, p. 2 ("an attention mechanism relating different positions of a single sequence"). §3.2, p. 3. | ✅ Missing cite. |
| 115 | "Particularly useful for time-series data …" | none | PatchTST §1, p. 1 ("attention … can automatically learn the connections between elements in a sequence, thus becomes ideal for sequential modeling") | ⚠️ Supports "sequential modelling". It does not specifically mention "complex and nonlinear" relationships. |
| 117–120 | Q, K, V from learned linear projections | Vaswani | Vaswani §3.2.2, p. 4 | ✅ Vaswani projects per head. The single-matrix form here is a fair simplification. |
| 122 | Relates tokens regardless of their position in the sequence | none | Vaswani §1, p. 2 ("modeling of dependencies without regard to their distance") | ✅ Missing cite. |
| 124–125 | Scaled dot-product attention equation | none | Vaswani §3.2.1, Eq. (1), p. 4 | ✅ Missing cite. |
| 127–131 | Multi-head attention and W^O | Vaswani | Vaswani §3.2.2, p. 5 | ✅ |
| 133–139 | Position-wise FFN with ReLU | Vaswani | Vaswani §3.3, Eq. (2), p. 5 | ✅ |
| 141 | Residual connections and layer norm wrap each sub-layer | none | Vaswani §3.1, p. 3 ("LayerNorm(x + Sublayer(x))") | ✅ Missing cite. |
| 141 | …"which help stabilise training and improve convergence" | none | He et al. 2016 abstract, p. 1 (residual nets "are easier to optimize"). Ba et al. 2016 abstract, p. 1 (layer norm "can substantially reduce the training time", "stabilizing the hidden state dynamics in recurrent networks"). | ⚠️ Vaswani does not make this claim. He and Ba support it in general terms but not for transformers specifically. |
| 143 | Attention has no notion of order, so position must be injected | Vaswani | Vaswani §3.5, p. 6 ("contains no recurrence and no convolution … we must inject some information about the … position") | ✅ |
| 143 | Original transformer uses fixed sinusoidal encoding; learned performs almost identically | Vaswani | Vaswani §3.5, p. 6, and Table 3 row (E), p. 9 | ✅ Text revised 14 Oct. |
| 143 | Encoder-only, bidirectional (every position attends to all) | none | Vaswani §3.2.3, p. 5 ("Each position in the encoder can attend to all positions in the previous layer") | ✅ Missing cite. |
| 143 | K²VAE uses a transformer encoder (the Integrator) on the nonlinear residual | K²VAE | K²VAE §3.1.2, Eqs. (12–13), p. 4 ("Integrator based on an Encoder-Only Vanilla Transformer") | ✅ |

### 3.3 Kalman Filter (L145–193)

Welch & Bishop (in K²VAE's reference list) matches this section almost equation for equation. Kalman (1960) supports the general idea, but its model is x(t+1) = Φx(t) + u(t), y(t) = Mx(t) (Eqs. 16–17, p. 9). There is no control input and no separate observation noise, and its "u(t)" is noise, not control. So Kalman 1960 should not be the citation for the specific equations.

| Line | Claim | Current cite | Proposed source → location | Status / notes |
|---|---|---|---|---|
| 147 | Recursive algorithm that estimates state from noisy observations; assumes a linear state-space model | Kalman 1960 | Kalman 1960 abstract, p. 1, and Eqs. (16–17, 21), p. 9. Welch abstract, p. 1 ("an efficient computational (recursive) means to estimate the state of a process"). | ✅ Add Welch. |
| 147 | "Alternates between a process model and an observation model" | Kalman 1960 | Welch §1, p. 4 (time update and measurement update) | ⚠️ Better supported by Welch. |
| 149–154 | Process model x_k = Ax_{k−1} + Bu_k + w_k, w ~ 𝒩(0,Q), with the meaning of A, B, u | none | Welch §1, Eqs. (1.1) and (1.3), p. 2. K²VAE Eq. (14), p. 4. | ✅ Welch indexes u_{k−1}. The thesis follows K²VAE's u_k. Both are fine. |
| 156–161 | Observation model o_k = Hx_k + v_k, v ~ 𝒩(0,R) | none | Welch Eqs. (1.2) and (1.4), p. 2. K²VAE Eq. (16), p. 4. | ✅ |
| 163–175 | Predict step (state and covariance) | none | Welch Table 1-1, Eqs. (1.9–1.10), p. 5. K²VAE Eqs. (17–18), p. 5. | ✅ |
| 177–180 | Kalman gain | none | Welch Table 1-2, Eq. (1.11), p. 5. K²VAE Eq. (19), p. 5. | ✅ |
| 182–189 | State and covariance update | none | Welch Eqs. (1.12–1.13), p. 5. K²VAE Eqs. (20–21), p. 5. | ✅ |
| 191 | o_k − Hx̂_k is the innovation or residual | none | Welch §1, Eq. (1.7), p. 3 ("called the measurement innovation, or the residual") | ✅ |
| 191 | K → 1 trusts the observation; K → 0 trusts the prediction | none | Welch §1, p. 3 ("as R approaches zero … K = H⁻¹"; "as P⁻ approaches zero … K = 0") | ✅ The scalar case with H = 1 gives exactly K → 1. |
| 193 | EKF and UKF are nonlinear extensions | KalmanNet | KalmanNet §I, p. 1 | ✅ |
| 193 | KalmanNet uses an RNN to learn the Kalman gain | KalmanNet | KalmanNet abstract, p. 1, and §I, p. 2 ("replace it with a compact RNN") | ✅ |
| 193 | K²VAE handles nonlinearity via Koopman, then filters in the latent space | K²VAE | K²VAE §1, p. 2, and §3.1.2, p. 4 | ✅ |
| 193 | K²VAE's "KalmanNet" learns A, B, H, Q, R rather than the gain | K²VAE | K²VAE §3.1.2, p. 4 ("In the KalmanNet, all the matrices are learnable") | ✅ |

### 3.4 Variational Autoencoders (L195–249)

| Line | Claim | Current cite | Proposed source → location | Status / notes |
|---|---|---|---|---|
| 199–201 | AE reconstructs its input; encoder narrows to a code, decoder reconstructs | Hinton | Hinton abstract, p. 2 ("small central layer to reconstruct high-dimensional input vectors"). Fig. 1, p. 3 (2000 → 1000 → 500 → 30 encoder, mirrored decoder). | ✅ |
| 205 | AEs are trained to minimise reconstruction error | none | Hinton, p. 3 ("trained together by minimizing the discrepancy between the original data and its reconstruction") | ✅ Missing cite. |
| 205 | Latent space has disjoint clusters and empty regions, cannot be sampled, decoder only trained on encoded points | none | — | 🚩 Not in Hinton, Kingma or Doersch. See headline flag 9. |
| 207–211 | VAE encoder outputs μ(x), σ(x); diagonal Gaussian approximate posterior | Kingma | Kingma §3, Eq. (9), p. 5 ("mean and s.d. of the approximate posterior … are outputs of the encoding MLP"). App. C.2, p. 11. | ✅ |
| 213 | True posterior is intractable | Kingma | Kingma §2.1, p. 2 ("the true posterior density p(z\|x) … is intractable") | ✅ |
| 217 | log P(x) requires integrating over z, so it is intractable | Kingma | Kingma §2.1, p. 2 ("the integral of the marginal likelihood … is intractable") | ✅ |
| 217–221 | ELBO; minimise its negative = reconstruction + KL | Kingma | Kingma §2.2, Eq. (3), p. 3. §2.3, p. 4 ("expected negative reconstruction error"). | ✅ |
| 220 | Prior 𝒩(0, I) | Kingma | Kingma §3, p. 5 ("centered isotropic multivariate Gaussian p(z) = 𝒩(z; 0, I)") | ✅ |
| 223 | Gaussian decoder with fixed variance gives NLL ∝ squared Euclidean distance | Doersch | Doersch §2, p. 7 ("Since P(X\|z) is an isotropic Gaussian, the negative log probability of X is proportional squared Euclidean distance") | ✅ |
| 223 | KL acts as a regulariser pulling the posterior toward the prior | Kingma | Kingma §2.3, p. 4 ("interpreted as regularizing φ, encouraging the approximate posterior to be close to the prior") | ✅ |
| 223–227 | Closed-form Gaussian KL | Kingma | Kingma §3, Eq. (10), p. 5, and App. B | ✅ |
| 229 | KL = 0 only at μ = 0, σ = 1 | none | Follows from Eq. (10) | 🛠 Derivation. No cite needed. |
| 231 | KL makes encodings overlap; points in between decode to plausible outputs | none | — | 🚩 No source. See headline flag 9. |
| 233–237 | Sampling is not differentiable; reparameterisation z = μ + σ⊙ε | Kingma | Kingma §2.4, p. 4. The z = μ + σ⊙ε form is in §3, Eq. (10), p. 5. | ✅ |
| 239 | PTSF: model the future Y given context X | none | K²VAE §2 ("VAE for PTSF"), p. 3 | ✅ Missing cite. |
| 239 | A regressor predicts something in between plausible futures | Doersch | Doersch §3, p. 15 ("the best solution the regressor can produce is something which is in between the possibilities") | ✅ |
| 239 | CVAE conditions the generative process on the input and learns P(Y\|X) | Doersch | Doersch §3, Eq. (12), p. 16. **Sohn 2015** abstract, p. 1, and §4, p. 3 (the primary CVAE source; models "one-to-many mapping"). | ✅ Add Sohn (open item from an earlier session). |
| 239–243 | K²VAE is trained with the conditional ELBO | K²VAE | K²VAE §2, Eq. (2), p. 3. §3.1.4, Eq. (26), p. 5. | ✅ |
| 245 | Prior written as ℙ(Z\|X) = 𝒩(0, I) | K²VAE | K²VAE §3.1.4, p. 5 | ✅ |
| 247 | Doersch's encoder sees both context and target: Q(z\|Y, X) | Doersch | Doersch §3, Eqs. (13–15), p. 16. Sohn Eq. (4), p. 3. | ✅ |
| 247 | K²VAE's encoder sees only X | none | K²VAE Eq. (2), p. 3 (Q(Z\|X)). Sohn §4.2, Eq. (8), p. 4 (GSNN: q(z\|x,y) = p(z\|x), the closest published analogue). | ✅ Sohn is optional. |
| 249 | KoopmanNet, Integrator and KalmanNet form the encoder; the decoder is an inverse measurement function | K²VAE | K²VAE §3.1, p. 3 ("The KoopmanNet and KalmanNet consitute the Encoder"; "Decoder works as the inverse measurement function"). The Integrator sits inside KalmanNet in Fig. 3, p. 4. | ✅ |

---

## 4. K²VAE chapter

### 4.1 Model pipeline (L255–263)

| Line | Claim | Proposed source → location | Status / notes |
|---|---|---|---|
| 257–261 | Overall data flow: patch → Koopman → residual → Integrator → Kalman → sample → decode | K²VAE §3.1, p. 3, and Figs. 2–3, pp. 3–4 | ✅ One cite at the end of L261 would cover the paragraph. The RevIN steps in it are ours. |
| 259 | Overview figure | — | 🛠 Our figure. |

### 4.2 Pre-processing (L265–310)

| Line | Claim | Current cite | Proposed source → location | Status / notes |
|---|---|---|---|---|
| 267–279 | PTSF as a conditional generative task; X ∈ ℝ^{N×T}, Y ∈ ℝ^{N×L}, model P(Y\|X) | none | K²VAE §2 ("VAE for PTSF"), p. 3 | ✅ Missing cite. The paper writes the horizon as ending at x̂_L, which is a typo. The thesis's x_{T+L} is correct. |
| 281 | Chronological split; standardise using train statistics only | none | — | 🛠 Our protocol. It differs from ProbTS (see benchmark-comparability notes), so do not cite ProbTS for it. |
| 283–290 | Sliding windows and window count | none | — | 🛠 |
| 292–296 | Non-overlapping patches, s = T/n | none | K²VAE §3.1.1, Eq. (3), p. 3 | ✅ Missing cite. Optional for the patching idea itself: Triformer (credited by K²VAE as the first to patch, §3.1.1, p. 3) and PatchTST §1, p. 1. |
| 298 | Divisibility checks; m = L/s | none | K²VAE §3.1.2, p. 4 ("m = L/s"). Koopa Eq. (8), p. 6, assumes divisibility and pads otherwise. | ⚠️ m = L/s is from the paper. The loader checks are 🛠. |
| 300–304 | Flatten, then one linear projection to d | none | K²VAE §3.1.1, Eq. (4), p. 3 | ✅ Missing cite. |
| 306 | Channel-independent models vs. multivariate tokens fusing variables | K²VAE | K²VAE §3.1.1, p. 3. PatchTST §1, p. 1 defines channel independence. | ✅ Could add PatchTST for "channel-independent models". |
| 306–308 | Projection trained jointly; patching done inside the model | none | — | 🛠 |
| 310 | Batch size 32 "following the original paper" | none | K²VAE App. C.4, p. 18 ("batch size is set to 32, with the option to reduce it by half … in case of OOM") | ✅ Missing cite. |

### 4.3 RevIN (L312–340)

| Line | Claim | Proposed source → location | Status / notes |
|---|---|---|---|
| 314 | Non-stationarity: local mean and variance shift over time | RevIN abstract (verified via the official README). Koopa abstract, p. 1. PatchTST §3.1, p. 5. | ✅ Needs the `kim2022revin` bib entry. |
| 314 | Global standardisation fails to fix localised shift across windows; this causes prediction drift | RevIN intro (unverified) | 🚩 Cannot verify until I can read the RevIN PDF. |
| 314 | Scale entanglement; a single variance parameter compromises across variables | — | 🛠 / 🚩 Our reasoning. No source found. Fine as our argument, but it should not read as established fact. |
| 314–316 | "Originally proposed by Kim et al." | RevIN | ⚠️ Name it with `[@kim2022revin]`. |
| 316–326 | Per-variable instance mean and std with ε; affine γ, β | RevIN official code `RevIN.py` (`_get_statistics`, `_normalize`) | ⚠️ Matches exactly, including ε inside the square root. Paper equation numbers are unverified. |
| 328 | γ and β initialised to 1 and 0 | RevIN code `_init_params` | ⚠️ Code only. Check against the paper. |
| 328 | Affine parameters let the model partly undo the normalisation when magnitude is informative | — | 🚩 Interpretation. Not verified in RevIN. |
| 330–334 | Inverse transform with the ε² term | RevIN code `_denormalize` (`x / (affine_weight + eps*eps)`) | ⚠️ Matches exactly. The paper is unverified. |
| 336 | "Standard implementations apply patchification during data loading" | Contradicted by PatchTST §3.1, p. 5 | 🚩 See headline flag 7. |
| 336 | Statistics from context only; horizon denormalised with context statistics | RevIN README ("remove and restore the statistical information of a time-series instance"). Code: denorm reuses the stored statistics. | ✅ / 🛠 The design follows RevIN. The leakage argument is ours. |
| 338–340 | Instance-rescaled variance decoding; σ-scaled reconstruction loss | — | 🛠 Our adaptation. |

### 4.4 The Koopman Network (L342–363)

| Line | Claim | Proposed source → location | Status / notes |
|---|---|---|---|
| 344 | RNN, diffusion and flow models predict iteratively; errors compound exponentially | K²VAE §1, p. 2 ("remarkable error accumulation") | 🚩 See headline flag 4. |
| 344 | Koopman maps to a higher-dimensional latent space where dynamics are approximately linear; stepping forward is a matrix multiply | Brunton Fig. 5.2(b), p. 62. K²VAE §3.1.2, p. 4. | ✅ |
| 344, 356 | "Bypasses this feedback loop entirely" / "breaks the autoregressive error compounding loop" | Contradicted by K²VAE §3.1.1, p. 3, and §5.1, p. 9 | 🚩 See headline flag 4. |
| 346 | Measurement function is an MLP | K²VAE §3.1.2, p. 4 ("learnable MLP-based network") | ✅ Dropout is 🛠 (`src/koopman.py:25`). |
| 346 | Find 𝒦 with x*_{t+1} ≈ 𝒦x*_t | K²VAE §3.1.2. Brunton §5.4, p. 62. | ✅ |
| 348 | 𝒦_loc computed per window by one-step eDMD | K²VAE Eqs. (6–8), p. 4. Koopa Eq. (10), p. 6 ("varies with windows"). | ✅ |
| 348–352 | Underdetermined system; ridge-regularised least squares instead of the pseudoinverse | — (`src/koopman.py:79-100`) | 🛠 Our change. No ridge-DMD source found in the chain. Acceptable uncited as our choice. |
| 354 | 𝒦_glo learnable and shared; addresses instability | K²VAE §3.1.2, p. 4, and §4.3.1, p. 8 | ✅ |
| 354 | Orthogonal SVD initialisation | — (`src/koopman.py:32-33`) | 🛠 See headline flag 3. |
| 356 | Spectral norm clamped to ≤ 1 | — (`src/koopman.py:114`) | 🛠 Optional motivation: Koopa "Learning stable operators" analysis, p. 9, and App. D.4, p. 19 (eigenvalue modulus far from 1 leads to "explosive" long-term evolution). |
| 356 | Identity fallback on NaN | — (`src/koopman.py:117-120`) | 🛠 |
| 356 | Forecast starts from the last context state z₀ = x_n* | Differs from K²VAE Eq. (11), p. 4 | 🚩 / 🛠 See headline flag 5. |
| 356 | "In theory … matrix powers 𝒦^t" | K²VAE Eq. (11), p. 4 | ✅ |
| 358–363 | X^Res = X^{P*} − X̂_C | K²VAE §3.1.2, Eq. (12), p. 4 | ✅ Missing cite. |

### 4.5 The Integrator (L365–375)

| Line | Claim | Proposed source → location | Status / notes |
|---|---|---|---|
| 367 | Linear 𝒦 misses nonlinear behaviour; the residual isolates it | K²VAE §3.1.2, p. 4 ("fully reuse the nonlinear residual"). §1, p. 2 ("integrating the residual nonlinear information as control inputs"). | ✅ |
| 367 | "Residuals are not random noise; they contain structural, sequential patterns" | — | ⚠️ K²VAE calls the residual "nonlinear information" but does not claim sequential structure. Soften or mark as our motivation. |
| 369 | Integrator is an encoder-only transformer | K²VAE §3.1.2, p. 4 | ✅ |
| 369 | "A standard neural network processes inputs independently and struggles to map long-range connections" | Vaswani §4 and Table 1, p. 6 (path length vs. recurrent and convolutional layers) | ⚠️ Vaswani compares against RNNs and CNNs, not plain feedforward networks. Reword to match, or drop. |
| 369–373 | U = Integrator(X^Res) ∈ ℝ^{d×m} | K²VAE Eq. (13), p. 4 | ✅ Missing cite. |
| 375 | Three-stage implementation (adapt, encode, flatten-project) | — (`src/integrator.py`) | 🛠 |

### 4.6 The Kalman Network (L377–408)

| Line | Claim | Current cite | Proposed source → location | Status / notes |
|---|---|---|---|---|
| 379 | Two information sources fused by relative certainty | none | K²VAE §1, p. 2 ("fuses observations from multiple sensors"). Welch §1, p. 3 (gain limits). | ✅ |
| 381 | Matrices learnable and trained by backprop | K²VAE | K²VAE §3.1.2, p. 4 | ✅ |
| 381 | Koopman forecast X̂_H is the measurement; U is the control input | none | K²VAE §3.1.2, p. 4 ("we treat the prediction X̂_H as the prior observation in Update Step (20)"). §1, p. 2 ("integrating the residual … as control inputs"). | ✅ Missing cite. |
| 381 | z₀ = embedding of the last context patch | none | K²VAE Eq. (15), p. 4 (z₀ = x_n*) | ✅ Missing cite. |
| 381 | P and all other matrices initialised as identity | none | K²VAE, p. 5: Q and R only ("initialize the covariance matrices Q and R as identity matrices") | ⚠️ A, B, H and P₀ as identity is 🛠 (`src/kalman.py:16-18, 123`). |
| 383 | Predict, gain and update steps | none | K²VAE Eqs. (17–21), p. 5. Welch Tables 1-1/1-2, p. 5. | ✅ |
| 385 | Repeated over m horizon steps | none | K²VAE, p. 5 ("conduct the Prediction Step and Update Step iteratively") | ✅ |
| 385 | Z' = Z + U skip connection | none | K²VAE Eq. (22), p. 5 | ✅ Missing cite. |
| 385 | Reason: the Kalman gain can dampen U | none | K²VAE §4.3.2, p. 8 gives a different rationale ("constraints Integrator predicting residuals from residuals"; without it the model "completely depends on the linear fitting ability of the KalmanNet") | ⚠️ Our rationale differs from the paper's. Either cite the paper's reason or mark ours as our interpretation. |
| 385 | As 𝒦 improves, U → 0 and Z' → Z | none | K²VAE, p. 5 ("causing U → 0"). Theorem 3.2, p. 5, and App. A.2, p. 15. | ✅ Missing cite. |
| 387 | Loss of PSD would cause a runtime error | none | — | 🛠 |
| 389–392 | Q = L_Q L_Qᵀ, R = L_R L_Rᵀ | K²VAE | K²VAE, p. 5 | ✅ |
| 394 | "This is known as a Cholesky decomposition" | none | — | 🚩 Name not in any chain source. See headline flag 8. |
| 396 | Floating-point error loses PD, most often in the update step | K²VAE | K²VAE §3.2.1, p. 5 ("which often occurs in the step (21)") | ✅ |
| 396–399 | Joseph form; mathematically identical to Eq. (21) | none | K²VAE Theorem 3.1, Eq. (29), p. 5. Equivalence proof in App. A.1, p. 15. | ⚠️ The equations are covered. The name "Joseph" is 🚩. The equivalence holds for the optimal gain, which is the case here. |
| 401 | Sum of two PSD terms preserves PD better | K²VAE | K²VAE §3.2.1, p. 5 | ✅ |
| 403–406 | Symmetrise with 0.5(P + Pᵀ) | none | K²VAE Eq. (28), p. 5 | ✅ Missing cite. The paper presents this as part of its stable form, not as an extra fix. |

### 4.7 How the model acts as a VAE (L410–436)

| Line | Claim | Current cite | Proposed source → location | Status / notes |
|---|---|---|---|---|
| 412 | Standard VAE recap | none | Kingma §2–3 | ✅ Already covered in Ch. 2. |
| 414 | Architecture figure | K²VAE | K²VAE Fig. 3, p. 4 | ✅ |
| 416–418 | Walk-through of the figure | none | K²VAE §3.1, pp. 3–5 | ✅ One cite covers it. |
| 418–420 | Q(Z\|X) = 𝒩(Z', P); reparameterised sample | none | K²VAE §3.1.3, Eq. (23), p. 5. Kingma §2.4. | ✅ |
| 420 | Sample through the Cholesky factor of P, plus jitter | none | — | 🛠 Implementation. "Cholesky" naming 🚩 as above. Kingma covers only the diagonal case. |
| 420 | Mean Z' decoded at evaluation; samples used for CRPS | none | K²VAE App. C.3, p. 18 (100 samples for the empirical CDF) | ⚠️ The sample count is from the paper. Decoding the mean is 🛠. |
| 422–432 | Decoder has two heads for μ and σ | none | K²VAE §3.1.3, Eq. (24), p. 5 ("two same MLP structures") | ✅ |
| 424 | "The original framework describes the decoder simply as an inverse measurement function" | — | Contradicted by K²VAE Eq. (24) | 🚩 See headline flag 6. |
| 434 | Softplus, RevIN rescale, σ floor; σ → 0 makes the Gaussian NLL blow up | none | — | 🛠 The NLL blow-up is basic algebra. No cite needed. |

### 4.8 The loss function (L438–448)

| Line | Claim | Proposed source → location | Status / notes |
|---|---|---|---|
| 440–444 | Loss = NLL + KL + reconstruction | K²VAE §3.1.4, Eqs. (26–27), p. 5 | ✅ |
| 446 | β and λ weights | K²VAE, p. 5 ("weightsumed by L_ELBO and L_Rec"). Higgins 2017 for the β-weighted KL. | ⚠️ K²VAE weights ELBO vs. reconstruction. It does not put β on the KL. Higgins is still to be verified (headline flag 12). |
| 446 | KL between 𝒩(Z', P) and the standard normal | K²VAE §3.1.3–3.1.4, p. 5 | ✅ |
| 446 | Reconstruction = MSE between the Koopman-reconstructed context and the true context | K²VAE Eqs. (25, 27), p. 5 | ✅ The paper decodes X̂_C through μ⁻¹ first (Eq. 25). |
| 446 | Reconstruction keeps information about the system from being lost | K²VAE, p. 5 ("L_Rec facilitates the linearization of the measurement space") | ⚠️ The paper's stated purpose is linearisation, not information retention. |
| 448 | Early stopping on validation loss; keep the best epoch | — | 🛠 |

---

## 5. Proposed new bib entries (not added yet)

- `welch1995` — Welch & Bishop, *An Introduction to the Kalman Filter*, UNC TR 95-041 (updated 2004).
- `kim2022revin` — Kim et al., *Reversible Instance Normalization …*, ICLR 2022. **The PDF must be read before use.**
- `sohn2015cvae` — Sohn, Lee & Yan, NeurIPS 2015.
- `liu2023koopa` — Liu et al., *Koopa*, NeurIPS 2023 (may already be planned for Ch. 4).
- `higgins2017betavae` — Higgins et al., ICLR 2017. **The PDF must be read before use.**
- Optional: `cirstea2022triformer`, `ba2016layernorm`, `he2016resnet`.

## 6. Still needing a source outside the current chain

- "Joseph form" naming (Kalman-filter textbook, e.g. Simon's *Optimal State Estimation* or Grewal & Andrews).
- "Cholesky" naming (a linear-algebra text such as Golub & Van Loan).
- The AE latent-space structure argument (L205, L231).
- The Markov / non-Markov argument (L75), unless it is reframed or cut.
- If kept: "errors compound exponentially" for autoregressive models (L344).
