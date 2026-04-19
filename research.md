# EKVAE Research Analysis

## What We Learned from Reviews

From the reviews and rebuttal, the main points are:

1. The strongest support is for empirical dynamics performance (prediction and system identification).
2. Attribution is a known weakness because CO, EKVAE, and VHP are combined.
3. Reproducibility risk is higher for us because there is no official repository to follow.

So in practice:

- Prioritize controlled, component-by-component experiments over broad extension work.

## Scope Reduction Analysis

Based on the review feedback and no-code constraints, here's the analysis of what should stay, what should be deferred, and what should be removed.

### Keep in Immediate Scope

1. Keep all three paper datasets for the core study.
   Why: this stays faithful to the benchmark setup while avoiding new dataset confounders.
   Included: pendulum, reacher-angle, reacher-RGB.

2. Keep staged attribution experiments.
   Why: directly addresses the review criticism on unclear contribution attribution.
   Order: ELBO baseline -> +CO -> +EKVAE -> +VHP ablation.

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
