# 0002: Observability is OpenTelemetry spans into Postgres, Phoenix optional

- Status: accepted
- Date: 2026-11-21
- Ticket: #6
- Decided by: agent (autonomous)

## Context
SPEC.md section 15 requires OpenTelemetry GenAI spans stored in our own schema, with Phoenix as an optional profile. Trace data is load-bearing, not just debugging: the **Audit Ledger** is derived from it, **Compounding Metrics** (cost and time per verified answer, human effort) are computed from handoff and ledger data, spend caps need token and cost accounting, and the **Builder** mines it for friction. Section 17 requires that secrets never appear in traces and that source data is treated as untrusted text. The OTel GenAI semantic conventions are still marked experimental.

## Decision
- **Instrumentation is OpenTelemetry only.** Back-end, LangGraph node wrappers, the ADK runner and LiteLLM call wrapper emit spans using the GenAI semantic conventions (`gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`/`output_tokens`, tool-call spans), plus AutoQ attributes: `autoq.mission_id`, `autoq.step_run_id`, `autoq.agent_id`, `autoq.agent_version`, `autoq.cost_usd`. Convention attribute names are isolated in one module so an upstream rename is a one-line change.
- **A custom SpanProcessor/exporter writes spans into Postgres** in our own schema (a `trace_span` table keyed by trace/span id, with parent, times, status, attributes as JSONB, indexed by mission, step run and agent version), batched and asynchronous. This table is the source from which handoffs are linked, the ledger is derived and metrics are computed. The **hash-chained ledger** is a separate append-only table written transactionally; traces feed it but are not trusted as tamper-proof themselves.
- **Content capture is off by default.** Prompts, completions and tool arguments are stored only as references to content-addressed rows in a separate table, behind a config switch, and pass through a redactor first. API keys, authorization headers and session secrets are stripped by an allow-list of attributes at the exporter, so unknown attributes are dropped rather than stored. Source data in prompts is stored as untrusted text and never interpreted.
- **Phoenix is an optional compose profile.** An additional OTLP exporter sends the same spans to Phoenix when `COMPOSE_PROFILES=phoenix`. Nothing in the product depends on Phoenix being up, and the product UI never reads from it.
- Retention: spans kept for the life of the deployment in v1 (data is tiny); a pruning job is a v1.1 concern.

## Alternatives considered
- **Phoenix (or Langfuse) as the primary store**: good UI for free, but a second database to run, a schema we do not control, and the ledger and metrics would depend on a third-party store. Kept as an optional viewer instead.
- **Plain application logging / bespoke event tables without OTel**: simpler, but loses the standard vocabulary, ecosystem exporters and ADK's native OTel emission.
- **OTel Collector plus ClickHouse/Tempo**: scales better, far more infrastructure than "hundreds of rows" and one VM justify.
- **Storing full prompts by default**: invaluable for debugging, but risks leaking keys and sensitive-labelled data; opt-in is the safer default.

## Consequences
- One query layer (Postgres) serves traces, handoffs, ledger and metrics, and works under `docker compose up` with no extra service.
- We own the exporter and schema, so we carry maintenance, and Postgres write volume grows with span count (acceptable at v1 scale).
- Experimental semantic conventions may change; the isolating module limits blast radius.
- Reversal: the OTel instrumentation is backend-agnostic, so the Postgres exporter can be swapped for OTLP to another store without touching call sites.
