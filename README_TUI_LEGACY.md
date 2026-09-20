# 🍲 Pot of Mannah

> **A keyboard-first nutrition, pantry planning, workout tracking, and micronutrient intelligence TUI.**

Pot of Mannah is a terminal-based health and nutrition application built with **Python**, **Textual**, and **SQLite**.

It combines detailed food nutrient data, daily food logging, macro and micronutrient analysis, pantry inventory, pantry-based menu generation, exercise tracking, workout logging, notes, goals, favorites, and exportable reports in one keyboard-driven interface.

---

## ✨ Highlights

- 🥗 Detailed food and nutrient search
- 📊 Macro and micronutrient tracking
- 🍽️ Daily meal logging
- 🧺 Pantry inventory
- 👨‍🍳 Pantry-based Menu Maker
- 🏋️ Exercise database
- 💪 Workout and set logging
- 📝 Daily, food, and workout notes
- 🎯 Configurable nutrition goals
- 🔎 Nutrient-gap analysis
- ❤️ Favorite foods and exercises
- 📤 Markdown, CSV, and JSON reports
- ⌨️ Keyboard-first Textual interface
- 💾 Local-first SQLite persistence
- 🧪 Automated tests
- 🚀 GitHub Actions CI/CD
- 📦 Published through PyPI

---

# 📦 Installation

## Install from PyPI

Create an isolated Python environment:

```bash
python3 -m venv ~/.venvs/pot-of-mannah
source ~/.venvs/pot-of-mannah/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install Pot of Mannah:

```bash
pip install pot-of-mannah
```

Launch:

```bash
pot-of-mannah
```

The shorter command is also available:

```bash
mannah
```

---

## 🔄 Upgrade

Upgrade to the latest release:

```bash
pip install --upgrade pot-of-mannah
```

Check the installed version:

```bash
pip show pot-of-mannah
```

---

# 🖥️ Application

Pot of Mannah separates nutrition, pantry management, exercise, workouts, and notes into dedicated workflows.

```text
┌─────────────────────────────────────────────────────┐
│                   POT OF MANNAH                     │
├─────────────────────────────────────────────────────┤
│ Dashboard │ Food │ Pantry │ Menu │ Exercise │ Notes │
├─────────────────────────────────────────────────────┤
│                                                     │
│                  Application View                   │
│                                                     │
├─────────────────────────────────────────────────────┤
│  ? Help     / Search     E Export     Q Quit        │
└─────────────────────────────────────────────────────┘
```

Major application areas include:

```text
📊 Dashboard
🥗 Food
📅 Today
🧺 Pantry
🍽️ Menu Maker
🏋️ Exercise
💪 Workout
📝 Notes
📈 Stats
🎯 Goals
```

---

# ❓ Contextual Help

Press:

```text
?
```

from the application menus to display instructions for the current section.

Common controls include:

| Key | Action |
|---|---|
| `?` | Help / Instructions |
| `/` | Search |
| `E` | Export |
| `Q` | Quit |

Additional controls are displayed according to the active menu.

---

# 📊 Dashboard

The Dashboard summarizes today's nutrition and activity.

Example:

```text
TODAY
────────────────────────────────

Calories       1,740 / 2,200
Protein          126 / 160 g
Carbs            181 / 240 g
Fat               54 / 75 g
Fiber             24 / 30 g

MICRONUTRIENTS
────────────────────────────────

Vitamin C          92%
Vitamin A          74%
Vitamin B12       115%
Calcium            61%
Iron               83%
Magnesium          48%
Potassium          67%

ACTIVITY
────────────────────────────────

Workout Sets        12
Notes                 2
```

The Dashboard connects nutrition and training statistics without mixing their underlying workflows.

---

# 🥗 Food Intelligence

Search thousands of foods and inspect detailed nutritional information.

Pot of Mannah tracks substantially more than calories.

## Macronutrients

- Calories
- Protein
- Carbohydrates
- Total fat
- Saturated fat
- Monounsaturated fat
- Polyunsaturated fat
- Fiber
- Sugar

## Minerals

- Calcium
- Copper
- Iron
- Magnesium
- Manganese
- Phosphorus
- Potassium
- Selenium
- Sodium
- Zinc

## Vitamins

- Vitamin A
- Vitamin B6
- Vitamin B12
- Vitamin C
- Vitamin E
- Vitamin K
- Niacin
- Riboflavin
- Thiamin
- Pantothenic acid

Additional nutrient data includes:

```text
Choline
Cholesterol
Carotene
Lycopene
Lutein / Zeaxanthin
Retinol
Water
```

---

# 🍽️ Daily Food Logging

Foods can be added directly from search results into the daily food log.

Each entry records information including:

```text
Food
Meal
Amount
Calories
Protein
Carbohydrates
Fat
Fiber
Vitamins
Minerals
Timestamp
```

Nutrients are automatically scaled according to the amount consumed.

For example:

```text
Food: Chicken Breast
Amount: 150 g

Nutrients stored for 150 g
rather than only the database's
original 100 g reference values.
```

Meals can be categorized as:

- 🌅 Breakfast
- ☀️ Lunch
- 🌙 Dinner
- 🍎 Snack
- 🍽️ Meal

---

# 🧬 Nutrient Snapshots

Pot of Mannah stores a **nutrient snapshot** when food is logged.

This is an important architectural decision.

Instead of historical entries depending on the current reference database:

```text
Food Database ────────> Historical Report
```

the application uses:

```text
Food Database
      │
      ▼
Food Logged
      │
      ▼
Nutrient Snapshot
      │
      ▼
Historical Report
```

If the packaged food database changes later, previously logged nutrition data remains reproducible.

---

# 🔎 Micronutrient Gap Analysis

Pot of Mannah compares daily intake against configured nutrition targets.

Example:

```text
NUTRIENT COVERAGE
────────────────────────────────

Magnesium         48%    LOW
Vitamin E         52%    LOW
Potassium         61%    LOW
Calcium           64%    LOW

Iron              87%    OK
Zinc              91%    OK

Vitamin C        118%    MET
Vitamin B12      132%    MET
```

This makes the application useful for more than calorie counting.

Instead of asking only:

```text
How many calories did I eat?
```

Pot of Mannah can also help answer:

```text
Which tracked nutrients are currently
underrepresented in today's food log?
```

---

# 🧺 Pantry

The Pantry represents food currently available.

Foods can be added to Pantry directly from Food search.

Example:

```text
PANTRY
────────────────────────────────

Chicken Breast          850 g
Brown Rice             1200 g
Spinach                 400 g
Eggs                    600 g
Bananas                 500 g
Oatmeal                 900 g
Greek Yogurt            700 g
```

Pantry quantities can be updated as inventory changes.

The pantry becomes the source of truth for Menu Maker.

---

# 👨‍🍳 Menu Maker

Menu Maker generates meal suggestions using **only foods currently available in Pantry**.

It does not simply recommend arbitrary foods from the entire nutrition database.

The workflow is:

```text
🥗 Food Database
       │
       ▼
🧺 Pantry
       │
       ▼
👨‍🍳 Menu Maker
       │
       ▼
🍽️ Breakfast / Lunch / Dinner
       │
       ▼
📅 Daily Food Log
       │
       ▼
📊 Nutrition Analysis
```

Generate a menu from the Menu Maker screen:

```text
M
```

The planner can create:

```text
🌅 Breakfast
☀️ Lunch
🌙 Dinner
```

Food selection can consider nutritional characteristics including:

- Calories
- Protein
- Fiber
- Magnesium
- Potassium
- Calcium
- Iron
- Vitamin C
- Vitamin E

Log a generated menu:

```text
L
```

When pantry-backed menu items are logged, available pantry quantities can be reduced accordingly.

---

# ❤️ Favorites

Frequently used foods and exercises can be stored as favorites.

Favorites allow commonly used records to be accessed without repeatedly searching the full reference databases.

Examples:

```text
Favorite Foods
──────────────
Chicken Breast
Eggs
Oatmeal
Brown Rice
Spinach

Favorite Exercises
──────────────────
Bench Press
Squat
Pull-Up
Barbell Row
Overhead Press
```

---

# 🏋️ Exercise Intelligence

Nutrition and exercise are intentionally kept in separate application sections.

Search exercises by:

```text
Exercise Name
Muscle
Equipment
```

Exercise records can contain:

```text
Name
Primary Muscle
Secondary Muscles
Equipment
Difficulty
Mechanics
Force
Preparation
Execution
```

Example:

```text
BARBELL BENCH PRESS
────────────────────────────────

Primary Muscle
Pectoralis Major

Secondary Muscles
Triceps
Anterior Deltoid

Equipment
Barbell

Mechanics
Compound

Difficulty
Intermediate
```

---

# 💪 Workout Logging

Exercises can be added to the workout log.

Workout sets support:

```text
Exercise
Set Number
Weight
Repetitions
Notes
Timestamp
```

Example:

```text
BENCH PRESS
────────────────────────────────

Set 1    135 lb × 10
Set 2    155 lb × 8
Set 3    175 lb × 6
```

This creates persistent workout history independently of the reference exercise database.

---

# 📝 Notes

Not every useful health or training observation is numerical.

Pot of Mannah therefore includes persistent notes.

Note categories include:

```text
📝 General
🥗 Food
🏋️ Workout
📓 Daily Journal
```

Example:

```text
July 25

Energy was high today.

Chicken and rice lunch kept me full longer.

Left shoulder felt tight during incline press.
```

Notes remain available across application restarts.

---

# 🎯 Goals

Nutrition goals are configurable.

Tracked goals can include:

```text
Calories
Protein
Carbohydrates
Fat
Fiber

Calcium
Iron
Magnesium
Potassium
Zinc
Selenium

Vitamin A
Vitamin B6
Vitamin B12
Vitamin C
Vitamin E
Vitamin K

Choline
```

Nutrition requirements can vary between individuals.

Pot of Mannah therefore treats these values as **configurable tracking targets**, not universal medical recommendations.

---

# 📤 Reports and Export

Pot of Mannah supports report export in:

```text
📝 Markdown
📊 CSV
🔧 JSON
```

Reports are written to:

```text
~/Downloads/pot-of-mannah-reports/
```

Markdown is useful for readable daily reports.

CSV is useful for:

```text
Excel
LibreOffice
Google Sheets
Python / pandas
Data analysis
```

JSON provides structured data suitable for:

```text
Automation
APIs
Scripts
Data pipelines
Future integrations
```

---

# 📑 Example Daily Report

```text
POT OF MANNAH DAILY REPORT
────────────────────────────────

Date: July 25, 2026

NUTRITION

Calories       2,081 / 2,200
Protein          154 / 160 g
Carbs            221 / 240 g
Fat               67 / 75 g

MICRONUTRIENT GAPS

Magnesium         51%
Vitamin E         44%
Potassium         63%

WORKOUT

Bench Press
175 lb × 6
155 lb × 8

NOTES

Left shoulder felt tight during incline press.
```

---

# 💾 Data Architecture

Pot of Mannah separates packaged reference datasets from mutable user information.

```text
                    POT OF MANNAH
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
       REFERENCE DATA              USER DATA
              │                       │
      ┌───────┴────────┐           mannah.db
      │                │              │
      ▼                ▼        ┌─────┼─────────┐
   food.db        exercise.db    │     │         │
                                 ▼     ▼         ▼
                               Food  Workouts   Notes
                               Logs
```

Reference databases:

```text
pot_of_mannah/data/food.db
pot_of_mannah/data/exercise.db
```

Personal tracking information is stored separately.

This includes data such as:

```text
food_log
workouts
workout_sets
notes
goals
favorites
pantry
meal templates
workout templates
```

This keeps the application's reference datasets isolated from user-generated information.

---

# 🏗️ Application Architecture

```text
┌──────────────────────────────────────────────────┐
│                    TEXTUAL TUI                   │
│                                                  │
│ Dashboard │ Food │ Pantry │ Menu │ Exercise     │
│ Workout   │ Notes │ Stats │ Goals               │
└────────────────────────┬─────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────┐
│              APPLICATION SERVICES                │
│                                                  │
│ Search       Tracking       Menu Planning        │
│ Reports      Goals          Favorites            │
│ Nutrient Analysis                                │
└───────────────┬──────────────────┬───────────────┘
                │                  │
                ▼                  ▼
       REFERENCE DATABASES     USER DATABASE
                │                  │
       food.db / exercise.db    mannah.db
```

---

# 🛠️ Technology Stack

Pot of Mannah uses:

| Technology | Purpose |
|---|---|
| 🐍 Python | Application language |
| 🖥️ Textual | Terminal user interface |
| 💾 SQLite | Local data persistence |
| 🔎 SQL | Search and analytics |
| 🧪 Pytest | Automated testing |
| 📦 Setuptools | Python packaging |
| 🤖 GitHub Actions | CI/CD |
| 📦 PyPI | Package distribution |
| 🔐 OIDC | Trusted Publishing |

The repository also preserves earlier **Flask API and Docker** work as part of the project's development history.

---

# 📁 Project Structure

```text
pot-of-mannah/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── publish.yml
│
├── pot_of_mannah/
│   ├── __init__.py
│   ├── data.py
│   ├── menu.py
│   ├── tracker.py
│   ├── tui.py
│   │
│   └── data/
│       ├── food.db
│       └── exercise.db
│
├── scripts/
│   └── rebuild_exercise_db.py
│
├── tests/
│   ├── test_data.py
│   └── test_tracker.py
│
├── DATA/
├── POT-OF-MANNAH-API/
│
├── CHANGELOG.md
├── README.md
├── install.sh
├── pyproject.toml
└── requirements.txt
```

---

# 🧑‍💻 Install From Source

Clone:

```bash
git clone git@github.com:iamrichmack111/pot-of-mannah.git
cd pot-of-mannah
```

Create the environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install:

```bash
python -m pip install --upgrade pip
pip install -e .
```

Launch:

```bash
pot-of-mannah
```

---

# 🔧 Development Setup

Clone the project:

```bash
git clone git@github.com:iamrichmack111/pot-of-mannah.git
cd pot-of-mannah
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install development dependencies:

```bash
python -m pip install --upgrade pip
pip install -e '.[dev]'
```

Run the test suite:

```bash
pytest -q
```

Launch the development version:

```bash
pot-of-mannah
```

---

# 🗃️ Rebuilding Exercise Data

The exercise reference database can be rebuilt deterministically from its canonical dataset.

Run:

```bash
python scripts/rebuild_exercise_db.py
```

This provides a reproducible ingestion path rather than depending on a manually constructed SQLite database.

---

# 📦 Building the Distribution

Install build tooling:

```bash
python -m pip install --upgrade build twine
```

Remove old artifacts:

```bash
rm -rf build dist *.egg-info
```

Build:

```bash
python -m build
```

Validate:

```bash
python -m twine check dist/*
```

A successful build produces files similar to:

```text
dist/
├── pot_of_mannah-2.2.0-py3-none-any.whl
└── pot_of_mannah-2.2.0.tar.gz
```

---

# 🚀 CI/CD

Pot of Mannah uses GitHub Actions.

Continuous integration:

```text
.github/workflows/ci.yml
```

PyPI publishing:

```text
.github/workflows/publish.yml
```

The release pipeline is:

```text
          DEVELOPMENT
               │
               ▼
           GIT COMMIT
               │
               ▼
          GITHUB PUSH
               │
               ▼
          CI + TESTING
               │
               ▼
          VERSION TAG
               │
               ▼
        GITHUB RELEASE
               │
               ▼
        GITHUB ACTIONS
               │
               ▼
     BUILD WHEEL + SDIST
               │
               ▼
   PYPI TRUSTED PUBLISHING
               │
               ▼
 pip install pot-of-mannah
```

PyPI publishing uses **Trusted Publishing / OIDC**, avoiding the need to store a permanent PyPI API token in the repository.

---

# 🏷️ Release Process

Update the package version in:

```text
pyproject.toml
```

Example:

```toml
version = "2.2.1"
```

Commit and push:

```bash
git add .
git commit -m "Release Pot of Mannah v2.2.1"
git push origin main
```

Create the tag:

```bash
git tag -a v2.2.1 -m "Pot of Mannah v2.2.1"
git push origin v2.2.1
```

Create the GitHub release:

```bash
gh release create v2.2.1 \
  --title "Pot of Mannah v2.2.1" \
  --generate-notes
```

GitHub Actions then builds the distributions and publishes the release to PyPI.

---

# 🧪 Testing

Run all tests:

```bash
pytest -q
```

For a clean PyPI installation test:

```bash
python3 -m venv /tmp/pot-mannah-test
source /tmp/pot-mannah-test/bin/activate

python -m pip install --upgrade pip
pip install pot-of-mannah

pot-of-mannah
```

---

# 🧠 Design Principles

### ⌨️ Keyboard First

Core workflows are designed for terminal users and keyboard-driven navigation.

### 🏠 Local First

Tracking information is stored locally with SQLite.

### 🧬 Nutrition Beyond Calories

Vitamins and minerals are treated as first-class data alongside calories and macros.

### 🧺 Pantry-Aware Planning

Menu Maker works with food you actually place in Pantry rather than recommending arbitrary ingredients.

### 💾 Separate Reference and User Data

Packaged food and exercise databases remain separate from mutable personal tracking data.

### 📸 Reproducible Nutrition History

Logged food entries retain nutrient snapshots so historical reports remain consistent.

### 📤 Portable Data

Reports can be exported into standard formats rather than locking information inside the application.

### 🔧 Automation Friendly

JSON and CSV exports provide a foundation for future scripts, analytics, APIs, and integrations.

---

# 🗺️ Roadmap

Potential future improvements include:

- 🍱 Named meal templates
- 🏋️ Saved workout templates
- 📈 7-day and 30-day trends
- 🏆 Personal record detection
- 📊 Training volume analysis
- 🧬 Nutrient-source analysis
- 🔍 "What am I missing?" food recommendations
- ⚖️ Pantry-aware nutrition optimization
- 🛒 Shopping-list generation
- 📅 Calendar history
- 📉 Historical nutrient trends
- 📑 Additional report formats
- 🔌 API integrations
- ⌨️ Command palette

---

# ⚠️ Disclaimer

Pot of Mannah is a software and data-analysis project.

Nutrition totals, nutrient targets, menu generation, exercise information, and related statistics are provided for informational and tracking purposes.

The application is not intended to diagnose, treat, prevent, or provide individualized medical advice.

---

# 📌 Current Version

```text
2.2.0
```

Install:

```bash
pip install pot-of-mannah
```

Run:

```bash
pot-of-mannah
```

or:

```bash
mannah
```

---

# 👨‍💻 Author

Developed by **iamrichmack111**.

Pot of Mannah is part of a broader collection of terminal-first software projects focused on local-first applications, data engineering, automation, developer tooling, and practical terminal interfaces.

---

## ⭐ Support the Project

If Pot of Mannah is useful to you, consider starring the repository.

```bash
gh repo view iamrichmack111/pot-of-mannah --web
```

**Eat. Track. Train. Analyze. All from the terminal. 🍲**

---

## Web interface

This bundle also includes the Pot of Mannah dark web interface. It adds account-based food logging by exact grams, Nutrition Needs, nutrient-aware food suggestions, a Smart Planner, Progress trends, hydration, favorites, custom foods, themes, and local admin tools.

See [`WEB_APP.md`](WEB_APP.md) for the page map and run instructions.
