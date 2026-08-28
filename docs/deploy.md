# Runbook de despliegue — VPS Linux con Docker

Guía para publicar TechDebt Radar en un servidor VPS Linux con Docker.
Sin dominio: se accede por `http://<IP_PUBLICA>:8088` (HTTP).
Para HTTPS con dominio, se añade un reverse proxy como Caddy o Nginx al frente.

## Fase 1 · Preparar la infraestructura (VPS Linux)

1. Contratar o inicializar un servidor VPS (Ubuntu 22.04 / 24.04 LTS o Debian) en tu proveedor de preferencia.
2. Especificaciones recomendadas:
   - 1–2 vCPU, 2–4 GB de RAM (o mínimo 1 GB + Swap habilitado).
   - Abrir en el firewall/Security Group: puerto `22/tcp` (SSH) y `8088/tcp` (HTTP frontend). Mantener cerrados los puertos internos (8001, 6379).
   - Guardar la clave privada SSH (`.pem` o `id_rsa`) y la **IP pública** del servidor.
3. Conectar al servidor: `ssh -i <tu-clave.pem> <usuario>@<IP_PUBLICA>`

## Fase 2 · Instalar Docker en la máquina

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# reconectar la sesión o aplicar grupo
newgrp docker
docker --version && docker compose version
```

## Fase 3 · Traer el código y configurar variables

```bash
git clone https://github.com/LuisFloresA/TechDebt-Radar.git
cd TechDebt-Radar
cp .env.prod.example .env
# editar .env según sea necesario
```

## Fase 4 · Iniciar contenedores

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose ps
```

`docker-compose.prod.yml` ata la API (:8001) internamente a `127.0.0.1`,
de forma que la API no es accesible directamente desde internet; el frontend
la consulta mediante el reverse proxy Nginx del contenedor web.

## Fase 5 · Verificar funcionamiento

```bash
curl -s http://127.0.0.1:8001/api/health          # {"status":"ok",...}
curl -s http://127.0.0.1:8088/api/health/ready    # 200
```
Abrir `http://<IP_PUBLICA>:8088` en el navegador y ejecutar un análisis de prueba.

> La base de datos SQLite vive en el volumen `radar_data`, por lo que persiste ante
> reinicios de contenedores (`down/up`). Para actualizar tras nuevos commits:
> `git pull origin main && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build`.

## (Opcional) HTTPS con dominio y Caddy

```bash
sudo apt update && sudo apt install -y caddy
sudo tee /etc/caddy/Caddyfile >/dev/null <<'EOF'
tu-dominio.com {
    reverse_proxy 127.0.0.1:8088
}
EOF
sudo systemctl restart caddy
```
Caddy emite y renueva certificados TLS de Let's Encrypt automáticamente.

## (Opcional) HTTPS con Cloudflare Tunnel (Quick Tunnel)

Un túnel de Cloudflare permite obtener una URL **HTTPS** sin necesidad de abrir puertos de entrada en el firewall.

Instalar `cloudflared` (según la arquitectura de tu procesador):
```bash
# Para x86_64:
sudo curl -fsSL -o /usr/local/bin/cloudflared \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64

# O para ARM64:
# sudo curl -fsSL -o /usr/local/bin/cloudflared \
#   https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64

sudo chmod +x /usr/local/bin/cloudflared
```

Lanzar un túnel temporal apuntando al frontend (`127.0.0.1:8088`):
```bash
nohup cloudflared tunnel --url http://127.0.0.1:8088 --no-autoupdate \
  > /tmp/cloudflared.log 2>&1 &
sleep 8; grep trycloudflare /tmp/cloudflared.log
```

Para detener el túnel: `pkill -f cloudflared`.

## Notas de dimensionamiento y memoria

Si el servidor cuenta con 1 GB o poca memoria RAM y el worker se detiene por OOM (Out Of Memory) al clonar repositorios pesados:
1. En `.env` establece `MAX_IN_FLIGHT_JOBS=1` y reduce `MAX_REPO_SIZE_MB=100`.
2. Añade un archivo de intercambio (swap) en la máquina host Linux:
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```