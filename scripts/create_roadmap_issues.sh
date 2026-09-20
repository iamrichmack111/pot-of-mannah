#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-iamrichmack111/pot-of-mannah}"
command -v gh >/dev/null || { echo "GitHub CLI (gh) is required." >&2; exit 1; }

ensure_issue() {
  local title="$1" body="$2"
  if gh issue list -R "$REPO" --state all --search "in:title $title" --limit 100 --json title --jq '.[].title' | grep -Fxq "$title"; then
    echo "exists: $title"
  else
    gh issue create -R "$REPO" --title "$title" --label enhancement --body "$body"
  fi
}

ensure_issue "feat: mobile barcode scanning" "Add camera-assisted barcode lookup to the web food logger with manual barcode fallback."
ensure_issue "feat: reusable meal templates" "Allow users to save a group of foods/grams as a reusable breakfast, lunch, dinner, or custom meal template."
ensure_issue "feat: weekly micronutrient report" "Add a 7-day nutrient coverage summary so daily outliers do not dominate the nutrition view."
ensure_issue "ci: add accessibility checks" "Add Playwright + axe accessibility checks to CI and publish the report as an artifact."
ensure_issue "platform: add PWA offline shell" "Add manifest/service worker support so the web shell can be installed and reopened offline."
