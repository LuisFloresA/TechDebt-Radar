"""Modelos Pydantic de request/response."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AnalyzeRequest(BaseModel):
    url: str = Field(..., description="URL https del repositorio GitHub público.")
    branch: str = Field(
        "main",
        description=(
            'Rama a analizar ("main" o un nombre concreto) '
            'o "all" para todas las ramas.'
        ),
    )


class BranchesResponse(BaseModel):
    branches: list[str]
    default: str = "main"


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    branch: str = "main"
    status: str
    progress: int
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    url: str
    metrics: dict[str, Any]
    created_at: datetime


class ReportResponse(BaseModel):
    job: JobOut
    report: ReportOut | None = None
