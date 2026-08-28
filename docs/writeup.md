# Write-up técnico

## TechDebt Radar — analítica de salud técnica para repositorios

### Resumen

TechDebt Radar es una plataforma *self-hosted* que, a partir de la URL de un repositorio GitHub, produce un **diagnóstico de mantenibilidad** en tres bloques: métricas de **historial de Git** (hotspots, churn, bus factor, cadencia), **deuda estática** (TODOs, tamaño, duplicados, complejidad) y un **score de salud 0-100** con radar y recomendaciones priorizadas. Todo con heurísticos deterministas y sin ejecutar código del repositorio ni depender de claves o LLM.

### Problema

La deuda técnica es invisible hasta que cuesta caro. Herramientas como SonarQube o Code Climate son potentes pero pesadas, con suscripciones y complejas de desplegar. Un desarrollador con un repo público —o un entrevistador que quiere evaluar la salud de una base— no necesita un SAST industrial: necesita **indicadores claros y explicables** sobre dónde duele el código.

### Enfoque

Dos fuentes de datos que se complementan:

1. **Historial (comportamiento real)**: `git log --numstat` sobre un clon *shallow*. Qué archivos concentran cambios (hotspots), cuánto se reescribe (churn), cuántas personas tocan cada archivo (bus factor) y la cadencia de commits.
2. **Estática (estado actual del snapshot)**: conteo de TODO/FIXME, líneas por archivo, archivos grandes, duplicados y una heurística de complejidad por recuento de palabras clave de control.

Con eso se calcula un **score 0-100** como promedio ponderado de 5 componentes (bus factor 20%, hotspots 20%, churn 15%, deuda 25%, cadencia 20%). Cada componente es un eje del radar, lo que hace el score **transparente y depurable**: cualquiera puede explicar un número en 30 segundos.

Las **recomendaciones** se generan con reglas deterministas sobre las métricas: un hotspot tocado por una sola persona (riesgo de bus factor) → tests y reparto de propiedad; N TODOs/FIXMEs → plan de pago; un archivo de 900 líneas → dividir; duplicados → extraer lógica común; churn alto → estabilizar.

### Decisiones clave (resumen de ADRs)

- **Anti-SSRF** desde el primer día: solo `github.com`, resolución de IP global, patrón de ruta estricto.
- **Análisis asíncrono** con Celery + Redis para no bloquear la API con clonados de minutos.
- **`git log --numstat` en batch** en lugar de recorrer objetos con GitPython: más rápido y estable.
- **Heurísticos propios** para la estática (desviación del plan que proponía Radon): sin dependencias externas y agnósticos del lenguaje; suficiente para el objetivo del MVP.
- **Score propio** (no radon-cli, no sonar): simple, documentado y auditable.

### Seguridad

Postura de seguridad completa en `docs/seguridad.md`: validación de URLs (anti-SSRF), clon aislado con límites de tamaño/tiempo, **rate limiting** por IP y de jobs en vuelo, **CSP** estricta y headers de seguridad en nginx, y el principio central de que **el código del repo nunca se ejecuta**.

### Cómo está construido

| Capa | Tecnología |
|---|---|
| Backend | Python 3.14, FastAPI, Pydantic v2 |
| Cola | Celery + Redis |
| Persistencia | SQLite (jobs + reports JSON) |
| Git | CLI `git` en subprocess (batch) |
| Frontend | React 19, TypeScript, Vite, Chart.js |
| Infra | Docker Compose (redis, api, worker, frontend-nginx) |
| Calidad | pytest + coverage, ruff, vitest, typecheck, build en GitHub Actions |

### Resultados y validación

- **Tests**: 25 en backend (pytest, incluido un pipeline *eager* end-to-end con repo ficticio), 11 en frontend (vitest + testing-library).
- **E2E manual**: análisis real de `octocat/Hello-World` y `expressjs/express` (el segundo también alimenta la semilla del demo offline).
- **Demo offline**: el dashboard funciona sin infraestructura gracias a una semilla embebida, ideal para portafolio y entrevistas.

### Qué seguiría (F4-F5)

- **F4 · Deploy** (fase independiente): publicación en VPS / Cloud con badge de CI.
- **F5 · Integración ampliada**: soporte de GitLab/Bitbucket, tendencia del score *over-time* al re-analizar, autenticación y proyectos.

### Aprendizajes

- El `git log --numstat` en batch es sorprendentemente potente y barato para métricas de historial.
- Un score opaco genera desconfianza; el radar por componentes hace la métrica **explicable**.
- Limitar recursos (profundidad, tamaño, jobs en vuelo) desde el día 1 evitó que el MVP fuera abusable.
- El modo demo offline separa el "mostrar la app" del "tener infraestructura levantada".
