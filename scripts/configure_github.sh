#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-iamrichmack111/pot-of-mannah}"
command -v gh >/dev/null || { echo "GitHub CLI (gh) is required." >&2; exit 1; }

gh repo edit "$REPO" \
  --description "Local-first nutrition intelligence: dark Flask web app + Textual TUI, 7,000+ foods, nutrient gaps, Playwright, Docker" \
  --enable-issues \
  --enable-wiki \
  --add-topic nutrition \
  --add-topic food-tracker \
  --add-topic micronutrients \
  --add-topic flask \
  --add-topic sqlite \
  --add-topic playwright \
  --add-topic docker \
  --add-topic python \
  --add-topic textual
