# Integrating the briefing into your personal website

Your briefing lives in this repo and is published by GitHub Pages at:

```
https://yangcheng258.github.io/Regional_Science_Briefing/
```

It re-publishes automatically every time the weekly update pushes — the "last updated"
timestamp in the header and the NEW badges refresh on their own. You never touch it.

Below are the ways to surface it on your personal GitHub Pages site, from simplest to
most native. Option 1 or 2 is recommended.

---

## Option 1 — Link it from a specific place on your site (simplest)

Add a link wherever you want it (nav menu, Research page, sidebar).

**Jekyll** (most academic themes, e.g. minimal-mistakes, al-folio): in your site's
navigation file (usually `_data/navigation.yml`) add:

```yaml
- title: "Journal Watch"
  url: https://yangcheng258.github.io/Regional_Science_Briefing/
```

Or inline in any Markdown page:

```markdown
[📚 Regional Science Journal Watch — updated weekly](https://yangcheng258.github.io/Regional_Science_Briefing/)
```

**Hugo**: in `config.toml` / `hugo.toml`:

```toml
[[menu.main]]
  name = "Journal Watch"
  url = "https://yangcheng258.github.io/Regional_Science_Briefing/"
  weight = 50
```

---

## Option 2 — A dedicated page on YOUR site that shows the briefing (iframe stub)

Create one small page in your site repo, e.g. `journal-watch.md` (Jekyll):

```markdown
---
title: Journal Watch
layout: page
permalink: /journal-watch/
---

<iframe src="https://yangcheng258.github.io/Regional_Science_Briefing/"
        style="width:100%;height:85vh;border:none;border-radius:12px;"
        title="Regional Science Journal Watch"></iframe>
```

Now `https://your-personal-site/journal-watch/` shows the full interactive briefing inside
your own site, always current. (Hugo: same iframe in any page template or a
`layout: raw` content file.)

---

## Option 3 — "Latest papers" widget for your homepage

Paste this anywhere HTML is allowed on your site. It reads the live archive JSON and
renders the 5 newest papers in plain, styleable markup:

```html
<div id="jw-widget"><em>Loading latest papers…</em></div>
<script>
fetch('https://yangcheng258.github.io/Regional_Science_Briefing/data/papers.json')
  .then(r => r.json())
  .then(papers => {
    const latest = papers
      .sort((a, b) => (b.added + b.date).localeCompare(a.added + a.date))
      .slice(0, 5);
    document.getElementById('jw-widget').innerHTML =
      '<ul style="padding-left:1.2em">' + latest.map(p =>
        `<li style="margin:.4em 0"><a href="${p.url}" target="_blank" rel="noopener">${p.title}</a>` +
        `<br><small>${p.journal} · ${p.date}</small></li>`).join('') +
      `</ul><p><a href="https://yangcheng258.github.io/Regional_Science_Briefing/">Full briefing →</a></p>`;
  })
  .catch(() => { document.getElementById('jw-widget').textContent = 'Briefing temporarily unavailable.'; });
</script>
```

---

## Option 4 — Fully native under your own domain (later, if wanted)

The weekly task can push `index.html`, `briefing.xlsx`, and `data/` into a
`/briefing/` folder of your personal site's repo instead of (or in addition to) this
one. Result: `https://your-personal-site/briefing/` with no iframe. Trade-offs: weekly bot
commits appear in your site's history, and the access token must be scoped to your
site repo. Ask Claude to switch modes and it's a 10-minute change.

---

## Timestamps

- Header of `index.html`: "last updated YYYY-MM-DD · N added in latest update".
- Every paper record in `data/papers.json` carries `added` (date it entered the archive).
- Every Git commit is a dated snapshot — the full history of the document lives in
  this repo's commit log.
