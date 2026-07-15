#!/usr/bin/env bash
# new-deck.sh — scaffold a new brand deck from the starter, then start live editing.
#
#   new-deck.sh ~/Desktop/my-talk.md        # create + open live preview
#   new-deck.sh ~/Desktop/my-talk.md --no-live   # just create the file
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${1:?usage: new-deck.sh <dest.md> [--no-live]}"
[ -e "$DEST" ] && { echo "Refusing to overwrite existing file: $DEST" >&2; exit 1; }

mkdir -p "$(dirname "$DEST")"
cp "$SKILL_DIR/assets/starter.md" "$DEST"
echo "Created $DEST"

if [ "${2:-}" != "--no-live" ]; then
  exec "$SKILL_DIR/scripts/marp-live.sh" "$DEST"
fi
