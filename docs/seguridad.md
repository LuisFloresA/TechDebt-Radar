# Seguridad

Postura de seguridad de TechDebt Radar. El servicio acepta repositorios de terceros, por lo que la superficie principal de riesgo es el **clonado y procesado de contenido externo**. El código del repositorio **nunca se ejecuta**: solo se leen con `git log`/`git blame` y análisis estático de texto.

## Modelo de amenazas

| Amenaza | Impacto | Mitigación |
|---|---|---|
| SSRF vía URL maliciosa | Acceso a red interna | Solo hosts github.com; resolución de IP global; esquema https |
| Clonar repositorios gigantes (DoS) | Agotar disco/CPU | Clon shallow `--depth 50`, `MAX_REPO_SIZE_MB` (200), timeout |
| Abuso del endpoint de análisis | Sobrecarga de la cola | Rate limit por IP (5/min) + máximo de jobs en vuelo (3) |
| *Path traversal* en rutas | Lectura de archivos fuera del repo | Rutas derivadas del walk de archivos; storage aislado por job bajo la raíz |
| Contenido HTML malicioso en la UI | XSS | React escapa texto por defecto; CSP estricta; sin `dangerouslySetInnerHTML` |
| Carga de datos | Integridad de reportes | Validación de URL previa al clon |

## Defensas en profundidad

### 1. Validación de URL (anti-SSRF) — `backend/app/clone/validation.py`
- Solo se aceptan URLs `https://github.com` o `www.github.com`.
- El host debe resolver a una dirección IP **global** (se rechaza si es privada/reservada o no resuelve).
- La ruta debe encajar `owner/repo` y no contener `..`.

### 2. Clonado seguro — `backend/app/clone/clone.py`
- Clon *shallow* (`--depth`) y `--no-tags`; con una rama concreta usa `--single-branch --branch <rama>`, y con `"all"` omite `--single-branch`.
- Listado de ramas (`ls-remote`) con timeout propio y cache corta, sin clonar el árbol.
- Directorio aislado por job bajo el storage (`job-{id}`), verificado con `resolve().is_relative_to(base)`.
- Límites de tamaño y timeout; `GIT_TERMINAL_PROMPT=0` para evitar prompts.
- El código nunca se ejecuta (no hay `exec`, `eval` ni contenedores de build).

### 3. Rate limiting — `backend/app/core/ratelimit.py`
- Ventana deslizante en memoria por IP cliente (respeta `X-Forwarded-For` de nginx).
- Se aplica en `POST /api/analyze`; además hay un límite de **jobs en vuelo** para no saturar el worker.

### 4. Headers HTTP y CSP — `frontend/nginx.conf`
- `Content-Security-Policy`: `default-src 'self'`, sin inline scripts, `frame-ancestors 'none'`.
- `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy` (cámara/mic/geo/pago denegadas), `Cross-Origin-Opener-Policy: same-origin`.
- `limit_req` en `/api/analyze` a nivel de proxy (defensa adicional).

### 5. Contenedores
- Imágenes: usuario no root (`USER app`), Python slim.
- El worker y la API comparten solo el volumen de datos (`radar_data`).
- Redis sin exposición a host (red interna de compose).

## Límites recomendados de configuración

Revisar `.env.example`:

```ini
RATE_LIMIT_PER_MINUTE=5
MAX_IN_FLIGHT_JOBS=3
MAX_REPO_SIZE_MB=200
CLONE_DEPTH=50
CLONE_TIMEOUT_SECONDS=120
LS_REMOTE_TIMEOUT_SECONDS=20
```

## Pendientes / mejoras futuras

- Postgres en vez de SQLite si se escala (ADR-006).
- Cancel de jobs en vuelo desde la API (hoy el límite es preventivo).
- Rate limit distribuido (Redis) si se despliega con más de un worker.
- HSTS y redirección a HTTPS al publicar (F4).
