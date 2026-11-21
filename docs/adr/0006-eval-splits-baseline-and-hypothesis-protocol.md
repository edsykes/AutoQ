# 0006: Eval splits, Baseline v0 and the hypothesis protocol

- Status: accepted
- Date: 2026-11-21
- Ticket: #9
- Decided by: agent (autonomous)

## Context
SPEC section 13 fixes the shape (Dev and Promotion sets, frozen Baseline v0, hypothesis on every change, a gate) but leaves the protocol open: how cases are drawn, what the Builder can see, the exact gate arithmetic, and how a hypothesis is monitored and rolled back. Eval tickets (#86, #26) implement this directly. Spec traceability: US 28-33.

## Decision

### Sets
- **Dev**: 10 cases, visible to the Builder. Two cases in each of the five categories (identification, meaning, evidence, verification, answer), on three world seeds (`dev-a`, `dev-b`, `dev-c`).
- **Promotion**: 10 *different* cases, same 2-per-category spread, on three *other* seeds (`promo-a`, `promo-b`, `promo-c`). Hidden from the Builder: the Builder role has no read grant on the promotion case store, seeds or Answer Keys. Only the Evaluator and Promoter see them, and they return only an aggregate verdict (pass/fail per guarded and target metric, plus per-category pass-rate), never case-level detail.
- **Sealed**: not in v1 (v2). The set and its Promotion-vs-Sealed divergence alert are out of scope; the case-store schema carries a `set` column that admits `sealed` later.
- Seeds are fixed in repo config for Dev and in operator-held config for Promotion. Case definitions are versioned files owned by the Eval Curator path (human-approved change only). The Builder cannot modify cases, seeds, the gate rules or the Evaluator.
- A case = world seed + question + Answer Key reference + category + acceptance checks. Each case scores pass/fail on its checks; answer-correctness cases use the spec tolerance (drivers within 10% of the Answer Key, every planted duplicate flagged).

### Baseline v0
- Baseline v0 is the thin agents as first built, frozen under git tag `baseline-v0` and stored as a registry version `v0` that is read-only. It ships with exactly one seeded deficiency (default: Discover does not reuse source profiles), listed in `evals/baseline/SEEDED_DEFICIENCY.md`.
- Baseline v0 and the candidate run the **identical question sequence on identical seeds**, in the same harness, with the same LLM provider/model and temperature 0 where supported.
- Baseline v0 is re-run only when the harness, model or case set changes; results are cached keyed by (agent-set hash, case-set hash, model, seed). Re-baselining is a human-approved change and creates `baseline-v0` results anew; the tag never moves.
- Compounding metrics are always reported vs Baseline v0.

### Run protocol (LLM variance)
Each case runs **N = 3** times per agent set (candidate and baseline); a case's score is the pass fraction over the runs (pass-rate), and metric values are means. Cost, time and human-effort metrics are means over the same runs. N is config, not part of the gate rule.

### Hypothesis record (required on every Improvement Proposal)
Fields: `id`, `proposal_id`, `change_type`, `friction_category` and `friction_handoff_ids` (evidence from ADR 0010), `target_metric` (one of the four compounding metrics or a per-category pass-rate), `expected_direction`, `expected_effect` (a number with unit, for example "-20% cost per verified answer"), `guarded_metrics` (default: all four compounding metrics and overall Promotion pass-rate), `disproof` (the smallest evidence that would disprove it, as a testable predicate), `monitor_window` (default: the next 5 missions after promotion, or 7 days if fewer), `created_by_agent_version`. A proposal without a complete hypothesis record is rejected at intake.

### Gate rule (Promotion gate)
A candidate is promoted only if all hold, evaluated on **Promotion** (and Dev must also pass as a sanity check, but Dev alone never promotes):
1. **No regression on guarded metrics**: for every guarded metric, candidate is no worse than the incumbent (the live version, not just Baseline) by more than the **noise tolerance**.
2. **Improvement on target**: candidate beats the incumbent on the hypothesis' target metric by more than the noise tolerance, in the expected direction.
3. **Per-category floor**: no Promotion category's pass-rate falls below the incumbent's by more than one case-run.
4. **Dev/Promotion consistency**: the Dev improvement on the target metric and the Promotion improvement have the same sign. A candidate that improves Dev but not Promotion is rejected and recorded as an overfitting suspect.
5. **Safety invariants hold**: zero new violations of read-only sources, spend cap or sandbox policy in the run.

**Noise tolerance** = max(10% relative, 1 standard deviation across the N runs of the incumbent on that metric). The 10% is a first guess to revisit after the first build (SPEC risks). Gate rules and tolerance live in operator-controlled config and change only through the human-approved path.

Outcome is one of `promoted`, `rejected` (with reason codes: `regression`, `no_improvement`, `category_floor`, `overfit_suspect`, `safety`, `incomplete_hypothesis`), recorded as a Ledger Entry with the aggregate numbers.

### Post-promotion monitoring and rollback
For `monitor_window`, the realised effect on the target metric is measured from live handoff and ledger data against the pre-promotion level. If the effect is not at least half the expected effect by the end of the window, or any guarded metric regresses beyond the noise tolerance, the Promoter **rolls back automatically** to the prior version and writes a Ledger Entry. A deliberately failing hypothesis exists in the acceptance scenarios (SPEC scenario 8) and must trigger this path.

## Alternatives considered
- Single eval set: invites overfitting by the Builder; the spec already requires a hidden set.
- Gate against Baseline v0 only: would let a candidate regress against the live incumbent while still beating the weak baseline. Baseline is for compounding metrics; the gate is against the incumbent.
- Fixed absolute thresholds: brittle under LLM variance; relative tolerance plus run variance is simpler to defend.
- Sealed set now: deferred to v2 by the spec.

## Consequences
Eval tickets implement the case schema, runner (N runs), baseline cache, gate function and hypothesis schema as above. The 10% tolerance, N = 3 and the half-effect rollback rule are tunable config, so changing them is a config change plus an ADR note, not a re-architecture. Small sets (10 cases) mean low statistical power; the consistency check and tolerance exist because of that.
