"""Tests de la API y del pipeline asíncrono (Celery eager)."""

from fastapi.testclient import TestClient


def test_analyze_rejects_invalid_url(client: TestClient) -> None:
    res = client.post("/api/analyze", json={"url": "http://nohttps.com/x"})
    assert res.status_code == 422


def test_analyze_pipeline_creates_report(
    client: TestClient, _local_clone: None
) -> None:
    res = client.post(
        "/api/analyze", json={"url": "https://github.com/LuisFloresA/TechDebt-Radar"}
    )
    assert res.status_code == 202
    job_id = res.json()["id"]

    status_res = client.get(f"/api/jobs/{job_id}")
    assert status_res.status_code == 200
    body = status_res.json()
    assert body["job"]["status"] == "succeeded"

    metrics = body["report"]["metrics"]
    assert "hotspots" in metrics
    assert metrics["summary"]["files_analyzed"] >= 1


def test_job_not_found(client: TestClient) -> None:
    res = client.get("/api/jobs/999999")
    assert res.status_code == 404
