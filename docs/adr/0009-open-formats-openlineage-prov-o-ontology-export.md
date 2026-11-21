# 0009: Open formats: OpenLineage, PROV-O and ontology export

- Status: accepted
- Date: 2026-11-21
- Ticket: #7
- Decided by: agent (autonomous)

## Context
SPEC section 5 requires data lineage as **OpenLineage** events with our contract fields as custom facets, provenance of assertions, answers and claims exportable as **W3C PROV-O**, and the ontology exportable in a standard form. The internal source of truth for lineage and contracts is relational (ADR-0003, ADR-0008). This ADR fixes the shape of the exports so they interoperate with outside tooling (Marquez, DataHub, Atlan, generic RDF stores) without leaking internal storage choices.

## Decision

### 1. OpenLineage (data lineage)
- **Generated from, never stored instead of,** `lineage_edge` and contract rows. One `RunEvent` per Step Run that reads or writes data (`START`, `COMPLETE`, `FAIL`), emitted to an internal table and optionally an HTTP endpoint the Operator configures.
- Mapping: `job.namespace = "autoq"`, `job.name = <transformation ref>@<version>`; `run.runId` = the Step Run's UUID (UUIDv7 for time ordering); `inputs`/`outputs` datasets use `namespace = "autoq://lake"` and `name = <address>` (ADR-0008, e.g. `aq:mat/finance.spend@3/01J...`, `aq:snap/s4cloud/20261121T000000Z/sha256-ab12...`).
- Standard facets used: `schema`, `dataSource` (connector), `columnLineage` (from measures/columns), `dataQualityAssertions` (from `checks.latest`), `parent` (mission run), `nominalTime`.
- **Custom facets** (prefix `autoq_`, each with `_producer` = the AutoQ repo URL and `_schemaURL` pointing at a JSON Schema file kept in `docs/schemas/openlineage/` once the contract ticket creates it):
  - **`autoq_contract`** (dataset facet on every output): `{ contractSchema: "autoq.contract/1", definition: "aq:def/...@n", status, grain: [...], keys: [{column, entity}], measures: [{column, concept, assertion}], time: {semantics, freshnessSla, sourceAsof}, steward, sensitivity, contentHash, zone }`. It carries the contract fields that are meaningful to outsiders; `economics` and `retention` are included only when the Operator enables them. Field names and values are exactly the contract's, so the facet schema is the contract's JSON Schema subset.
  - **`autoq_reproducibility`** (dataset facet): `{ snapshots, definitionVersions, mappingVersions, agentVersions, contentHash }`.
  - **`autoq_mission`** (run facet): `{ missionId, stepRunId, step: frame|discover|clarify|evidence|verify|answer, agentVersion, questionVersion }`.
  - **`autoq_core`** (run facet): `{ stableCoreVersion: "core/1" }` so consumers can detect migrations (ADR-0008).
- Facets follow OpenLineage versioning: additive changes keep the `_schemaURL` version; breaking changes publish a new facet version. Dataset `sensitivity=restricted|secret` facets are **redacted** to name and address only when exported outside the deployment.

### 2. PROV-O (provenance of assertions, answers and claims)
- On-demand **JSON-LD export** (also Turtle) per object and subtree: assertion, answer, claim graph, mission. Generated from lineage edges, handoff records and the ledger.
- Mapping: `prov:Entity` = assertion versions, answers, claims, definition versions, snapshots, materialisations (type with `autoq:` subclasses); `prov:Activity` = Step Runs, Missions, meaning missions, Builder changes; `prov:Agent` = agent versions (`prov:SoftwareAgent`) and humans/authorities (`prov:Person`) with `prov:actedOnBehalfOf` for role.
- Relations: `derived_from` -> `prov:wasDerivedFrom`; output of a run -> `prov:wasGeneratedBy` and `prov:used` for inputs; `produced_by_agent` -> `prov:wasAttributedTo` / `prov:wasAssociatedWith`; `superseded_by` -> `prov:wasRevisionOf` (inverse); human approvals -> `prov:wasAssociatedWith` with a `prov:Association` role (`autoq:approver`). Confidence, status and rationale are `autoq:` datatype properties on the entity; evidence-backed vs human-asserted claim is an `autoq:basis` property.
- IRIs: `https://<deployment-base>/aq/<address-path>`, derived deterministically from the address (`aq:def/finance.spend@3` -> `.../aq/def/finance.spend@3`), so IRIs are as stable as addresses.

### 3. Ontology export
- Concepts and hierarchies export as **SKOS** (`skos:Concept`, `broader/narrower`, `prefLabel`, `definition`); entity types and relations as **OWL 2** classes and object properties in a lightweight profile (no reasoning required); both serialised as Turtle and JSON-LD.
- Assertions are exported as reified statements typed `autoq:Assertion` with `autoq:confidence`, `autoq:status`, `autoq:scope`, version, and PROV-O provenance (section 2), so consumers can filter to `committed` or above a confidence.
- Only **committed** assertions are exported by default; `proposed` and `contested` are opt-in. Departments' differing definitions export as separate scoped assertions linked to the same Concept, never merged.
- The internal ontology representation and commit model belong to ADR-0004; if 0004 chooses a representation that cannot produce this export without loss, 0004 must say so and this section is amended.

### 4. Shared rules
Exports are read-only, versioned (`autoq.export/1` marker), regenerated rather than stored, and respect `sensitivity` (restricted values never appear in exports). Conformance is tested with the official OpenLineage client JSON Schemas and a PROV-O/SKOS round-trip parse in CI.

## Alternatives considered
- **Emit OpenLineage as the primary lineage store**: rejected; events are append-only logs and awkward to traverse for impact analysis, and we need atomicity with contracts (ADR-0003).
- **Contract fields as a profile of the `schema` facet**: rejected, too narrow; custom `autoq_contract` facet is the sanctioned extension point.
- **DCAT / Data Contract Specification / ODCS instead of custom facets**: they describe the contract document, not run-time lineage. We may add an ODCS export later as a pure view.
- **PROV-O only (no OpenLineage)**: poor tool support in data catalogues.
- **RDF as internal ontology format just to get export free**: left to ADR-0004.
- **Custom JSON export**: no interoperability value.

## Consequences
- Easier: standard tools can consume our lineage and contracts; provenance is auditable outside the product; the Lineage view can be fed from the same generated shape.
- Harder: we keep facet and export schemas versioned and tested; redaction rules must be applied consistently.
- Reversal: exports are generated views, so changing or dropping a format costs only the generator; no stored data depends on them. Facet naming (`autoq_*`) is public once released, so renames need a new facet version.
- Downstream: lineage, contract, ontology and Lineage-view tickets implement the generators; core address and contract fields come from ADR-0008.
