#!/usr/bin/env bash
set -euo pipefail

FEED_PATH="${1:-$HOME/dev-journal/DEVLOG_FEED.md}"
BRANCH_NAME="devlog/$(date +%Y-%m-%d-%H%M%S)"

if [[ -n "$(git status --short)" ]]; then
  echo "Working tree is not clean. Commit or stash changes before creating a devlog PR."
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required to create a devlog PR."
  exit 1
fi

POST_PATH="$(python3 ./scripts/import-devlog-feed.py --feed "$FEED_PATH")"

if [[ "$POST_PATH" == "No new devlog entries to import." ]]; then
  echo "$POST_PATH"
  exit 0
fi

if [[ ! -f "$POST_PATH" ]]; then
  echo "Importer did not return a valid post path: $POST_PATH"
  exit 1
fi

if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
  echo "Branch already exists: $BRANCH_NAME"
  exit 1
fi

hugo --minify

git switch -c "$BRANCH_NAME"
git add "$POST_PATH"
git commit -m "Add devlog draft"
gh pr create \
  --title "Add devlog draft" \
  --body "Automated devlog draft import from shared feed. Please review carefully for tone and sensitive information before merging."
