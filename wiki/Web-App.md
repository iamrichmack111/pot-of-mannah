# Web App

The web interface is organized around seven permanent application tabs:

1. **Today** — daily calorie/macronutrient summary, current nutrient gaps, recent entries, hydration, quick foods.
2. **Diary** — meals, water, notes, and day tools.
3. **Log Food** — local/global food search, exact gram entry, favorites, recents, per-100 g source values, live portion math.
4. **Nutrition** — overview, missing nutrients, macros, vitamins, minerals, foods to add.
5. **Planner** — food suggestions based on current gaps.
6. **Progress** — 30-day trends, consistency, weight history, achievements.
7. **Foods** — saved/imported foods, favorites, and custom foods.

Account and Admin are kept separate from the primary tracking workflow.

## Screenshots

![Diary](https://raw.githubusercontent.com/iamrichmack111/pot-of-mannah/main/media/screenshots/02-diary.png)

![Log Food](https://raw.githubusercontent.com/iamrichmack111/pot-of-mannah/main/media/screenshots/03-log-food.png)

![Nutrition gaps](https://raw.githubusercontent.com/iamrichmack111/pot-of-mannah/main/media/screenshots/04-nutrition-missing.png)

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python web.py
```

Open `http://127.0.0.1:8012`.

To expose it on your LAN:

```bash
HOST=0.0.0.0 python web.py
```
