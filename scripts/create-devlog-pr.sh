#!/usr/bin/env bash
set -euo pipefail

FEED_PATH="${1:-$HOME/dev-journal/DEVLOG_FEED.md}"
BRANCH_NAME="devlog/$(date +%Y-%m-%d-%H%M%S)"
POST_PATH=""
BRANCH_CREATED=0
COMMIT_CREATED=0

cleanup() {
  local exit_code="$1"

  if [[ "$exit_code" -ne 0 && "$COMMIT_CREATED" -eq 0 && -n "$POST_PATH" && -f "$POST_PATH" ]]; then
    rm -f "$POST_PATH"
    rmdir "$(dirname "$POST_PATH")" 2>/dev/null || true
  fi

  if [[ "$exit_code" -ne 0 && "$BRANCH_CREATED" -eq 1 && "$COMMIT_CREATED" -eq 0 ]]; then
    git switch - >/dev/null 2>&1 || true
    git branch -D "$BRANCH_NAME" >/dev/null 2>&1 || true
  fi
}

trap 'cleanup $?' EXIT

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
BRANCH_CREATED=1
git add "$POST_PATH"
git commit -m "Add devlog draft"
COMMIT_CREATED=1
git push -u origin "$BRANCH_NAME"
gh pr create \
  --head "$BRANCH_NAME" \
  --title "Add devlog draft" \
  --body "Automated devlog draft import from shared feed. Please review carefully for tone and sensitive information before merging."

trap - EXIT
