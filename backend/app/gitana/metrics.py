"""Cálculo de métricas de salud a partir de RepoAnalysis."""

from __future__ import annotations

from app.gitana.parser import RepoAnalysis


def hotspots(analysis: RepoAnalysis, top: int = 12) -> list[dict]:
    """Archivos que concentran más cambios (priorizados)."""
    items = sorted(
        analysis.files.values(), key=lambda f: (f.changes, f.commits), reverse=True
    )
    out: list[dict] = []
    for f in items[:top]:
        bus_factor = len(f.authors)
        out.append(
            {
                "path": f.path,
                "changes": f.changes,
                "added": f.added,
                "deleted": f.deleted,
                "commits": f.commits,
                "authors": bus_factor,
            }
        )
    return out


def churn(analysis: RepoAnalysis) -> list[dict]:
    """Churn (añadidas+borradas) por ruta, de mayor a menor."""
    items = sorted(
        analysis.files.values(),
        key=lambda f: f.added + f.deleted,
        reverse=True,
    )
    return [
        {
            "path": f.path,
            "added": f.added,
            "deleted": f.deleted,
            "churn": f.added + f.deleted,
        }
        for f in items
    ]


def bus_factor(analysis: RepoAnalysis) -> list[dict]:
    """Riesgo por archivo: pocos autores concentran muchos cambios."""
    items: list[dict] = []
    for f in analysis.files.values():
        authors = len(f.authors)
        items.append(
            {
                "path": f.path,
                "authors": authors,
                "changes": f.changes,
            }
        )
    return sorted(items, key=lambda d: (d["authors"], -d["changes"]))


def cadence(analysis: RepoAnalysis) -> dict[str, int]:
    """Commits por día ordenados cronológicamente."""
    return dict(sorted(analysis.commits_per_day.items()))


def summarize(analysis: RepoAnalysis) -> dict:
    """Composición del reporte con las métricas principales."""
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
    }
