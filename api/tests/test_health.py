from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_liveness():
    assert client.get("/healthz").json() == {"status": "ok"}


def test_health_ok_when_database_up(monkeypatch):
    monkeypatch.setattr(main, "database_ok", lambda: True)
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "database": "ok"}


def test_health_degraded_when_database_down(monkeypatch):
    monkeypatch.setattr(main, "database_ok", lambda: False)
    r = client.get("/api/health")
    assert r.status_code == 503
    assert r.json()["status"] == "degraded"
