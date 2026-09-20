# Changelog

## 3.0.0 - 2026-09-20

### Added
- Full dark tabbed Flask web application alongside the existing Textual TUI.
- Today, Diary, Log Food, Nutrition, Planner, Progress, Foods, Account, and Admin workflows.
- Exact gram-based portion calculations from per-100 g nutrient values.
- Local food search plus USDA and Open Food Facts imports.
- Favorites, hydration, daily notes, weight check-ins, custom goals, nutrient-gap analysis, planning suggestions, and progress trends.
- 12 dark themes and expanded interface animations.
- Playwright screenshot and browser-demo automation.
- Dockerfile, Docker Compose, health check, and GHCR publishing workflow.
- Web smoke tests, wiki publishing, GitHub release automation, issue templates, and roadmap tasks.

## 2.2.0

- Added persistent Pantry inventory with gram quantities.
- Added pantry-only Menu Maker for breakfast, lunch, and dinner.
- Added one-key menu logging with automatic pantry deduction.
- Added Markdown, JSON, and CSV daily report exports.
- Added contextual `?` instructions to every primary menu.
- Added food and exercise favorites.
- Added nutrient-source analysis backend and meal/workout template schema.
- Added pantry/menu/export/favorites automated tests.
- Expanded README and keyboard documentation.

## 2.1.0

- Added persistent daily food logging and micronutrient totals.
- Added workout set logging, notes, goals, and gap analysis.
- Separated reference databases from personal tracking data.
- Corrected exercise ingestion and package discovery.

## Web v3.1
- Replaced email login with username/password authentication.
- Added automatic migration for older local web databases.
- Added Harvest, Midnight, Ocean, and Berry themes with browser persistence.
- Added a seeded local administrator account and Admin control center.
- Added admin password changing and non-admin account removal.

## Web UI v7 — organized navigation
- Separated Today, Diary, Nutrition, Foods, and Account into focused screens.
- Added a dedicated Diary route for meals, hydration, and notes.
- Renamed the food-entry experience to Log Food and kept it separate from the Diary.
- Moved daily nutrient coverage and 30-day trends into Nutrition.
- Removed Admin from the primary user navigation; administrators enter it from Account.
- Simplified theme access so themes change appearance without changing information hierarchy.
- Rebuilt the responsive desktop and mobile navigation around the same structure.

## v9 — Expanded pages and nutrition guidance
- Split Nutrition Needs from Progress.
- Added Nutrition Score and biggest-gap ranking.
- Added local nutrient-aware food suggestions from the 7,413-food database.
- Added Nutrient Explorer drill-down pages.
- Added Smart Planner for next-meal ideas based on current daily gaps.
- Added separate Progress page with 30-day energy history, 7-day consistency, achievements, streaks, and weight check-ins.
- Added mobile More page to keep bottom navigation organized.
- Added daily CSV diary export.
- Added intersection reveals, number count-ups, ripple feedback, animated charts, ambient motion, tilt motion, and richer panel transitions.
- Kept all themes dark-only.
