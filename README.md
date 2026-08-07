# TechDebt Radar

Analítica de salud técnica de repositorios. Introduces una URL de GitHub y la plataforma analiza el historial de Git y el árbol de código para producir un dashboard con métricas accionables: deuda técnica, hotspots, bus factor, churn y un score de salud global.

**Estado:** F2 — deuda estática + score 0-100 + radar. Ver README de planificación en `docs/planificacion/`.

---

## F1 · Git Analytics MVP

Backend de análisis asíncrono del historial de repositorios GitHub + dashboard interactivo:

- `POST /api/analyze` crea un *job* y lo envía a Celery vía Redis.
- El worker clona el repo de forma **segura** (anti-SSRF, shallow `--depth`, límite de tamaño), extrae `git log --numstat` y calcula **hotspots**, **churn**, **bus factor** y **cadencia**.
- `GET /api/jobs/{id}` devuelve el estado y, si terminó, el reporte con las métricas.
- Dashboard (React 19 + Chart.js): form de análisis con *polling*, cards de resumen y widgets **Hotspots**, **Churn**, **Bus factor** y **Cadencia**.
- **Modo demo** sin red: semilla embebida (express/express) con botón "Ver demo".

## F2 · Deuda estática + Score de salud

Extiende el pipeline con análisis estático del árbol y scoring:

- **Escaneo estático** del snapshot clonado: TODOs/FIXMEs, líneas por archivo, archivos grandes (>500 líneas), bloques duplicados y una heurística de complejidad por archivo (heurísticos básicos, sin dependencias externas).
- **Score 0-100** compuesto por 5 ejes ponderados: **bus factor**, **hotspots**, **churn**, **deuda técnica** y **cadencia**. Cada eje es una dimensión del radar (0-100).
- **Radar de componentes** y **gauge** del score global en el dashboard.
- **Recomendaciones priorizadas** (alta/media/baja) generadas por reglas sobre las métricas (hotspot de un solo autor, deuda acumulada, archivos grandes, duplicados, churn alto).

```
Cliente -> API (FastAPI) -> Redis/Celery -> Worker
   |-> clon seguro (aislado + límites)
   |-> git log --numstat -> hotspots, churn, bus factor, cadencia
   |-> scan estático -> TODOs, líneas, duplicados, complejidad
   |-> scoring ponderado -> score 0-100 + radar + recomendaciones
   |-> guarda Report (SQLite)
```

## Quickstart

```bash
docker compose up --build
```

Servicios: `redis`, `api` (:8001), `worker`, `frontend` (:8088).

```bash
curl http://localhost:8001/api/health        # {"status":"ok", ...}
curl http://localhost:8001/api/health/ready  # 200

# Analizar un repositorio público
curl -X POST http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com/LuisFloresA/TechDebt-Radar"}'
# -> 202 {"id":1, "status":"queued", ...}

# Estado / reporte
curl http://localhost:8001/api/jobs/1
# -> {"job":{"status":"succeeded",...},"report":{"metrics":{...}}}
```

## Desarrollo local

### Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

Tests y lint:

```bash
pytest
ruff check .
```

### Frontend

```bash
cd frontend
npm install
npm run dev     # http://localhost:5173 (proxy /api -> :8000)
npm test
npm run build
```

## Estructura

```
techdebt-radar/
├── backend/            # FastAPI + (/api, /core)
├── frontend/           # React 19 + Vite
├── docker-compose.yml
├── .github/workflows/  # CI
└── docs/               # planificación
```

## Roadmap

F0 esqueleto → F1 Git Analytics MVP → F2 deuda + score (✓) → F3 contenido/deploy → F4 (opt) integración. Ver `docs/planificacion/`.

## Licencia

MIT.

## Autor

Luis Patricio Flores Álvarez — [GitHub](https://github.com/LuisFloresA)