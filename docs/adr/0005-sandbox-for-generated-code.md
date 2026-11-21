# 0005: Generated code runs in a per-execution locked-down Docker container

- Status: accepted
- Date: 2026-11-21
- Ticket: #6
- Decided by: agent (autonomous)

## Context
The Builder and Evidence agents produce code (tools, transformations, checks) that must run against data without being able to reach the network, the host, secrets, sources or the rest of the lake. SPEC.md section 15 asks for a sandbox container with no network, read-only mounts and resource limits; section 17 states v1 posture: synthetic data only, and that sandbox escape and prompt injection are **not adversarially tested** in v1. The deployment is `docker compose up` on a laptop or one cloud VM, so the sandbox must work with plain Docker and no special host features.

## Decision
- **Each execution is a fresh, short-lived container** from a dedicated sandbox image (pinned Python plus DuckDB and a small allow-list of libraries, installed at build time). It is destroyed after the run; nothing persists between runs.
- **Restrictions on every run:** `--network none`; read-only root filesystem; inputs mounted read-only (Parquet snapshots or Retained models named in the call, nothing else); one writable tmpfs for scratch plus one output directory whose contents are copied back and validated; non-root user; `--cap-drop ALL`; `no-new-privileges`; default seccomp profile; memory, CPU and `pids` limits; wall-clock timeout enforced by the caller with kill; output size cap; no environment variables except an explicit allow-list (never LLM keys); no Docker socket inside.
- **Interface:** the back end calls a small `Sandbox` port with `run(code, inputs, limits) -> result{stdout, stderr, outputs, exit_status, usage}`. The Docker implementation lives behind it. The back end reaches Docker through a narrowly scoped socket proxy limited to create, start, wait, logs and remove on containers carrying the sandbox label, rather than mounting the full Docker socket.
- **Outputs are untrusted:** results are schema-validated and pass the same checks as any Evidence before use; sandbox runs and their resource use are recorded as spans (0002) and as ledger entries when they change a governed asset.
- **Optional hardening, off by default:** where the host supports it, set the runtime to gVisor (`runsc`) through configuration. Not required for v1 and not tested in CI.

## Alternatives considered
- **In-process restriction (RestrictedPython, `exec` with limited builtins):** well known to be bypassable and gives no resource or filesystem isolation. Rejected.
- **Pyodide / WebAssembly runtime:** strong isolation and no Docker, but a constrained library set (DuckDB-on-Parquet, pandas performance and file access are awkward) and an unfamiliar operational path for the Builder's tool code.
- **Firecracker / microVMs, or a hosted sandbox (E2B and similar):** strongest isolation, but need KVM access or external accounts and keys, break the one-command, offline-capable spin-up and send data off the box. Reconsider if real data or untrusted users arrive.
- **A single long-lived sandbox container exec'd into repeatedly:** faster, but state leaks between runs and one escape or fork bomb affects everything. Startup cost per run (well under a second to a few seconds) is acceptable at v1 scale.
- **Full Docker socket mounted into the back end:** simple, but equals host root if the back end is compromised; the socket proxy limits that.

## Consequences
- Easier: strong default isolation with tools every contributor already has; the guarantees match the spec's wording directly and are testable (a network call, a write to a read-only mount and a memory bomb should each fail).
- Harder: per-run container startup latency; sandbox image maintenance; Docker-in-compose socket plumbing; Docker containers share the host kernel, so this is **not** safe against a determined attacker, and the v1 posture of synthetic data only is what makes that acceptable. This residual risk stays documented in the spec.
- Reversal: the `Sandbox` port lets a gVisor, microVM or hosted implementation replace the Docker one without changing callers; that change should supersede this ADR.
