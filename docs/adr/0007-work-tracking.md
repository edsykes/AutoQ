# 0007: Work tracking

- Status: accepted
- Date: 2026-11-21
- Ticket: #9
- Decided by: agent (autonomous)

## Context
SPEC.md names ADR 0007 "Work tracking" without detailing it. Two kinds of work need tracking and must not be confused: (a) **product work**: Questions, Missions, sub-missions and Step Runs inside AutoQ, shown on the mission board with "needs you" queues, and (b) **build work**: the tickets that build AutoQ (GitHub Issues under #1). Both need traceability (SPEC Further Notes: tickets list the user stories and scenarios they satisfy).

## Decision

### Product work
- **Postgres is the system of record** for work state; LangGraph checkpoints hold only execution internals and are never read to answer "what state is this mission in".
- Tables: `question`, `mission`, `sub_mission`, `step_run`, `queue_item`. Each row has `id`, `parent_id`, `status`, `version`, timestamps and `contract_ref`/`handoff_ref` where relevant.
- Mission status machine: `proposed -> awaiting_approval -> approved -> running -> (blocked_on_human | verifying) -> answered | failed | cancelled`. `blocked_on_human` carries a diagnosis and an assigned authority or role. Transitions are only made through one service function that writes a handoff (ADR 0010) and a ledger entry for every transition.
- Step Runs record Loop step (Frame, Discover, Clarify, Evidence, Verify, Answer), attempt number, agent version, cost and timing, so revisits are visible and countable.
- **Needs-you queues** are a query over `queue_item` (assignee role/authority, due time, reminded-at, rerouted-at). v1 escalation: remind, then re-route to the operator (SPEC 3); timestamps of each are stored.
- Work is never deleted: cancelled and failed rows stay, since records are kept forever in v1.

### Build work
- GitHub Issues under #1 remain the build tracker. Each ticket states the user stories and acceptance scenarios it satisfies; tests reference them with a marker (`# covers: US28, S7`) so a script can check story coverage.
- Autonomous decisions are ADRs per `docs/adr/README.md`; a ticket's PR links its ADRs.
- No second tracker (no Jira, no in-repo TODO database) in v1.

## Alternatives considered
- Derive state from LangGraph checkpoints: couples product queries to library internals.
- Event-sourcing only: heavier than needed; handoffs and ledger already give an append-only history.
- External tracker for product work: duplicates state and breaks the no-side-channels rule.

## Consequences
Mission board, queues and metrics read plain SQL. State changes are centralised, so audit and friction mining see every transition. Reverse by replacing the service function's storage; the status vocabulary is the contract.
