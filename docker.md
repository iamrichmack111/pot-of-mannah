# Pot of Mannah v3 — Docker

The v3 container runs the tabbed Flask web app with Gunicorn on port `8012`.

## Quick start

```bash
cp .env.example .env
# edit SECRET_KEY and MANNAH_ADMIN_PASSWORD

docker compose up -d --build
```

Open `http://localhost:8012`.

## Persistence

The Compose file mounts the named volume `mannah-data` at `/data`. The web SQLite database is stored at `/data/mannah_web.db` inside the container.

## Health check

```bash
curl http://127.0.0.1:8012/healthz
```

Expected shape:

```json
{"status":"ok","foods":7413}
```

## Direct Docker

```bash
docker build -t pot-of-mannah:3.0.0 .
docker run --rm -p 8012:8012 \
  -e SECRET_KEY='replace-me' \
  -e MANNAH_ADMIN_PASSWORD='replace-me-too' \
  -v mannah-data:/data \
  pot-of-mannah:3.0.0
```

## GitHub Container Registry

`.github/workflows/container.yml` publishes multi-architecture images to:

```text
ghcr.io/iamrichmack111/pot-of-mannah
```
