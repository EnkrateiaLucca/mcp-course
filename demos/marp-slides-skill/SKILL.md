---
name: marp-slides
description: Create high-quality slide decks fast with Marp, rendered to live-reloading HTML for instant editing. Default house style is the Automata Learning Lab brand theme with 12 copy-paste layout snippets (cover, agenda, two-column, stat grid, bento, comparison, process, timeline, chart, code, quote, closing). Use when the user wants to make slides, a presentation, a talk, a deck, lecture/seminar/workshop material, or says "turn this into slides", "make a Marp deck", or "make slides look good".
---

# Marp Slides — a system for fast, good-looking decks

A deck is plain Markdown. This skill renders it to **self-contained HTML that live-reloads in the browser** as you edit, styled by a registered brand theme so the source stays clean. Build by **assembling snippets**, not writing CSS.

## The 3 moving parts

1. **`assets/brand/automata.css`** — the registered `automata` Marp theme (Automata Learning Lab: cream/ink/dark-red, Fraunces + Inter). Decks reference it with one line: `theme: automata`. The theme is **inlined into the exported HTML**, so any deck you build is a portable single file.
2. **`assets/snippets.md`** — a palette of 12 ready layouts. Copy a block, swap the text. No CSS needed; every helper class lives in the theme.
3. **`scripts/`** — `marp-live.sh` (edit + auto-reload), `new-deck.sh` (scaffold), `marp-build.sh` (export HTML/PDF/PPTX). All wrap Marp CLI with the brand theme + `html: true` + `--no-stdin` preconfigured via `.marprc.yml`.

## Where to save the deck

If the user names a location, use it. **If they don't, save the deck inside the
Obsidian vault at `~/lucas-notes/marp-slides-temp/`** (create the folder if it's
missing) — e.g. `~/lucas-notes/marp-slides-temp/<name>.md`. This keeps unplaced
decks out of the Desktop and together in one predictable spot.

## Always open the result in the browser

After building a deck with this skill, **always open the rendered HTML in the
browser** so the user sees it immediately — don't just hand back a command.
Either start the live watcher (`marp-live.sh`, which builds + opens + auto-reloads)
or build the HTML and `open` it. Do this every time the skill is used, even if the
user didn't explicitly ask to open it.

## Default workflow (use this unless told otherwise)

1. **Scaffold** a deck from the brand starter, into the save location above
   (the user's path, or `~/lucas-notes/marp-slides-temp/<name>.md` by default):
   ```bash
   ~/.claude/skills/marp-slides/scripts/new-deck.sh ~/lucas-notes/marp-slides-temp/my-talk.md --no-live
   ```
   (`starter.md` is a 4-slide brand deck: cover → agenda → content → closing.)
2. **Fill it in** by editing the Markdown and pasting layouts from `assets/snippets.md`. Match the content to the right snippet (numbers → stat-grid, steps → process, milestones → timeline, etc.). Keep each slide to one idea, 3–5 lines.
3. **Live-edit as HTML** — start the watcher; it builds the HTML, opens it in the browser, and **auto-reloads on every save**:
   ```bash
   ~/.claude/skills/marp-slides/scripts/marp-live.sh ~/Desktop/my-talk.md
   ```
   Leave this running while you iterate. Ctrl-C to stop.
4. **Export** when done (optional — the watched `.html` is already shareable):
   ```bash
   ~/.claude/skills/marp-slides/scripts/marp-build.sh ~/Desktop/my-talk.md ~/Desktop/my-talk.pdf
   ```

> When the user just says "make me slides about X", do steps 1–2 yourself (scaffold + fill with snippets), then open it in the browser for them (see "Always open the result in the browser" above). Don't make them assemble anything or run a command themselves.

## Deck front-matter (every brand deck starts with this)

```markdown
---
marp: true
theme: automata
paginate: true
---
```

Per-slide style modifiers go in an HTML comment at the top of the slide:
`<!-- _class: dark -->` (dark slide), `lead` (vertically centered cover/closing), `quote` (big pull-quote), and `<!-- _paginate: false -->` to hide the page number. Combine them: `<!-- _class: lead dark -->`.

## The 12 snippets (`assets/snippets.md`)

| Snippet | Use it for | Snippet | Use it for |
|---|---|---|---|
| `cover` | title slide | `comparison` | A-vs-B table |
| `agenda` | what we'll cover | `process` | left→right steps |
| `two-col` | problem/approach | `timeline` | milestones |
| `stat-grid` | 3 big numbers | `chart` | CSS bar chart |
| `bento` | feature grid | `code` | syntax-highlighted code (dark) |
| `closing` | thanks / CTA | `quote` | pull-quote (dark) |

Grep one by its marker, e.g. `SNIPPET: stat-grid`. The bottom of `snippets.md` also lists **image** patterns (`![bg right:40%](img.png)`, full-bleed, tinted, split).

## Branding & themes

- **Default to the `automata` brand theme.** It's the house style and what makes decks look good with zero effort. Brand source: `/Users/greatmaster/Desktop/projects/ai-ref-docs/ui-design/brand-guidelines-automata-learning-lab.pdf`.
- To tweak the look, edit `assets/brand/automata.css` (tokens at the top: `--accent`, `--cream`, `--ink`, fonts). Changes apply to every deck.
- **Alternative themes** (tech, dark, business, minimal, colorful, gradient, default) exist as self-contained templates in `assets/template-*.md` — each embeds its own `<style>`. Use one only if the user explicitly wants a different look than the brand. Otherwise prefer `automata`.

## Editing live in VS Code instead (alternative to the script)

If the user prefers VS Code's built-in Marp preview, add to their settings.json:
```json
"markdown.marp.enableHtml": true,
"markdown.marp.themes": ["/Users/greatmaster/.claude/skills/marp-slides/assets/brand/automata.css"]
```
Then open the deck and click the Marp preview icon. (The `marp-live.sh` script needs no VS Code and works the same way in any browser.)

## Quality bar

- One idea per slide; 3–5 bullet lines max; break dense slides in two.
- Lead with a **bold** keyword or use the `.kicker` eyebrow label for section context.
- Use `<em>` (renders in accent color) and `**bold**` sparingly for emphasis.
- Prefer a visual snippet (stat-grid / chart / bento / timeline) over a bullet list when the content is numbers, steps, or comparisons.
- Title slide uses `lead dark`; closing mirrors it. Keep pagination off on those.
- Verify it renders before handing off: `marp-build.sh deck.md /tmp/check.html` should exit 0.
- **Hyperlink every paper/source reference.** Whenever a slide cites a paper, study, or external source (e.g. `Author Year`), wrap the citation in a link to the source so it's one click to verify: `[Author Year](url)` in markdown bullets/text, or `<a href="url">Author Year</a>` inside HTML blocks like `<div class="by">` quote attributions (markdown link syntax doesn't parse inside raw HTML). On a cover slide, add a small note that references are clickable.

## Gotchas (learned, baked into the scripts)

- **HTML must be enabled** — the layouts use `<div>`. The scripts and `.marprc.yml` set `html: true`; if you ever call `marp` directly, pass `--html`.
- **`--no-stdin` is required** when invoking Marp non-interactively (scripts, agents, CI) or it hangs waiting on stdin. Already in every script.
- **PDF/PPTX need Chrome/Chromium** installed (HTML does not). If export fails, fall back to HTML.
- Marp CLI runs via `npx @marp-team/marp-cli@latest` — first call downloads it (slow once, cached after).

## References (read on demand)

- `references/marp-syntax.md` — directives, front-matter, pagination, fragments
- `references/image-patterns.md` — official Marpit image/background syntax
- `references/theme-css-guide.md` — how the theme CSS works, to customize `automata`
- `references/advanced-features.md` — math, emoji, fragmented lists, CLI/VS Code
- `references/best-practices.md` — slide-design guidelines
- Official: https://marp.app/ · https://marpit.marp.app/directives · https://github.com/marp-team/marp-cli
