<!--
  SNIPPET PALETTE — Automata Learning Lab brand layouts.
  Each block between two `---` rules is one reusable slide. Copy the block you need
  into a deck that uses `theme: automata` and `html: true`. No <style> needed —
  every helper class (.two-col, .stat-grid, .bento, .flow, .timeline, .chart) lives
  in assets/brand/automata.css.

  Grep a single snippet by its marker, e.g.  `SNIPPET: stat-grid`.
  Slide-level modifiers go in an HTML comment: <!-- _class: dark lead quote -->
-->

---

<!-- SNIPPET: cover -->
<!-- _class: lead dark -->
<!-- _paginate: false -->

<div class="kicker">Automata Learning Lab</div>

# A presentation title <em>in your voice</em>

A short subtitle that frames the talk.

---

<!-- SNIPPET: agenda -->

<div class="kicker">Agenda</div>

## What we'll cover

1. **First section** — the setup
2. **Second section** — the core idea
3. **Third section** — putting it to work

---

<!-- SNIPPET: two-col -->

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

<!-- SNIPPET: stat-grid -->

## The numbers

<div class="stat-grid">
<div class="stat"><div class="num">900M</div><div class="label">Big headline metric</div></div>
<div class="stat"><div class="num">3×</div><div class="label">Improvement factor</div></div>
<div class="stat"><div class="num">40%</div><div class="label">Lower cost</div></div>
</div>

---

<!-- SNIPPET: bento -->

## Feature bento

<div class="bento">
<div class="cell wide"><h3>Headline feature</h3><p>The one that does most of the work.</p></div>
<div class="cell"><h3>Feature</h3><p>Supporting detail.</p></div>
<div class="cell"><h3>Feature</h3><p>Supporting detail.</p></div>
<div class="cell"><h3>Feature</h3><p>Supporting detail.</p></div>
<div class="cell wide"><h3>Wide feature</h3><p>Another that needs room.</p></div>
</div>

---

<!-- SNIPPET: comparison -->

## Comparison

| | Option A | Option B |
|---|---|---|
| Speed | Fast | Faster |
| Cost | $$ | $ |
| Effort | Low | Medium |
| Best for | Quick wins | Scale |

---

<!-- SNIPPET: process -->

## Process

<div class="flow">
<div class="step"><h3>Step one</h3><p>Capture input</p></div>
<div class="arrow">→</div>
<div class="step"><h3>Step two</h3><p>Transform</p></div>
<div class="arrow">→</div>
<div class="step"><h3>Step three</h3><p>Ship output</p></div>
</div>

---

<!-- SNIPPET: timeline -->

## Timeline

<div class="timeline">
<div class="pt"><div class="dot"></div><div class="when">Milestone 1</div><div class="what">Kickoff</div></div>
<div class="pt"><div class="dot"></div><div class="when">Milestone 2</div><div class="what">Build</div></div>
<div class="pt"><div class="dot"></div><div class="when">Milestone 3</div><div class="what">Launch</div></div>
<div class="pt"><div class="dot"></div><div class="when">Milestone 4</div><div class="what">Scale</div></div>
</div>

---

<!-- SNIPPET: chart -->

## Chart

<div class="chart">
<div class="bar" style="height:40%"><span>Q1</span></div>
<div class="bar" style="height:55%"><span>Q2</span></div>
<div class="bar" style="height:70%"><span>Q3</span></div>
<div class="bar" style="height:95%"><span>Q4</span></div>
</div>

---

<!-- SNIPPET: code -->
<!-- _class: dark -->

<div class="kicker">Code block</div>

```python
def build_slide(sketch, notes):
    """Turn a drawing + dictation into a finished slide."""
    return agent.generate(sketch=sketch, notes=notes)
```

---

<!-- SNIPPET: quote -->
<!-- _class: dark quote -->

> <span class="mark">"</span>A bold pull-quote to anchor your point.<span class="mark">"</span>

<div class="by">— Attribution, Role</div>

---

<!-- SNIPPET: closing -->
<!-- _class: dark lead -->
<!-- _paginate: false -->

<div class="kicker">Thank you</div>

# Thanks for <em>listening</em>

A short closing line or call to action.

---

<!--
  IMAGE SNIPPETS (Marpit native syntax — no class needed):
  Side image:        ![bg right:40%](path/to/image.png)
  Full-bleed bg:     ![bg](path/to/image.png)
  Tinted bg:         ![bg brightness:0.4](path/to/image.png)   then use _class: dark
  Centered, sized:   ![w:600](path/to/image.png)
  Two split bgs:     ![bg left](a.png)  ![bg right](b.png)
-->
