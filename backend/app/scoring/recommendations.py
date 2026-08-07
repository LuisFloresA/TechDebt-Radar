"""Recomendaciones priorizadas de mantenimiento."""

from __future__ import annotations

from app.gitana.parser import RepoAnalysis
from app.static.scan import StaticScan

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def build_recommendations(analysis: RepoAnalysis, static: StaticScan) -> list[dict]:
    recs: list[dict] = []

    # 1) Hotspot con un único autor: riesgo de bus factor concentrado.
    hotspots = sorted(
        analysis.files.values(), key=lambda f: f.changes, reverse=True
    )[:5]
    for f in hotspots:
        if len(f.authors) == 1 and f.changes > 0:
            recs.append(
                {
                    "severity": "high",
                    "title": f"{f.path} concentra cambios de 1 autor",
                    "detail": (
                        f"{f.changes} líneas cambiadas por una sola persona. "
                        "Añade tests y reparte la propiedad del módulo."
                    ),
                }
            )

    # 2) Deuda estática acumulada.
    debt_units = static.total_todos * 2 + static.total_fixmes * 4
    if debt_units >= 20:
        recs.append(
            {
                "severity": "medium",
                "title": "Pagar deuda marcada",
                "detail": (
                    f"Hay {static.total_todos} TODO y {static.total_fixmes} FIXME. "
                    "Empieza por los FIXME de los hotspots."
                ),
            }
        )

    # 3) Archivos muy grandes.
    for f in sorted(static.large_files, key=lambda x: x.lines, reverse=True)[:3]:
        recs.append(
            {
                "severity": "medium",
                "title": f"{f.path} tiene {f.lines} líneas",
                "detail": "Dividir módulos grandes reduce complejidad y coste de revisión.",
            }
        )

    # 4) Código duplicado.
    if static.duplicate_units > 0:
        recs.append(
            {
                "severity": "low",
                "title": f"{static.duplicate_units} bloques/archivos duplicados",
                "detail": "Extrae la lógica compartida a un módulo común.",
            }
        )

    # 5) Churn alto (mucha eliminación => inestabilidad).
    total = sum(f.changes for f in analysis.files.values())
    deleted = sum(f.deleted for f in analysis.files.values())
    if total > 0 and deleted / total > 0.4:
        recs.append(
            {
                "severity": "medium",
                "title": "Churn elevado (inestabilidad)",
                "detail": (
                    f"{round(100 * deleted / total)}% de los cambios son borrados. "
                    "Revisa el diseño de los módulos que más rotan."
                ),
            }
        )

    recs.sort(key=lambda r: SEVERITY_ORDER[r["severity"]])
    return recs
