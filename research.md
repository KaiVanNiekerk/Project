# Research Notes: Reduced Scope for Supervisor Discussion

## What the Reviews Actually Tell Us

- The strongest part of the paper is the empirical result on dynamics and system identification.
- Reviewers were not fully convinced about attribution, because several ideas are combined (CO, EKVAE, VHP).
- Reproducibility is a real concern in our case, especially without an official repository.

Given that, the key question for this project should stay narrow:

- Can we show, in a controlled way, that CO and latent-structure choices improve dynamics learning over standard ELBO training?

## Recommended Reduced Scope

### Keep in Scope

1. Use only the paper datasets for the main study.
   Why: this keeps the comparison fair and avoids introducing new data-related uncertainty.
   Datasets: pendulum, reacher-angle, reacher-RGB.

2. Run staged attribution experiments.
   Why: this is the most direct response to the attribution criticism.
   Order: ELBO baseline, then +CO, then +EKVAE, then +VHP ablation.

3. Limit the baseline set to a representative minimum.
   Why: we still get meaningful comparison without spending most of the project on rebuilding many models.
   Suggested minimum: one standard DSSM baseline, one KVAE-family baseline, and EKVAE.

4. Set a realistic replication target from the start.
   Why: exact number matching is risky without official code and hidden implementation details.
   Target: trend-level replication and component-wise direction; metric-range closeness where possible.

### Defer Until Core Results Are Stable

1. New transfer datasets (finance/health beyond the paper setup).
   Why: useful extension, but not needed to answer the core replication question.

2. Full baseline-family reproduction.
   Why: high effort for limited immediate evidence.

3. Large sensitivity sweeps (for example full $D_0$ grids).
   Why: important later, but not first-pass critical.

### Remove from Immediate Scope

1. RL/disentanglement extensions and broader side narratives.
   Why: outside the core supervisor-critical objective.

2. Strong Jacobian/linearization correctness claims without dedicated diagnostics.
   Why: difficult to defend properly unless we run focused verification experiments.

3. Exact numeric replication as a hard milestone.
   Why: too brittle under independent reimplementation conditions.

## Why This Scope Cut Is Reasonable

- It addresses the two biggest risks raised by reviews: attribution and reproducibility.
- It lowers delivery risk in a no-repo setting.
- It keeps the scientific core intact instead of spreading effort too thin.
- It gives a clean workflow: validate the core claim first, then broaden if time allows.

## Minimum Deliverable for This Reduced Scope

1. A complete experiment matrix on paper datasets with staged components (ELBO, +CO, +EKVAE, +VHP).
2. Quantitative metrics: MSE and a latent-state quality metric (for example $R^2$, where available).
3. At least one qualitative trajectory plot per dataset family showing success/failure behavior.
4. A reproducibility note stating what matched, what did not, and likely reasons for differences.

## Decisions to Confirm with Supervisor

1. Is trend-level replication acceptable as the primary endpoint?
2. Is the reduced baseline set acceptable for this stage?
3. Are extra datasets explicitly deferred until core validation is complete?
4. Are RL/disentanglement and strong Jacobian claims out of immediate scope?
5. Should we include one small $D_0$ sensitivity check now, or defer it?

## Risk Controls During Execution

1. Too many moving parts: only add one component at a time.
2. Attribution confusion: keep one-change-at-a-time experiment design.
3. No source code: strict config tracking, fixed seeds, and run logs.
4. Evaluation drift: define conditioning/sampling/reporting protocol before full runs.

## Meeting Notes

- Date:
- Feedback:
- Decisions:
- Action items:

