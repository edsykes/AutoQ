# 0010: Handoff schema and friction taxonomy

- Status: accepted
- Date: 2026-11-21
- Ticket: #9
- Decided by: agent (autonomous)

## Context
SPEC section 10 requires every agent-to-agent and agent-human interaction to be a typed, schema-defined handoff with no side channels, and section 13 requires a fixed friction taxonomy for the Builder to mine. Handoff-record tickets (#86, #26) implement this. Traceability: US 28, 29, 31.

## Decision

### Handoff record
Stored in Postgres (table `handoff`), append-only except for the single later-linked outcome fields. Kept forever in v1. Fields:

| Field | Type | Notes |
|---|---|---|
| `id` | uuid | |
| `schema_version` | int | starts at 1 |
| `created_at` | timestamptz | |
| `mission_id`, `step_run_id` | uuid, nullable | trace to ADR 0007 work rows |
| `trace_id`, `span_id` | text | link to OpenTelemetry span (ADR 0002) |
| `sender` | actor | see below |
| `receiver` | actor | |
| `purpose` | enum | `request`, `deliver`, `decide`, `escalate`, `review`, `clarify`, `correct`, `approve`, `reject`, `report_failure` |
| `payload_ref` | uri | reference to payload (asset, contract, claim, message); no inline blobs |
| `decision` | text | what was decided or asked; nullable for pure deliveries |
| `rationale` | text | |
| `alternatives` | list of {option, reason_not_chosen} | may be empty |
| `confidence` | float 0..1, nullable | |
| `human_intervention` | enum | `none`, `clarification`, `correction`, `rejection`, `approval`, `override`, `retry` |
| `human_wait_seconds` | int, nullable | queue wait attributable to a human |
| `cost` | {tokens_in, tokens_out, usd}, nullable | |
| `duration_ms` | int | |
| `outcome` | enum, nullable | `used`, `corrected`, `rejected`, `ignored`; null until linked |
| `outcome_handoff_id` | uuid, nullable | the later handoff that caused the outcome |
| `outcome_at` | timestamptz, nullable | |
| `friction` | list of friction tags | see below; may be empty |

**Actor** = {`kind`: `agent` | `human`, `id`, `agent_version` (agents), `role` (humans: exec, vp, analyst, an authority, operator)}. Humans are actors like agents.

Rules: no interaction occurs without a handoff row; outcome is set exactly once, by the consumer's later handoff or by an explicit sweep that marks never-used payloads `ignored` at mission end; schema changes bump `schema_version`.

### Friction taxonomy
A fixed enum, `friction.category`, exactly these seven (matching the glossary and SPEC 13), with sub-types:

1. `rework_loop`: same work redone after rejection or failed check (`rework.retry`, `rework.step_revisit`, `rework.correction_cycle`).
2. `information_loss`: a receiver lacked or misread something the sender had (`info.missing_field`, `info.stale_context`, `info.ambiguous_payload`).
3. `redundant_work`: artefact re-derived that already existed (`redundant.rediscovery`, `redundant.duplicate_computation`).
4. `escalation_error`: `escalation.over` (asked a human unnecessarily), `escalation.under` (proceeded where a human was needed), `escalation.human_overturn` (a human reversed an agent decision).
5. `agent_disagreement`: two agents produced conflicting outputs or self-contradiction (`disagree.inter_agent`, `disagree.self_contradiction`).
6. `waste`: `waste.tokens`, `waste.time`, `waste.queue_wait`, `waste.estimate_error` (predicted vs actual cost/time off by more than a configured ratio).
7. `missing_capability`: no agent, skill, tool or check could do what was needed (`missing.skill`, `missing.tool`, `missing.check`, `missing.mapping`).

A friction tag = {`category`, `subtype`, `detected_by` (`rule` | `retrospective_agent`), `evidence` (short text), `severity` 1..3}. Agent failures and timeouts are tagged under their closest category (`rework.retry`, `waste.time`). Findings are attributed to a handoff id and the sender's agent version, so the Change Designer can target a specific version.

Rule-based detectors (retry counts, human overturns, duplicate payload hashes, estimate ratio) run on write and are deterministic; the Retrospective agent adds judgment-based tags after each mission. Adding a category is a schema bump plus a new ADR; subtypes may be added by a normal change.

## Alternatives considered
- Free-text friction notes: not minable or countable.
- Inline payloads in the handoff: bloats the table and duplicates assets; `payload_ref` keeps lineage.
- Mutable outcome history: single outcome per handoff is enough for v1; later corrections are new handoffs.

## Consequences
Compounding metrics (human effort, cost/time, rediscovery) are plain aggregates over this table. Hypothesis records (ADR 0006) cite `friction_category` and handoff ids. Obeying "no side channels" means every agent adapter must emit a handoff; the runtime ticket enforces this at the call boundary.
