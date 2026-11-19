# AutoQ — Specification (v1, draft 1)

Status: DRAFT for review · Date: 2026-11-19 · Owner: Ed Heretsch (GitHub: edsykes) · Licence: Apache-2.0

Source material: talk "The exponential data organisation" (Data Berlin, 3 Nov 2026) — altitude levels, the Business Question Loop, the Business Question Flywheel, "Beyond Engineering" stewardship, and the outline doc's harness descriptions.

## 1. Purpose

AutoQ is an open-source, self-hostable **altitude-5 harness** for a data organisation: it does not just answer business questions, it **builds and improves the system that answers them**. Each answered question must leave the system measurably better at answering the next.

Altitude 5 = "Engineering the delivery system. Improve this delivery. Strengthen the next."

### 1.1 Principles
1. Start from a business question and the decision it informs; capture *why* it is asked.
2. Humans hold authority (what is worth asking, what things mean, what may run); agents do the work.
3. Learning is retained in structured, verifiable form (ontology, facts, decisions, evals) — not loose markdown.
4. Nothing is promoted without evidence (eval gate) and everything is reversible (rollback).
5. Open source, any LLM, bring your own key, one-command spin-up.

### 1.2 Non-goals (v1)
- No writing to source systems, ever (read-only).
- No real customer data (synthetic only).
- No multi-tenancy or billing (one org per deployment).
- No real SAP extraction (RFC/ODP); sims implement the standard connector interface only.
- Deferred: Helm chart, OIDC, rich notebook visualisation, adversarial steward agent, shadow ontology commits, full STRIDE threat model.

## 2. Personas and authorities

| Role | Does | Authority |
|---|---|---|
| Exec / board | Asks top-level questions; receives decision briefs | Asks |
| VP (Procurement, Finance, Plants…) | Owns domain sub-questions; receives caveated answers | Owns domain meaning input |
| Analyst | Owns leaf questions; sees facts, SQL, lineage | Refines/asks |
| **Question Governance Authority** | Decides whether a question is worth answering and whether its breakdown is sound | Gate on question tree |
| **Meaning Authority** | Ratifies what enters the ontology; resolves cross-department meaning conflicts | Gate on ontology |
| **Mission Approver** | Approves missions per risk/cost *policy* (low-risk auto-approves) | Gate on execution |
| Operator | Configures LLMs, budgets, policies, kill switch | System |

Authorities are roles, assignable to users. v1 identity: local users with roles; OIDC pluggable later. Demo seeds personas.

## 3. Core concepts

- **Question**: text + intent ("what decision does this inform?") + asker + altitude. Forms a **tree**: exec → VP → analyst (leaf).
- **Mission**: typed contract attached to a leaf question: goal, inputs/sources, acceptance checks, budget, risk class, approver, assigned agent versions. One question = 1+ missions.
- **Loop**: the six steps executed by agents inside a mission — Ask/Frame → Discover → Clarify meaning → Obtain evidence (develop facts & explanations) → Verify (reconcile stories) → Answer (communicate). Steps may be revisited.
- **Flywheel**: after every mission the Builder runs: Build & test → Verified learning → Improve the builder (create/modify agents, skills, mappings).
- **Ontology**: fuzzy, versioned concept model with provenance and a confidence per assertion.
- **Answer**: rendered at the asker's altitude (board brief / VP caveats + meaning choices / analyst facts+SQL+lineage), always showing how ambiguity was resolved and confidence.
- **Decision record**: the decision the answer informed, and later its outcome.

## 4. Question cascade and governance flow

1. Exec asks "Why is cost of goods rising?" + decision context.
2. Planner agent proposes a breakdown into VP sub-questions then analyst questions.
3. **Question Governance Authority** accepts/edits/rejects (worth answering? breakdown sound?). Nothing downstream starts until accepted.
4. Each leaf gets a mission contract; **Mission Approver policy** routes by estimated cost/risk (auto or human).
5. Agents execute the loop. Needs-human items (clarifications, meaning conflicts) go to the relevant queue.
6. Answers roll up the tree with **confidence propagation**; the exec view shows open leaves.
7. Decision record captured; outcome later.

## 5. The loop — step requirements

| Step | Behaviour (v1) |
|---|---|
| Frame | Restate question, context, constraints; estimate cost/ambiguity/data availability (feeds mission approval). |
| Discover | Goes **straight to sources** via connectors; profiles tables/fields; asks source-owner agents/humans questions; checks the ontology and lake for what already exists. |
| Clarify meaning | Detects different meanings across systems/departments; presents differences (simple side-by-side view in v1; notebook-style later); routes to Meaning Authority; records resolution. |
| Obtain evidence | Decides which facts and granularity are needed; **decides whether a lake exists and whether the data is already there**, lands data in the lakehouse only when needed; builds source-to-target mappings and fact tables. |
| Verify | Executable checks: reconciliation to source totals, cross-system consistency, competing explanations/stories, assumptions listed. |
| Answer | Altitude-appropriate story, commit answer + meaning to knowledge store, spawn follow-up questions. |

## 6. Meaning reconciliation and the fuzzy ontology

- Cross-department/system differences surface as **conflicts** with options and evidence.
- Commitment policy is **configurable per concept**: authority decision, role-weighted vote, or evidence-weighted confidence (defaults shipped).
- Each assertion has confidence, provenance (PROV-style), version, status (proposed / committed / contested / deprecated).
- Committed meanings are reused by later missions and used to auto-resolve new sources.
- Form (standards-based RDF/SKOS vs property graph) decided in **ADR-004**.
- v1 demo conflict: **"spend"** — Procurement = committed PO value; Finance = posted invoices net of credit notes; Plants = goods receipts. At least one must be recorded and reused.

## 7. Flywheel (the altitude-5 core)

- Runs **after every mission**: retrospective → candidate improvements → evaluation → promotion.
- Builder decides what kind of agent/skill is needed and creates it using **Google ADK** where possible; can create agent specs, skills, mappings, tests, and sandboxed tool code.
- **Fully autonomous promotion**, bounded by non-negotiable guardrails:
  1. Eval gate (no promotion without passing; no regressions) and one-click rollback.
  2. Read-only sources.
  3. Spend caps per mission and per day, auto-halt.
  4. Immutable append-only audit ledger + operator kill switch.
- **Anti-Goodhart eval design**: three-way split — *dev* (Builder can see), *promotion* (hidden from Builder), *sealed audit* (operator/CI only); world generator mints fresh seeds. Compare against frozen **v0 baseline** on the same question sequence.
- **Compounding metrics** (shown on metrics page): (1) rediscovery rate ↓, (2) verification/eval pass-rate ↑, (3) human effort per mission ↓ (clarifications, edits, retries), (4) cost and wall-clock per verified answer ↓.

## 8. Simulated sources and ground truth

- **Company world model** (hidden truth): suppliers, materials, POs, goods receipts, invoices, payments, org units, FX, time evolution.
- Three SAP-shaped sims rendered as lossy, convention-skewed views: **SAP ECC 6.0**, **S/4HANA on-prem**, **S/4HANA Cloud** (public tables/field names only; non-affiliation disclaimer; naming per owner decision to use SAP names plainly).
- Per-system differences: schemas (LFA1/EKKO/EKPO/EKBE/RBKP/BSEG vs ACDOCA/Business Partner vs released CDS/API views), custom Z-fields, currencies, fiscal calendars, duplicate vendor IDs across systems.
- **Org politics**: Procurement, Finance, Plants hold legitimately different definitions, so reconciliation is a judgement call.
- **Planted COGS drivers** (answer key derived from world model): supplier price increase; FX movement; mix/volume shift; data artefacts (duplicate invoices, credit-note timing, one supplier under multiple vendor IDs).
- Sources are read-only behind a **connector interface** so any source can plug in.

## 9. Architecture (summary)

- **Front end**: React. **Back end**: FastAPI (Python).
- **Agents**: Google ADK agent definitions; **LiteLLM** gateway (any frontier lab or local open-weight model; BYO key, stored per deployment/session); **LangGraph** for durable mission/loop workflows with checkpoints.
- **State**: Postgres (+pgvector). **Lakehouse**: DuckDB/Parquet (Iceberg later), created only when a mission needs it.
- **Observability**: OpenTelemetry GenAI spans into our own Postgres schema = source of truth for trace, audit ledger and evals; Arize Phoenix as optional compose profile.
- **Sandbox**: generated code runs in a separate container, no network, read-only data, resource limits.
- **Packaging**: `docker compose up` (v1), one VM deployment on a cloud chosen later (cheapest/portable); Helm deferred.
- Open-source components wherever possible.

## 10. UI surfaces

1. **Ask**: question + decision context; altitude by role.
2. **Question tree & mission board**: tree, mission cards (goal, checks, agent version, cost, result), live activity, "needs you" queue.
3. **Answer**: per-altitude rendering with ambiguity resolution and confidence.
4. **Governance queues**: question governance, meaning workbench (conflicts, options, votes, ratification), mission approval.
5. **Builder**: agent/skill registry, versions, eval scores, proposed/promoted/rolled-back, audit ledger, kill switch.
6. **Metrics**: four compounding metrics vs v0 baseline.
7. **Sources & settings**: connectors, LLM providers, budgets, policies.

## 11. Testing and CI

- Recorded LLM **cassettes** for deterministic CI; a small local open-weight model for smoke evals; real-model evals opt-in nightly with BYO secret.
- Eval sets per §7; answer key from world model.

## 12. Definition of done for v1

Within the thin slice (§13), all must be demonstrated:
1. An exec question is broken down into VP then analyst questions, accepted by the governance authority.
2. One leaf becomes an approved mission executed by agents across all three sims.
3. At least one cross-department meaning ("spend") is surfaced, ratified, and recorded in the ontology.
4. A subsequent related question is answered better (all four metrics improve vs v0 baseline; eval gate passes; a rollback is demonstrated).
5. `docker compose up` works on a clean machine; a live instance runs on a cloud VM (BYO key only) with docs.

## 13. v1 thin slice (target: days)

In: world model + 3 SAP-shaped sims (P2P subset), cascade UI, v0 agents for all six steps, one "spend" conflict, ontology (authority + vote), eval-gated flywheel on agent specs/skills, metrics page, OTel→Postgres ledger, compose + one VM.
Deferred: Helm, OIDC, notebook viz, adversarial steward, shadow commits, injection test data, threat model.

## 14. Risks and open items

- **Scope vs "days"**: very ambitious; thin slice is mandatory.
- **Security**: v1 minimal posture (owner decision) while the Builder generates code — residual risk of prompt injection via free-text and sandbox weakness; mitigated only by sandbox + read-only + synthetic data. Recommend planted-injection evals soon after v1.
- **SAP naming**: using SAP names plainly (owner decision) carries trademark risk; disclaimer included; revisit before wider promotion.
- **Autonomy**: fully autonomous promotion relies on eval quality; sealed audit set and v0 baseline are the safeguard.
- Open: cloud provider/account for live VM; GitHub repo creation needs `gh` install + owner login; Docker needed locally to verify compose.

## 15. ADRs to write
001 Agent runtime (ADK + LiteLLM + LangGraph) · 002 Observability backbone · 003 Lakehouse/data path · 004 Ontology representation · 005 Sandbox for generated code · 006 Eval splits and baseline protocol · 007 Work tracking (GitHub Issues/Projects + repo docs).
