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
| [0003](0003-lake-engine-table-format-catalogue-and-lineage-store.md) | Lake engine, table format, catalogue and lineage store | accepted | #7 |
| [0008](0008-stable-core-and-migration-path.md) | Stable core and migration path | accepted | #7 |
| [0009](0009-open-formats-openlineage-prov-o-ontology-export.md) | Open formats: OpenLineage, PROV-O, ontology export | accepted | #7 |
| [0011](0011-autonomous-build-decisions-are-logged-as-adrs.md) | Autonomous build decisions are logged as ADRs | accepted | n/a |
| [0004](0004-ontology-representation-and-fuzzy-commit-model.md) | Ontology representation and fuzzy commit model | accepted | #8 |
| [0012](0012-skeleton-stack-and-repo-layout.md) | Skeleton stack and repo layout | accepted | #4 |
| [0013](0013-health-endpoint-contract.md) | Health endpoint contract | accepted | #4 |
| [0014](0014-ci-on-github-actions.md) | CI on GitHub Actions | accepted | #4 |
