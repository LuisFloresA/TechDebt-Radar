"""Composición del reporte completo de salud de un repositorio."""

from __future__ import annotations

from pathlib import Path

from app.gitana.metrics import bus_factor, cadence, churn, hotspots
from app.gitana.parser import RepoAnalysis
from app.scoring.recommendations import build_recommendations
from app.scoring.score import compute_score
from app.static.scan import StaticFile, scan_repo


def static_to_json(static_files: list[StaticFile]) -> dict:
    files = sorted(
        (f for f in static_files if f.todos or f.fixmes or f.lines > 500),
        key=lambda f: (f.todos + f.fixmes, f.lines),
        reverse=True,
    )[:20]
    return {
        "files": [
            {
                "path": f.path,
                "lines": f.lines,
                "todos": f.todos,
                "fixmes": f.fixmes,
                "complexity": f.complexity,
            }
            for f in files
        ],
        "total_todos": sum(f.todos for f in static_files),
        "total_fixmes": sum(f.fixmes for f in static_files),
        "total_lines": sum(f.lines for f in static_files),
        "large_files": sum(1 for f in static_files if f.lines > 500),
        "duplicate_units": sum(
            max(0, len([x for x in static_files if x.digest == d]) - 1)
            for d in {f.digest for f in static_files if f.digest}
        ),
    }


def build_report(analysis: RepoAnalysis, repo: Path) -> dict:
    static = scan_repo(repo)
    scoring = compute_score(analysis, static)
    recommendations = build_recommendations(analysis, static)
    return {
        "summary": {
            "total_commits": analysis.total_commits,
            "total_authors": len(analysis.total_authors),
            "files_analyzed": len(analysis.files),
        },
        "hotspots": hotspots(analysis),
        "churn": churn(analysis),
        "bus_factor": bus_factor(analysis),
        "cadence": cadence(analysis),
        "static": static_to_json(static.files),
        "score": scoring,
        "recommendations": recommendations,
    }
