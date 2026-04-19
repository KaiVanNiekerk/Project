# Supervisor Meeting Notes (Essential)

## Context (from OpenReview and paper discussion)

- The paper was accepted, but reviewers repeatedly noted that the contribution is broad (CO + EKVAE + VHP), making attribution difficult.
- The strongest accepted claim is empirical: better system identification and prediction when these components are combined.
- Two recurring concerns were reproducibility (no official code) and clarity of what each component contributes.

## Questions to Ask

1. Which model comparisons are mandatory for our scope (minimum baseline set)?
2. Which paper sections are optional and can be excluded if time is limited (for example RL/disentanglement)?
3. What reproduction standard should we target given no official source code: trend match, approximate numbers, or full table replication?
4. Should $D_0$ sensitivity testing be required in our first full evaluation?
5. Should we avoid strong Jacobian-style claims unless we add explicit verification experiments?
6. Is it acceptable to prioritize a staged reproduction (CO first, then EKVAE, then VHP) rather than reproducing everything at once?
7. Which additional dataset family should we prioritize after paper datasets: finance-style, health/wearables, or another domain?

## What to Evaluate First

1. ELBO vs actual predictive quality (do high ELBO models fail on dynamics?).
2. CO vs annealing on the same model backbone (same data, same seed policy).
3. EKVAE vs selected baselines on paper datasets (pendulum, reacher-angle, reacher-RGB).
4. With/without VHP prior effect on prediction quality and generative stability.

Minimum evidence target:

- Quantitative: MSE and latent-state quality metric (for example $R^2$ where available).
- Qualitative: at least one failure/success comparison plot.
- Reporting: explicit note on what was matched versus not matched from the paper.

## Main Risks and How We Handle Them

1. Too many moving parts.
   Mitigation: stage as CO first, then EKVAE, then VHP ablations.
2. Attribution unclear.
   Mitigation: one-change-at-a-time experiments.
3. Missing source code.
   Mitigation: strict config tracking, fixed seeds, and run logs.
4. Evaluation ambiguity.
   Mitigation: write explicit conditioning/sampling protocol before running full experiments.

5. Scope drift due to missing code.
   Mitigation: define a fixed "minimum reproducibility" endpoint before adding extra models/datasets.

## No Official Source Code: Practical Implications

- Expect longer debugging cycles and possible mismatch with undocumented implementation details.
- Treat this as an independent reimplementation rather than exact code replication.
- Success should be judged on methodological faithfulness and trend agreement, unless supervisor requires exact numeric reproduction.

## Meeting Notes

- Date:
- Feedback:
- Decisions:
- Action items:

