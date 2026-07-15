#!/usr/bin/env bash
# marp-build.sh — one-shot export of a Marp deck. Format inferred from output extension.
#
#   marp-build.sh deck.md               # -> deck.html (self-contained, theme inlined)
#   marp-build.sh deck.md deck.pdf      # -> PDF   (needs Chrome/Chromium installed)
#   marp-build.sh deck.md deck.pptx     # -> PPTX  (needs Chrome/Chromium installed)
#   marp-build.sh deck.md deck.html     # explicit HTML
#
# PDF/PPTX/PNG use a headless browser; if you don't have Chrome, install it or use HTML.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DECK="${1:?usage: marp-build.sh <deck.md> [output.(html|pdf|pptx|png)]}"
[ -f "$DECK" ] || { echo "No such file: $DECK" >&2; exit 1; }
OUT="${2:-${DECK%.md}.html}"

npx --yes @marp-team/marp-cli@latest \
  --config "$SKILL_DIR/.marprc.yml" \
  --theme-set "$SKILL_DIR/assets/brand" \
  --html \
  --no-stdin \
  "$DECK" -o "$OUT" </dev/null

echo "Built $OUT"
