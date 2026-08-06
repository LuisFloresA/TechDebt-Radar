# TechDebt Radar

Analítica de salud técnica de repositorios. Introduces una URL de GitHub y la plataforma analiza el historial de Git y el árbol de código para producir un dashboard con métricas accionables: deuda técnica, hotspots, bus factor, churn y un score de salud global.

**Estado:** F0 — esqueleto self-host (ver README de planificación en `docs/`).

---

## F0 · Esqueleto self-host

Esta fase entrega la pila base funcionando con Docker Compose:

- Backend FastAPI con endpoints de salud `/api/health` y `/api/health/ready`.
- Frontend React 19 + Vite + TypeScript con *health badge* que consulta la API.
- Pipeline de CI (lint, test, build) en GitHub Actions.
- Criterio de salida: `docker compose up` levanta la pila y `/api/health` responden `OK`.

### Stack

| Capa      | Tecnología                              |
|-----------|-----------------------------------------|
| Backend   | Python 3.14 · FastAPI · pydantic v2      |
| Frontend  | React 19 · TypeScript 5 · Vite · Chart.js (F1) |
| Infra     | Docker + Docker Compose · GitHub Actions |
| Storage   | SQLite (volume)                          |

## Quickstart

```bash
docker compose up --build
```

- API:  http://localhost:8001 (`/docs` para OpenAPI)
- Front: http://localhost:8088

```bash
curl http://localhost:8001/api/health        # {"status":"ok", ...}
curl http://localhost:8001/api/health/ready  # 200
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

F0 esqueleto → F1 Git Analytics MVP → F2 deuda + score → F3 contenido/deploy → F4 (opt) integración. Ver `docs/planificacion/`.

## Licencia

MIT.

## Autor

Luis Patricio Flores Álvarez — [GitHub](https://github.com/LuisFloresA)