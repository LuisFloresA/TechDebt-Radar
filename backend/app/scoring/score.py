"""Algoritmo de score de salud (0-100) y ejes del radar."""

from __future__ import annotations

from app.gitana.parser import RepoAnalysis
from app.static.scan import StaticScan


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _bus_factor_component(analysis: RepoAnalysis) -> float:
    total = sum(f.changes for f in analysis.files.values())
    if total == 0:
        return 100.0
    risky = sum(f.changes for f in analysis.files.values() if len(f.authors) == 1)
    return clamp(100.0 * (1.0 - risky / total))


def _hotspots_component(analysis: RepoAnalysis) -> float:
    total = sum(f.changes for f in analysis.files.values())
    if total == 0:
        return 100.0
    top5 = sorted(
        analysis.files.values(), key=lambda f: f.changes, reverse=True
    )[:5]
    top5_changes = sum(f.changes for f in top5)
    return clamp(100.0 * (1.0 - top5_changes / total))


def _churn_component(analysis: RepoAnalysis) -> float:
    total = sum(f.changes for f in analysis.files.values())
    deleted = sum(f.deleted for f in analysis.files.values())
    if total == 0:
        return 100.0
    # Alta proporción de eliminaciones => inestabilidad.
    return clamp(100.0 * (1.0 - deleted / total))


def _tech_debt_component(static: StaticScan) -> float:
    debt = (
        static.total_todos * 2
        + static.total_fixmes * 4
        + len(static.large_files) * 3
        + static.duplicate_units * 2
    )
    return clamp(100.0 - debt * 2)


def _cadence_component(analysis: RepoAnalysis) -> float:
    if analysis.total_commits == 0:
        return 0.0
    activity = 0.5 * min(1.0, analysis.total_commits / 10) + 0.5 * min(
        1.0, len(analysis.total_authors) / 3
    )
    return clamp(100.0 * activity)


WEIGHTS = {
    "bus_factor": 0.20,
    "hotspots": 0.20,
    "churn": 0.15,
    "tech_debt": 0.25,
    "cadence": 0.20,
}


def compute_score(analysis: RepoAnalysis, static: StaticScan) -> dict:
    """Devuelve score global y desglose (ejes de radar), todos 0-100."""
    components = {
        "bus_factor": round(_bus_factor_component(analysis)),
        "hotspots": round(_hotspots_component(analysis), 1),
        "churn": round(_churn_component(analysis), 1),
        "tech_debt": round(_tech_debt_component(static), 1),
        "cadence": round(_cadence_component(analysis)),
    }
    total = sum(WEIGHTS[k] * components[k] for k in WEIGHTS)
    return {"score": round(total), "components": components}
