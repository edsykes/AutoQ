# 0008: Stable core (addressing, contract schema, lineage format) and its migration path

- Status: accepted
- Date: 2026-11-21
- Ticket: #7
- Decided by: agent (autonomous)

## Context
SPEC section 5 names three things as the **stable core**: the addressing scheme (definition, version, snapshot), the Contract schema and the lineage format. Everything else (zone layout, retention weights, shape patterns) is changeable policy the Builder may propose. Contract, lake and lineage tickets need these fixed now. Changes need a human-approved path where the **Operator approves**, the approval is written to the ledger and the migration is replay-tested first (US 27a). The Builder must not be able to change the core.

## Decision

### 1. Addressing scheme (stable core, version `core/1`)
Every governed object has an immutable **address**, a URI of the form `aq:<kind>/<path>`. Addresses are never reused and never mutated; a "change" is a new address.

| Kind | Address | Notes |
|---|---|---|
| Definition | `aq:def/<domain>.<name>` | e.g. `aq:def/finance.spend`. Slug `[a-z][a-z0-9_]*` per segment, domain in {`procurement`,`finance`,`plants`,`core`, ...}. Identity of the Definition across versions. |
| Definition version | `aq:def/<domain>.<name>@<n>` | `n` is a positive integer, monotonic, gap-free, assigned by the catalogue. Each version is immutable once committed. |
| Snapshot | `aq:snap/<source>/<asof>/<hash>` | `source` = connector id slug (`ecc`, `s4onprem`, `s4cloud`); `asof` = UTC instant `YYYYMMDDTHHMMSSZ` the source was read; `hash` = `sha256-` plus first 16 hex of the SHA-256 over the canonical content digest of the landed files. Same content and same as-of give the same address, so re-landing is idempotent. |
| Materialisation | `aq:mat/<domain>.<name>@<n>/<build>` | `build` is a ULID. A Definition version can have many builds (rebuilds); each is a cache entry. Reproducible rebuild is verified by comparing content hashes. |
| Mapping version | `aq:map/<source>.<object>@<n>` | Source mapping layer entries. |
| Answer | `aq:ans/<ulid>` | Immutable; question versions are distinct ULIDs linked from the Question. |
| Assertion version | `aq:asr/<ulid>@<n>` | Ontology assertions (ADR-0004 owns their content). |
| Agent version | `aq:agent/<name>@<n>` | Used in lineage and ledger. |

Rules: addresses are case-sensitive, ASCII, at most 255 characters. The catalogue is the only allocator of version numbers and builds. The physical path of a materialisation is derived from its address (`/` and `@` mapped per ADR-0003) but physical layout is **not** part of the core. References between objects always store full addresses. Resolve-before-create looks up by `(concept, entity, grain, scope)` attributes on the Definition, then yields an address.

### 2. Contract schema (stable core)
The Contract is one JSON document per materialisation (and per Definition version for the static parts), validated by JSON Schema 2020-12, stored in Postgres as `jsonb` with the schema version on every record. Fields (required unless marked optional):

```
contract_schema: "autoq.contract/1"
address:        aq:mat/...                      # the materialisation described
definition:     { ref: aq:def/...@n }
grain:          [ {entity: <ontology entity ref>, attribute: <column>} ... ]   # what one row is
keys:           [ {column, entity: <ontology entity ref>} ... ]                # entity-bound keys
measures:       [ {column, concept: <ontology concept ref>, assertion: aq:asr/...@n, unit, aggregation} ... ]
columns:        [ {name, type, nullable} ... ]                                 # physical schema
time:           { semantics: as_of|period|event, column?, period_grain?, freshness_sla?, source_asof: [aq:snap/...] }
lineage:        { inputs: [address ...], transformation: {ref, version, code_hash}, run: <run id> }
checks:         { declared: [ {id: aq:chk/...@n, kind, params} ], latest: [ {id, result: pass|fail|error, at, evidence_ref} ] }
status:         scratch|retained|trusted|stale|deprecated|quarantined          # derived, see rules
steward:        { agent: aq:agent/...@n, policy_ref }
sensitivity:    public|internal|restricted|secret                              # plus optional per-column overrides
economics:      { rebuild_cost: {tokens, seconds, usd}, reuse_count, last_used_at, carrying_cost? }
retention:      { score?: number, weights_ref?: <policy version>, scored_at? }  # v1 keeps everything; v1.2 computes
reproducibility:{ snapshots: [...], definition_versions: [...], mapping_versions: [...], agent_versions: [...], content_hash }
scope:          { mission?: <id>, zone: snapshots|scratch|retained|quarantine }
created_at, created_by
```

Rules the contract tickets implement: (a) a model with an incomplete contract (any required field absent or invalid) cannot leave `scratch`; (b) `status=trusted` is only ever set by the mechanical derivation (every concept committed above threshold, checks pass, replay reproduces `content_hash`), never by a human or by the writing agent; (c) `zone` always follows `status`; (d) the contract is immutable apart from the mutable block `{checks.latest, status, economics, retention, scope.zone}`, and each change to that block appends a history row.

### 3. Lineage format (stable core)
Lineage is an append-only set of edges, one per (output, input) pair per run:

```
lineage_format: "autoq.lineage/1"
edge_id:       ULID
from:          address     # input (snapshot, materialisation, mapping, definition version, check, agent version)
to:            address     # output (materialisation, answer, claim, assertion ...)
relation:      derived_from | mapped_by | validated_by | produced_by_agent | superseded_by | identity_link
transformation:{ ref, version, code_hash }
run:           { id, mission_id, step_run_id }
recorded_at:   UTC instant
```

Edges are never updated or deleted (a correction is a new edge with `relation=superseded_by` or a newer run). Impact analysis walks `from -> to`; replay walks `to -> from`. This relational format maps one-to-one to OpenLineage and PROV-O exports (ADR-0009), so exports are generated views, never the source of truth.

### 4. Versioning of the core and the migration path
- The core as a whole carries a **core version** `core/N` (integer), stored in the catalogue (`stable_core(version, adopted_at, approval_ledger_id)`). The three parts also carry their own tags (`autoq.contract/1`, `autoq.lineage/1`, address scheme `core/1`) on every record.
- **Compatible (additive) changes within a version** are allowed without migration only for optional contract fields and new address kinds; they are still a core change and follow steps 1-4 below with a lighter replay test. **Anything else is a new version** `N+1`: removing or renaming a field, changing a required field's meaning, changing an address grammar, changing an edge's meaning.
- **Approval path (all of it mandatory, in order):**
  1. **Proposal.** Anyone (human or agent, including the Builder) files a *Stable Core Change Proposal*: what changes, why, affected records, rollback plan, and a migration script with a down path. The Builder may only propose; it has no write path to core definitions, schemas or the migration runner (separation of duties, SPEC section 13).
  2. **Replay test.** CI applies the migration to a clone of the catalogue and replays a defined sample (all trusted materialisations and every stored Answer) from recorded snapshots; results must reproduce hashes and numbers exactly, and old-address resolution must still work. The test report is attached to the proposal.
  3. **Operator approval.** The Operator approves explicitly, with the test report in view. The approval (who, what, hashes of proposal and report) is written to the Audit Ledger *before* the migration runs.
  4. **Migration.** Runs in one catalogue transaction; keeps **dual-read** of `N` and `N+1` for one release; old addresses stay valid (an address-alias table maps old to new; physical files are not rewritten unless the proposal says so).
  5. **Rollback.** The down migration is tested in step 2 and remains available until dual-read ends.
- Everything outside the core (zone layout, retention weights, shape patterns, physical file layout, check library contents) is changeable policy that passes the normal eval gate and never needs this path.

## Alternatives considered
- **Content-hash-only addresses** (no human-readable names): robust identity, unusable for people and for ontology-addressed lookup. Hashes are kept for snapshots and builds where they are the point.
- **UUIDs for definitions**: stable but opaque; the slug is also the lookup key in resolve-before-create. Slugs are immutable and never reused, so they give the same stability.
- **Semantic versions for definitions** (`1.2.0`): compatibility class is tracked by the smallest-change rule and replay of dependants, not encoded in the number; plain integers avoid false promises.
- **Mutable contracts with free-form fields**: rejected; the spec requires machines to reason over contracts, so shape must be validated and versioned.
- **Lineage in a graph store**: see ADR-0003.
- **Multi-party approval** for core changes: US 27a names the Operator; one approver plus a ledger entry and a mandatory replay test is enough for v1.

## Consequences
- Easier: later tickets have a concrete grammar and field list; replay and impact analysis are mechanical; exports are generated.
- Harder: every core change is slow and gated by design; we must maintain the alias table and a replay test suite from the start.
- Reversal: this ADR itself can be superseded only through the path in section 4. Field-level details inside `economics` and `retention` (optional blocks) may evolve additively.
- Downstream: contract, lake, lineage and ledger tickets implement these schemas; the ADR for ontology (0004) defines concept and assertion references used here.
