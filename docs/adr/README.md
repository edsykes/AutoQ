# ADR log

Every non-trivial decision made while building AutoQ is recorded here, one file per decision, named `NNNN-short-title.md`.

## Autonomy policy (owner decision, 2026-11-21)

For build tickets, agents work **fully autonomously**: they do not stop to ask the owner for choices. Instead they make the most sensible decision, record it as an ADR in this folder, and carry on.

- **Record, don't ask.** If a ticket forces a choice the spec doesn't settle (library, schema shape, naming, trade-off, ambiguity in acceptance criteria), decide and write an ADR in the same change as the code.
- **Small or reversible choices** get a short ADR (a few lines). Don't skip them: the log is how the owner reviews autonomous decisions afterwards.
- **Respect existing ADRs and the spec** (`docs/SPEC.md`, issue #1). If a decision contradicts one, say so explicitly in the new ADR and why.
- **Still stop for the hard limits** that autonomy does not cover: actions needing the owner's own accounts or credentials, spending money, destructive or irreversible actions outside the repo, and the two `ready-for-human` tickets.
- Use the terms in `GLOSSARY.md`.

## Numbering

`0001`–`0010` are reserved for the ten ADRs the spec plans (SPEC.md section 18, tickets 5–8): 0001 agent runtime, 0002 observability, 0003 lake/catalogue/lineage store/table format, 0004 ontology representation and fuzzy commit, 0005 sandbox, 0006 eval splits/baseline/hypothesis protocol, 0007 work tracking, 0008 stable core and migration path, 0009 open formats, 0010 handoff schema and friction taxonomy.
Autonomous decisions made during the build start at `0011` and continue upward.

## ADR format

```markdown
# NNNN: Title

- Status: accepted | superseded by NNNN | reverted
- Date: YYYY-MM-DD
- Ticket: #<issue>
- Decided by: agent (autonomous) | owner

## Context
What forced the decision.

## Decision
What was chosen.

## Alternatives considered
Short list with why not.

## Consequences
What this makes easier or harder, and how to reverse it.
```

## Index

| ADR | Title | Status | Ticket |
|---|---|---|---|
| [0006](0006-eval-splits-baseline-and-hypothesis-protocol.md) | Eval splits, Baseline v0 and the hypothesis protocol | accepted | #9 |
| [0007](0007-work-tracking.md) | Work tracking | accepted | #9 |
| [0010](0010-handoff-schema-and-friction-taxonomy.md) | Handoff schema and friction taxonomy | accepted | #9 |
| [0011](0011-autonomous-build-decisions-are-logged-as-adrs.md) | Autonomous build decisions are logged as ADRs | accepted | n/a |
