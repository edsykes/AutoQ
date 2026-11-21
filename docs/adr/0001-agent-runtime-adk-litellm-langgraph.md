# 0001: Agent runtime is Google ADK + LiteLLM + LangGraph

- Status: accepted
- Date: 2026-11-21
- Ticket: #6
- Decided by: agent (autonomous)

## Context
SPEC.md sections 4 and 15 fix the stack but not how the three pieces divide work. Each **Loop** step is a workflow of **Agents** that needs durable checkpoints, bounded retries, human-wait states (`blocked_on_human`) and loop-back edges across a **Mission**. **Agent** definitions are versioned artefacts the **Builder** edits and the Eval Gate promotes or rolls back, so they must be declarative and separable from orchestration. Models must be swappable (any frontier or local open-weight model), the operator or hosted visitor brings the key, and keys are never logged.

## Decision
Three layers, each owning one concern:

1. **Google ADK owns the Agent definition.** An Agent is an ADK `LlmAgent` (instructions, tools, skills, memory scope) built from a versioned definition stored in Postgres. ADK is used as the agent-definition and single-agent execution library, not as the orchestrator: each Step Run invokes an ADK `Runner` with an in-memory session and returns a typed result. ADK's own multi-agent and workflow agents are not used for Loop control.
2. **LangGraph owns orchestration and durability.** One graph per Loop step (and one for the Mission, composing them). Nodes call ADK agents. State is checkpointed with the Postgres checkpointer. Retries, `blocked_on_human` waits (graph interrupts resumed by an API call), loop-back edges and sub-mission fan-out are LangGraph concerns. The graph's state holds references and typed handoffs, never raw conversation transcripts as the system of record; the handoff and ledger tables in our own schema are the record.
3. **LiteLLM owns model access.** Agents reference a logical model alias (for example `reasoning`, `fast`, `local`); a single resolver maps alias to a LiteLLM model string via operator config. ADK talks to it through its LiteLLM model adapter. LiteLLM runs **in-process as a library**, not as a separate proxy, in v1. The API key is passed per call from the operator secret store or the hosted visitor's session, held in memory only, and never written to traces, logs or checkpoints (see 0002). LiteLLM's own success/failure callbacks and verbose logging are disabled; spend is metered by our own OTel-derived accounting, which also enforces **spend caps**.

Version policy: exact-pinned, hash-locked dependencies for all three; upgrades are deliberate and run the cassette-replay suite first. Everything outside the thin adapter modules (agent factory, graph builder, model resolver) must not import ADK, LangGraph or LiteLLM directly, so a layer can be replaced without touching domain code.

## Alternatives considered
- **ADK alone** (its sequential/loop/parallel agents plus its session service): fewer moving parts, but no durable human-wait, weak checkpoint/resume semantics and awkward loop-back edges for a Mission that may block for days. Rejected.
- **LangGraph alone with LangChain agents**: strong orchestration, but the spec makes ADK the Agent definition format; ADK's declarative agent, tool and skill model suits Builder-generated versions better.
- **LiteLLM proxy server as a sidecar**: gives central key management, budgets and a UI, but adds a service, a Postgres schema and a second place keys live. Hosted-visitor keys must stay session-scoped, which is simpler in-process. Revisit if multiple back-end replicas need shared budgets.
- **Temporal / Prefect / Dagster for durability**: heavier infrastructure than one `docker compose up` justifies at v1.
- **Direct provider SDKs**: lock-in, and breaks the "any model, including local" requirement.

## Consequences
- Easier: Builder changes an Agent by writing a new definition row; orchestration is untouched. Models are switched by config. Missions survive restarts and long human waits.
- Harder: three frameworks to keep compatible, with an ADK-in-a-LangGraph-node impedance (two notions of session/state); mitigated by keeping ADK sessions ephemeral per Step Run.
- Spend caps depend on our own token accounting, because we do not use LiteLLM's budget features.
- Reversal: the adapter-only import rule means swapping any single layer is a contained change. A superseding ADR would be needed to drop ADK or LangGraph as it touches the spec.
