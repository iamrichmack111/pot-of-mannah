# Pot of Mannah Wiki

Pot of Mannah v3 is a local-first nutrition intelligence project with two interfaces:

- **Web app** — dark themed daily nutrition tracking, exact gram logging, nutrient gaps, planning, progress, and food library.
- **Textual TUI** — keyboard-first nutrition, pantry, menu, exercise, and reporting workflows.

The project ships with a local nutrition database containing **7,000+ foods**, detailed per-100 g nutrients, SQLite persistence, Playwright media automation, CI/CD, and Docker support.

![Today dashboard](https://raw.githubusercontent.com/iamrichmack111/pot-of-mannah/main/media/screenshots/01-today.png)

## Start here

- [[Web App]]
- [[Nutrition Intelligence]]
- [[Food Data and Measurements]]
- [[Docker]]
- [[CI-CD]]
- [[Playwright Demo]]
- [[Architecture]]
- [[Development]]

## Default local admin

The web app seeds a local admin account unless overridden with environment variables.

- Username: `admin`
- Password: `MannahAdmin2026!`

Change the password immediately for any non-development deployment, or set `MANNAH_ADMIN_PASSWORD` before first run.
