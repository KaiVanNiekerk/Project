# EKVAE Query and Planning Brief

## Purpose

This doc is for supervisor meetings. It contains:

- the original scope we started with,
- key questions we need answered before implementation starts,
- agreed ground rules and assumptions,
- minimum deliverables,
- execution controls to prevent scope creep.

See `research.qmd` for the analysis of reviews and scope reduction reasoning.

## Initial Scope (Original Plan)

This is the full scope we initially aligned on:

1. Faithful reproduction first.
2. Include all major model families in scope.
3. Use all three paper datasets.
4. Expand only later after paper-level reproduction is stable.

This is still useful as the long-term plan, but it is too broad for the first phase if we keep the no-code limitation in mind.

## Ground Rules (Agreed Assumptions)

1. We are not expected to re-derive or replicate formal proofs.
2. We will treat Jacobian/theory-heavy proof details as given unless the supervisor asks for more.
3. We are not targeting a 1:1 numeric match with the paper.
4. We are targeting method-faithful implementation and trend-level agreement.
5. Sensitivity sweeps are optional for now, not core deliverables.

## Recommended Minimum Deliverable

1. One full experiment matrix across paper datasets with staged components: ELBO, +CO, +EKVAE, +VHP.
2. Quantitative reporting: MSE and a latent-state quality metric (for example $R^2$ where available).
3. Qualitative reporting: at least one trajectory plot per dataset family showing success and failure behavior.
4. Reproducibility statement: what matched, what did not, and likely reasons for differences.

## Query List for Supervisor

### Scope and Success Criteria

1. Is trend-level replication acceptable for D1, given the lack of official code?
2. Is the reduced baseline set acceptable for the first milestone?
3. Do you want all three paper datasets completed before any extension work?
4. Should we explicitly exclude RL/disentanglement work for now?

### Evaluation and Method

1. Which latent-state quality metric should be mandatory when $R^2$ is unavailable?
2. What is the minimum qualitative evidence expected (number/type of plots)?
3. Do you want any sensitivity check in D1, or should we skip it completely for now?

### Risk and Reporting

1. How should we report mismatches vs the paper: deviation table, narrative, or both?
2. What level of implementation detail should be included to defend reproducibility?
3. Do you want a strict stop condition for scope creep before adding extra models/datasets?

## Quick Meeting Sequence

1. Confirm success criterion: trend-level vs exact numeric replication.
2. Confirm immediate model/dataset scope.
3. Confirm what is explicitly deferred.
4. Confirm minimum evidence required for sign-off.
5. Confirm stop conditions to prevent scope creep.

## Execution Controls

1. Add one component at a time; no multi-change runs.
2. Lock configuration per experiment; keep fixed seeds and full run logs.
3. Define conditioning/sampling and metric protocol before full experiments.
4. Do not add new datasets until the minimum deliverable is complete and reviewed.

## Meeting Capture Template

- Date:
- Attendees:
- Supervisor feedback:
- Decisions made:
- Scope changes approved:
- Action items:
- New risks identified:
