#!/usr/bin/env bash
set -euo pipefail

: "${GITHUB_REPOSITORY:=iamrichmack111/pot-of-mannah}"
: "${GH_TOKEN:?GH_TOKEN is required to publish the GitHub Wiki}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
REMOTE="https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.wiki.git"

if ! git clone "$REMOTE" "$TMP/wiki"; then
  mkdir -p "$TMP/wiki"
  git -C "$TMP/wiki" init
  git -C "$TMP/wiki" branch -M master
  git -C "$TMP/wiki" remote add origin "$REMOTE"
fi

find "$TMP/wiki" -maxdepth 1 -type f -name '*.md' -delete
cp "$ROOT"/wiki/*.md "$TMP/wiki"/

git -C "$TMP/wiki" config user.name "github-actions[bot]"
git -C "$TMP/wiki" config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git -C "$TMP/wiki" add -A
if git -C "$TMP/wiki" diff --cached --quiet; then
  echo "Wiki already current."
  exit 0
fi
git -C "$TMP/wiki" commit -m "docs: sync Pot of Mannah wiki"
git -C "$TMP/wiki" push -u origin master
