# Weekly update runbook — Regional Science Briefing

You are a Claude session running a scheduled weekly update of this repository.
Follow these steps exactly. The goal: add newly published papers from 15 journals
to `data/papers.json`, refresh the overview, rebuild `index.html` + `briefing.xlsx`,
and push. GitHub Pages serves `index.html` automatically.

## 0. Ground rules (critical)

- NEVER invent a title, author, abstract, keyword, or DOI. Only record what you
  actually saw on a fetched page or verified API/mirror response. Missing → `""`.
- Never delete existing entries in `data/papers.json` — this is a growing archive.
- De-duplicate by DOI (case-insensitive), then by normalized title.
- Pace web fetches: ~4s sleep between requests; on repeated 429s, wait 60s.

## 1. The 15 journals and the retrieval routes that work

Publisher pages of Elsevier (sciencedirect.com), Taylor & Francis (tandfonline.com),
and Wiley (onlinelibrary.wiley.com) BLOCK automated fetching. Crossref/OpenAlex APIs
are robots-blocked for WebFetch. Use these proven routes instead:

| Journal | New-article discovery | Abstract source |
|---|---|---|
| Journal of Regional Science (Wiley) | Crossref via agent WebSearch, or OUCI search | OUCI: `https://ouci.dntb.gov.ua/en/?q=<DOI>` (mirrors Wiley Crossref abstracts) |
| Growth and Change (Wiley) | same | same |
| Annals of Regional Science (Springer) | `https://link.springer.com/journal/168/online-first` (fetchable) | SpringerLink article pages (fetchable) |
| Int'l Regional Science Review (SAGE) | `https://journals.sagepub.com/toc/irxa/current` + OnlineFirst | SAGE pages or OUCI (SAGE deposits abstracts to Crossref) |
| Environment & Planning A (SAGE) | `https://journals.sagepub.com/toc/epna/current` + OnlineFirst | SAGE pages (fetchable) |
| Journal of Economic Geography (OUP) | `https://academic.oup.com/joeg/advance-articles` | OUP pages / OUCI (OUP deposits abstracts) |
| Journal of Urban Economics (Elsevier) | IDEAS: `https://ideas.repec.org/s/eee/juecon.html` | IDEAS article pages (full abstracts + keywords) |
| Regional Science & Urban Economics (Elsevier) | IDEAS: `https://ideas.repec.org/s/eee/regeco.html` (volume-assigned) + WebSearch for articles-in-press DOIs | IDEAS pages when available; in-press items usually have NO open abstract — leave `""` |
| Land Use Policy (Elsevier) | IDEAS: `https://ideas.repec.org/s/eee/lauspo.html` | IDEAS article pages |
| Papers in Regional Science (Elsevier) | WebSearch "Papers in Regional Science 2026 volume issue" + Crossref-indexed DOIs via search | NOT openly mirrored (not on RePEc post-2024, no Crossref abstracts). Leave `""`, keep DOI link |
| Regional Science Policy & Practice (Elsevier) | same approach | same — leave `""` |
| Journal of Rural Studies (Elsevier) | WebSearch site:sciencedirect.com or journal TOC via search snippets | NOT openly mirrored. Leave `""` |
| Regional Studies (T&F) | Crossref DOIs via WebSearch / OUCI search by journal | T&F deposits NO abstracts anywhere open. Leave `""` |
| Spatial Economic Analysis (T&F) | same | same |
| Economic Geography (T&F) | same | same |

Tip: spawn 2–3 parallel general-purpose agents (one per publisher group) with
explicit anti-fabrication instructions and the pacing rules above.

## 2. Merge into data/papers.json

Each record:
```json
{"journal": "...", "group": "Core regional science|Urban / spatial / econ geography|Rural & land",
 "date": "YYYY-MM-DD or issue string", "title": "...", "authors": "Full Name; Full Name",
 "keywords": "kw1; kw2 or empty", "abstract": "verbatim or empty", "doi": "10.xxxx/... or empty",
 "url": "https://doi.org/<doi> (or publisher PII url if no DOI)", "added": "<today YYYY-MM-DD>"}
```
- `added` = today's date for new records only. Never change `added` on old records.
- Journal names must match existing spelling exactly (see ORDER list in scripts/build_html.py).
- Cap per-journal additions at 15/week (note in commit message if capped).
- Also try to FILL BLANKS in existing records (missing abstracts/authors) via the routes above.

## 3. Refresh data/overview.json

- Update `updated` to today.
- Revise `themes` (8 max) if new papers shift the picture; otherwise light edits.
- Revise `picks` (10 max): keep must-reads, swap in strong new papers. The user is an
  applied/agricultural economist at UW–Madison (regional science, rural, land use) —
  tilt picks toward applied ag/rural/regional-methods relevance.
- Keep `deep_dois` in sync with picks (DOIs of picked papers).

## 4. Rebuild and verify

```bash
cd <repo>
python3 scripts/build_html.py        # writes index.html
python3 scripts/build_xlsx.py        # writes briefing.xlsx (needs: pip install openpyxl --break-system-packages)
```
Verify before pushing:
- `index.html` parses: the `const DATA=[...]` JSON loads, paper count >= previous count.
- No record lost: new papers.json length >= old length.
- Every record has a non-empty `url`.

## 5. Commit & push

```bash
git add -A
git commit -m "Weekly update YYYY-MM-DD: +N papers (M with abstracts)"
git push origin main
```
The push credentials are embedded in the remote URL already configured in the clone command you were given.

## 6. Report

End your session output with a short summary: N new papers, per-journal counts,
how many abstracts retrieved, any journals that returned nothing (say why), and
1-2 sentences on notable new papers. This summary reaches the user via push/email
notification.
