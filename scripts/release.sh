#!/usr/bin/env bash
set -euo pipefail
VERSION="${1:-3.0.0}"
TAG="v${VERSION#v}"

git diff --quiet && git diff --cached --quiet || { echo "Working tree is not clean." >&2; exit 1; }
git push origin main
if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "$TAG already exists locally."
else
  git tag -a "$TAG" -m "Pot of Mannah $TAG — web app, Playwright media, Docker, and CI/CD"
fi
git push origin "$TAG"
echo "Pushed main and $TAG"
