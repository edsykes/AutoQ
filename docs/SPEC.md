# AutoQ — Specification (v1 spine, draft 3)

Status: DRAFT for review · 2026-11-19 · Owner: Ed Heretsch (GitHub: edsykes) · Licence: Apache-2.0
Vocabulary: [GLOSSARY.md](../GLOSSARY.md) · Later versions: [ROADMAP.md](ROADMAP.md) · Work: [BACKLOG.md](BACKLOG.md)
Source: the talk "The exponential data organisation" (Data Berlin, 3 Nov 2026), and the architecture grilling session of 2026-11-19 (decisions recorded below as D-numbers where useful).

---

## Problem Statement

Data organisations answer business questions one delivery at a time. Each answer is rebuilt largely from scratch: sources are rediscovered, departments re-argue what "spend" or "supplier" mean, and what was learned stays in heads, notebooks and markdown. AI speeds up individuals and teams (altitudes 1–4) but the learning is not retained in a verifiable, reusable form, so the organisation does not get measurably better at answering the *next* question.

The business never wanted to manage data. It wants to govern **which questions are worth asking**, **what things mean** and **what it values**. Today those authorities have no software to exercise that authority, and agents have no governed context to work from.

Classic data architecture (load everything, model it in advance as Kimball, vault or mesh) assumed we could not know the questions in advance. With agents the question arrives first. The right structure should therefore emerge per question and per step, constrained by contracts and policy and not by a prescribed modelling shape.

## Solution

**AutoQ** is an open-source, self-hostable, LLM-agnostic **altitude-5 harness**. It:

1. **Answers business questions through governed missions.** An exec asks and states the decision it informs. A Question Governance Authority approves a breakdown into VP and analyst questions. Leaf questions become missions executed by agents through six steps (Frame, Discover, Clarify, Evidence, Verify, Answer). Differences in meaning go to a Meaning Authority and are committed to a fuzzy ontology. The answer is a verified **claim graph**, reviewed by humans by claim and domain, and rendered at the asker's level with confidence, lineage and the company values it bears on.
2. **Builds and improves the system that answers.** Every handoff between agents and humans is recorded. After every mission a Builder mines those records for friction, proposes the smallest effective change with a hypothesis, tests it behind a hidden eval gate against a frozen baseline, promotes it autonomously, monitors the effect, and rolls back if the hypothesis fails. Anything that touches human governance is only ever a proposal.
3. **Stores only what earns its place, in a structure that emerges.** The durable asset is the governed *definition*; data is a rebuildable materialisation. The system mandates a machine-managed **contract** on every stored model, not a modelling shape.

### Principles
1. Start from the question and the decision it informs; capture *why* it is asked, in the ontology.
2. Humans hold authority over questions, meaning and values; agents steward everything below that.
3. Resolve before create; change as little as possible.
4. Retain learning as structured, verifiable, replayable records.
5. Nothing is promoted without evidence; everything is reversible; human review of answers is always required.
6. Open source, any LLM, BYO key, open formats, one-command spin-up.

---

## User Stories

**Exec**
1. As an exec, I want to ask a business question in my own words and state the decision it informs, so that the answer targets what I must decide.
2. As an exec, I want to see how my question broke down into VP and analyst questions and which are answered, open or low-confidence, so that I know how far to rely on the whole.
3. As an exec, I want a decision-level brief with confidence, the meanings assumed, and the company values the facts bear on, so that I can act without reading analysis.
4. As an exec, I want follow-up questions to reach the level that can decide whether to pursue them, so that I am not asked about detail.
5. As an exec, I want to record the decision I took and later its outcome, so that the system learns what mattered.
6. As an exec, I want to see that the system answers related questions faster and cheaper over time, so that I can judge the investment.

**VP / Analyst**
7. As a VP, I want to own the sub-questions in my domain and edit, reject or split them, so that they reflect how my domain works.
8. As a VP or analyst, I want to review only the claims about my domain, including claims made by other domains about mine, so that I am accountable for what is said about my area and nothing else.
9. As a reviewer, I want to bring a counter-claim based on evidence not connected at fact level and see it tested, included, rejected or deferred with reasons, so that human knowledge enters the story honestly.
10. As a reviewer, I want to propose a counter-story, add or amend a check, challenge a reconciliation, and re-weight claims, so that I can steer Verify.
11. As an analyst, I want facts, SQL and lineage behind every claim, so that I can verify and reuse them.
12. As an analyst, I want agents to ask me targeted questions instead of guessing, and my corrections retained, so that I do not repeat myself.
13. As a VP, I want to be told when my department's definition differs from another's, so that I can influence the reconciliation.
14. As an asker, I want to question the answer in dialogue and have questions become tracked questions with their own intent, so that nothing I wondered is lost.

**Authorities**
15. As a Question Governance Authority, I want a queue of proposed breakdowns and follow-ups with estimated cost, availability and ambiguity, so that I decide what is worth answering.
16. As a Question Governance Authority, I want decisions retained as precedent and declined follow-ups remembered, so that the same question is not re-proposed without new information.
17. As a Meaning Authority, I want a workbench of semantic conflicts with options, evidence and example records, so that I resolve meaning deliberately (reconcile, keep distinct, defer).
18. As a Meaning Authority, I want agents to spawn meaning missions when a concept is missing or in conflict, so that ontology work is tracked and measured like other work.
19. As a Meaning Authority, I want a sensitivity check showing how much an answer changes under each candidate meaning, so that I focus on conflicts that matter.
20. As a Values Authority, I want a governed Values Register with indicators and sensible defaults, so that stories can be tied to what the company values.
21. As any authority, I want delegates and time-limited escalation so that queues do not stall, without anything being decided in my place.
22. As a Mission Approver, I want to see each mission contract, its estimated cost and risk, and which policy routed it, so that I approve with confidence.

**Operator**
23. As an operator, I want any LLM provider (frontier or local) with my own key, so that I am not locked in.
24. As an operator, I want per-mission and per-day spend caps, an immutable audit ledger and a kill switch, so that autonomy stays bounded.
25. As an operator, I want to see storage space and cost, by snapshot, zone and model, so that I can manage them.
26. As an operator, I want a lineage view for any graph in the product, so that I can trace any answer, claim, assertion, model, agent change or question to its origin.
27. As an operator, I want one-command spin-up and a hosted instance, so that evaluation takes minutes.

**Builder and flywheel**
28. As the Builder, I want every agent and human handoff recorded with decision, rationale, alternatives and downstream outcome, so that I can find where work goes wrong.
29. As the Builder, I want a fixed friction taxonomy to mine, so that improvements target real problems.
30. As the Builder, I want to choose the smallest effective change and estimate its blast radius first, so that changes stay small and reversible.
31. As the Builder, I want each change to state a hypothesis that is measured after promotion, so that compounding is visible per change.
32. As an auditor, I want eval sets the Builder cannot see or alter, so that improvement is not overfit.
33. As a stakeholder, I want four defined compounding metrics against a frozen baseline, so that nobody can game them quietly.

**Data and assets**
34. As an analyst, I want Discover to go straight to sources, profile them read-only, and reuse profiles across missions, so that findings are fresh and cheap.
35. As an agent, I want every stored model to carry a machine-readable contract (definition, grain, entity-bound keys, concept-bound measures, lineage, checks, status, steward, sensitivity, economics), so that I can decide to reuse, rebuild, retain or evict it without a human.
36. As a data consumer, I want models to join through ontology entities and governed identity links, so that data from different systems connects.
37. As a steward agent, I want remediation rules as governed, versioned definitions applied only inside the lake, so that data defects are fixed without touching sources.
38. As a reviewer, I want old answers annotated when the meaning they used has changed, and a human-triggered rebuild to create a new version of the question, so that history stays intact.
39. As a developer, I want a public Apache-2.0 repository, docs and CI, so that I can run and extend it.
40. As a presenter, I want a scripted scenario demonstrating cascade, meaning conflict, review and measurable improvement, so that the product can be shown live.

---

## Implementation Decisions

### 1. Scope
v1 is the **spine**: one thin pass through every idea. The full architecture below is the target; items marked *(v1.1/v1.2/v2)* are designed in, not built. See ROADMAP.md.

### 2. Humans and authority
Seven roles: Exec, VP, Analyst (askers/reviewers); four authorities — **Question Governance** (inquiry and purpose), **Meaning**, **Values**, **Mission Approver** — and **Operator**. Roles may be scoped to a domain (Procurement, Finance, Plants). Each authority has named delegates and a time-limited escalation chain (delegate → authority above → operator). On timeout agents only **remind, re-route and prepare a summary**; nothing is decided in a human's place (**D: no proxy decisions**). Wait time is recorded as human effort. Where two authorities disagree, the Question Governance Authority arbitrates and the case is recorded. v1 identity: local users with roles and seeded personas; OIDC later.

### 3. Domain model
- **Question** (text, intent link, parent, version, status) forming a **Question Tree** (exec → VP → analyst leaf). Status: `draft → proposed → accepted | rejected | rework → in_progress → answered → closed`. A human-triggered rebuild creates **question version n+1** (§12).
- **Intent Record** (decision, stakes, audience, constraints) linked to a question; an instance linking into the ontology's purpose partition (§8).
- **Need Spec** (§6): the governed definitions a question needs, in ontology terms.
- **Mission** with a **Mission Contract** (goal, Need Spec, inputs, acceptance checks, budget, risk class, approver, assigned agent versions). Missions have **sub-missions** that each change exactly one governed asset (§7). Mission types: *answer mission* and *meaning mission* (§8). Lifecycle: `proposed → awaiting_approval → approved → running ⇄ blocked_on_human → verifying → completed | failed | cancelled | halted`.
- **Handoff** (§10), **Asset** (§5) and its **Contract**, **Concept / Assertion / Conflict Case** (§8), **Claim / Story / Counter-claim** (§11), **Answer** (immutable, versioned), **Decision Record**, **Agent / Skill / Tool / Check / Improvement Proposal / Hypothesis / Eval Suite / Promotion** (§12), **Ledger Entry** (append-only, hash-chained).

### 4. The loop and its agents
Each step is a LangGraph workflow of Google ADK agents with durable checkpoints, retries, human-wait states and loop-back edges. In v1 each step has **one thin agent**; the full role sets below are the target.

| Step | Roles (target) | Output |
|---|---|---|
| **Frame** | Question Interpreter; Need Spec Builder; Prior-Knowledge Checker; Estimator; Mission Planner | Intent Record, Need Spec, estimates, minimal mission plan |
| **Discover** | Need Resolver; Source Profiler; Lake Auditor; Source Liaison; Discovery Synthesiser | Discovery Report per need: candidate assets, reuse verdict, gaps, open questions |
| **Clarify** | Concept Comparator; Sensitivity Analyser; Option Presenter; Resolution Applier; Meaning Steward | Conflict Cases, resolutions, meaning missions |
| **Evidence** | Fact Designer; Lake Planner; Mapping Builder; Transformer; Quality Agent; Explanation Builder | Registered facts and candidate explanations |
| **Verify** | Reconciler; Story Weaver; Counter-Story Generator; Claim Router; Review Facilitator; Confidence Assessor | Reviewed claim graph, confidence |
| **Answer** | Communicator; Dialogue Agent; Commit Agent; Follow-up Agent | Immutable answer, follow-ups, decision-record request |

Failure handling: bounded retries, then `blocked_on_human` with diagnosis; agent failures, timeouts and self-contradictions are recorded as friction. Estimate accuracy (predicted vs actual cost/time) is a friction signal.

### 5. Data architecture (the lake and its assets)
**No prescribed modelling shape.** The system mandates a **contract**; Kimball, mesh, vault, event log, graph and others are patterns agents may choose and must justify.

- **Retention by earned keep.** Everything begins as *scratch*, scoped to one mission. A model is *retained* if it earns its keep: a **retention score** blends expected reuse, rebuild savings and trust against carrying cost (re-check effort, staleness and conflict risk, discovery noise, reproducibility burden). The weights are an operator-owned, evaluated policy the Builder may propose to change. Overlapping models are **consolidated** (a better one supersedes). Storage size is not a retention criterion; *(v1.2)* implements scoring/eviction, v1 keeps everything.
- **The durable asset is the definition.** A governed definition (measure or entity bound to ontology concepts, with grain, scope, version) is durable; its physical materialisation is a rebuildable cache.
- **Landing.** Sources are never mirrored. Landing is minimal and per mission (only fields and rows the approved mapping needs), as immutable **as-of-stamped snapshots**. **All snapshots are kept by default**; operators can set an expiry policy, in which case answers whose snapshots expired become "not replayable" and leave the eval sets. An admin view shows storage space and cost per snapshot, zone and model.
- **Reproducibility.** Every materialisation records source snapshot as-of, definition versions, mapping versions and agent versions. Every answer is replayable.
- **Contract** (machine-managed; agents write and read it; humans do not fill it in): definition reference and version; grain; keys bound to entities; measures bound to concepts and assertion versions; time semantics and freshness; lineage; declared checks and latest results; derived status; steward agent and policy ref; sensitivity; economics (rebuild cost, reuse count, last used); retention score. A model without a complete contract cannot leave scratch.
- **Status** values: scratch, retained, trusted, stale, deprecated, quarantined. **Trust is derived mechanically**: every concept used is committed above threshold, checks pass, and a replay reproduces the model. No human signs off individual models.
- **Lifecycle zones** (logical, mapped to locations by the Lake Adapter): *snapshots*, *scratch*, *retained*, *quarantine*. Zones follow contract status, never modelling shape.
- **Connectivity.** Keys bind to ontology entities. **Identity links** (e.g. several vendor IDs = one Supplier) are governed definitions with confidence, produced by a **matching agent** (blocking → scoring by rules, similarity and an LLM judge on ambiguous pairs → policy bands: auto-commit high, human review of sampled/contested middle, reject low). Humans set thresholds and policy; they do not approve individual links. Cross-model joins go through entity bindings and identity links. *(v1: one entity — supplier; full matching bands v1.1.)*
- **Engine.** One columnar engine behind a swappable **Lake Adapter**: DuckDB over Parquet, with a Postgres **snapshot catalogue** and contract store; open table formats compared in ADR-003. pgvector for similarity.
- **Catalogue and lineage.** Contracts and an explicit lineage graph (asset → asset via transformation and version) live in Postgres as relational edges; impact analysis and replay are traversals. A graph database only if traversal becomes a bottleneck (ADR-003).
- **Stable core vs changeable layout.** The **addressing scheme** (definition, version, snapshot), the **contract schema** and the **lineage format** are the stable core: versioned, migrated, and changed only through a human-approved path. Zone layout, retention weights and shape patterns are changeable policy the Builder may propose.
- **Open formats.** Data lineage as **OpenLineage** events with our contract fields as custom facets; provenance of assertions, answers and claims exportable as **W3C PROV-O**; ontology export in a standard form (ADR-004).
- **Existing lakes** *(v1.1)*: AutoQ builds its own lake afresh and never writes elsewhere, but a pre-existing org lake may be read as a **fourth system of facts** through the connector interface. Trust is earned per lake model by Discover cross-referencing to primary sources (control totals, key coverage, freshness, lineage claims) and stored as assertions; each lake model gets a **reuse verdict** (reuse as-is / with adjustments / do not reuse) recorded in lineage; lake reuse counts toward lower rediscovery. Lake meaning (hierarchies, catalogue definitions, semantic-layer metrics) arrives only as *proposed* provenance-tagged lower-confidence assertions; hierarchies become versioned ontology relations.

### 6. Resolve-before-create and the Need Spec
Frame produces a **Need Spec**: the governed definitions required (entities, measures, grains, time scope) in ontology terms. Every later step **resolves existing assets against it first** and creates only when nothing satisfies a need, registering what it creates against that need. Lookup is **ontology-addressed first** (concept, entity, grain, scope, version); semantic similarity (pgvector) only yields fuzzy candidates that an agent must justify, and a fuzzy match is never trusted without verification.

### 7. Evolving assets and smallest change
When a near-match exists, choose by compatibility, ordered by smallest change: (1) **reuse as-is**; (2) **compatible extension** (additive; new version; dependants unaffected); (3) **create alongside** when the difference is legitimate (linked by relation); (4) **incompatible change** (new version, **impact analysis** through lineage) as last resort. Compatibility is verified by replaying dependants. After an incompatible change, agents **automatically re-evaluate** dependants and produce an impact report (unchanged / within tolerance / materially changed); old answers are annotated, never overwritten; a new question version is created only when a human triggers it, unless an operator policy enables automatic republication.
**Smallest-change rule:** a sub-mission changes exactly one governed asset, has its own acceptance check, is independently verifiable and reversible, and fits one agent context. Blast radius is estimated before acting and the smallest option wins; larger changes are verified sequences. Change size is a tracked metric.

### 8. The ontology: meaning, purpose, values
Three governed partitions: **Meaning** (concepts, relations, hierarchies, identity links — Meaning Authority), **Purpose** (decision types, stakes, stakeholders, initiatives; a question *informs* a decision that *serves* a value or initiative — Question Governance Authority), **Values** (register with indicators — Values Authority). Intent Records instantiate links into Purpose; missing items are proposed by agents and committed by the owning authority.
- **Assertion**: statement, scope, confidence (0..1), status (`proposed / committed / contested / deprecated`), provenance, version.
- **Commit Policy** per concept: authority, vote (role/domain-weighted, quorum, default threshold 0.7, contest limit 0.3) or evidence-weighted; hybrid configurable. *(v1: authority only; vote/evidence v1.1.)*
- **Two layers of meaning.** The **source mapping layer** (what each source field or lake model means in ontology terms, with confidence) is high-volume and agent-governed; it escalates only when a mapping implies a meaning conflict. Humans govern the business ontology.
- **Conflicts are typed.** *Semantic* (same word, different meanings) → Meaning Authority. *Factual* (same meaning, different numbers) → data owner as a quality finding; agents fix at data level with **remediation rules** (governed, versioned definitions applied in our lake with lineage, never edits to a source) that wait on a meaning mission if they depend on a meaning decision. Classification is itself evaluated.
- **Meaning missions** are first-class missions: contract, Meaning Authority approver, own metrics. A **sensitivity check** measures how much an answer changes under each candidate meaning. Resolution rule: **auto-resolve and record** when a committed assertion applies with confidence above threshold; **provisional** (labelled assumption, meaning mission opened) when no committed meaning applies but the choice is immaterial; **block and escalate** when material or when the concept requires humans. *(v1: all conflicts that matter block for the Meaning Authority; sensitivity and provisional path v1.1.)*
- **Values Register** with five default values and indicators (see §14).
- Demo conflict **"spend"**: Procurement = committed PO value; Finance = posted invoice value net of credit notes; Plants = goods received value.

### 9. Questions, missions and approval
1. Exec asks + intent. 2. Planner proposes the breakdown. 3. **Question Governance Authority** accepts, edits, rejects or sends back; decisions kept as precedent. 4. Leaf missions are planned as minimal sub-missions; an **approval policy** (rules over estimated cost, risk class, new ontology commitments, prior success) auto-approves or routes to a Mission Approver. 5. Agents run the loop; human items go to the right queue. 6. Answers roll up with confidence propagation.
**Follow-ups** are routed to the lowest level whose intent covers them and whose authority can afford them; that level's governance authority decides whether to take another turn around the loop. Declines are retained so identical follow-ups are not re-proposed without new information.

### 10. Interaction records (cross-cutting)
All communication between agents, and between agents and humans, is a **typed, schema-defined handoff** with no side channels. Each handoff record: sender and receiver (agent version or human), purpose, payload reference, decision, rationale, alternatives considered, confidence, human intervention, and later-linked **downstream outcome** (used, corrected, rejected, ignored). Humans are actors like agents. Stored in Postgres alongside the ledger; OpenTelemetry spans carry cost and timing.

### 11. Verify, stories and review
A **story is a claim graph**: each claim links to supporting facts (and so lineage) and, via indicators, to the values it bears on; the graph includes counter-stories considered and rejected. Prose is rendered from the graph per asker level. Claims citing a value without a supporting indicator are rejected. Claim types: *evidence-backed* and *human-asserted* (labelled with author and basis; never rendered as fact).
**Review is always required.** Every concept belongs to a domain; each claim inherits the domains of the concepts it uses plus the question's domain; each subject domain's reviewer reviews it (so a claim about another domain needs that domain's reviewer). Each claim gets a disposition (approved / counter-claimed / rejected); an answer is released only when every claim has one; there is **no provisional release**.
Human inputs in Verify (all recorded as handoffs): propose a counter-story, add or amend an acceptance check, challenge a reconciliation, raise counter-claims, re-weight claims.
**Counter-claim**: author, statement, targeted claims, basis (unlinked evidence), why unlinked, proposed action; agent triage may spawn a test sub-mission; outcomes: *resolved by evidence*, *included* as qualified claim, *rejected*, *deferred*; adjudicated by the reviewer of record (asker or domain VP; Meaning Authority only if meaning changes); retained as reusable context for Frame and Verify.
**Check library**: acceptance checks are reusable versioned assets tied to concepts/patterns; extended by the Builder from failures, review findings and counter-claims; basis of the eval sets.
Confidence: leaf = min(verification pass fraction, evidence coverage, lowest dependent assertion confidence); parent = importance-weighted mean capped by the weakest critical child; shown with the reason it is limited. Review agreement rates are tracked per claim class and domain; the system may **propose** relaxing review for a class, only as a policy proposal that humans approve *(v1.2)*.

### 12. Answers, versions and rebuilds
An **answer is an immutable, versioned asset**: Need Spec, definitions and versions used, facts and lineage, claim graph (story and values), confidence, decision record. Follow-ups reuse answers through ontology-addressed needs, not text search. When meaning changes: old answers stay **pinned** to the versions they used; affected retained models are marked **stale** and rebuilt lazily; readers of an old answer see "meaning changed since". A **human-triggered rebuild** creates **question version n+1** and a new answer, restarting from the earliest affected step (Clarify if meaning changed, Evidence if source data changed); the old answer stays linked. Questions raised in dialogue become child or sibling questions with their own Intent Record, answered immediately from existing assets when possible.

### 13. The Builder and the flywheel
**Trigger:** after every mission. **Roles (target):** Retrospective Analyst, Change Designer, Candidate Builder, Evaluator, Promoter, Policy Proposer, Eval Curator. **Separation of duties:** the Evaluator, Eval Curator, the Promoter's gate rules and the ledger are outside the Builder's reach and change only through a human-approved path. *(v1: Retrospective, Change Designer/Candidate Builder, Evaluator and Promoter as thin agents.)*
- **Friction taxonomy** mined from handoffs (agents and humans): rework loops; information loss at handoff; redundant work; over- and under-escalation (including human overturns); agent disagreement; waste (tokens, time, queue wait); missing capability. Findings are attributed to handoffs and agent versions.
- **Change types:** agent spec (ADK), skill, tool (sandboxed code), mapping, check, modelling pattern, workflow, and **policy proposals** (review, routing, thresholds, retention weights). Proposals touching human governance are only proposals that the relevant authority approves; agent changes pass the eval gate.
- **Hypothesis record** on every change: the friction targeted, the metric expected to move and by roughly how much, and the smallest evidence that would disprove it. After promotion the realised effect is measured; if the effect does not appear in the window, the change **rolls back automatically**.
- **Eval design:** three sets — **Dev** (visible), **Promotion** (hidden), **Sealed** (operator/CI only); fresh world seeds; comparison with frozen **Baseline v0** on identical question sequences; divergence between Promotion and Sealed raises an alert. Gate: no regression on guarded metrics, better on at least one target metric within noise tolerance.
- **Guardrails (non-negotiable):** eval gate + rollback; read-only sources; spend caps with automatic halt; immutable hash-chained ledger and kill switch. The Builder cannot modify eval sets, the ledger, governance policies, the guardrails or its own gate.
- **Escaping local minima** *(designed in; v1.2)*: an exploration budget for deliberately different candidates ("scouts", offline, normal gate), periodic fresh-eyes rebuilds of a step competing with the evolved one, plateau detection that permits larger offline changes, and diverse eval worlds. The smallest-change rule governs promotion into production; exploration happens off to the side.
- **Compounding metrics** (computed from handoff and ledger data, always vs Baseline v0): (1) **rediscovery rate** (artefacts re-derived ÷ artefacts needed; reuse of lake or retained assets counts as reuse); (2) **eval pass-rate** (Promotion, and Sealed for audit; overall and per category: identification, meaning, evidence, verification, answer); (3) **human effort per mission** (clarifications, corrections, rejections, retries needing a human, minutes of human wait); (4) **cost and time per verified answer**. Change size (blast radius) is also tracked.

### 14. World model, sources and values data
**World Model** (hidden, seeded, evolving): companies/plants, departments, suppliers, materials and families, contracts and prices, POs, receipts, invoices and credit notes, payments with dates, certifications, currencies and FX, fiscal calendars. **Planted drivers** for "Why is cost of goods rising?": supplier price increase, FX movement, mix/volume shift, and data artefacts (duplicate invoices, credit-note timing, one supplier under several identifiers). The **Answer Key** is the true decomposition plus the naive distortion. v1 world is tiny (hundreds of rows); seed and size are configurable.
**Three SAP-style sims** named plainly (ECC 6.0, S/4HANA on-prem, S/4HANA Cloud), only public structures and synthetic data, non-affiliation disclaimer. All expose the same read-only **Connector interface** (list, describe, profile, sample, query, capability metadata).
**Default values** (committed in the seed; the Values Authority may change them): *Fair dealing with suppliers* (on-time payment rate; payment terms vs standard; share of disputed invoices); *Cost discipline* (price variance; off-contract spend; unit-cost trend); *Supply resilience* (single-source share; supplier concentration; top-supplier share); *Integrity and control* (duplicate payment rate; spend without a PO; vendor-master duplicates); *Responsible sourcing* (certified-supplier share; spend by region of origin). The world model generates the data these indicators need.
*(v1.1)* A minimal simulated **existing lakehouse**: one curated supplier-spend model, a supplier hierarchy, one planted defect.

### 15. Architecture
React front end; FastAPI back end with server-sent events; **Google ADK** agent definitions; **LiteLLM** gateway (any frontier or local open-weight model; BYO key; never logged); **LangGraph** durable workflows with Postgres checkpoints; Postgres (+pgvector) for state, catalogue, contracts, ontology, handoffs and ledger; DuckDB/Parquet lake behind the Lake Adapter; OpenTelemetry GenAI spans into our own schema (Phoenix optional profile); sandbox container (no network, read-only mounts, resource limits) for generated tools; `docker compose up`, one cloud VM (provider decided later); public Apache-2.0 monorepo with CI.

### 16. UI surfaces
Ask; question tree and mission board with "needs you" queues; Answer (per level, claim graph with values, lineage, follow-ups, decision record); governance queues (question, meaning workbench, mission approval, claim review with counter-claims); Builder (registry, proposals, hypotheses, promotions, rollbacks, ledger, kill switch); Metrics (four metrics vs baseline); Operator (sources, LLM providers, budgets, policies, storage space and cost); **Lineage view available for any graph in the product** (answers, claims, assertions, models, agent changes, question trees).

### 17. Security and safety (v1 posture)
Synthetic data only; sources read-only; generated code sandboxed; spend caps; ledger; kill switch; secrets never written to traces; source data treated as untrusted text; sensitivity labels in contracts restrict reads by role and agent. Known residual risk: prompt injection via free text and sandbox escape are not adversarially tested in v1.

### 18. ADRs
001 Agent runtime (ADK + LiteLLM + LangGraph) · 002 Observability (OTel → Postgres, Phoenix optional) · 003 Lake, catalogue, lineage store and table format · 004 Ontology representation and fuzzy commit model · 005 Sandbox · 006 Eval splits, baseline and hypothesis protocol · 007 Work tracking · 008 Stable core (addressing, contract schema, lineage format) and its migration path · 009 Open formats (OpenLineage, PROV-O, ontology export) · 010 Handoff schema and friction taxonomy.

---

## Testing Decisions

Good tests assert externally observable behaviour from a defined starting world, never prompts or agent wiring.
**Primary seam (single): the backend HTTP API driven by scripted scenarios** against a seeded world, with recorded LLM cassettes in CI, a small local model for smoke evals and opt-in real-model evals with a BYO key. One Playwright smoke test for the UI. Unit tests only for pure logic (world-generator invariants and answer key, confidence and vote arithmetic, policy evaluation, ledger hash chain, contract validation).
**Acceptance scenarios (v1):**
1. *Cascade*: exec question → breakdown → governance edits and accepts → missions planned as minimal sub-missions and policy-routed.
2. *Discover across three sims*, read-only (a write attempt is refused); source profiles retained and reused.
3. *Resolve-before-create*: a second question reuses a retained definition and landed facts instead of re-deriving them; contract present and complete; lineage emitted as OpenLineage.
4. *Spend conflict*: surfaced as a meaning mission; Meaning Authority ratifies; the committed assertion is reused automatically later.
5. *Answer correctness*: decomposition matches the Answer Key within tolerance; naive artefact distortion detected; confidence reflects open assumptions.
6. *Review*: claims routed to the right domain reviewers (including cross-domain claims); a counter-claim is raised and dispositioned; the answer is not released until every claim has a disposition; no provisional release.
7. *Handoffs*: every agent and human action appears as a typed handoff with outcome linkage.
8. *Flywheel*: the Builder proposes a change with a hypothesis; a worse candidate is rejected; a better one is promoted with a ledger entry; a deliberately failing hypothesis is rolled back; a candidate that games Dev but fails Promotion is not promoted; the Builder cannot alter eval sets, gate or ledger.
9. *Guardrails*: spend cap halts a mission; kill switch halts all; ledger tamper is detectable; timeout escalation reminds and re-routes but decides nothing.
10. *Compounding*: across a scripted question sequence the four metrics improve vs Baseline v0.
11. *Admin and lineage*: storage cost view and a lineage view resolve for an answer, a claim, an assertion and an agent change.
12. *Spin-up*: `docker compose up` from a clean machine reaches healthy and a scenario passes.

## Out of Scope (v1)
Everything listed in ROADMAP.md under v1.1, v1.2 and v2; real SAP/production connectors; real customer data; writing to any source; multi-tenancy and billing; non-English UI.

## Further Notes
**Demo script.** Exec asks "Why is cost of goods rising?" (decision: renegotiate or re-source?). The tree is accepted. A mission discovers across the three sims; "spend" becomes a meaning mission and is ratified. Evidence builds facts with contracts and lineage; Verify finds the duplicate-invoice and multi-vendor artefacts; domain reviewers dispose of their claims and one raises a counter-claim. The answer ships as a claim graph with values and confidence. The Builder proposes an improvement with a hypothesis, promotes it, then a bad candidate is rejected and a rollback demonstrated. A follow-up question is answered with less rediscovery and effort and lower cost than baseline.
**Risks.** Scope vs "days" (the spine is mandatory); minimal security posture while the Builder generates code; SAP names used plainly (trademark risk, disclaimer included); autonomy depends on eval quality; LLM variance in evals; unknown unknowns (build and see what emerges). Recorded gap defaults: authority arbitration by Question Governance; estimate error as friction; agent failure handling; sensitivity labels; traceability of tickets and tests to stories and decisions.
