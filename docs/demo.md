# Demo

Guion de demostración de TechDebt Radar (útil para portafolio, entrevistas o el README).

## 1. Arranque

```bash
docker compose up --build
```

Espera a que los 4 servicios estén *healthy* (`docker compose ps`). La app queda en:

- Frontend: http://localhost:8088
- API: http://localhost:8001 (Swagger en `/docs`)

## 2. Ruta corta: modo demo sin red

1. Abre http://localhost:8088.
2. Pulsa **"Ver demo"**.
3. Aparece el dashboard completo del repo `expressjs/express` (semilla embebida, sin red):
   - Gauge de **score de salud** (0-100) y **radar** de los 5 componentes.
   - Widgets: **Hotspots**, **Churn**, **Bus factor**, **Cadencia**.
   - **Deuda técnica estática** (TODOs/FIXMEs, líneas, complejidad).
   - **Recomendaciones** priorizadas.

*Rapidez: el demo funciona aunque no haya backend.*

## 3. Ruta completa: análisis real

1. Pega una URL de un repo público, p. ej. `https://github.com/octocat/Hello-World` (muy rápido) o `https://github.com/expressjs/express` (más rico).
2. Pulsa **"Analizar"**.
3. Verás el progreso (`Analizando … 55%`) y al terminar, el dashboard con datos reales.

## 4. Qué contar durante la demo

- **Flujo**: el clonado es *shallow* y con límites; el análisis es asíncrono (Celery + Redis).
- **Score**: cada número es explicable — 5 componentes ponderados, cada uno visible en el radar.
- **Recomendaciones**: salen de reglas sobre las métricas (hotspot de un solo autor, deuda, archivos grandes).
- **Seguridad**: solo GitHub público, anti-SSRF, rate limiting, el código nunca se ejecuta.
- **Demo offline**: la semilla embebida demuestra que la app se puede mostrar sin infraestructura.

## Problemas frecuentes

| Síntoma | Causa / solución |
|---|---|
| "No se pudo clonar" | Repo privado o inexistente; usa un repo público |
| "Demasiadas peticiones" | Espera 1 minuto (rate limit por IP) |
| El análisis no avanza | Comprueba `docker compose ps` (redis/worker) y los logs: `docker compose logs worker` |
