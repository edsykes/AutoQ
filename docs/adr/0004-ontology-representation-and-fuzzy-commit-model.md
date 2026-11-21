# 0004: Ontology representation and fuzzy commit model

- Status: accepted
- Date: 2026-11-21
- Ticket: #8
- Decided by: agent (autonomous)

## Context

SPEC.md section 8 defines the Ontology as the versioned, fuzzy set of Concepts and Assertions, in three partitions (Meaning, Purpose, Values), with a Commit Policy per Concept (authority, vote, evidence-weighted). v1 is authority-only; vote and evidence-weighted are v1.1. Spec section 10 says operational records live in Postgres. The ontology-core ticket (#45) needs a concrete schema, commit semantics and export form. The spec does not fix those, so this ADR does.

Requirements that drive the shape:
- Meaning is legitimately different per Department ("spend" differs in Procurement, Finance and Plants). Different committed definitions must coexist, scoped by domain, without being a conflict by themselves.
- Everything an agent proposes (definitions, relations, hierarchy edges, identity links, source mappings) must carry confidence, status, provenance and version, and be committed only by the owning authority.
- Commit must be pluggable: v1 authority-only now, vote and evidence-weighted later, without a schema migration.
- The ontology must be exportable in an open, diffable form (ADR 0009 covers open formats generally; this ADR fixes the ontology's export shape).

## Decision

### 1. One generic Assertion table; Concepts are stable identities

Postgres schema `ontology`. A **Concept** is only a stable identity plus governance metadata. Its name, definition, relations and hierarchy position are all **Assertions**. This keeps the "fuzzy, versioned, per-scope" semantics in one place.

```sql
CREATE TYPE ontology.partition AS ENUM ('meaning','purpose','values');
CREATE TYPE ontology.assertion_kind AS ENUM
  ('label','definition','relation','identity_link','source_mapping','indicator');
CREATE TYPE ontology.assertion_status AS ENUM
  ('proposed','committed','contested','deprecated');

CREATE TABLE ontology.domain (          -- Procurement, Finance, Plants, plus 'enterprise' (cross-domain)
  id text PRIMARY KEY, name text NOT NULL
);

CREATE TABLE ontology.concept (
  id           uuid PRIMARY KEY,
  slug         text NOT NULL UNIQUE,                 -- stable, kebab-case, e.g. 'spend', 'supplier'
  partition    ontology.partition NOT NULL DEFAULT 'meaning',  -- 'purpose' unused in v1 (v1.2)
  domain_id    text NOT NULL REFERENCES ontology.domain(id),   -- owning domain; drives review routing
  commit_policy jsonb NOT NULL DEFAULT '{"kind":"authority"}', -- see section 3
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE ontology.assertion (
  id            uuid PRIMARY KEY,
  key           uuid NOT NULL,                       -- logical assertion identity, shared by all its versions
  version       int  NOT NULL,                       -- 1,2,3... per key; content rows are immutable
  kind          ontology.assertion_kind NOT NULL,
  subject_id    uuid NOT NULL REFERENCES ontology.concept(id),
  predicate     text,                                -- controlled vocabulary for kind='relation' (below)
  object_id     uuid REFERENCES ontology.concept(id),-- concept-valued objects
  object_value  jsonb,                               -- literals / structured payloads (see kinds)
  statement     text NOT NULL,                       -- human-readable statement, always present
  scope         jsonb NOT NULL DEFAULT '{}',         -- {"domain":"finance","source_system":"s4-cloud","valid_from":..}
  scope_key     text NOT NULL,                       -- canonical, sorted rendering of scope, e.g. 'domain=finance'
  confidence    numeric(4,3) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  status        ontology.assertion_status NOT NULL DEFAULT 'proposed',
  provenance    jsonb NOT NULL,                      -- section 2
  supersedes_id uuid REFERENCES ontology.assertion(id),
  committed_in  int,                                 -- ontology release number (section 4), null until committed
  deprecated_in int,                                 -- release in which it stopped being live, null while live
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (key, version)
);
-- One committed definition per concept per scope; other domains hold their own scope_key.
CREATE UNIQUE INDEX one_committed_definition ON ontology.assertion (subject_id, scope_key)
  WHERE kind = 'definition' AND status = 'committed';
-- At most one live (not deprecated) version per key
CREATE UNIQUE INDEX one_live_version ON ontology.assertion (key) WHERE status <> 'deprecated';

CREATE TABLE ontology.assertion_event (   -- append-only transition log; feeds the Audit Ledger
  id bigserial PRIMARY KEY, assertion_id uuid NOT NULL REFERENCES ontology.assertion(id),
  at timestamptz NOT NULL DEFAULT now(), actor text NOT NULL,   -- agent version or human id
  from_status ontology.assertion_status, to_status ontology.assertion_status NOT NULL,
  handoff_id uuid, note text
);

CREATE TABLE ontology.release (           -- one row per commit-affecting change set
  number serial PRIMARY KEY, at timestamptz NOT NULL DEFAULT now(), actor text NOT NULL, note text
);

CREATE TABLE ontology.conflict_case (
  id uuid PRIMARY KEY,
  concept_id uuid NOT NULL REFERENCES ontology.concept(id),
  type text NOT NULL CHECK (type IN ('semantic','factual')),   -- v1: factual detected and flagged only
  assertion_ids uuid[] NOT NULL,            -- the competing assertions
  options jsonb NOT NULL, evidence jsonb NOT NULL,
  status text NOT NULL CHECK (status IN ('open','resolved_reconcile','resolved_keep_distinct','deferred')),
  mission_id uuid                           -- the meaning mission, if spawned
);
```

Rules:
- **Assertion rows are immutable except `status` and `committed_in`.** A change creates a new row with `version+1`, `supersedes_id` set; committing it deprecates the superseded version in the same transaction. Every status change writes an `assertion_event`. Triggers enforce this; application code goes through one `ontology` module (the only writer).
- **Confidence** is 0..1, set by the proposer, never silently rewritten. A commit does not set it to 1; it records the degree of support at commit time. In v1 confidence is information (displayed, propagated into Answer confidence, used for the auto-resolve threshold, default 0.8), **not** a commit gate.
- **Status machine:** `proposed → committed`, `proposed → deprecated` (rejected/withdrawn), `committed → contested` (a reviewer or agent raises a challenge, opens a Conflict Case), `contested → committed` (upheld, or a new version commits) or `→ deprecated`, `committed → deprecated` (superseded or retired). Only `committed` assertions are used to auto-resolve meaning. `contested` assertions are still served but flagged, and a Mission using them is told so.
- **Provenance** (jsonb, required keys): `proposed_by` (agent version or human id), `mission_id`, `step_run_id`, `handoff_id`, `basis` (`agent_inference | human_asserted | seed | imported`), `evidence` (array of refs: Fact ids, lineage nodes, source rows, documents), `derived_from` (assertion ids). Maps to PROV-O on export.

### 2. What each kind represents

| Need | Representation |
|---|---|
| Concept naming | `label` assertion (`object_value` = `{"text","lang"}`); alt labels allowed as further `label` assertions |
| Definition | `definition` assertion; `statement` is the definition; `scope` carries the department. e.g. Finance-Spend := posted invoice value net of credit notes |
| Relation | `relation` with `predicate` from a controlled list and `object_id`. v1 list: `broader` (hierarchy, SKOS), `part_of`, `related`, `measure_of`, `depends_on`, `same_as_concept`, `different_from`, `indicator_of`, `bears_on_value` |
| Hierarchy | `relation` with `predicate='broader'` (child → parent). Cycles forbidden by a check in the module at commit time. Transitive queries use a recursive CTE over committed edges (a `concept_closure` view); no materialised closure in v1 |
| Identity link | `identity_link`: subject is the entity Concept, `object_value` = `{"members":[{"source_system","identifier"}...]}`, confidence from the Matching agent. Query by member via a GIN index on `object_value`. Same status machine; links are agent-governed (see commit routing) |
| Source mapping layer | `source_mapping`: subject is the Concept, `object_value` = `{"source_system","table","column","transform"}`. Agent-governed and high-volume (separate commit routing below), kept in the same table so confidence, provenance and export work uniformly |
| Domain | `ontology.domain` rows; a Concept has one owning `domain_id`; `scope.domain` on assertions expresses the department whose meaning it is. `enterprise` means unscoped/cross-domain |
| Values and indicators | Concepts with `partition='values'`; indicators are Concepts linked by `indicator_of` assertions. Seeded as committed data in v1 (spec section 8) |
| Purpose (v1.2) | `partition='purpose'` is reserved; no v1 data. The Intent Record stays a plain record attached to the Question |

A Conflict Case of type `semantic` is created when two committed or proposed `definition` assertions on the same Concept have overlapping scope (for example both `enterprise`) or when a mapping implies a meaning different from the committed definition. Different department scopes alone are **not** a conflict; the Concept is flagged "multi-meaning" and Frame must pick a scope or ask. Factual conflicts are stored with `type='factual'`, routed to the data owner and not fixed in v1.

### 3. Commit Policy: authority-only in v1, pluggable later

`concept.commit_policy` is a jsonb document with a `kind` discriminator:

```json
{"kind":"authority"}
{"kind":"vote","threshold":0.7,"contest_limit":0.3,"quorum":3,"weights":{"role:vp":2,"domain:finance":1.5}}   // v1.1
{"kind":"evidence","min_evidence":3,"threshold":0.85}                                                      // v1.1
{"kind":"hybrid","all_of":[ ... ]}                                                                         // v1.1
```

In code, a `CommitPolicy` interface: `evaluate(assertion, ballots, evidence) -> Decision{ commit | hold | reject, reason }`. v1 ships only `AuthorityPolicy`; the module **rejects** (at write time) any `commit_policy.kind` other than `authority`, so unsupported policies cannot be configured by accident. Adding vote/evidence is a new policy class plus a `ballot` table in v1.1, with no change to `assertion` or the status machine.

**v1 authority policy:**
1. Agents (and humans) **propose**: insert `status='proposed'` with provenance. Agents can never commit, deprecate or contest-resolve; the `ontology` module checks the actor's role.
2. The committing actor must hold the Authority role for the assertion's partition and domain: `meaning` → Meaning Authority (scoped to the Concept's `domain_id`, or enterprise-wide); `values` → Values Authority; `purpose` → Question Governance Authority (v1.2). An unscoped authority role may commit anywhere in its partition.
3. Commit is one transaction: set `committed`, set `committed_in` to a new `release.number`, deprecate the superseded version, write `assertion_event` and an Audit Ledger entry (with the `handoff_id` of the decision, which records rationale and alternatives).
4. **Routing exception for the source mapping layer:** `source_mapping` and `identity_link` assertions are agent-governed (spec section 8). An agent with the Matching or Mapping role may commit them when `confidence >= 0.9` and no existing committed assertion on the same Concept contradicts them; otherwise they stay `proposed` and become a meaning mission. Such commits are recorded with `committed_by = agent:<version>` and a policy flag `auto`, so they remain auditable and revertible. These thresholds are policy defaults, evaluated later (ADR 0006), not constants in code.
5. Resolution when a Mission needs meaning, in v1: a committed assertion for the Concept and scope applies automatically if confidence is above threshold (record a meaning choice on the Answer); anything material without a committed assertion **blocks** and opens a meaning mission for the Meaning Authority (the provisional path is v1.1).
6. No timeouts decide anything (spec section 2): queue items only remind and re-route.

### 4. Versioning, releases and as-of queries

The ontology version is the integer `release.number`, incremented per commit transaction. Any Answer records the release number it used, so meaning at answer time is reproducible: `SELECT ... WHERE status IN ('committed','contested') AND committed_in <= :release AND (deprecated_in IS NULL OR deprecated_in > :release)`.  Deprecation stamps `deprecated_in`. Assertion-level `version` tracks one statement's history; release number tracks the whole ontology.

### 5. Export form

The ontology exports as **JSON-LD** (canonical), with a derived **Turtle** rendering, from a function `export(release, include=[committed,contested])`:
- Concepts → `skos:Concept` with `skos:prefLabel`/`skos:altLabel`, `skos:definition` per scope (as language-independent named nodes: `aq:ScopedDefinition` with `aq:scope`), `skos:broader` for `broader`, `skos:related`, and `aq:` terms for the other predicates. Values/indicators use `aq:Value`/`aq:Indicator`.
- Each exported Assertion is **reified** as an `aq:Assertion` node (not RDF-star, for tool support) carrying `aq:confidence`, `aq:status`, `aq:version`, `aq:release`, and PROV-O provenance (`prov:wasAttributedTo`, `prov:wasGeneratedBy` the Mission, `prov:wasDerivedFrom` the evidence).
- Identity links export as `owl:sameAs`-style clusters under `aq:IdentityLink` with member identifiers and confidence (reified, never as bare `owl:sameAs`, because links are fuzzy).
- Output is **deterministic** (sorted by slug then assertion key) so it diffs cleanly; `proposed` assertions are excluded unless asked for (`--include proposed`). Each release can be written to `ontology/export/ontology-r<N>.jsonld` for review and archive; import is the inverse and is how the seed ontology is loaded.
- Exact vocabulary IRIs and the PROV-O profile are finalised with the other open formats in ADR 0009; this ADR fixes the mapping shape and that JSON-LD plus SKOS and PROV-O is the target, so 0009 may rename terms but should not change the form.

## Alternatives considered

- **Triple store / RDF-native (e.g. Oxigraph).** Natural for export, but adds a second store, and confidence/status/versioning need reification anyway. Postgres is already the store for ledger, handoffs and queues; we export RDF instead.
- **Separate tables per kind (definition, relation, link, mapping).** Cleaner typing, but duplicates confidence/status/provenance/versioning logic and makes the commit module and export four times larger. A single table with a `kind` discriminator wins for v1.
- **Mutable rows with a history table.** Simpler writes, but weakens immutability and as-of reads. Immutable versions plus a status machine is safer for an Audit Ledger.
- **Confidence as a commit gate in v1.** Contradicts "authority only"; confidence stays informational until the evidence-weighted policy exists.
- **OWL/SHACL as the primary export.** Heavier tooling and implies a crisp logic; the ontology is fuzzy. SKOS plus reified assertions fits.
- **Vote and evidence-weighted now.** Deferred by spec to v1.1; only the extension point is built.

## Consequences

- Ontology-core (#45) can implement the DDL, the single writer module, the status machine, the `AuthorityPolicy`, the release counter and the exporter directly from this ADR.
- Adding vote/evidence-weighted commit means a new `CommitPolicy` class and a ballot table; no migration of `assertion`.
- Auto-commit of `source_mapping` and `identity_link` at confidence >= 0.9 is a deliberate carve-out from "authority commits"; it is spec-aligned (agent-governed layer) but should be revisited if wrong mappings slip through. Reverse by raising the threshold to 1.1 (no auto-commit) in policy.
- A single wide table means kind-specific payload shapes in `object_value` are validated in code (JSON Schema per kind), not by the database.
- Per-scope definitions coexisting means consumers must always pass a scope or accept a multi-meaning flag; this is intended.
- Reverse the whole ADR before data exists by changing DDL; afterwards by writing a migration and exporting through JSON-LD, which is the portable form.
- Interacts with ADR 0008 (stable core: if the Contract references `concept.id` and `release.number`, those become stable-core identifiers) and ADR 0009 (export vocabulary).
