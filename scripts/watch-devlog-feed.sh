#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_PATH="$(cd "$SCRIPT_DIR/.." && pwd)"
FEED_PATH="${1:-$HOME/dev-journal/DEVLOG_FEED.md}"
export PATH="/opt/homebrew/bin:$HOME/.local/bin:$HOME/.pyenv/shims:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

if ! command -v fswatch >/dev/null 2>&1; then
  echo "fswatch is required to watch the shared devlog feed."
  exit 1
fi

mkdir -p "$(dirname "$FEED_PATH")"
touch "$FEED_PATH"

fswatch -o "$FEED_PATH" | while read -r _; do
  if ! bash "$REPO_PATH/scripts/create-devlog-pr.sh" "$FEED_PATH"; then
    echo "Devlog PR creation failed. Watcher is still running." >&2
  fi
done
