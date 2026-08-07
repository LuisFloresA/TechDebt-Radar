"""Tarea de análisis de repositorio en background."""

from __future__ import annotations

import json

from app.analytics import build_report
from app.clone.clone import cleanup, clone_to_storage
from app.clone.validation import RepoRef, parse_github_url
from app.db.models import Job, Report
from app.db.session import SessionLocal
from app.gitana.parser import parse_numstat, run_git_log
from app.workers.celery_app import celery_app


def _update(
    job_id: int,
    status: str | None = None,
    progress: int | None = None,
    error: str | None = None,
) -> None:
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if job is None:
            return
        if status is not None:
            job.status = status
        if progress is not None:
            job.progress = progress
        if error is not None:
            job.error = error
        db.commit()
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.analyze_repo")
def analyze_repo(job_id: int, url: str, branch: str = "main") -> dict:
    """Clona un repo, extrae el historial y persiste el reporte."""
    _update(job_id, status="running", progress=5, error=None)
    repo = None
    try:
        ref: RepoRef = parse_github_url(url)
        _update(job_id, progress=20)
        repo = clone_to_storage(ref, job_id, branch=branch)
        _update(job_id, progress=55)
        output = run_git_log(repo, all_branches=branch == "all")
        analysis = parse_numstat(output)
        metrics = build_report(analysis, repo)
        metrics["branch"] = branch
        _update(job_id, progress=85)

        db = SessionLocal()
        try:
            report = Report(job_id=job_id, url=url, metrics=json.dumps(metrics))
            job = db.get(Job, job_id)
            if job is not None:
                job.status = "succeeded"
                job.progress = 100
                job.report = report
                db.add(report)
            db.commit()
        finally:
            db.close()
        return metrics
    except Exception as exc:  # noqa: BLE001
        _update(job_id, status="failed", error=str(exc))
        raise
    finally:
        if repo is not None:
            cleanup(repo)
