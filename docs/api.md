# API

OpenAPI interactivo disponible en `GET /docs` cuando la API corre en local (vía Docker: `http://localhost:8001/docs`).

## Endpoints

### `GET /api/health`
Estado básico del servicio.

```bash
curl http://localhost:8001/api/health
# {"status":"ok","version":"0.1.0"}
```

### `GET /api/health/ready`
Indica que la base de datos está lista. Devuelve 200 cuando lo está.

```bash
curl http://localhost:8001/api/health/ready   # 200
```

### `POST /api/analyze`
Inicia el análisis asíncrono de un repositorio GitHub público.

- Body: `{"url": "https://github.com/owner/repo"}`
- Respuesta: `202 Accepted` con el `Job` creado.
- `422`: URL inválida (no GitHub, sin https, ruta malformada o host no verificable).
- `429`: demasiadas peticiones por IP o demasiados análisis en vuelo.

```bash
curl -X POST http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com/octocat/Hello-World"}'
# -> 202 {"id":1,"url":"...","status":"queued","progress":0,"error":null,...}
```

### `GET /api/jobs/{id}`
Estado del job y, si terminó, el reporte.

- `200`: `{"job": {...}, "report": {"metrics": {...}}}`.
- `404`: job inexistente.

```bash
curl http://localhost:8001/api/jobs/1
```

## Modelo del reporte (`metrics`)

```jsonc
{
  "summary": { "total_commits": 50, "total_authors": 26, "files_analyzed": 215 },
  "hotspots":  [ { "path", "changes", "added", "deleted", "commits", "authors" } ],
  "churn":     [ { "path", "added", "deleted", "churn" } ],
  "bus_factor":[ { "path", "authors", "changes" } ],
  "cadence":   { "2026-01-01": 3, "2026-01-02": 1 },
  "static": {
    "files": [ { "path", "lines", "todos", "fixmes", "complexity" } ],
    "total_todos": 12, "total_fixmes": 3, "total_lines": 12345,
    "large_files": 2, "duplicate_units": 1
  },
  "score": {
    "score": 62,
    "components": { "bus_factor": 80, "hotspots": 55, "churn": 70,
                    "tech_debt": 60, "cadence": 45 }
  },
  "recommendations": [ { "severity": "high|medium|low", "title", "detail" } ]
}
```

## Errores

Todos los errores usan el formato FastAPI `{"detail": "mensaje"}` con los códigos:

| Código | Caso |
|---|---|
| 422 | URL inválida o formato incorrecto |
| 429 | Rate limit por IP o límite de jobs en vuelo |
| 404 | Job no encontrado |

## Notas de seguridad

- `POST /api/analyze` está limitado por IP (5 req/min por defecto) y por jobs en vuelo (3 por defecto).
- El worker solo admite repositorios GitHub públicos (anti-SSRF) y nunca ejecuta código del repo.
