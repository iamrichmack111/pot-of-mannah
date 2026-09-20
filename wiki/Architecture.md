# Architecture

```text
Browser
   │
   ▼
Flask web app (mannah_web)
   │
   ├── user/profile/log SQLite database
   │
   ├── Pot of Mannah read-only food SQLite database
   │
   ├── USDA FoodData Central (optional lookup)
   │
   └── Open Food Facts (optional lookup)

Textual TUI (pot_of_mannah)
   │
   └── local indexed SQLite datasets
```

## Important paths

- `mannah_web/app.py` — Flask routes, database migrations, nutrient targets, search/import APIs.
- `mannah_web/templates/` — web pages and tabs.
- `mannah_web/static/` — theme, animation, and interaction code.
- `pot_of_mannah/` — original terminal application.
- `pot_of_mannah/data/food.db` — canonical bundled food data.
- `scripts/seed_demo.py` — deterministic demo content.
- `scripts/playwright_capture.py` — screenshots and browser demo.
- `Dockerfile` / `docker-compose.yml` — container packaging.
