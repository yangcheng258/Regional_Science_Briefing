#!/usr/bin/env python3
"""Merge RIS citation files from inbox/ into data/papers.json.

- Parses every inbox/*.ris (Scopus, Web of Science, ScienceDirect, T&F exports).
- Matches records to the archive by DOI (case-insensitive), then normalized title.
- Fills ONLY empty fields (abstract, keywords, authors) — never overwrites existing data.
- Never creates new papers (unmatched RIS records are reported, not added).
- Processed files are moved to inbox/processed/.

Usage: python3 scripts/merge_ris.py
"""
import json, os, re, sys, shutil

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INBOX = os.path.join(BASE, "inbox")
DONE = os.path.join(INBOX, "processed")

def parse_ris(text):
    recs, cur = [], {}
    for line in text.splitlines():
        m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", line)
        if not m:
            # continuation line
            if cur and "_last" in cur and m is None and line.strip():
                cur[cur["_last"]] = cur.get(cur["_last"], "") + " " + line.strip()
            continue
        tag, val = m.group(1), m.group(2).strip()
        if tag == "ER":
            cur.pop("_last", None)
            if cur: recs.append(cur); cur = {}
            continue
        if tag in ("TY",):
            cur = {"_last": None}
        if tag in ("AU", "A1", "KW"):
            cur.setdefault(tag, []).append(val)
        else:
            cur[tag] = (cur.get(tag, "") + " " + val).strip() if tag in cur else val
        cur["_last"] = tag if tag not in ("AU","A1","KW") else None
    if cur and any(k for k in cur if k != "_last"):
        cur.pop("_last", None); recs.append(cur)
    return recs

def norm(t): return re.sub(r"[^a-z0-9]", "", (t or "").lower())

def main():
    papers = json.load(open(os.path.join(BASE, "data", "papers.json")))
    bydoi = {(p.get("doi") or "").lower(): p for p in papers if p.get("doi")}
    bytitle = {norm(p["title"]): p for p in papers}
    os.makedirs(DONE, exist_ok=True)

    files = [f for f in sorted(os.listdir(INBOX)) if f.lower().endswith((".ris", ".json"))]
    if not files:
        print("inbox empty — nothing to merge"); return
    filled_abs = filled_kw = filled_au = matched = unmatched = 0
    for fn in files:
        path = os.path.join(INBOX, fn)
        text = open(path, encoding="utf-8", errors="replace").read()
        if fn.lower().endswith(".json"):
            try:
                items = json.loads(text)
            except Exception:
                print(f"skipping unparseable {fn}"); items = []
            records = [{"DO": it.get("doi",""), "TI": it.get("title",""),
                        "AB": it.get("abstract",""),
                        "KW": [k.strip() for k in (it.get("keywords","") or "").split(";") if k.strip()]}
                       for it in items if isinstance(it, dict)]
        else:
            records = parse_ris(text)
        for r in records:
            doi = (r.get("DO") or r.get("DI") or "").lower().replace("https://doi.org/", "").strip()
            title = r.get("TI") or r.get("T1") or ""
            p = bydoi.get(doi) if doi else None
            if p is None: p = bytitle.get(norm(title))
            if p is None:
                unmatched += 1; continue
            matched += 1
            ab = (r.get("AB") or r.get("N2") or "").strip()
            if ab and not p.get("abstract"):
                # strip common Scopus copyright tail
                ab = re.sub(r"(©|Copyright ©).*$", "", ab).strip()
                p["abstract"] = ab; filled_abs += 1
            kws = r.get("KW") or []
            if kws and not p.get("keywords"):
                p["keywords"] = "; ".join(kws[:10]); filled_kw += 1
            aus = r.get("AU") or r.get("A1") or []
            if aus and not p.get("authors"):
                p["authors"] = "; ".join(a.strip() for a in aus); filled_au += 1
        shutil.move(path, os.path.join(DONE, fn))
        print(f"processed {fn}")
    json.dump(papers, open(os.path.join(BASE, "data", "papers.json"), "w"),
              indent=1, ensure_ascii=False)
    total = len(papers); withabs = sum(1 for p in papers if p.get("abstract"))
    print(f"matched {matched} records ({unmatched} unmatched, ignored)")
    print(f"filled: {filled_abs} abstracts, {filled_kw} keyword sets, {filled_au} author lists")
    print(f"archive now: {withabs}/{total} with abstracts")

if __name__ == "__main__":
    main()
