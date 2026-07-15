---
marp: true
theme: default
paginate: true
---

<!--
  12-LAYOUT BRAND DECK — "All 12 formats at a glance"
  Style: Automata Learning Lab (cream background, ink text, sparing dark-red accent)
  Source: slide-formats.png reference grid.

  HOW TO USE: each slide below is one reusable layout pattern. Copy the slide block
  you need into your deck and swap the placeholder content. The <style> block defines
  the brand tokens + helper classes (.stat-grid, .bento, .flow, .timeline, .two-col, etc.).
  The 12 layouts: Cover, Agenda, Two-column, Stat grid, Feature bento, Comparison,
  Process, Timeline, Chart, Code block, Quote, Closing.
-->

<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600;700&display=swap');

:root {
  --cream: #F5EDE0;
  --cream-card: #FBF6EC;
  --ink: #1F1B16;
  --ink-soft: #5A524A;
  --accent: #9B2C2C;       /* dark red */
  --accent-soft: #C9605F;
  --dark: #221512;         /* near-black maroon for dark slides */
  --border: #E4D8C4;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-display: 'Fraunces', Georgia, serif;
}

section {
  background: var(--cream);
  color: var(--ink);
  font-family: var(--font-body);
  font-size: 22px;
  line-height: 1.6;
  padding: 56px 64px;
  box-sizing: border-box;
}
h1, h2, h3 { font-family: var(--font-display); color: var(--ink); margin: 0 0 16px; font-weight: 600; }
h1 { font-size: 52px; line-height: 1.15; letter-spacing: -0.01em; }
h2 { font-size: 34px; margin-bottom: 28px; }
em { font-style: italic; color: var(--accent); }
strong { color: var(--accent); font-weight: 700; }
a { color: var(--accent); }
ul { padding-left: 26px; } li { margin-bottom: 10px; }
section::after { color: var(--ink-soft); font-size: 14px; } /* page number */
.kicker { font-family: var(--font-body); font-size: 14px; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--accent); font-weight: 600; margin-bottom: 14px; }

/* Dark variant */
section.dark { background: var(--dark); color: #F0E6D8; }
section.dark h1, section.dark h2, section.dark h3 { color: #FBF6EC; }
section.dark .kicker { color: var(--accent-soft); }

/* Lead / cover */
section.lead { display: flex; flex-direction: column; justify-content: center; }

/* Two-column */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: start; }

/* Stat grid */
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; margin-top: 24px; }
.stat { }
.stat .num { font-family: var(--font-display); font-size: 64px; color: var(--accent); line-height: 1; }
.stat .label { font-size: 16px; color: var(--ink-soft); margin-top: 8px; }

/* Feature bento */
.bento { display: grid; grid-template-columns: repeat(3, 1fr); grid-auto-rows: 150px; gap: 18px; margin-top: 20px; }
.bento .cell { background: var(--cream-card); border: 1px solid var(--border); border-radius: 14px;
  padding: 20px; }
.bento .cell.wide { grid-column: span 2; }
.bento .cell h3 { font-size: 20px; margin-bottom: 6px; }
.bento .cell p { font-size: 15px; color: var(--ink-soft); margin: 0; }

/* Comparison table */
table { border-collapse: collapse; width: 100%; font-size: 18px; margin-top: 16px; }
th, td { border: 1px solid var(--border); padding: 12px 16px; text-align: left; }
th { background: var(--accent); color: #FBF6EC; font-weight: 600; }
tr:nth-child(even) td { background: var(--cream-card); }

/* Process flow */
.flow { display: flex; align-items: center; gap: 14px; margin-top: 40px; }
.flow .step { flex: 1; background: var(--cream-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 20px; text-align: center; }
.flow .step h3 { font-size: 18px; margin: 0 0 4px; }
.flow .step p { font-size: 14px; color: var(--ink-soft); margin: 0; }
.flow .arrow { color: var(--accent); font-size: 28px; flex: 0 0 auto; }

/* Timeline */
.timeline { display: flex; justify-content: space-between; margin-top: 56px; position: relative; }
.timeline::before { content: ''; position: absolute; top: 9px; left: 4%; right: 4%;
  height: 2px; background: var(--border); }
.timeline .pt { position: relative; text-align: center; width: 22%; }
.timeline .pt .dot { width: 18px; height: 18px; border-radius: 50%; background: var(--accent);
  margin: 0 auto 14px; position: relative; z-index: 1; }
.timeline .pt .when { font-weight: 600; font-size: 16px; }
.timeline .pt .what { font-size: 14px; color: var(--ink-soft); }

/* Chart (CSS bars) */
.chart { display: flex; align-items: flex-end; gap: 24px; height: 300px; margin-top: 24px; padding-left: 8px; }
.chart .bar { flex: 1; background: var(--accent); border-radius: 8px 8px 0 0; position: relative; }
.chart .bar span { position: absolute; bottom: -28px; left: 0; right: 0; text-align: center;
  font-size: 14px; color: var(--ink-soft); }

/* Code block */
section.dark pre { background: #160D0C; border: 1px solid #3a2522; border-radius: 12px;
  padding: 24px; font-size: 18px; overflow: auto; }
section.dark code { color: #F0E6D8; font-family: 'JetBrains Mono', 'Consolas', monospace; }

/* Quote */
section.quote { display: flex; flex-direction: column; justify-content: center; }
section.quote blockquote { font-family: var(--font-display); font-size: 40px; line-height: 1.3;
  border: none; margin: 0; max-width: 80%; }
section.quote blockquote .mark { color: var(--accent); }
section.quote .by { margin-top: 28px; font-size: 18px; color: #C9B89C; }
</style>

<!-- ============ 1. COVER ============ -->
<!-- _class: lead dark -->
<!-- _paginate: false -->

<div class="kicker">Automata Learning Lab</div>

# A presentation title <em>in your voice</em>

A short subtitle that frames the talk.

---

<!-- ============ 2. AGENDA ============ -->

<div class="kicker">Agenda</div>

## What we'll cover

1. **First section** — the setup
2. **Second section** — the core idea
3. **Third section** — putting it to work

---

<!-- ============ 3. TWO-COLUMN ============ -->

## Two-column layout

<div class="two-col">
<div>

### The problem
- Point one about the problem
- Point two about the problem
- Why it matters now

</div>
<div>

### The approach
- How we solve it
- What's different
- The payoff

</div>
</div>

---

<!-- ============ 4. STAT GRID ============ -->

## The numbers

<div class="stat-grid">
<div class="stat"><div class="num">900M</div><div class="label">Big headline metric</div></div>
<div class="stat"><div class="num">3×</div><div class="label">Improvement factor</div></div>
<div class="stat"><div class="num">40%</div><div class="label">Lower cost</div></div>
</div>

---

<!-- ============ 5. FEATURE BENTO ============ -->

## Feature bento

<div class="bento">
<div class="cell wide"><h3>Headline feature</h3><p>The one that does most of the work.</p></div>
<div class="cell"><h3>Feature</h3><p>Supporting detail.</p></div>
<div class="cell"><h3>Feature</h3><p>Supporting detail.</p></div>
<div class="cell"><h3>Feature</h3><p>Supporting detail.</p></div>
<div class="cell wide"><h3>Wide feature</h3><p>Another that needs room.</p></div>
</div>

---

<!-- ============ 6. COMPARISON ============ -->

## Comparison

| | Option A | Option B |
|---|---|---|
| Speed | Fast | Faster |
| Cost | $$ | $ |
| Effort | Low | Medium |
| Best for | Quick wins | Scale |

---

<!-- ============ 7. PROCESS ============ -->

## Process

<div class="flow">
<div class="step"><h3>Step one</h3><p>Capture input</p></div>
<div class="arrow">→</div>
<div class="step"><h3>Step two</h3><p>Transform</p></div>
<div class="arrow">→</div>
<div class="step"><h3>Step three</h3><p>Ship output</p></div>
</div>

---

<!-- ============ 8. TIMELINE ============ -->

## Timeline

<div class="timeline">
<div class="pt"><div class="dot"></div><div class="when">Milestone 1</div><div class="what">Kickoff</div></div>
<div class="pt"><div class="dot"></div><div class="when">Milestone 2</div><div class="what">Build</div></div>
<div class="pt"><div class="dot"></div><div class="when">Milestone 3</div><div class="what">Launch</div></div>
<div class="pt"><div class="dot"></div><div class="when">Milestone 4</div><div class="what">Scale</div></div>
</div>

---

<!-- ============ 9. CHART ============ -->

## Chart

<div class="chart">
<div class="bar" style="height:40%"><span>Q1</span></div>
<div class="bar" style="height:55%"><span>Q2</span></div>
<div class="bar" style="height:70%"><span>Q3</span></div>
<div class="bar" style="height:95%"><span>Q4</span></div>
</div>

---

<!-- ============ 10. CODE BLOCK ============ -->
<!-- _class: dark -->

<div class="kicker">Code block</div>

```python
def build_slide(sketch, notes):
    """Turn a drawing + dictation into a finished slide."""
    return agent.generate(sketch=sketch, notes=notes)
```

---

<!-- ============ 11. QUOTE ============ -->
<!-- _class: dark quote -->

> <span class="mark">"</span>A bold pull-quote to anchor your point.<span class="mark">"</span>

<div class="by">— Attribution, Role</div>

---

<!-- ============ 12. CLOSING ============ -->
<!-- _class: dark lead -->
<!-- _paginate: false -->

<div class="kicker">Thank you</div>

# Thanks for <em>listening</em>

A short closing line or call to action.
