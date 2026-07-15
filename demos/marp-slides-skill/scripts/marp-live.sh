#!/usr/bin/env bash
# marp-live.sh — render a Marp deck to HTML and live-edit it.
#
# Builds <deck>.html with the Automata brand theme registered + HTML enabled,
# opens it in the default browser, then watches the source. On every save Marp
# rebuilds and the open browser tab auto-reloads over WebSocket (watch mode).
#
#   marp-live.sh path/to/deck.md            # -> path/to/deck.html, watched
#   marp-live.sh deck.md out.html           # custom output path
#
# Ctrl-C to stop watching. The exported .html inlines the theme CSS, so it's a
# self-contained file you can share or open anywhere.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DECK="${1:?usage: marp-live.sh <deck.md> [output.html]}"
[ -f "$DECK" ] || { echo "No such file: $DECK" >&2; exit 1; }
OUT="${2:-${DECK%.md}.html}"

MARP=(npx --yes @marp-team/marp-cli@latest
  --config "$SKILL_DIR/.marprc.yml"
  --theme-set "$SKILL_DIR/assets/brand"
  --html
  --no-stdin)   # without this, marp blocks waiting on stdin when run non-interactively

# Watch + auto-reload in the background, then open once the first build lands.
"${MARP[@]}" --watch "$DECK" -o "$OUT" </dev/null &
MARP_PID=$!
trap 'kill "$MARP_PID" 2>/dev/null || true' EXIT INT TERM

# Wait for the first HTML build, then open it.
for _ in $(seq 1 100); do [ -s "$OUT" ] && break; sleep 0.2; done
sleep 0.3
if command -v open >/dev/null 2>&1; then open "$OUT"; fi
echo "Live: editing $DECK -> $OUT  (save to reload; Ctrl-C to stop)"

wait "$MARP_PID"
