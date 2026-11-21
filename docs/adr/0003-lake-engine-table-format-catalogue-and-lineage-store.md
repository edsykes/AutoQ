# 0003: Lake engine, table format, catalogue and lineage store

- Status: accepted
- Date: 2026-11-21
- Ticket: #7
- Decided by: agent (autonomous)

## Context
SPEC section 5 fixes "one columnar engine behind a swappable Lake Adapter: DuckDB over Parquet, with a Postgres snapshot catalogue and contract store", and leaves open (a) whether to adopt an open table format, (b) the catalogue design, and (c) whether lineage needs a graph database. Requirements that drive the choice:

- Immutable, as-of-stamped **Snapshots**; every **Answer** replayable (data, definitions and numbers reproduce exactly).
- Tiny v1 data (hundreds of rows; no latency or scale targets), single node, `docker compose up`, no cloud account needed.
- Contracts, lineage and ontology already live in Postgres, so catalogue consistency with them matters more than raw lake features.
- The Lake Adapter must stay swappable, so the choice must be reversible.

## Decision
1. **Engine:** DuckDB, embedded in the back end and the sandbox-free Lake Adapter process.
2. **Storage format in v1:** plain **Parquet files, written once and never modified**, in a content-addressed layout `lake/<zone>/<asset-address-path>/<build-id>/part-*.parquet`. No table format layer in v1. Immutability of files plus a content hash per materialisation gives us time travel by construction: a version of an asset *is* a directory.
3. **Catalogue:** a Postgres **snapshot catalogue** (tables `lake_snapshot`, `lake_materialisation`, `lake_file`) holding addresses (ADR-0008), file lists, row counts, content hashes, as-of stamps and zone. Contracts live in a `contract` table in the same database. A materialisation becomes visible only when its catalogue row commits, in the same transaction as its contract and lineage edges. That transaction is the atomic commit point; orphaned files are garbage-collected.
4. **Lineage store:** relational edges in Postgres (`lineage_edge`: from address, to address, transformation ref, versions, run id), queried with recursive CTEs for impact analysis and replay planning. No graph database in v1. Revisit trigger: impact-analysis traversal over the real data exceeds 1 s at p95, or depth/fan-out makes CTEs unreadable. The first candidate then is Apache AGE (a Postgres extension, so no new store) before any separate graph database.
5. **Preferred successor, not adopted now:** **DuckLake** (DuckDB's lakehouse format, catalogue in a SQL database such as Postgres, data in Parquet). It matches our shape almost exactly. It is rejected for v1 only on maturity grounds (see below); the Lake Adapter interface is designed so that swapping to it is a new adapter plus a one-off catalogue migration.

### Table format comparison

| | Plain Parquet + Postgres catalogue (chosen) | DuckLake | Apache Iceberg | Delta Lake | Apache Hudi |
|---|---|---|---|---|---|
| DuckDB support | Native | Native (core extension by DuckDB Labs) | `iceberg` extension: strong read, write support newer and partial | `delta` extension: read; write limited or experimental | None native |
| Catalogue | Our Postgres | SQL database (Postgres fits) | Needs a catalogue service (REST, Hive, Glue, JDBC); extra moving part | Transaction log in object store; Unity optional | Timeline in object store |
| Metadata model | Rows we already own | Metadata as SQL tables; no manifest-file sprawl | Manifest lists and metadata JSON | JSON log plus checkpoints | Timeline plus metadata table |
| Time travel / snapshots | By immutable directories plus catalogue | Native snapshots | Native | Native | Native |
| Transactional with our contracts and lineage | Yes, one Postgres transaction | Yes if the catalogue is our Postgres | No, separate catalogue | No | No |
| Ecosystem interop (Spark, Trino, etc.) | Parquet only | Growing, young | Broadest | Broad | Narrower |
| Operational weight for a hundreds-of-rows demo | Lowest | Low | Medium to high | Medium | High |
| Maturity (at 2026-11) | Trivially stable | Young; spec and format still evolving quickly | Mature | Mature | Mature |

Why Iceberg, Delta and Hudi lose for v1: their main benefits (multi-engine concurrent writers, large-scale compaction, partition evolution, schema evolution at petabyte scale) solve problems the spec explicitly declares out of scope, and each adds a catalogue or log we would have to keep consistent with Postgres. Their DuckDB write paths are also the least mature part of each. Schema evolution in AutoQ is handled at the Definition level (new Definition version, ADR-0008), not inside the table, so we do not need the format to do it.

Why not DuckLake now: it is the best architectural fit, but it is young and its on-disk catalogue schema has been changing between releases. We would be placing the stable core's physical layout on a moving format. Because our own catalogue tables are tiny and the mapping is mechanical (snapshot, file, row count), the later migration is cheap.

## Alternatives considered
- **Iceberg via DuckDB** for interoperability: rejected, see above; also pulls in a REST catalogue service.
- **Postgres as the lake** (no DuckDB): rejected, contradicts the spec and loses columnar analytics.
- **Neo4j / graph DB for lineage**: rejected for v1; relational edges plus recursive CTEs handle depth in the tens at hundreds of rows, and a second store breaks the single atomic commit.
- **Catalogue in DuckDB file**: rejected; cannot share a transaction with contracts and lineage in Postgres, and single-writer locking hurts the back end.
- **Delta/Iceberg only for export**: possible later as a materialisation target, not a storage layer.

## Consequences
- Easier: one transactional commit covers data registration, contract and lineage; `docker compose up` stays small; replay is "read these files at these hashes".
- Harder: no ecosystem interop beyond Parquet; compaction, partitioning and schema evolution are our problem if data grows (it is not expected to in v1); we own garbage collection of orphaned files.
- Reversal: implement a `DuckLakeAdapter` (or Iceberg adapter) behind the Lake Adapter and migrate catalogue rows; addresses (ADR-0008) are format-independent, so nothing above the adapter changes. Supersede this ADR when doing so.
- Downstream: the lake, contract and lineage tickets build `lake_*`, `contract` and `lineage_edge` tables as specified here; DDL details are theirs. Addressing and contract fields come from ADR-0008, event export from ADR-0009.
