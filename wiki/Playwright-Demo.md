# Playwright Demo

Pot of Mannah includes a reproducible browser-media pipeline.

## Capture locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m playwright install chromium

export MANNAH_WEB_DB=/tmp/mannah-demo.db
python scripts/seed_demo.py
python web.py &
python scripts/playwright_capture.py
```

Outputs:

```text
media/screenshots/01-today.png
media/screenshots/02-diary.png
media/screenshots/03-log-food.png
media/screenshots/04-nutrition-missing.png
media/screenshots/05-planner.png
media/screenshots/06-progress.png
media/screenshots/07-foods.png
media/demo/pot-of-mannah-demo.webm
media/demo/pot-of-mannah-demo.mp4
```

![Progress](https://raw.githubusercontent.com/iamrichmack111/pot-of-mannah/main/media/screenshots/06-progress.png)
