# Control-plane API foundation

## Runtime and layout

Use a single-worker synchronous Python service: FastAPI with Uvicorn, SQLAlchemy 2.x with psycopg 3, and Alembic. Use standard-library configuration and redacted structured logging; do not add a worker queue, cloud SDK, settings package, or test framework in this foundation.

```
api/
  pyproject.toml
  requirements.lock
  Dockerfile
  alembic.ini
  migrations/
  src/jarvis_api/
    main.py       # app factory and lifespan
    config.py     # allow-listed config/file-secret parsing
    db.py         # engine, session factory, readiness probe
    health.py     # health router only
    api/v1/       # future contract routes
    domain/
    persistence/  # metadata, models, repositories, append-only audit writer
```

Initial code includes only app creation, configuration validation, database/session infrastructure, migration configuration, and health. It must not partially expose enrollment, events, timeline, policy, EMQX, Hermes, media, OAuth, backup, or dashboard APIs.

## Configuration and persistence

Allow only `JARVIS_ENV`, database host/port/name/user, `JARVIS_DB_PASSWORD_FILE`, and `JARVIS_DATA_ROOT`. The password setting is a mounted-file path only; contents are read once at boot, trimmed of one trailing newline, and never serialized or logged. Missing/invalid configuration fails closed.

PostgreSQL is authoritative. Use one bounded engine with `pool_pre_ping`, session-per-use-case, and `session.begin()` so future business mutation and its redacted audit row commit atomically. Repositories never commit independently. No implicit DDL or automatic migration runs at startup.

Alembic is the sole migration mechanism. Migrations are reviewed source files and run only with an explicit owner-approved one-shot `alembic upgrade head` command. If the database revision is missing, outdated, or branched, the API accepts no traffic.

## Health and container boundary

Expose only internal `GET /healthz`. It returns `200 {"status":"ok"}` after configuration validation, database `SELECT 1`, and schema-head verification; otherwise it returns a redacted `503` reason with `Cache-Control: no-store`. Disable public docs, root routes, and published API ports.

Build from an owner-reviewed immutable `python:3.13-slim` digest. `requirements.lock` exact-pins `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `psycopg[binary]`, and `alembic` with hashes; Docker installs only through `pip --require-hashes`. Run a fixed non-root UID with one Uvicorn worker on internal port 8080. The container receives only the control network, read-only database password file, and approved API data-root mount.

## Required approvals

Before dependency installation or runtime: approve Python base-image digest, locked package versions/hashes, Postgres image/secret/data-root details, initial migration contents and one-shot command, and final Dockerfile/Compose diff. Starting the API never implies migration approval.
