"""Tests del hardening: rate limiting y límite de jobs en vuelo."""

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.ratelimit import reset


def test_rate_limit_returns_429(
    client: TestClient, monkeypatch
) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "rate_limit_per_minute", 2)
    reset()

    for _ in range(2):
        res = client.post("/api/analyze", json={"url": "http://bad/x"})
        assert res.status_code == 422

    res = client.post("/api/analyze", json={"url": "http://bad/x"})
    assert res.status_code == 429


def test_max_in_flight_blocks_new_jobs(
    client: TestClient, monkeypatch
) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "max_in_flight_jobs", 1)

    from app.db import SessionLocal
    from app.db.models import Job

    db = SessionLocal()
    try:
        db.add(Job(url="https://github.com/a/b", status="running"))
        db.commit()
    finally:
        db.close()

    res = client.post(
        "/api/analyze", json={"url": "https://github.com/LuisFloresA/TechDebt-Radar"}
    )
    assert res.status_code == 429
