# 0012: Skeleton stack and repo layout

- Status: accepted
- Date: 2026-11-21
- Ticket: #4
- Decided by: agent (autonomous)

## Context
Ticket #4 needs `docker compose up` to start api, web and Postgres, all healthy. SPEC section 15 fixes React, FastAPI and Postgres (+pgvector) but not versions, tooling or layout.

## Decision
Monorepo with `api/` (Python 3.12, FastAPI, uvicorn, psycopg 3, pyproject.toml, pytest) and `web/` (Vite + React + TypeScript, vitest, built into an nginx image). Postgres uses `pgvector/pgvector:pg16` so the spec's pgvector is available later. nginx serves the SPA and proxies `/api/` to the api service, so the browser has one origin and no CORS config. Compose ports: web 3000, api 8000. Dev credentials are fixed (`autoq`/`autoq`) and are for local compose only.

## Alternatives considered
- Next.js: heavier; SPEC asks only for React and SSE from the API.
- Plain `postgres` image: would need swapping for pgvector later.
- uv/poetry: extra tooling for no skeleton benefit; pip + pyproject is enough.

## Consequences
Later tickets add routes, migrations and services here. Swapping tooling is cheap at this size. Real secrets handling is deferred to the deployment ticket.
