# 0014: CI on GitHub Actions

- Status: accepted
- Date: 2026-11-21
- Ticket: #4
- Decided by: agent (autonomous)

## Context
Ticket #4 requires CI that passes on every push.

## Decision
One workflow `.github/workflows/ci.yml` on push and pull_request with three jobs: `api` (pytest), `web` (vitest + build), and `compose` (build, `docker compose up --wait`, curl the web page's proxied `/api/health`, tear down). The compose job is the end-to-end proof of the acceptance criterion. No linting yet; added when there is enough code to justify the config.

## Alternatives considered
Skipping the compose job to save minutes: loses the only check that the stack actually starts.

## Consequences
Later tickets extend the jobs (for example the Playwright smoke test from the spec).
