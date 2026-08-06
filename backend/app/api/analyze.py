"""Endpoints de análisis y reportes."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.clone.validation import InvalidRepo, parse_github_url
from app.db import get_db
from app.db.models import Job, Report
from app.schemas import AnalyzeRequest, JobOut, ReportOut, ReportResponse
from app.workers.tasks import analyze_repo

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post(
    "/analyze",
    response_model=JobOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Inicia el análisis de un repositorio",
)
def start_analysis(
    payload: AnalyzeRequest, db: Session = Depends(get_db)
) -> Job:
    try:
        parse_github_url(payload.url)
    except InvalidRepo as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    job = Job(url=payload.url.strip(), status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)
    analyze_repo.delay(job.id, job.url)
    return job


@router.get("/jobs/{job_id}", response_model=ReportResponse, summary="Estado de un job")
def job_status(job_id: int, db: Session = Depends(get_db)) -> ReportResponse:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job no encontrado")

    report = db.query(Report).filter(Report.job_id == job_id).first()
    report_out = None
    if report is not None:
        metrics = json.loads(report.metrics)
        report_out = ReportOut(
            id=report.id,
            job_id=report.job_id,
            url=report.url,
            metrics=metrics,
            created_at=report.created_at,
        )
    return ReportResponse(job=job, report=report_out)
