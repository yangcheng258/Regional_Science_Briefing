# Journal Watch — Regional Science & Regional Economics

A living, auto-updating literature briefing curated by **Yang Cheng** (University of
Wisconsin–Madison), tracking newly published papers across 58 journals: regional science, urban/spatial
economics, rural & land, agricultural & applied economics, and environment & resource
economics (the full RSAI journals list plus AJAE, AEPP, Food Policy, ERAE, JEEM, JAERE,
Land Economics, and Ecological Economics).

**Live page:** https://yangcheng258.github.io/Regional_Science_Briefing/

---

## What the website does

`index.html` is a single self-contained interactive page (no server, no build step at
view time) that lets a reader:

- **Search** every title, author, abstract, and keyword at once.
- **Filter** by theme (8-topic taxonomy), journal, publication-date range (preset or
  custom from–to), or a specific weekly update ("what arrived on 2026-07-20").
- **Read abstracts inline** where openly available; every paper carries a DOI button
  to its version of record.
- **Track freshness**: NEW badges on the latest update's arrivals, an update-week
  filter to replay any Monday batch, and a themes overview on the About tab.

The page follows the Yang Cheng Design System (warm cream surfaces, sage accent,
Newsreader serif display, Geist sans body, Geist Mono kickers, square corners,
hairline publication rows) so it can sit natively inside the personal website.

## How it stays alive

A scheduled Claude (Anthropic) session runs **every Monday morning**: it sweeps the
journals' public pages and open bibliographic sources (SpringerLink, SAGE, Oxford
University Press, RePEc/IDEAS, OUCI/Crossref mirrors), appends new papers to the
archive, tags them by theme, refreshes the deep-read shortlist, rebuilds the page and
spreadsheet, and pushes. GitHub Pages republishes automatically. Every update is a
Git commit, so the full history of the document is preserved.

## Repository layout

| Path | Role |
|---|---|
| `index.html` | The website (generated — do not edit by hand) |
| `briefing.xlsx` | Same data as a sortable spreadsheet (generated) |
| `data/papers.json` | **The archive.** One record per paper: journal, date, title, authors, keywords, abstract, DOI, url, `added` date, `themes` tags. Grows weekly; records are never deleted |
| `data/overview.json` | Themes taxonomy, deep-read picks, site text (byline, how-it-works, disclaimers) |
| `data/journals.json` | Journal list & display order — add a journal here |
| `scripts/build_html.py` | Renders `index.html` from the data files |
| `scripts/build_xlsx.py` | Renders `briefing.xlsx` from the data files |
| `UPDATE_INSTRUCTIONS.md` | Runbook the weekly automated session follows |
| `INTEGRATION.md` | How to link/embed the page in a personal website |

## Maintaining it

- **Change any text on the page** (byline, tagline, disclaimers, themes, picks):
  edit `data/overview.json`, then run `python3 scripts/build_html.py`.
- **Add a journal**: add a line to `data/journals.json` and a retrieval route to the
  table in `UPDATE_INSTRUCTIONS.md`; the next weekly run picks it up.
- **Add a theme**: append to `themes_taxonomy` in `data/overview.json` (never rename
  existing ids — filters and shared links depend on them).
- **Rebuild locally**: `pip install openpyxl && python3 scripts/build_html.py && python3 scripts/build_xlsx.py`

## Journals covered

The full list (58) lives in `data/journals.json` — the original 15 regional-science core,
the complete RSAI journals list, and the agricultural/environmental economics set
(AJAE, AEPP, Food Policy, ERAE, JEEM, JAERE, Land Economics, Ecological Economics).
Small and regional-language journals are covered best-effort as they publish.

## Disclaimers

This is a personal project maintained in the author's individual capacity. It does not
represent the views of — and is not affiliated with, sponsored by, or endorsed by —
the University of Wisconsin–Madison, any funding agency, the listed journals, or their
publishers. Content is collected automatically and may contain errors or omissions;
all errors are the author's own. Paper titles, abstracts, and metadata remain the
copyright of their respective authors and publishers and are reproduced from openly
accessible sources for research and educational purposes only, with a link to the
version of record for every item. Built and maintained with Claude (Anthropic).
