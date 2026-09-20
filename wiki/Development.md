# Development

## Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Tests

```bash
pytest -q
python -m compileall -q pot_of_mannah mannah_web scripts
```

## Web app

```bash
python web.py
```

## Demo media

```bash
export MANNAH_WEB_DB=/tmp/mannah-demo.db
python scripts/seed_demo.py
python web.py &
python scripts/playwright_capture.py
```

## Docker

```bash
docker compose up --build
```
