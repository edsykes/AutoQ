"""AutoQ API: walking skeleton. Health endpoints only."""
import os

import psycopg
from fastapi import FastAPI, Response

app = FastAPI(title="AutoQ API", version="0.1.0")


def database_ok() -> bool:
    url = os.environ.get("DATABASE_URL")
    if not url:
        return False
    try:
        with psycopg.connect(url, connect_timeout=2) as conn:
            conn.execute("SELECT 1")
        return True
    except psycopg.Error:
        return False


@app.get("/healthz")
def liveness() -> dict:
    """Process is up. Used by the container health check."""
    return {"status": "ok"}


@app.get("/api/health")
def health(response: Response) -> dict:
    """Readiness: the API and its dependencies. Shown on the web page."""
    db = database_ok()
    if not db:
        response.status_code = 503
    return {"status": "ok" if db else "degraded", "database": "ok" if db else "down"}
