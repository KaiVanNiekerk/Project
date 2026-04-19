# EKVAE Research Notes + Query List

## 1. What This Doc Is For

This is a working notes doc for supervisor discussions. It combines:

- what we learned from the paper and OpenReview discussion,
- the original scope we started with,
- a proposed reduced scope,
- and the key questions we need answered before implementation starts.

## 2. What We Learned from Reviews

From the reviews and rebuttal, the main points are:

1. The strongest support is for empirical dynamics performance (prediction and system identification).
2. Attribution is a known weakness because CO, EKVAE, and VHP are combined.
3. Reproducibility risk is higher for us because there is no official repository to follow.

So in practice:

- Prioritize controlled, component-by-component experiments over broad extension work.

## 3. Initial Scope (Original Plan)

This is the full scope we initially aligned on:

1. Faithful reproduction first.
2. Include all major model families in scope.
3. Use all three paper datasets.
4. Expand only later after paper-level reproduction is stable.

This is still useful as the long-term plan, but it is too broad for the first phase if we keep the no-code limitation in mind.

## 4. Ground Rules (Agreed Assumptions)

1. We are not expected to re-derive or replicate formal proofs.
2. We will treat Jacobian/theory-heavy proof details as given unless the supervisor asks for more.
3. We are not targeting a 1:1 numeric match with the paper.
4. We are targeting method-faithful implementation and trend-level agreement.
5. Sensitivity sweeps are optional for now, not core deliverables.

## 5. Scope Reduction Proposal

### 5.1 Keep in Immediate Scope

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

### 5.2 Defer to a Later Phase

1. New transfer datasets (finance, health, or other non-paper datasets).
   Why: valuable, but not required to answer the first core research question.

2. Full baseline-family recreation.
   Why: high engineering cost and high risk of shallow comparisons.

3. Deep hyperparameter tuning sweeps.
   Why: useful later, but not vital for first-pass evidence.

### 5.3 Remove from Immediate Scope

1. RL/disentanglement extensions and side claims.
   Why: not central to the immediate supervisor-critical objective.

2. Exact numeric replication as a hard milestone.
   Why: too brittle in an independent reimplementation setting.

## 6. Recommended Minimum Deliverable

1. One full experiment matrix across paper datasets with staged components: ELBO, +CO, +EKVAE, +VHP.
2. Quantitative reporting: MSE and a latent-state quality metric (for example $R^2$ where available).
3. Qualitative reporting: at least one trajectory plot per dataset family showing success and failure behavior.
4. Reproducibility statement: what matched, what did not, and likely reasons for differences.

## 7. Query List for Supervisor

### 7.1 Scope and Success Criteria

1. Is trend-level replication acceptable for D1, given the lack of official code?
2. Is the reduced baseline set acceptable for the first milestone?
3. Do you want all three paper datasets completed before any extension work?
4. Should we explicitly exclude RL/disentanglement work for now?

### 7.2 Evaluation and Method

1. Which latent-state quality metric should be mandatory when $R^2$ is unavailable?
2. What is the minimum qualitative evidence expected (number/type of plots)?
3. Do you want any sensitivity check in D1, or should we skip it completely for now?

### 7.3 Risk and Reporting

1. How should we report mismatches vs the paper: deviation table, narrative, or both?
2. What level of implementation detail should be included to defend reproducibility?
3. Do you want a strict stop condition for scope creep before adding extra models/datasets?

## 8. Quick Meeting Sequence

1. Confirm success criterion: trend-level vs exact numeric replication.
2. Confirm immediate model/dataset scope.
3. Confirm what is explicitly deferred.
4. Confirm minimum evidence required for sign-off.
5. Confirm stop conditions to prevent scope creep.

## 9. Execution Controls

1. Add one component at a time; no multi-change runs.
2. Lock configuration per experiment; keep fixed seeds and full run logs.
3. Define conditioning/sampling and metric protocol before full experiments.
4. Do not add new datasets until the minimum deliverable is complete and reviewed.

## 10. Meeting Capture Template

- Date:
- Attendees:
- Supervisor feedback:
- Decisions made:
- Scope changes approved:
- Action items:
- New risks identified:

