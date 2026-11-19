# Handoff for the next session

Read this first, then `CLAUDE.md`. **`docs/SPEC.md` is authoritative**; this file explains how we got here and what to do next. Do not re-derive or rewrite the spec.

## State (2026-11-19)
- Repo: https://github.com/edsykes/AutoQ (public, Apache-2.0). Docs only; no code yet.
- Written: `docs/SPEC.md` (v1 spine), `GLOSSARY.md`, `docs/ROADMAP.md`, `docs/BACKLOG.md` (17 draft tickets), `CLAUDE.md`, `docs/agents/*` (GitHub issue tracker, default triage labels, single-context domain docs).
- Not done: no GitHub issues published; no ADRs written; no code; no Docker; no cloud chosen.
- Tooling: `gh` is at `~/.local/bin/gh` (logged in as `edsykes`); put `~/.local/bin` on PATH. Docker, Helm, Terraform not installed. No Homebrew.
- Origin: talk "The exponential data organisation" (Data Berlin, 3 Nov 2026), Google Drive deck "Exponential Data Org Data Berlin 03.11.2026" and outline doc "The expoential Data organization: data berlin".

## What to do next
1. Publish `docs/SPEC.md` as a GitHub issue (label `ready-for-agent`). It is already in the `to-spec` template; publish as is.
2. Run `/to-tickets <spec issue number>`; start from `docs/BACKLOG.md`. Show the breakdown for approval before publishing, with native blocking links.
3. Start the unblocked tickets in parallel: 1 (skeleton), 2 (ADRs), 3 (world model + first sim), 16 (Docker + cloud choice, owner action; use `wizard`).
4. Use `/implement` per ticket (TDD, code-review). Use `/wayfinder` or `research`/`prototype` for ADR unknowns.

## The product in one paragraph
AutoQ is a self-hostable, LLM-agnostic altitude-5 harness. Execs ask a question with its intent; a Question Governance Authority approves a breakdown into VP and analyst questions; leaf questions become missions run by agents through six steps (Frame, Discover, Clarify, Evidence, Verify, Answer); meaning conflicts go to a Meaning Authority and a fuzzy ontology; answers are claim graphs reviewed by humans per domain; a Builder mines every agent/human handoff for friction, proposes the smallest change with a hypothesis, and promotes it behind a hidden eval gate with rollback.

## Decision log (why)
| Decision | Why |
|---|---|
| Product anyone can spin up; BYO key; any LLM; open source (ADK, LiteLLM, LangGraph, Postgres, DuckDB) | Owner wants a reusable product, not a client deployment |
| Three SAP-style sims (ECC 6.0, S/4 on-prem, S/4 Cloud), views of one hidden world model, with org politics | Realistic meaning conflicts; ground truth from the world model |
| Procure-to-pay; seed question "Why is cost of goods rising?"; conflict "spend" | Fits VP procurement/finance personas and the talk's examples |
| Flywheel is the star; baseline loop shipped so there is something to improve | Altitude 5 = build the system that builds the loops |
| Fully autonomous promotion, but eval gate + rollback, read-only sources, spend caps, ledger + kill switch | Owner chose autonomy; guardrails made non-negotiable |
| Human review of answers always required; no proxy decisions on timeout (agents only remind/re-route) | Owner decision: no auto-commit at this stage |
| Three human authorities + Mission Approver: Question Governance, Meaning, Values | Talk's "Beyond Engineering": humans govern what is worth asking, what it means, what is valued |
| No prescribed data model (not Kimball/mesh); mandate a machine-managed contract; structure emerges | Agents see the question first; old "load everything" assumed unknown questions |
| Definition is the durable asset; data is a rebuildable materialisation | Meaning changes should trigger re-derivation, not migration |
| Retention by earned keep and net value; storage is cheap so size is not the criterion | Owner: carrying cost is re-check effort, staleness, discovery noise |
| Minimal per-mission landing; keep all snapshots; admin sees space and cost | Reproducibility; owner wants cost visibility |
| Keys bind to ontology entities; identity links by a matching agent | Same supplier appears under several IDs across systems |
| Existing lake = fourth system of facts, read-only, trust earned per model; lake meaning arrives as proposals | Owner: it can save effort and can contradict meaning |
| Resolve-before-create via a Need Spec; change as little as possible; sub-missions change one asset | Owner: changes must be small |
| Stories are claim graphs; review by claim and domain; counter-claims; values linked via indicators | Owner: humans must be able to add counter-claims; values must show up |
| Every agent and human handoff is recorded; friction taxonomy; hypotheses; rollback if effect absent | Owner: learning loop must watch agents and humans together |
| Open formats: OpenLineage, PROV-O; lineage view for any graph | Owner decision |
| v1 is a thin spine; sophistication in ROADMAP (v1.1/v1.2/v2) | "Days" timeline; owner asked for the smallest slice |
| Security posture minimal in v1; SAP names used plainly | Owner decisions; risks recorded in SPEC |

## Open items
- Cloud provider and account for the live instance (BYO LLM key only on the hosted instance).
- Write ADR-001 to ADR-010 (list in SPEC §18). ADR-004 (ontology form) and ADR-003 (table format, lineage store) block tickets 7 and 9.
- The first build will show what is missing; expect the spec to change.
