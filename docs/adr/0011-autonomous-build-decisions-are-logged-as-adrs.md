# 0011: Autonomous build decisions are logged as ADRs

- Status: accepted
- Date: 2026-11-21
- Ticket: n/a (process decision made after publishing the 105-ticket backlog)
- Decided by: owner

## Context
The v1 backlog is 105 small tickets, each meant for a fresh agent session. Stopping to ask the owner at every ambiguity would stall the chain and defeat the point of fine-grained tickets.

## Decision
Agents implement tickets autonomously. When a ticket needs a choice the spec does not settle, the agent decides and records the decision as an ADR in `docs/adr/` in the same change. The owner reviews the log afterwards. Hard limits (the owner's own accounts, money, irreversible actions outside the repo, `ready-for-human` tickets) still stop for the owner.

## Alternatives considered
- Ask the owner per decision: slow, blocks parallel sessions.
- Decide silently: unreviewable; later sessions cannot see why.
- Put decisions in ticket comments: scattered; not versioned with the code.

## Consequences
Decisions are reviewable in one place and versioned with the code. Later sessions read the log before working in an area. Any ADR can be superseded by a new one if the owner disagrees.
