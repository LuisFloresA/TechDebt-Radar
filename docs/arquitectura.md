# Arquitectura

TechDebt Radar analiza la salud técnica de repositorios GitHub sin ejecutar su código. Combina métricas del **historial de Git** (via `git log --numstat`) con **análisis estático del árbol** para producir un score 0-100, un radar por componente y recomendaciones priorizadas.

## Componentes

```
Cliente (React) -> nginx (:80)
   |-- /            -> SPA estática
   |-- /api/*       -> proxy -> FastAPI (:8000) -> Redis/Celery -> Worker
                                                                   |-> clon seguro (aislado + límites)
                                                                   |-> git log --numstat
                                                                   |-> scan estático
                                                                   |-> score + recomendaciones
                                                                   |-> Report (SQLite)
```

- **API (FastAPI)**: expone `POST /api/analyze`, `GET /api/jobs/{id}` y `/api/health*`. Valida URLs, aplica rate limiting y delega el análisis a Celery.
- **Worker (Celery)**: ejecuta la tarea `analyze_repo` (clon, historial, estática, scoring, persistencia).
- **Redis**: broker de la cola de tareas.
- **Frontend (React + Vite)**: dashboard con Chart.js; hace *polling* del job cada 1,5 s.
- **SQLite**: almacena `jobs` y `reports` (métricas JSON).

## Flujo de análisis

1. El cliente envía la URL del repo.
2. La API valida la URL (anti-SSRF) y crea un `Job` (`queued`).
3. El worker clona un snapshot *shallow* (`--depth 50`) en un directorio aislado con límites (tamaño máx., timeout).
4. Ejecuta `git log --numstat --date=short` y parsea autores/cambios por archivo.
5. Escanea la estática (TODO/FIXME, líneas, duplicados, complejidad).
6. Compone el **score** y las **recomendaciones** y persiste el `Report`.
7. La UI hace *polling* y renderiza el dashboard.

## Algoritmo de score (0-100)

Cinco componentes normalizados a 0-100 (mayor = mejor), combinados por ponderación:

| Componente | Peso | Base de cálculo |
|---|---|---|
| Bus factor | 0.20 | % de cambios en archivos con 1 solo autor |
| Hotspots | 0.20 | 1 − (cambios del top-5 / cambios totales) |
| Churn | 0.15 | 1 − (líneas borradas / cambios totales) |
| Deuda técnica | 0.25 | penalización por TODOs, FIXMEs, archivos >500 líneas y duplicados |
| Cadencia | 0.20 | actividad normalizada (commits y autores) |

`score = round(Σ peso_i · componente_i)`. Los mismos componentes son los ejes del radar.

### Detalle por componente

- **Bus factor**: `100·(1 − risky/total)` donde `risky` son cambios en archivos con un único autor.
- **Hotspots**: penaliza la concentración de cambios en pocos archivos.
- **Churn**: penaliza que una proporción alta de cambios sea de eliminación (inestabilidad).
- **Deuda técnica**: `clamp(100 − deuda·2)` con `deuda = todos·2 + fixmes·4 + grandes·3 + duplicados·2`.
- **Cadencia**: 0 si no hay commits; si no, mezcla commits (hasta 10) y autores (hasta 3).

## Recomendaciones

Reglas deterministas sobre las métricas (ver `backend/app/scoring/recommendations.py`):

1. **Alta**: hotspot con un único autor → tests + reparto de propiedad.
2. **Media**: deuda acumulada (TODOs/FIXMEs) por encima de un umbral.
3. **Media**: archivos >500 líneas → dividir el módulo.
4. **Baja**: bloques/archivos duplicados → extraer lógica común.
5. **Media**: churn alto (>40% de eliminaciones) → estabilizar módulos que rotan.

Se ordenan por severidad (alta → baja).

## ADRs

### ADR-001 · Anti-SSRF en el clonado
**Estado:** aceptado. **Decisión:** solo se admiten URLs `https://github.com`; se resuelve el host y se rechaza si no resuelve a IP global; el patrón de ruta está restringido a `owner/repo`. Alternativa (GitPython) rechazada por ampliar la superficie sin beneficio claro en MVP.

### ADR-002 · Análisis asíncrono con Celery + Redis
**Estado:** aceptado. **Decisión:** el clon y el análisis son operaciones largas; una cola desacopla la API de la duración del trabajo y permite reintentos. Alternativa (taskio sincrónico en la petición) rechazada por tiempos de respuesta inaceptables.

### ADR-003 · `git log --numstat` en vez de GitPython para métricas
**Estado:** aceptado. **Decisión:** batch de una sola invocación por repo, más rápido y con formato estable. GitPython se mantiene como dependencia de conveniencia pero no se usa para el análisis.

### ADR-004 · Estática con heurísticos propios (sin Radon)
**Estado:** aceptado (desviación del plan). **Decisión:** se implementa un escáner ligero (complejidad = recuento de palabras clave de control) sin dependencias externas, suficiente para MVP y agnóstico del lenguaje. Radon queda descartado por ser solo Python. Revisar si F5 requiere precisión.

### ADR-005 · Score 0-100 propio y transparente
**Estado:** aceptado. **Decisión:** fórmula simple, documentada y depurable (cada componente es un eje del radar). Sin ML ni cajas negras. El usuario puede explicar cualquier score en 30 segundos.

### ADR-006 · SQLite + jobs/reports
**Estado:** aceptado. **Decisión:** un solo proceso (API + worker) accede; SQLite es suficiente para el volumen de un portafolio y simplifica el deploy. La migración a Postgres queda abierta para F4/F5 si hace falta.

### ADR-007 · Rate limiting en API y nginx
**Estado:** aceptado. **Decisión:** limitador deslizante en memoria en la API (`rate_limit_per_minute`) y `limit_req` en nginx como defensa en profundidad; además un límite de jobs en vuelo para proteger los recursos de clonado.

## Límites de recursos

| Límite | Valor | Config |
|---|---|---|
| Profundidad del clon | 50 commits | `CLONE_DEPTH` |
| Tamaño máximo del repo | 200 MB | `MAX_REPO_SIZE_MB` |
| Timeout del clon | 120 s | `CLONE_TIMEOUT_SECONDS` |
| Rate limit por IP | 5 req/min | `RATE_LIMIT_PER_MINUTE` |
| Jobs en vuelo | 3 | `MAX_IN_FLIGHT_JOBS` |
