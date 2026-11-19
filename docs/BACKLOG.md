# AutoQ — v1 Backlog (dependency-ordered)

Work tracking recommendation: GitHub Issues + Projects in `edsykes/AutoQ`, specs/ADRs in `docs/`. Each item below becomes an issue; "after" = dependency. Items with no unmet dependency can run in parallel sessions.

## Wave 0 — foundations (sequential, small)
- W0.1 Install tooling (gh, Docker/Colima) and `gh auth login` (owner). Create public repo `edsykes/AutoQ`, Apache-2.0, README, CI skeleton.
- W0.2 Repo scaffold: monorepo layout (`apps/api`, `apps/web`, `packages/worldgen`, `packages/agents`, `deploy/`), compose skeleton, Postgres.
- W0.3 ADRs 001–007 (short).

## Wave 1 — parallel streams (after W0.2)
- A. **World model + SAP sims**: world generator (seeded, evolving, planted COGS drivers, org politics, "spend" definitions), ECC / S4 on-prem / S4 Cloud renderers, connector interface, answer-key generator, eval-set generator (dev/promotion/sealed).
- B. **Core backend**: domain model (question tree, mission contract, answer, decision record), roles/local auth, policy engine for mission approval, API.
- C. **Observability & ledger**: OTel GenAI spans → Postgres schema; append-only audit ledger; kill switch; spend caps.
- D. **UI shell**: Ask, question tree/mission board, governance queues (static data first).
- E. **LLM gateway**: LiteLLM config, BYO key settings, cassette recorder/replayer for CI.

## Wave 2 — loop (after A, B, C, E)
- F. v0 agents (ADK) for Frame, Discover, Clarify, Evidence, Verify, Answer; LangGraph mission workflow with checkpoints.
- G. Ontology store + confidence/commit policies (authority, vote, evidence) + meaning workbench API (after ADR-004).
- H. Lakehouse path: lake-exists/data-present check, landing, mapping and fact building.
- I. Answer renderer per altitude + confidence roll-up.

## Wave 3 — flywheel (after F, G, H)
- J. Retrospective + Builder agent; agent/skill registry with versions.
- K. Eval gate (three-way split, v0 baseline), promotion, rollback.
- L. Sandbox runtime for generated code (ADR-005).
- M. Metrics page (rediscovery, pass-rate, human effort, cost/time).

## Wave 4 — prove and ship (after Wave 3)
- N. Scripted demo: exec question → cascade → mission → "spend" conflict ratified → follow-up question measurably better; rollback demo.
- O. Compose verification on clean machine; docs; cloud VM deploy (BYO key); live instance.
- P. Post-v1: planted-injection evals, Helm, OIDC, notebook viz, adversarial steward, shadow commits, threat model.
