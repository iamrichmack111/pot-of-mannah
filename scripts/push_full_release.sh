#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-iamrichmack111/pot-of-mannah}"
VERSION="${VERSION:-3.0.0}"
TAG="v${VERSION#v}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${WORK:-$HOME/Downloads/pot-of-mannah-release-work}"

command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
command -v gh >/dev/null || { echo "GitHub CLI (gh) is required" >&2; exit 1; }
command -v rsync >/dev/null || { echo "rsync is required" >&2; exit 1; }
gh auth status >/dev/null

rm -rf "$WORK"
gh repo clone "$REPO" "$WORK"
rsync -a --delete --exclude='.git/' "$ROOT/" "$WORK/"
cd "$WORK"

git config user.name "${GIT_AUTHOR_NAME:-Jeremy Franklin}"
git config user.email "${GIT_AUTHOR_EMAIL:-iamrichmack111@users.noreply.github.com}"

git add -A
if git diff --cached --quiet; then
  echo "No source changes to commit."
else
  git commit -m "release: Pot of Mannah v3 web app, Playwright, Docker and CI/CD"
fi

git push origin main

# Configure repo metadata/topics and seed roadmap issues. Issue seeding is intentionally best-effort.
bash scripts/configure_github.sh "$REPO" || true
bash scripts/create_roadmap_issues.sh "$REPO" || true

# Wait for the media workflow created by the main push, then absorb the bot's media commit.
sleep 5
RUN_ID="$(gh run list -R "$REPO" --workflow playwright-media.yml --limit 1 --json databaseId --jq '.[0].databaseId // empty')"
if [[ -n "$RUN_ID" ]]; then
  echo "Watching Playwright Media run $RUN_ID"
  gh run watch -R "$REPO" "$RUN_ID" --exit-status
  git pull --ff-only origin main
else
  echo "No Playwright Media run found; triggering one."
  gh workflow run -R "$REPO" playwright-media.yml --ref main
  sleep 5
  RUN_ID="$(gh run list -R "$REPO" --workflow playwright-media.yml --limit 1 --json databaseId --jq '.[0].databaseId // empty')"
  [[ -n "$RUN_ID" ]] && gh run watch -R "$REPO" "$RUN_ID" --exit-status
  git pull --ff-only origin main
fi

# Publish the wiki immediately with the user's authenticated GitHub token, then leave the workflow in place for future syncs.
GH_TOKEN="$(gh auth token)" GITHUB_REPOSITORY="$REPO" bash scripts/publish_wiki.sh
gh workflow run -R "$REPO" wiki.yml --ref main || true

if git rev-parse "$TAG" >/dev/null 2>&1; then
  git tag -d "$TAG"
fi
if git ls-remote --exit-code --tags origin "refs/tags/$TAG" >/dev/null 2>&1; then
  echo "Remote tag $TAG already exists; leaving it unchanged."
else
  git tag -a "$TAG" -m "Pot of Mannah $TAG — web app, Playwright media, Docker, wiki and CI/CD"
  git push origin "$TAG"
fi

echo
echo "Pushed: https://github.com/$REPO"
echo "Tag: $TAG"
echo "Actions: https://github.com/$REPO/actions"
echo "Wiki: https://github.com/$REPO/wiki"
