# Docker

## Docker Compose

```bash
cp .env.example .env
# edit SECRET_KEY and MANNAH_ADMIN_PASSWORD

docker compose up -d --build
```

Open `http://localhost:8012`.

Persistent user data is stored in the `mannah-data` Docker volume.

## Plain Docker

```bash
docker build -t pot-of-mannah:3.0.0 .
docker run --rm -p 8012:8012 \
  -e SECRET_KEY='change-me' \
  -e MANNAH_ADMIN_PASSWORD='change-me-too' \
  -v mannah-data:/data \
  pot-of-mannah:3.0.0
```

## GHCR

The Container workflow publishes multi-architecture images to:

```text
ghcr.io/iamrichmack111/pot-of-mannah
```

Published tags include `latest`, branch/tag names, and commit SHA aliases.
