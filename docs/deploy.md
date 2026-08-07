# Runbook de despliegue — VPS gratuito (Oracle Cloud Always Free)

Guía para publicar TechDebt Radar en un VPS gratuito con Docker. Sin dominio:
se navega por `http://<IP>:8088` (HTTP). HTTPS con dominio se añade al final
con Caddy sin tocar la app.

## Fase 1 · Crear la infraestructura (consola de Oracle)

1. Alta en `cloud.oracle.com` (correo + verificación; el free tier no cobra).
2. Crear instancia gratuita:
   - Imagen **Ubuntu 22.04** · Shape **`VM.Standard.A1.Flex` (ARM)** · 1 OCPU, ~1 GB
     RAM, marcar *Always Free eligible*.
   - Red (security list / NSG): abrir `22/tcp` (SSH), `80/tcp` (HTTP) de momento.
     No abrir 8001/8088.
   - Guardar la clave privada (`.pem`) y la **IP pública**.
3. Conectar: `ssh -i tu-clave.pem ubuntu@<IP>`

## Fase 2 · Instalar Docker en la VM

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# reconectar la sesion y verificar
newgrp docker
docker --version && docker compose version
```

## Fase 3 · Traer el codigo y configurar

```bash
git clone https://github.com/LuisFloresA/TechDebt-Radar.git
cd TechDebt-Radar
cp .env.prod.example .env
# editar .env segun se desee
```

## Fase 4 · Arrancar

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose ps
```

`docker-compose.prod.yml` ata API (:8001) y frontend (:8088) a `127.0.0.1`,
de forma que la API no es accesible externamente; el frontend la llama por
proxy nginx mismo-origen.

## Fase 5 · Verificar

```bash
curl -s http://127.0.0.1:8001/api/health          # {"status":"ok",...}
curl -s http://127.0.0.1:8088/api/health/ready    # 200
```
Abrir `http://<IP>:8088` en el navegador y hacer un analisis de ejemplo.

> El SQLite vive en el volumen `radar_data`, por lo que persiste frente a
> `down/up`. Para actualizar tras un push: `git pull && docker compose -f
> docker-compose.yml -f docker-compose.prod.yml up -d --build`.

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
Caddy emite y renueva TLS de Let's Encrypt automaticamente.

## (Opcional) HTTPS sin dominio — Cloudflare Tunnel (Quick Tunnel)

Un túnel de Cloudflare da una URL **HTTPS** pública sin necesitar dominio ni
abrir puertos en el Security List.

Instalar `cloudflared` (para ARM/aarch64, como el shape de Oracle):
```bash
sudo curl -fsSL -o /usr/local/bin/cloudflared \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
sudo chmod +x /usr/local/bin/cloudflared
```

Lanzar un túnel rápido hacia el frontend local (`127.0.0.1:8088`):
```bash
nohup cloudflared tunnel --url http://127.0.0.1:8088 --no-autoupdate \
  > /home/ubuntu/cloudflared.log 2>&1 &
sleep 12; grep trycloudflare /home/ubuntu/cloudflared.log
```
Abre la URL `https://<aleatorio>.trycloudflare.com` que aparezca en el log.

> **Limitaciones**: sin cuenta/dominio la URL es **aleatoria y efímera** (cambia
> cada vez que lanzas el túnel y muere al reiniciar la VM). Es perfecta para
> una demo, no para producción. Para una URL estable se necesita un **named
> tunnel** con un dominio en Cloudflare (plan Free):
> `https://developers.cloudflare.com/cloudflare-one/connections/connect-apps`

Para detener el túnel: `pkill -f cloudflared`.
> Como el túnel ya da HTTPS, podrías volver a atar el frontend a `127.0.0.1`
> en `docker-compose.prod.yml` (más seguro: solo Cloudflare lo alcanza), pero
> deja así `0.0.0.0:8088` si también quieres acceso por IP directa.

## Notas de carga (free tier)

1 GB de RAM alcanza justos para API + worker + Redis + procesos `git`. Si el
worker muere por OOM, reduzca `MAX_IN_FLIGHT_JOBS=1` o `MAX_REPO_SIZE_MB` y
reinicie. Considera sumar swap en la VM.