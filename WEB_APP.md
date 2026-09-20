# Pot of Mannah Web — v3.0.0

The web interface is a dark, local-first nutrition journal built on the Pot of Mannah food database.

## Permanent app tabs

- **Today** — calories, macros, key gaps, recent foods, hydration, quick-add foods.
- **Diary** — meal log, exact grams, water, notes, repeat/remove entries, day tools.
- **Log Food** — local/global search, exact gram amount, live portion math, favorites and recents.
- **Nutrition** — Overview, Missing, Macros, Vitamins, Minerals, Foods to Add.
- **Planner** — Smart Picks, nutrient gaps, and next-meal planning tools.
- **Progress** — Overview, Calories, Consistency, Weight, Achievements.
- **Foods** — Saved Foods, Favorites, Create Custom.

Account has Personal, Goals, Themes, and Security sub-tabs. Admin is separate from normal tracking navigation.

## Food data

The bundled Pot of Mannah SQLite database contains 7,413 foods and 48 source fields. Food nutrition is normalized around values per 100 g. Logged meals save a nutrient snapshot so old entries do not silently change when a food record changes later.

Optional online search is also available through USDA FoodData Central and Open Food Facts. Imported results are saved locally.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python web.py
```

Open `http://127.0.0.1:8012`.

For LAN access:

```bash
HOST=0.0.0.0 python web.py
```

## Playwright media

```bash
pip install -r requirements-dev.txt
python -m playwright install chromium
export MANNAH_WEB_DB=/tmp/mannah-demo.db
python scripts/seed_demo.py
python web.py &
python scripts/playwright_capture.py
```

## Admin

Override the seeded local admin before launch:

```bash
export MANNAH_ADMIN_USERNAME=admin
export MANNAH_ADMIN_PASSWORD='choose-a-new-password'
python web.py
```

Nutrition targets and gap suggestions are informational reference tools, not diagnoses or medical prescriptions.
