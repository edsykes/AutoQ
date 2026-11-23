# 0013: Health endpoint contract

- Status: accepted
- Date: 2026-11-21
- Ticket: #4
- Decided by: agent (autonomous)

## Context
Containers need cheap liveness checks; the web page needs a meaningful readiness signal.

## Decision
`GET /healthz` on the api (and web) is liveness only and always 200 if the process is up. `GET /api/health` is readiness: it checks the database and returns 200 `{"status":"ok","database":"ok"}` or 503 `{"status":"degraded","database":"down"}`. Compose health checks use `/healthz` so a transient DB blip does not restart or block the api; startup order is enforced with `depends_on: service_healthy` (db, then api, then web).

## Alternatives considered
Single health endpoint checking the DB: couples container liveness to DB availability.

## Consequences
New dependencies add their own field to `/api/health`. The contract is not part of the stable core (spec ADR 008).
