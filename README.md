# AutoQ

An open-source, self-hostable **altitude-5 harness** for data organisations: it answers business questions through governed missions, and builds and improves the system that answers them, so each answer strengthens the next.

Status: walking skeleton (stack runs, health only). See [docs/SPEC.md](docs/SPEC.md) and [docs/BACKLOG.md](docs/BACKLOG.md).

## Run it

Requires Docker with Compose.

```bash
docker compose up --build --wait
```

Then open <http://localhost:3000>: the page shows the API and database health. The API is at <http://localhost:8000> (`/healthz` liveness, `/api/health` readiness). Stop with `docker compose down` (add `-v` to drop the database volume).

## Develop

```bash
cd api && pip install -e ".[dev]" && pytest
cd web && npm ci && npm test && npm run build
```

CI (GitHub Actions) runs the same tests plus a full compose start on every push. Decisions are logged in [docs/adr](docs/adr/README.md).

Inspired by the talk "The exponential data organisation" (Data Berlin, 2026).

Not affiliated with or endorsed by SAP SE. SAP names refer to publicly documented products; the simulated systems contain only synthetic data.

Licence: Apache-2.0
