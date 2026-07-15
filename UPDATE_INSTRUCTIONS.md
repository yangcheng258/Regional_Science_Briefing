# Weekly update runbook — Regional Science Briefing

You are a Claude session running a scheduled weekly update of this repository.
Follow these steps exactly. The goal: add newly published papers from the journals listed in data/journals.json (~58)
to `data/papers.json`, refresh the overview, rebuild `index.html` + `briefing.xlsx`,
and push. GitHub Pages serves `index.html` automatically.

## 0. Ground rules (critical)

- NEVER invent a title, author, abstract, keyword, or DOI. Only record what you
  actually saw on a fetched page or verified API/mirror response. Missing → `""`.
- The `abstract` field must be the COMPLETE VERBATIM abstract, word-for-word, saved at
  collection time. NEVER put a summary, paraphrase, or truncation in `abstract` — if you
  cannot obtain the full verbatim text, leave `""`. Your own one-sentence distillation
  goes in the separate `summary` field. Save the full data the first time; do not plan
  to re-search later.
- Never delete existing entries in `data/papers.json` — this is a growing archive.
- De-duplicate by DOI (case-insensitive), then by normalized title.
- Pace web fetches: ~4s sleep between requests; on repeated 429s, wait 60s.

## 1. Core journal routes (the full coverage list lives in data/journals.json)

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

### Additional journals (added 2026-07-15) — routes
| Journal | Route |
|---|---|
| American J. of Agricultural Economics, Applied Economic Perspectives & Policy, Geographical Analysis, Int'l J. of Urban and Regional Research (all Wiley) | WebSearch for recent DOIs → abstracts via OUCI |
| European Review of Agricultural Economics (OUP) | academic.oup.com/erae advance-articles (fetchable) / OUCI |
| JAERE (UChicago) | WebSearch DOIs 10.1086/* → OUCI |
| Land Economics (UW Press) | WebSearch / le.uwpress.org / OUCI |
| JEEM, Ecological Economics, Food Policy, Socio-Economic Planning Sciences, Transportation Research Part A (Elsevier) | IDEAS: eee/jeeman, eee/ecolec, eee/jfpoli, eee/soceps, eee/transa |
| Cities, Computers Environment & Urban Systems (Elsevier, non-econ) | WebSearch titles/DOIs; abstracts often unavailable |
| Urban Studies (SAGE) | journals.sagepub.com TOC + OnlineFirst (fetchable, abstracts) |
| J. Geographical Systems, Networks & Spatial Economics, Asia-Pacific JRS, Applied Spatial Analysis & Policy, Review of Regional Research (Springer) | link.springer.com online-first (fetchable, abstracts) |
| REGION (ERSA, OA) | region.ersa.org (fetchable) |
| The Review of Regional Studies (OA) | rrs.scholasticahq.com |
| Remaining small/regional-language RSAI journals in data/journals.json | check quarterly; skip silently if nothing new — do not spend more than 2 fetches each |

Tip: spawn 3–5 parallel general-purpose agents (one per publisher group) with
explicit anti-fabrication instructions and the pacing rules above. Prioritize the
majors; small journals are best-effort.

## 1b. Journals and themes are DATA, not code

- `data/journals.json` is the source of truth for the journal list and display order.
  If the user has added a journal there, include it in your sweep (find a retrieval
  route per the table above; document the route by appending to this file's table).
- `data/overview.json` → `themes_taxonomy` is the stable theme list ({id, label, desc}).
  Assign 1–3 theme ids to EVERY paper you add (field `themes`, judgment call from
  title/abstract). Only add a NEW taxonomy entry when a clearly distinct literature
  emerges that fits nothing existing — new themes should be rare and deliberate.
  Never rename or delete existing theme ids (links and filters depend on them).

## 1c. RIS inbox — merge before anything else

At the START of every run: if `inbox/` contains any `.ris` or `.json` files (the owner drops
Scopus exports there, and the website's self-healing feature auto-commits fetched
abstracts as `scopus-auto-*.json`), run
`python3 scripts/merge_ris.py`. It fills missing abstracts/keywords/authors by
DOI/title match, never overwrites existing data, never creates papers, and moves
processed files to `inbox/processed/`. Mention in your final summary how many
abstracts it filled.

If more than ~25 papers in the archive still have empty abstracts after the merge,
add one line to your final summary suggesting the owner do a 5-minute Scopus RIS
export (the query is documented in inbox/README.md's spirit — journals with walled
abstracts, PUBYEAR = current year).

## 2. Merge into data/papers.json

Each record:
```json
{"journal": "...", "group": "Core regional science|Urban / spatial / econ geography|Rural & land",
 "date": "YYYY-MM-DD or issue string", "title": "...", "authors": "Full Name; Full Name",
 "keywords": "kw1; kw2 or empty", "abstract": "verbatim or empty", "doi": "10.xxxx/... or empty",
 "url": "https://doi.org/<doi> (or publisher PII url if no DOI)", "added": "<today YYYY-MM-DD>",
 "themes": ["1-3 ids from overview.json themes_taxonomy"],
 "summary": "ONE sentence you write distilling the finding (labeled as AI-derived on the page)"}
```
- `added` = today's date for new records only. Never change `added` on old records.
- Journal names must match existing spelling exactly (see ORDER list in scripts/build_html.py).
- Cap per-journal additions at 15/week (note in commit message if capped).
- Also try to FILL BLANKS in existing records (missing abstracts/authors) via the routes above.

## 3. Refresh data/overview.json

- Update `updated` to today.
- You may lightly revise theme DESCRIPTIONS in `themes_taxonomy` if new papers shift the
  picture. Never rename or delete theme ids.
- The deep-read/picks feature has been REMOVED from the site. Do not create or edit
  `picks`, `deep_dois`, or `deep_titles`. In your final summary, you may still name 1–2
  notable new papers (applied ag/rural/regional tilt) for the owner's notification.

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
