# TechDebt Radar

Analítica de salud técnica de repositorios. Introduces una URL de GitHub y la plataforma analiza el historial de Git y el árbol de código para producir un dashboard con métricas accionables: deuda técnica, hotspots, bus factor, churn y un score de salud global.

Proyecto de portafolio. Estado: planificado — implementación por fases.

---

## Descripción

TechDebt Radar combina el análisis del **historial de Git** (git log/blame) con la **estática del código** (tamaño, duplicados, complejidad, TODOs) para estimar la mantenibilidad de un repositorio mediante indicadores propios. No depende de LLM ni de claves, por lo que el demo es siempre disponible.

### Funcionalidades

- Análisis de un repositorio por URL de GitHub pública o un `.zip`.
- Análisis asíncrono en background (Celery + Redis).
- Métricas de **hotspots**, **churn**, **bus factor**, **deuda técnica** y **cadencia** de commits.
- **Score de salud** (0-100) con desglose por componente.
- **Recomendaciones** priorizadas de mantenimiento.
- Dashboard interactivo con Chart.js (radar, heatmaps, líneas de actividad).
- Modo demo embebido con repositorios pre-analizados.

### Stack

- Backend: Python 3.14, FastAPI, Pydantic v2
- Git: GitPython + `git log` CLI batch
- Estática: Radon (complejidad) y heurísticos de duplicados
- Cola de tareas: Celery + Redis
- Storage: SQLite (reportes)
- Frontend: React 19, TypeScript, Vite, Chart.js
- Infra: Docker y Docker Compose, GitHub Actions

---

## Arquitectura

```
Cliente (React) -> API (FastAPI) -> Celery/Redis -> Worker
                                                     |-> Clonar snapshot (aislado)
                                                     |-> git log/blame -> hotspots, churn, bus factor
                                                     |-> Estática -> TODOs/FIXME, tamaño, duplicados
                                                     |-> Compute score + recomendaciones
                                                     |
                                            Storage (SQLite reports)
```

Flujo:

1. `POST /api/analyze` recibe la URL del repo y crea un job.
2. El worker clona un snapshot aislado y con límites.
3. Extrae el historial con `git log --numstat` y analiza autores y cambios por archivo.
4. Escanea la estática del árbol de código y compone el score.
5. La UI hace *polling* y muestra el dashboard con las recomendaciones.

Endpoints documentados en `/docs` (OpenAPI).

---

## Fases de desarrollo

La implementación se divide en fases independientes, cada una con un entregable usable.

### F0 — Esqueleto self-host (2-3 días)
- Repositorio base con `docker-compose`, scaffolds de FastAPI y React.
- Endpoints `/health` y `/health/ready`.
- Pipeline de CI (lint, test, build).

Criterio de salida: `docker compose up` levanta la pila y los `/health` responden OK.

### F1 — Git Analytics MVP (6-8 días)
- Clonado seguro del repositorio con límites.
- Extracción de `git log --numstat` para hotspots, churn y bus factor.
- API de reportes y dashboard base con Chart.js.
- Modo demo con repositorio pre-analizado.

Criterio de salida: analizar un repo y ver los indicadores de historial en el dashboard.

### F2 — Deuda estática y score (3-4 días)
- Conteo de TODOs/FIXMEs, tamaño y duplicados, complejidad.
- Algoritmo propio de score de salud (0-100) y radar.
- Recomendaciones priorizadas.

Criterio de salida: el reporte incluye score, desglose y recomendaciones accionables.

### F3 — Contenido y hardening (3-4 días)
- README completo y `docs/` (arquitectura, api, demo, seguridad, ADRs).
- Hardening: rate limiting, CSP, validación de rutas, límites de clonado, cancel de jobs.
- Tests con cobertura y CI mejorado.
- Write-up técnico asociado.

Criterio de salida: documentación completa y postura de seguridad endurecida, sin depender de un hosting externo.

### F4 — Deploy (independiente, 1-2 días)
- Despliegue en Render/OCI con badge de CI.
- Criterio de salida: servicio público con demo funcional.

### F5 — Integración ampliada (opcional, 5-7 días)
- Soporte de GitLab/Bitbucket.
- Historial *over-time* al re-analizar el mismo repositorio.
- Autenticación y proyectos por cuenta.

---

## Documentación

- `docs/arquitectura.md` — decisiones de diseño (ADRs) y algoritmo de score.
- `docs/api.md` — endpoints y ejemplos de `curl`.
- `docs/demo.md` — guión de demostración.
- `docs/seguridad.md` — postura de seguridad y detalle de amenazas.

---

## Seguridad

Aunque no ejecuta código, acepta repositorios de terceros:

- El código del repositorio **nunca se ejecuta**: solo `git log`/`blame` y análisis estático en texto.
- Clonado en directorio aislado, clon *shallow* y límites de tamaño.
- Validación de URL a GitHub para evitar SSRF.
- Validación de rutas bajo la raíz del repositorio (*path traversal*).
- CSP estricta y render seguro en la interfaz.
- Rate limiting en `/api/analyze` y cancel de jobs.

Ver `docs/seguridad.md` para el detalle de amenazas y mitigaciones.

---

## Estructura del repositorio

```
techdebt-radar/
├── backend/            # FastAPI + workers Celery
├── frontend/           # React 19 + Vite
├── docker-compose.yml
├── .github/workflows/  # CI/CD
└── docs/
```

---

## Licencia

MIT.

## Autor

Luis Patricio Flores Álvarez — [GitHub](https://github.com/LuisFloresA)