# Pot of Mannah

A keyboard-first Textual nutrition, pantry, menu-planning, exercise, and notes application backed by indexed SQLite reference datasets.

## Highlights

- Search 7,000+ foods with macro and micronutrient details.
- Persistent daily food log with meal labels and gram-based nutrient scaling.
- Pantry inventory with available quantities.
- **Menu Maker** creates breakfast, lunch, and dinner using only foods currently in your pantry.
- Daily macro and micronutrient gap analysis.
- Exercise library plus persistent workout-set logging.
- General, food, workout, and daily-journal notes.
- Favorites for foods and exercises.
- Context-sensitive `?` instructions on every menu.
- Export a daily report as Markdown, JSON, or CSV.
- Personal data is isolated in `mannah.db`; packaged reference databases remain read-only.

## Install

```bash
bash install.sh
source .venv/bin/activate
pot-of-mannah
```

Or from an existing virtual environment:

```bash
pip install -e .
pot-of-mannah
```

## Core keys

| Key | Action |
|---|---|
| `?` | Instructions for the active menu |
| `Ctrl+K` | Search |
| `A` | Log food / exercise set |
| `P` | Add selected food to Pantry |
| `M` | Build a pantry menu |
| `L` | Log generated menu |
| `U` | Update pantry quantity |
| `F` | Favorite / unfavorite selected food or exercise |
| `N` | New note |
| `E` | Export report |
| `Delete` | Delete selected food-log or pantry row |
| `R` | Refresh |
| `Q` | Quit |

## Pantry Menu Maker

1. Open **Food** and search for foods you have.
2. Highlight a food and press `P`.
3. Enter the number of grams available.
4. Repeat for your pantry ingredients.
5. Press `M` from Pantry, Dashboard, or Menu Maker.
6. The planner builds breakfast, lunch, and dinner from pantry foods only.
7. Press `L` to log the generated menu and deduct the planned quantities from Pantry.

The planner uses your configured calorie/protein goals plus fiber and micronutrient density to score pantry foods. It runs locally and does not invent ingredients that are not in Pantry.

## Reports

Press `E` and choose:

- Markdown: human-readable daily report
- CSV: food-log spreadsheet export
- JSON: full structured daily data, nutrient gaps, workout sets, and notes

Reports are written to:

```text
~/Downloads/pot-of-mannah-reports/
```

## Data model

Reference data ships inside the package:

```text
pot_of_mannah/data/food.db
pot_of_mannah/data/exercise.db
```

User data is stored separately through `platformdirs` in `mannah.db` and includes food logs, workouts, notes, goals, pantry inventory, favorites, and templates.

## Development

```bash
pip install -e '.[dev]'
pytest -q
```
