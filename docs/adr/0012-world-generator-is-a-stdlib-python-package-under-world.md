# 0012: World generator is a stdlib-only Python package under `world/`

- Status: accepted
- Date: 2026-11-21
- Ticket: #10
- Decided by: agent (autonomous)

## Context
The World Model generator (SPEC section 14) must be seeded, deterministic and self-contained, while the compose skeleton (api, web, Postgres) is built concurrently. The dev machine has Python 3.9 and no pytest.

## Decision
- Package `autoq_world` lives in `world/` (tests in `world/tests/`), imported with `world/` on the path. No third-party dependencies; Python 3.9 compatible.
- Tests use stdlib `unittest`: `cd world && python3 -m unittest discover -s tests`.
- `generate_world(WorldConfig(seed, n_suppliers, n_pos, ...))` returns a `World` of plain lists of dict rows (`to_dict()` for JSON). Randomness only through `random.Random(seed)`.
- Money is integer minor units in document currency; dates are ISO strings; FX is a monthly `rate_to_base` per currency; each company has its own fiscal calendar.
- Planted Drivers and the Answer Key are deliberately absent (ticket #11); they will extend this generator.

## Alternatives considered
- pytest / pydantic / Faker: extra dependencies for no gain at this size.
- Generating straight into Postgres: couples to the skeleton; rows-as-dicts can be loaded anywhere later.

## Consequences
Easy to import from the API or eval harness and to diff worlds by seed. If the api service pins a different Python or test runner, move the package and tests; behaviour is unaffected.
