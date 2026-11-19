# AutoQ Glossary

Canonical terms. Use these words in code, issues, tests and docs. "Avoid" lists drifting synonyms.

## Organisation and authority

- **Altitude** (of an improvement): the reach of an improvement. Five levels from the talk: 1 Personal productivity, 2 Personal agent team, 3 Shared agent team, 4 Agentic delivery workflows, 5 Engineering the delivery system. AutoQ is altitude 5.
- **Asker level**: the organisational level of a person asking or receiving an answer: **Exec**, **VP**, **Analyst**. Determines answer rendering. _Avoid: "altitude" for this._
- **Authority**: a human role with a decision gate. Three: **Question Governance Authority**, **Meaning Authority**, **Mission Approver**. An authority decides; agents propose.
- **Operator**: administers the deployment (LLM providers, budgets, policies, kill switch). Not an authority over business content.

## Questions and missions

- **Question**: a business question with its **Intent** (the decision it informs and why it is asked). Questions form a **Question Tree**.
- **Question Tree**: Exec question → VP questions → Analyst (leaf) questions.
- **Leaf Question**: a question with no children; the only kind that gets Missions.
- **Mission**: a bounded, verifiable unit of agent work attached to a Leaf Question, defined by a **Mission Contract**. One Question = 1+ Missions. _Avoid: task, job, run._
- **Mission Contract**: goal, inputs/sources, acceptance checks, budget, risk class, approver, assigned agent versions.
- **Approval Policy**: rules that auto-approve or route a Mission to a Mission Approver by estimated cost and risk.
- **Loop**: the six steps a Mission executes: **Frame, Discover, Clarify, Evidence, Verify, Answer**. Steps can be revisited.
- **Step Run**: one execution of one Loop step within a Mission.
- **Answer**: the verified result for a Question, with **Confidence**, assumptions, lineage and meaning choices. Rendered per Asker level.
- **Decision Record**: the decision an Answer informed, and later its outcome.

## Meaning

- **Concept**: a named business meaning (e.g. Spend, Supplier, Late Delivery).
- **Assertion**: a statement in the Ontology (e.g. "Finance-Spend := posted invoice value net of credit notes") with Confidence, provenance, version and status.
- **Ontology**: the versioned, fuzzy set of Concepts and Assertions. _Avoid: knowledge base, company brain (informal only)._
- **Conflict Case**: a detected difference in meaning of a Concept across Departments or Source Systems, with options and evidence.
- **Commit Policy**: per-Concept rule for how an Assertion becomes committed: **Authority**, **Vote**, or **Evidence-weighted**.
- **Confidence**: 0..1 degree of support for an Assertion or Answer.
- **Department**: Procurement, Finance, Plants (v1). Holders of legitimately different definitions.

## Data

- **Source System**: an external system read through a **Connector**. v1: three simulated SAP-style systems (**ECC-style, S4-OnPrem-style, S4-Cloud-style**). Always read-only.
- **World Model**: the hidden simulated company truth from which each Source System is a lossy, convention-skewed view.
- **Answer Key**: ground truth derived from the World Model for a question.
- **Planted Driver**: a deliberately hidden cause in the World Model (price increase, FX, mix shift, data artefacts).
- **Lake**: the optional lakehouse into which Evidence data is landed, only when a Mission needs it.
- **Fact**: a derived, verifiable data product used as Evidence, with lineage.

## Flywheel

- **Flywheel**: after every Mission, the Builder runs Build & test → Verified learning → Improve the builder.
- **Builder**: the agent system that creates and improves agents, skills, mappings and tests.
- **Agent**: a versioned Google ADK definition (instructions, tools, skills, memory scope, evals). **Skill**: reusable know-how. **Tool**: callable capability (including sandboxed generated code).
- **Improvement Proposal**: a candidate change to Agents/Skills/Mappings with its evidence.
- **Eval Suite**: the three sets **Dev** (Builder-visible), **Promotion** (hidden from Builder), **Sealed** (operator/CI only).
- **Promotion**: making a candidate version live after passing the Eval Gate. **Rollback**: restoring the prior version.
- **Baseline (v0)**: the frozen first agent set, the control for compounding metrics.
- **Guardrails**: Eval Gate + rollback, read-only sources, spend caps, immutable Audit Ledger + Kill Switch.
- **Audit Ledger**: append-only record of every autonomous change and decision, derived from trace data.
- **Compounding Metrics**: Rediscovery Rate, Eval Pass-rate, Human Effort per Mission, Cost and Time per Verified Answer.

## Data architecture (added 2026-11-19)

- **Definition**: a governed measure or entity bound to ontology concepts, with grain, scope and version. The durable asset. _Avoid: table, dataset, as the unit of value._
- **Materialisation**: a rebuildable physical realisation of a Definition. A cache.
- **Contract**: the machine-managed record every stored model must carry (definition ref, grain, entity-bound keys, concept-bound measures, time and lineage, checks, status, steward, sensitivity, economics, retention score). Written and read by agents.
- **Status**: scratch, retained, trusted, stale, deprecated, quarantined. **Trusted** is derived mechanically, never signed off by a human.
- **Retention score**: blend of expected reuse, rebuild savings and trust against carrying cost (re-check effort, staleness and conflict risk, discovery noise, reproducibility burden). Weights are evaluated policy.
- **Lifecycle zones**: Snapshots, Scratch, Retained, Quarantine. Logical, follow Status, not modelling shape.
- **Snapshot**: immutable as-of-stamped minimal landing from a source. All kept by default.
- **Lake Adapter**: swappable interface to the physical lake engine (DuckDB over Parquet in v1).
- **Need Spec**: the Definitions a question needs, in ontology terms. Output of Frame.
- **Resolve-before-create**: every step looks for an existing asset satisfying a need before creating one.
- **Identity link**: governed, confidence-bearing statement that several source identifiers are one entity. Produced by the **Matching agent**.
- **Source mapping layer**: agent-governed mapping of source fields to ontology concepts. Distinct from the human-governed business ontology.
- **Stable core**: addressing scheme (definition, version, snapshot), Contract schema and lineage format. Versioned and changed only via a human-approved path.
- **Remediation rule**: governed versioned Definition that fixes a factual data defect inside our lake. Never edits a source.
- **Blast radius**: number of dependants affected by a change, estimated from lineage.
- **Sub-mission**: smallest unit of a mission; changes exactly one governed asset.

## Meaning, purpose and values

- **Ontology partitions**: **Meaning** (Meaning Authority), **Purpose** (Question Governance Authority), **Values** (Values Authority).
- **Values Authority**: fourth human authority; commits values and indicators.
- **Intent Record**: decision, stakes, audience and constraints behind a question; links into the Purpose partition.
- **Meaning mission**: a mission whose goal is to create or resolve an ontology item.
- **Sensitivity check**: measure of how much an answer changes under each candidate meaning.
- **Semantic vs factual conflict**: same word different meanings (Meaning Authority) vs same meaning different numbers (data owner, agent remediation).
- **Reuse verdict**: reuse as-is, reuse with adjustments, or do not reuse.

## Stories and review

- **Claim graph**: the story as claims linked to facts, lineage, values and rejected counter-stories.
- **Evidence-backed vs human-asserted claim**: the latter is labelled with author and basis and never rendered as fact.
- **Counter-claim**: reviewer claim with evidence not connected at fact level; outcomes resolved-by-evidence, included, rejected, deferred.
- **Claim routing**: each claim is reviewed by the reviewer of every domain it touches. Review is always required.
- **Check library**: growing versioned acceptance checks; basis of the eval sets.
- **Question version**: a human-triggered rebuild creates version n+1 with a new Answer; the old one stays linked.

## Flywheel

- **Handoff**: typed record of any agent or human interaction, with decision, rationale, alternatives and downstream outcome.
- **Friction taxonomy**: rework loops, information loss, redundant work, over/under-escalation, disagreement, waste, missing capability.
- **Hypothesis record**: friction targeted, metric expected to move, evidence that would disprove it; monitored after promotion.
- **Scout / fresh-eyes rebuild / plateau detection**: exploration mechanisms against local minima (v1.2).
