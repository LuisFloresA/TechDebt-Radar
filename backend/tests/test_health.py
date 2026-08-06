"""Tests de los endpoints de salud."""

from fastapi.testclient import TestClient


def test_health_liveness_ok(client: TestClient) -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["version"]


def test_health_ready_ok(client: TestClient) -> None:
    res = client.get("/api/health/ready")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"


def test_openapi_docs_available(client: TestClient) -> None:
    res = client.get("/openapi.json")
    assert res.status_code == 200
    assert res.json()["info"]["title"]
