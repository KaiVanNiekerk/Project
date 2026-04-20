# EKVAE Query and Planning Brief

## Purpose

This is the supervisor-facing planning note. It summarises the current scope, the questions that still need decisions, the assumptions we are working with, and the controls we want to keep the project focused.

See [research.md](research.md) for the supporting analysis, watch-outs, and scope reduction reasoning.

## Initial Scope (Original Plan)

1. Faithful reproduction first.
2. Include the main model families in scope.
3. Use all three paper datasets.
4. Expand only after the paper-level reproduction is stable.

This remains the long-term plan, but it is too broad for the first phase if we keep the no-code limitation in mind.

## Working Assumptions

1. We are not expected to re-derive or repeat proofs.
2. Jacobian or other technical details are taken as given unless the supervisor wants more.
3. We are not aiming for a 1:1 numeric match with the paper.
4. The main goal is an implementation that stays faithful to the method and gives trend-level agreement.
5. Sensitivity sweeps are optional, not core deliverables.

## Minimum Deliverable

1. One experiment matrix across the paper datasets with staged steps: ELBO, +CO, +EKVAE, +VHP.
2. Quantitative reporting: MSE and a latent-state quality metric such as $R^2$ where available.
3. Qualitative reporting: at least one success/failure trajectory plot per dataset family.
4. A reproducibility note covering what matched, what did not, and likely reasons for differences.

## Questions for Supervisor

### Scope and success criteria

1. Is trend-level replication acceptable for D1, given the lack of official code?
2. Is the reduced baseline set acceptable for the first milestone?
3. Should the first phase stay strictly on the paper datasets, with any new datasets deferred?
4. Do you want the baseline set limited to one standard DSSM, one KVAE-family baseline, and EKVAE?
5. Should we explicitly exclude RL/disentanglement work for now?

### Evaluation and method

1. Which latent-state quality metric should be mandatory when $R^2$ is unavailable?
2. What is the minimum qualitative evidence expected?
3. Should we skip sensitivity checks for D1, or keep only a small one?
4. For CO, should $D_0$ be fixed per dataset or allow a small sensitivity range?
5. For EKVAE, which implementation details matter most: transition model, decoder, filter update, or all of them?
6. For VHP, should it stay as a later comparison step only if the earlier stages are stable?
7. Should the short-sequence and hidden-dynamics concerns stay as notes, rather than becoming a separate evaluation task?
8. If the paper mostly used toy data or short sequences, should we treat that as a sign that longer-horizon datasets may be harder and less directly comparable?
9. For our own datasets, should we deliberately prefer longer sequences to test whether the method still holds beyond toy settings?

### Reporting and scope control

1. How should we report mismatches vs the paper: deviation table, narrative, or both?
2. What level of implementation detail should be included to defend reproducibility?
3. Do you want a strict stop condition for scope creep before adding extra models or datasets?
4. How much detail should we include for the known watch-outs so they stay useful without making the document too long?
5. Should we record the main limitations as research notes only, or also mention them in the proposal if needed later?
6. If the paper mostly used short toy sequences, should we lower our expectations for exact replication on longer datasets and focus on trend-level agreement?

## Quick Meeting Sequence

1. Confirm success criterion: trend-level vs exact numeric replication.
2. Confirm immediate model and dataset scope.
3. Confirm what is explicitly deferred.
4. Confirm minimum evidence required for sign-off.
5. Confirm stop conditions to prevent scope creep.
6. Confirm which watch-outs should influence implementation.
7. Confirm how to treat short-sequence results when moving to harder datasets.

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
