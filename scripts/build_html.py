#!/usr/bin/env python3
"""Build index.html from data/papers.json + data/overview.json + data/journals.json.

Styled per the Yang Cheng Design System (claude.ai/design project):
warm cream surfaces, sage accent, Newsreader serif display, Geist sans body,
Geist Mono uppercase kickers, square corners, hairline pub-rows, no shadows.

Usage: python3 scripts/build_html.py [YYYY-MM-DD]
Weekly updates should ONLY edit the data/*.json files and rerun this script.
"""
import json, os, sys, re
from datetime import date

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
papers = json.load(open(os.path.join(BASE, "data", "papers.json")))
OV = json.load(open(os.path.join(BASE, "data", "overview.json")))
JOURNALS = json.load(open(os.path.join(BASE, "data", "journals.json")))
TODAY = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
LATEST = max(p.get("added", "") for p in papers)

ORDER = [j["name"] for j in JOURNALS]
TAX = OV.get("themes_taxonomy", [])
SITE = OV.get("site", {})

def ptype(t):
    tl = t.lower()
    if tl.startswith("corrigendum") or tl.startswith("erratum"): return "Corrigendum"
    if tl.startswith("book review") or tl == "book review": return "Book review"
    return "Research"

data = []
for p in papers:
    url = p.get("url") or ("https://doi.org/" + p["doi"] if p.get("doi") else "")
    disp = p.get("doi") or (("ScienceDirect: " + url.split("/pii/")[-1]) if "/pii/" in url else url)
    data.append({
        "journal": p["journal"], "group": p.get("group",""), "date": p.get("date",""),
        "title": p["title"], "authors": p.get("authors",""), "type": ptype(p["title"]),
        "keywords": [k.strip() for k in p.get("keywords","").split(";") if k.strip()],
        "abstract": p.get("abstract",""), "summary": p.get("summary",""), "url": url, "doi": disp,
        "themes": p.get("themes", []),
        "added": p.get("added",""), "new": p.get("added","") == LATEST,
        "id": (p.get("doi") or "").lower() or re.sub(r"[^a-z0-9]+","-", p["title"].lower()).strip("-")[:80],
        "jorder": ORDER.index(p["journal"]) if p["journal"] in ORDER else 99,
    })
data.sort(key=lambda d: (d["jorder"], d["date"]))

n_total = len(data)
n_abs = sum(1 for d in data if d["abstract"])
n_new = sum(1 for d in data if d["new"])
n_j = len(set(d["journal"] for d in data))

HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Journal Watch — Yang Cheng</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&family=Geist+Mono:wght@400;500&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,300;1,6..72,400&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#f6f4ef; --card:#fbfaf6; --footer-bg:#e8e3d5; --line:#d8d4ca;
  --fg:#1a1a1a; --muted:#6a6a66;
  --accent:#4a5d3a; --accent-hover:#3d4d2f; --accent-soft:#b8c9a8;
  --chip-active:#c8d29a; --chip-active-ink:#2c3a1a;
  --serif:'Newsreader',ui-serif,Georgia,serif;
  --sans:'Geist',ui-sans-serif,system-ui,-apple-system,sans-serif;
  --mono:'Geist Mono',ui-monospace,Menlo,monospace;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{font-family:var(--sans);background:var(--bg);color:var(--fg);
 -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;line-height:1.5}
a{color:var(--accent);text-decoration:none}
a:hover{color:var(--accent-hover);text-decoration:underline}
.shell{max-width:1200px;margin:0 auto;padding:0 56px 0}
@media(max-width:760px){.shell{padding:0 20px}}

/* ── Topbar ── */
.topbar{display:flex;justify-content:space-between;align-items:center;
 padding:14px 0;border-bottom:1px solid var(--line);
 position:sticky;top:0;z-index:10;background:rgba(246,244,239,.9);
 backdrop-filter:blur(8px) saturate(140%)}
.mark{font-family:var(--serif);font-style:italic;font-size:22px;color:var(--fg);letter-spacing:-.01em}
.topnav{display:flex;gap:26px;align-items:center}
.topnav a{color:var(--fg);font-size:13px;font-weight:500;letter-spacing:.02em}
.topnav a:hover{color:var(--accent);text-decoration:none}
.topnav a.current{color:var(--accent)}

/* ── Page head ── */
.pagehead{padding:20px 0 32px;margin-top:44px;border-top:2px solid var(--fg);
 border-bottom:1px solid var(--line);display:grid;grid-template-columns:1fr 230px;
 gap:32px;align-items:start;position:relative}
@media(max-width:760px){.pagehead{grid-template-columns:1fr}}
.pagehead .tag{position:absolute;top:-10px;left:0;background:var(--bg);padding-right:16px;
 font-family:var(--mono);font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:var(--muted)}
.pagehead h1{font-family:var(--serif);font-size:clamp(40px,6vw,64px);line-height:1;
 letter-spacing:-.02em;font-weight:300;margin:0 0 12px;text-wrap:balance}
.pagehead h1 em{font-style:italic;color:var(--accent);font-weight:300}
.pagehead .desc{font-size:14px;line-height:1.55;color:var(--fg);margin:0 0 10px;max-width:52ch}
.byline{font-size:13px;color:var(--muted)}
.byline strong{color:var(--fg);font-weight:500}
.sidemeta{font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;
 color:var(--muted);line-height:1.8;padding-top:4px;justify-self:end;text-align:right}
.sidemeta strong{color:var(--fg);font-weight:500;display:block;font-family:var(--sans);
 text-transform:none;letter-spacing:0;font-size:15px}

/* ── Collapsible sections ── */
details.sect{border-bottom:1px solid var(--line);padding:0 0 4px}
details.sect summary{cursor:pointer;list-style:none;padding:16px 0;
 font-family:var(--mono);font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:var(--fg)}
details.sect summary::-webkit-details-marker{display:none}
details.sect summary::before{content:"› ";color:var(--accent)}
details.sect[open] summary::before{content:"⌄ "}
.theme{margin:6px 0 14px}
.theme h4{font-family:var(--serif);font-weight:400;font-size:18px;margin:0 0 2px;letter-spacing:-.01em}
.theme p{margin:0;font-size:13px;color:var(--muted);max-width:70ch}
.pick{margin:0 0 14px;padding-left:14px;border-left:2px solid var(--accent)}
.pick .t{font-family:var(--serif);font-size:16px;font-weight:500;letter-spacing:-.005em}
.pick .a{font-size:12px;color:var(--muted);margin-top:1px}
.pick .w{font-size:13px;margin-top:2px}
.about p{font-size:14px;line-height:1.6;max-width:75ch;margin:0 0 10px}
.about .dhead{font-family:var(--mono);font-size:10px;letter-spacing:.15em;
 text-transform:uppercase;color:var(--accent);margin:18px 0 8px}
.about li{font-size:13px;color:var(--muted);line-height:1.6;margin-bottom:6px;max-width:80ch}
details.jgrp{border:1px solid var(--line);background:var(--card);margin:0 0 10px}
details.jgrp summary{cursor:pointer;list-style:none;padding:12px 14px;
 font-family:var(--mono);font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:var(--fg)}
details.jgrp summary::-webkit-details-marker{display:none}
details.jgrp summary::before{content:"› ";color:var(--accent)}
details.jgrp[open] summary::before{content:"⌄ "}
.jcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:1px;background:var(--line);border-top:1px solid var(--line)}
.jcard{display:flex;gap:10px;align-items:center;background:var(--card);padding:10px 12px;text-decoration:none}
.jcard:hover{background:var(--bg);text-decoration:none}
.jthumb{width:40px;height:52px;flex:none;display:flex;align-items:center;justify-content:center;
 font-family:var(--mono);font-size:11px;font-weight:500;color:rgba(255,255,255,.95);letter-spacing:.05em;
 position:relative;overflow:hidden}
.jthumb img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.jname{font-family:var(--serif);font-size:13.5px;font-weight:500;line-height:1.25;color:var(--fg)}
.jmeta{font-family:var(--mono);font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-top:2px}

/* ── Controls ── */
.controls{position:sticky;top:51px;z-index:9;background:rgba(246,244,239,.94);
 backdrop-filter:blur(8px) saturate(140%);padding:14px 0 12px;border-bottom:1px solid var(--line)}
#q{width:100%;padding:11px 14px;font-size:14px;font-family:var(--sans);
 border:1px solid var(--line);background:var(--card);color:var(--fg);outline:none;border-radius:0}
#q:focus{border-color:var(--accent)}
.row{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;align-items:center}
select,input[type=date]{background:var(--card);color:var(--fg);border:1px solid var(--line);
 border-radius:0;padding:7px 9px;font-size:12px;font-family:var(--sans)}
.toggle{display:flex;align-items:center;gap:6px;color:var(--muted);font-size:12px;cursor:pointer;user-select:none}
.toggle input{accent-color:var(--accent)}
.lbl,.fb-label{font-family:var(--mono);font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:var(--muted)}
.fb-label{min-width:64px}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;align-items:center}
.chips.collapsed{max-height:32px;overflow:hidden}
.chipfold{font-family:var(--mono);font-size:10px;letter-spacing:.15em;text-transform:uppercase;
 color:var(--muted);background:none;border:none;cursor:pointer;padding:6px 0;min-width:88px;text-align:left}
.chipfold:hover{color:var(--accent)}
.chip{font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;
 padding:6px 12px;background:transparent;color:var(--fg);border:1px solid var(--line);
 border-radius:999px;cursor:pointer;white-space:nowrap}
.chip:hover{border-color:var(--fg)}
.chip.active{background:var(--chip-active);color:var(--chip-active-ink);border-color:var(--chip-active)}
.count{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;
 margin:14px 0 4px;font-family:var(--mono);font-size:10px;letter-spacing:.1em;
 text-transform:uppercase;color:var(--muted)}
.clear{color:var(--accent);cursor:pointer}
.clear:hover{color:var(--accent-hover)}

/* ── Publication rows ── */
.pf{border-bottom:1px solid var(--line);transition:transform .2s ease}
.pf:hover{transform:translateY(-2px)}
.prow{display:grid;grid-template-columns:72px 1fr;gap:22px;padding:18px 4px;align-items:start}
@media(max-width:600px){.prow{grid-template-columns:1fr;gap:6px}}
.ycol .year{font-family:var(--serif);font-size:18px;line-height:1.1;padding-top:2px}
.ycol small{display:block;font-family:var(--mono);font-size:9px;letter-spacing:.1em;
 text-transform:uppercase;color:var(--accent);font-weight:500;margin-top:2px}
.ycol .newb{display:inline-block;margin-top:6px;font-family:var(--mono);font-size:9px;
 letter-spacing:.1em;text-transform:uppercase;background:var(--accent);color:#fff;padding:2px 6px}
.kicker{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;
 color:var(--accent);font-weight:500;margin-bottom:4px;display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.kicker .typ{color:var(--muted)}
.kicker .deep{color:var(--fg);background:var(--chip-active);padding:1px 7px}
.ptitle{font-family:var(--serif);font-size:19px;font-weight:500;line-height:1.25;
 letter-spacing:-.005em;margin:0 0 4px;text-wrap:balance}
.authors{font-size:12px;color:var(--muted);margin-bottom:6px}
.tchips{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0 2px}
.pc-chip{font-family:var(--mono);font-size:9px;letter-spacing:.1em;text-transform:uppercase;
 padding:3px 8px;border-radius:999px;border:1px solid var(--accent);color:var(--accent);
 background:var(--card);cursor:pointer}
.pc-chip:hover{background:var(--accent);color:#fff}
.kws{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0 2px}
.kws span{font-family:var(--mono);font-size:9px;letter-spacing:.1em;text-transform:uppercase;
 padding:3px 8px;border-radius:999px;border:1px solid var(--line);color:var(--muted);
 background:var(--card);cursor:pointer}
.kws span:hover{border-color:var(--fg);color:var(--fg)}
.sumline{font-family:var(--serif);font-style:italic;font-size:15px;line-height:1.5;color:var(--fg);margin:2px 0 4px;max-width:80ch}
.abs{font-size:13.5px;line-height:1.6;color:var(--fg);margin:8px 0 2px;max-width:85ch}
.abs.clamped{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.absmore{font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;
 color:var(--accent);cursor:pointer;margin:2px 0 0;display:inline-block}
.noabs{font-size:12.5px;font-style:italic;color:var(--muted);margin:6px 0 2px}
.plinks{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-top:10px;padding-top:8px;
 border-top:1px solid var(--line)}
.plinks a.doi{display:inline-block;padding:4px 10px;background:var(--fg);color:var(--bg);
 font-family:var(--mono);font-size:10px;letter-spacing:.05em;text-decoration:none}
.plinks a.doi:hover{background:var(--accent);color:#fff}
.plinks .doitxt{font-family:var(--mono);font-size:10px;color:var(--muted);word-break:break-all}
.empty{text-align:center;color:var(--muted);padding:48px 0;font-family:var(--serif);font-style:italic;font-size:18px}
.inlbl{font-family:var(--mono);font-size:9px;letter-spacing:.15em;text-transform:uppercase;
 color:var(--muted);margin-right:4px;align-self:center}
div.inlbl{margin:8px 0 2px}
.count .rgroup{display:flex;gap:12px;flex-wrap:wrap;align-items:center}

/* ── Footer ── */
footer{background:var(--footer-bg);margin-top:64px;border-top:1px solid var(--line)}
footer .inner{max-width:1200px;margin:0 auto;padding:36px 56px 44px}
@media(max-width:760px){footer .inner{padding:28px 20px}}
footer .fmark{font-family:var(--serif);font-style:italic;font-size:20px;margin-bottom:6px}
footer p{font-size:12.5px;color:var(--muted);line-height:1.6;max-width:88ch;margin:0 0 8px}
footer .fmono{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;
 color:var(--muted);margin-top:14px}
</style></head><body>

<div class="shell">
  <div class="topbar">
    <div class="mark">__AUTHOR__</div>
    <nav class="topnav">
      <a href="#" id="nav-all">Papers</a>
      <a href="#about" id="nav-about">About</a>
      <a href="https://github.com/yangcheng258/Regional_Science_Briefing/raw/main/briefing.xlsx">Spreadsheet</a>
      <a href="https://raw.githubusercontent.com/yangcheng258/Regional_Science_Briefing/main/data/papers.json" target="_blank" rel="noopener">Data</a>
      <a href="https://github.com/yangcheng258/Regional_Science_Briefing" target="_blank" rel="noopener">GitHub</a>
    </nav>
  </div>

  <section class="pagehead">
    <div class="tag">Journal Watch · Updated __TODAY__</div>
    <div>
      <h1>The literature, <em>as it lands.</em></h1>
      <p class="desc">__TAGLINE__ New papers from __NJALL__ journals across regional science, urban economics, rural &amp; land studies, and agricultural &amp; environmental economics — collected automatically every Monday, tagged by theme, searchable, every entry linked to its version of record.</p>
      <p class="desc"><a href="#about">About this page &amp; how to use</a></p>
      <p class="byline">Curated by <strong>__AUTHOR__</strong> · __AFFILIATION__ · maintained with Claude</p>
    </div>
    <div class="sidemeta">
      Papers indexed<strong>__NT__</strong>
      Journals covered<strong>__NJALL__</strong>
      Abstracts inline<strong>__NA__</strong>
      New this update<strong>__NNEW__</strong>
    </div>
  </section>

  <div id="view-all">
  <div class="controls">
    <input id="q" placeholder="Search titles, authors, abstracts, keywords…" autocomplete="off">
    <div class="row">
      <select id="sort">
        <option value="jorder">Sort: by journal</option>
        <option value="date_desc">Sort: newest first</option>
        <option value="date_asc">Sort: oldest first</option>
        <option value="title">Sort: title A–Z</option>
      </select>
      <select id="pubrange">
        <option value="">Published: all time</option>
        <option value="1">Published: last month</option>
        <option value="3">Published: last 3 months</option>
        <option value="12">Published: last 12 months</option>
      </select>
      <select id="upd"><option value="">Update: all</option></select>
      <span class="lbl">from</span><input type="date" id="from">
      <span class="lbl">to</span><input type="date" id="to">
    </div>
    <div class="row">
      <label class="toggle"><input type="checkbox" id="onlyabs"> abstract available</label>
      <label class="toggle"><input type="checkbox" id="research" checked> research only</label>

    </div>
    <div class="chips collapsed" id="trow"><button class="chipfold" data-row="trow">Theme ▸</button><span id="tchips" style="display:contents"></span></div>
    <div class="chips collapsed" id="jrow"><button class="chipfold" data-row="jrow">Journal ▸</button><span id="jchips" style="display:contents"></span></div>
  </div>

  <div class="count" id="countbar"><span id="count"></span><span class="clear" id="clear">✕ clear filters</span></div>
  <div id="list"></div>
  </div><!-- /view-all -->

  <div id="view-about" style="display:none">
    <p class="lede">About this page — what it is, how it works, and the fine print.</p>
    <div class="about">
      __HOW__
      <div class="dhead">Themes</div>
      <div id="themes"></div>
      <div class="dhead">Journals covered</div>
      <div id="jlist"></div>
      <div class="dhead">How to use</div>
      <ul>__USING__</ul>
      <div class="dhead">Your reading log &amp; bookmarks</div>
      <ul>__READING__</ul>
      <div class="dhead">Add journals, themes, or edits</div>
      <ul>__ADDING__</ul>
      <div class="dhead">Disclaimers</div>
      <ul>__DISCLAIMERS__</ul>
    </div>
  </div>
</div>

<footer>
  <div class="inner">
    <div class="fmark">__AUTHOR__</div>
    <p>__FOOTDISC__</p>
    <p class="fmono">Journal Watch · updated __TODAY__ · built &amp; maintained with Claude (Anthropic) ·
    <a href="https://github.com/yangcheng258/Regional_Science_Briefing" target="_blank" rel="noopener">source &amp; history on GitHub</a></p>
  </div>
</footer>

<script>
const DATA=__PAYLOAD__;
const JALL=__JALL__;
const TAX=__TAX__;
const TODAY="__TODAY__";
const TLABEL={}; TAX.forEach(t=>TLABEL[t.id]=t.label);

// Owner keys (planted by the private setup link; absent for visitors)
function lsGet(k){try{return localStorage.getItem(k)}catch(e){return null}}

const jlistEl=document.getElementById("jlist");
if(jlistEl){
 const GGRAD={
  "Core regional science":["#cdd9bf","#8aa074","#4a5d3a"],
  "Urban / spatial / econ geography":["#c0d6e8","#7a9bc2","#33567a"],
  "Rural & land":["#e3d9c2","#a89272","#5d4a2c"],
  "Agricultural & applied economics":["#e7d6b8","#c8a97a","#7a6347"],
  "Environment & resource economics":["#c8e2cb","#6fa57c","#2c5a3a"]};
 const initials=n=>n.replace(/[^A-Za-z ]/g,"").split(" ").filter(w=>w.length>2&&!/^(and|the|of|in|for|part)$/i.test(w)).map(w=>w[0]).join("").slice(0,3).toUpperCase()||n.slice(0,2).toUpperCase();
 const groups={};
 JALL.forEach(j=>{(groups[j.group]=groups[j.group]||[]).push(j);});
 const counts={};
 DATA.forEach(d=>{counts[d.journal]=(counts[d.journal]||0)+1;});
 jlistEl.innerHTML=Object.entries(groups).map(([g,js],gi)=>{
  const grad=GGRAD[g]||["#d8d4ca","#a8a49a","#6a6a66"];
  return `<details class="jgrp"${gi===0?" open":""}><summary>${g} · ${js.length} journals</summary><div class="jcards">${
   js.map((j,i)=>{
    const a=grad[i%2], b=grad[(i%2)+1];
    const ang=(i*47)%360;
    return `<a class="jcard" href="${j.url||"#"}" target="_blank" rel="noopener">
      <span class="jthumb" data-jn="${j.name.replace(/"/g,"&quot;")}" style="background:linear-gradient(${ang}deg,${a},${b})">${initials(j.name)}${j.img?`<img src="${j.img}" alt="" loading="lazy" onerror="this.remove()">`:""}</span>
      <span><span class="jname">${j.name}</span><br><span class="jmeta">${counts[j.name]?counts[j.name]+" papers · ":""}visit journal ↗</span></span></a>`;
   }).join("")
  }</div></details>`;
 }).join("")+
 `<p style="font-size:12px;color:#6a6a66;margin-top:8px">Papers counts reflect the current archive; journals without a count are covered and will appear as they publish.</p>`;
 setTimeout(resolveWikiCovers,1500);
}
async function resolveWikiCovers(){
 const wikimap={};JALL.forEach(j=>{if(j.wiki)wikimap[j.wiki]=j.name;});
 const titles=Object.keys(wikimap);if(!titles.length)return;
 const byName={};
 for(let i=0;i<titles.length;i+=25){
  const batch=titles.slice(i,i+25);
  try{
   const u="https://en.wikipedia.org/w/api.php?action=query&format=json&origin=*&prop=pageimages&pithumbsize=200&redirects=1&titles="+encodeURIComponent(batch.join("|"));
   const r=await fetch(u);if(!r.ok)continue;
   const d=await r.json();
   const redir={};(d.query.redirects||[]).forEach(x=>{redir[x.to]=x.from;});
   const norm={};(d.query.normalized||[]).forEach(x=>{norm[x.to]=x.from;});
   Object.values(d.query.pages||{}).forEach(p=>{
    if(!p.thumbnail||!p.thumbnail.source)return;
    let t=p.title;
    if(redir[t])t=redir[t];
    if(norm[t])t=norm[t];
    const name=wikimap[t]||wikimap[p.title];
    if(name)byName[name]=p.thumbnail.source;
   });
  }catch(e){}
 }
 document.querySelectorAll(".jthumb[data-jn]").forEach(el=>{
  if(el.querySelector("img"))return;              // publisher cover already showing
  const src=byName[el.dataset.jn];
  if(!src)return;
  const im=document.createElement("img");
  im.alt="";im.loading="lazy";im.src=src;
  im.onerror=()=>im.remove();
  el.appendChild(im);
 });
}
const themesEl=document.getElementById("themes");
if(themesEl)themesEl.innerHTML=TAX.map(t=>
 `<div class="theme"><h4>${t.label}</h4><p>${t.desc}</p></div>`).join("");


const esc=s=>(s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));

function pdate(d){
  let m=(d||"").match(/(\\d{4})-(\\d{2})(?:-(\\d{2}))?/);
  if(m) return m[1]+"-"+m[2]+"-"+(m[3]||"15");
  m=(d||"").match(/(\\d{4})/);
  return m? m[1]+"-06-15" : "";
}
function monthsAgo(n){
  const t=new Date(TODAY+"T00:00:00Z"); t.setUTCMonth(t.getUTCMonth()-n);
  return t.toISOString().slice(0,10);
}
function dparts(d){
  const y=(d||"").match(/\\d{4}/); const md=(d||"").match(/\\d{4}-(\\d{2})(?:-(\\d{2}))?/);
  let sub=(d||"").replace(/\\d{4}-?/,"").trim();
  if(md) sub=md[2]? `${md[1]}·${md[2]}` : `iss ${md[1]}`;
  return {year: y?y[0]:"—", sub: sub||""};
}

let state={q:"",sort:"jorder",jfilter:"",tfilter:"",pubrange:"",upd:"",from:"",to:"",
           onlyabs:false,research:true};

const tchips=document.getElementById("tchips");
tchips.innerHTML=`<button class="chip active" data-t="">All</button>`+
 TAX.map(t=>{const n=DATA.filter(d=>d.themes.includes(t.id)).length;
   return `<button class="chip" data-t="${t.id}">${t.label} (${n})</button>`;}).join("");
tchips.addEventListener("click",e=>{const c=e.target.closest(".chip");if(!c)return;
 state.tfilter=c.dataset.t;[...tchips.children].forEach(x=>x.classList.toggle("active",x===c));render();});

const jchips=document.getElementById("jchips");
const journals=[...new Set(DATA.map(d=>d.journal))];
jchips.innerHTML=`<button class="chip active" data-j="">All</button>`+
 journals.map(j=>`<button class="chip" data-j="${esc(j)}">${esc(j)} (${DATA.filter(d=>d.journal===j).length})</button>`).join("");
jchips.addEventListener("click",e=>{const c=e.target.closest(".chip");if(!c)return;
 state.jfilter=c.dataset.j;[...jchips.children].forEach(x=>x.classList.toggle("active",x===c));render();});

const updSel=document.getElementById("upd");
[...new Set(DATA.map(d=>d.added).filter(Boolean))].sort().reverse().forEach(a=>{
  const n=DATA.filter(d=>d.added===a).length;
  const o=document.createElement("option"); o.value=a; o.textContent=`Update: ${a} (${n})`; updSel.appendChild(o);
});

document.querySelectorAll(".chipfold").forEach(b=>{
 b.addEventListener("click",()=>{
  const row=document.getElementById(b.dataset.row);
  const c=row.classList.toggle("collapsed");
  b.textContent=b.textContent.split(" ")[0]+(c?" ▸":" ▾");
 });
});

const bind=(id,key,ev,fn)=>document.getElementById(id).addEventListener(ev,e=>{state[key]=fn?fn(e):e.target.value;render();});
bind("q","q","input",e=>e.target.value.toLowerCase());
bind("sort","sort","change");
bind("pubrange","pubrange","change");
bind("upd","upd","change");
bind("from","from","change");
bind("to","to","change");
bind("onlyabs","onlyabs","change",e=>e.target.checked);
bind("research","research","change",e=>e.target.checked);

// ---- GitHub commit helpers (used by self-healing) ----
const REPO_API="https://api.github.com/repos/yangcheng258/Regional_Science_Briefing/contents/";
async function ghGet(path,token){
 const r=await fetch(REPO_API+path,{headers:{Authorization:"Bearer "+token,Accept:"application/vnd.github+json"}});
 if(r.status===404)return null;
 if(!r.ok)throw new Error("GitHub GET "+path+": "+r.status);
 return r.json();
}
async function ghPut(path,token,obj,sha,msg){
 const content=btoa(unescape(encodeURIComponent(JSON.stringify(obj,null,1))));
 const body={message:msg,content:content};if(sha)body.sha=sha;
 const r=await fetch(REPO_API+path,{method:"PUT",
  headers:{Authorization:"Bearer "+token,Accept:"application/vnd.github+json","Content-Type":"application/json"},
  body:JSON.stringify(body)});
 if(!r.ok)throw new Error("GitHub PUT "+path+": "+r.status);
 return r.json();
}





document.getElementById("clear").addEventListener("click",()=>{
  state={q:"",sort:"jorder",jfilter:"",tfilter:"",pubrange:"",upd:"",from:"",to:"",
         onlyabs:false,research:true};
  document.getElementById("q").value="";document.getElementById("sort").value="jorder";
  document.getElementById("pubrange").value="";document.getElementById("upd").value="";
  document.getElementById("from").value="";document.getElementById("to").value="";
  document.getElementById("onlyabs").checked=false;
  document.getElementById("research").checked=true;
  [...tchips.children].forEach((x,i)=>x.classList.toggle("active",i===0));
  [...jchips.children].forEach((x,i)=>x.classList.toggle("active",i===0));
  render();});

function matches(d){

 if(state.jfilter&&d.journal!==state.jfilter)return false;
 if(state.tfilter&&!d.themes.includes(state.tfilter))return false;
 if(state.onlyabs&&!d.abstract)return false;
 if(state.research&&d.type!=="Research")return false;
 if(state.upd&&d.added!==state.upd)return false;
 const pd=pdate(d.date);
 if(state.pubrange&&(!pd||pd<monthsAgo(+state.pubrange)))return false;
 if(state.from&&(!pd||pd<state.from))return false;
 if(state.to&&(!pd||pd>state.to))return false;
 if(state.q){const hay=(d.title+" "+d.authors+" "+d.abstract+" "+d.keywords.join(" ")+" "+d.journal+" "+d.themes.map(t=>TLABEL[t]||t).join(" ")).toLowerCase();
   return state.q.split(/\\s+/).every(w=>hay.includes(w));}
 return true;
}
function sortFn(a,b){
 if(state.sort==="date_desc")return pdate(b.date).localeCompare(pdate(a.date));
 if(state.sort==="date_asc")return pdate(a.date).localeCompare(pdate(b.date));
 if(state.sort==="title")return a.title.localeCompare(b.title);
 return a.jorder-b.jorder || (a.date||"").localeCompare(b.date||"");
}
function rowHTML(d,i,pref){
  const dp=dparts(d.date);
  const typ=d.type!=="Research"?`<span class="typ">${d.type}</span>`:"";
  const tp=d.themes.length?`<div class="tchips"><span class="inlbl">Themes</span>${d.themes.map(t=>`<span class="pc-chip" data-t="${t}">${TLABEL[t]||t}</span>`).join("")}</div>`:"";
  const kw=d.keywords.length?`<div class="kws"><span class="inlbl">Keywords</span>${d.keywords.map(k=>`<span data-k="${esc(k)}">${esc(k)}</span>`).join("")}</div>`:"";
  const brief=d.summary?`<div class="inlbl">In brief · AI</div><div class="sumline">${esc(d.summary)}</div>`:"";
  const longAbs=d.abstract.length>420;
  const aid=(pref||"a")+"abs"+i;
  const abs=d.abstract
    ?`<div class="inlbl">Abstract</div><div class="abs${longAbs?' clamped':''}" id="${aid}">${esc(d.abstract)}</div>${longAbs?`<span class="absmore" data-a="${aid}">› more</span>`:""}`
    :`<div class="noabs">Abstract not openly mirrored — read it at the version of record.</div>`;
  const link=d.url?`<a class="doi" href="${d.url}" target="_blank" rel="noopener">DOI ↗</a>
       <span class="doitxt">${esc(d.doi)}</span>`:`<span class="doitxt">no link</span>`;
  return `<div class="pf"><div class="prow">
   <div class="ycol"><div class="year">${dp.year}<small>${dp.sub||"&nbsp;"}</small></div>${d.new?'<span class="newb">New</span>':''}</div>
   <div class="content">
     <div class="kicker">${esc(d.journal)}${typ}</div>
     <h3 class="ptitle">${esc(d.title)}</h3>
     <div class="authors">${esc(d.authors)||"—"}</div>
     ${tp}${kw}${brief}${abs}
     <div class="plinks">${link}</div>
   </div></div></div>`;
}

function attachHandlers(list){
 list.querySelectorAll(".kws span").forEach(s=>s.addEventListener("click",()=>{
   location.hash="";document.getElementById("q").value=s.dataset.k;state.q=s.dataset.k.toLowerCase();render();
   window.scrollTo({top:0,behavior:"smooth"});}));
 list.querySelectorAll(".pc-chip").forEach(s=>s.addEventListener("click",()=>{
   location.hash="";state.tfilter=s.dataset.t;
   [...tchips.children].forEach(x=>x.classList.toggle("active",x.dataset.t===s.dataset.t));
   render();window.scrollTo({top:0,behavior:"smooth"});}));

 list.querySelectorAll(".absmore").forEach(s=>s.addEventListener("click",()=>{
   const el=document.getElementById(s.dataset.a);
   el.classList.toggle("clamped");
   s.textContent=el.classList.contains("clamped")?"› more":"‹ less";}));
}

function render(){
 const list=document.getElementById("list");
 const rows=DATA.filter(matches).sort(sortFn);
 document.getElementById("count").textContent=rows.length+" of "+DATA.length+" papers";
 if(!rows.length){list.innerHTML=`<div class="empty">No papers match your filters.</div>`;}
 else{list.innerHTML=rows.map((d,i)=>rowHTML(d,i,"a")).join("");attachHandlers(list);}
}


function route(){
 const view=location.hash==="#about"?"about":"all";
 document.getElementById("view-all").style.display=view==="all"?"":"none";
 document.getElementById("view-about").style.display=view==="about"?"":"none";
 document.getElementById("nav-all").classList.toggle("current",view==="all");
 document.getElementById("nav-about").classList.toggle("current",view==="about");
 if(view!=="all")window.scrollTo({top:0,behavior:"instant"});
}
window.addEventListener("hashchange",route);
document.getElementById("nav-all").addEventListener("click",e=>{e.preventDefault();location.hash="";});
// ---- Self-healing abstracts (owner only) ----
// When the owner opens the page with "my log" on, silently fetch missing
// abstracts via the Elsevier API (owner's key, owner's network) and queue
// them to the repo inbox with the stored GitHub token. Published at next rebuild.
async function selfHeal(){
 const ek=lsGet("els-key"), gt=lsGet("jw-token");
 if(!ek)return;                       // visitors: nothing happens
 const missing=DATA.filter(d=>!d.abstract&&d.id.indexOf("10.")===0);
 if(!missing.length)return;
 healToast("Fetching "+missing.length+" missing abstracts in the background — keep this tab open (~2 min)…");
 const got=[];let netErr=0,unavail=0,denied=0;
 for(const m of missing){
  try{
   const r=await fetch("https://api.elsevier.com/content/abstract/doi/"+encodeURIComponent(m.id)+"?apiKey="+encodeURIComponent(ek)+"&httpAccept=application%2Fjson");
   if(r.ok){
    const d=await r.json();
    const core=(d["abstracts-retrieval-response"]||{}).coredata||{};
    const ab=(core["dc:description"]||"").replace(/^©[^A-Z]*?(?=[A-Z])/,"").trim();
    let kws=[];
    try{const ak=(d["abstracts-retrieval-response"].authkeywords||{})["author-keyword"]||[];
     kws=(Array.isArray(ak)?ak:[ak]).map(x=>x["$"]||"").filter(Boolean);}catch(e){}
    if(ab)got.push({doi:m.id,abstract:ab,keywords:kws.join("; ")});else unavail++;
   }else if(r.status===401||r.status===403){
    denied++;
    if(denied>=8&&got.length===0){
     healToast("Elsevier refused the key from this network ("+denied+"×). Connect UW VPN / campus Wi-Fi and reload — then this runs by itself.");
     return;
    }
   }else{unavail++;}
  }catch(e){netErr++;if(netErr>=5&&got.length===0){healToast("Self-heal stopped: network/CORS blocked ("+netErr+" errors). Tell Claude.");return;}}
  await new Promise(r=>setTimeout(r,400));
 }
 if(!got.length){healToast("Self-heal finished: 0 fetched — "+denied+" refused (off-campus?), "+unavail+" not indexed yet, "+netErr+" errors.");return;}
 if(!got.length)return;
 if(!gt){healToast(got.length+" abstracts fetched — turn on publishing (GitHub token) to queue them");return;}
 try{
  const path="inbox/scopus-auto-"+TODAY.replace(/-/g,"")+".json";
  const g=await ghGet(path,gt);
  let payload=got,sha=null;
  if(g){sha=g.sha;
   try{const prev=JSON.parse(decodeURIComponent(escape(atob(g.content.replace(/\s/g,"")))));
    const seen=new Set(prev.map(x=>x.doi));
    payload=prev.concat(got.filter(x=>!seen.has(x.doi)));}catch(e){}}
  await ghPut(path,gt,payload,sha,"Auto-heal: "+got.length+" abstracts fetched via owner browser");
  healToast("✓ "+got.length+" abstracts fetched & queued — live at next rebuild");
 }catch(e){healToast(got.length+" abstracts fetched, but queueing failed: "+e.message);}
}
function healToast(msg){
 const el=document.createElement("div");
 el.style.cssText="position:fixed;bottom:16px;right:16px;background:#4a5d3a;color:#fff;font-family:ui-monospace,Menlo,monospace;font-size:11px;letter-spacing:.05em;padding:10px 14px;z-index:99;max-width:320px";
 el.textContent=msg;document.body.appendChild(el);setTimeout(()=>el.remove(),10000);
}

// One-tap setup: read keys from the URL fragment (#els=…&gh=…), store on this
// device, and scrub them from the address bar (fragments never reach any server).
(function(){
 if(!location.hash||location.hash.indexOf("=")===-1)return;
 const h=new URLSearchParams(location.hash.slice(1));
 let changed=false;
 const e=h.get("els");if(e){try{localStorage.setItem("els-key",e.trim())}catch(x){}h.delete("els");changed=true;}
 const g=h.get("gh");if(g){try{localStorage.setItem("jw-token",g.trim())}catch(x){}h.delete("gh");changed=true;}
 if(changed){
  const rest=h.toString();
  history.replaceState(null,"",location.pathname+location.search+(rest?"#"+rest:""));
  healToast("✓ Setup complete — keys stored privately on this device.");
 }
})();

render();
route();
setTimeout(selfHeal,2500);
</script></body></html>"""

how_html = "\n".join(f"<p>{p}</p>" for p in SITE.get("how", []))
howbrief_html = "\n".join(f"<p>{p.split('. ')[0]}.</p>" for p in SITE.get("how", []))
using_html = "\n".join(f"<li>{d}</li>" for d in SITE.get("using", []))
reading_html = "\n".join(f"<li>{d}</li>" for d in SITE.get("reading", []))
adding_html = "\n".join(f"<li>{d}</li>" for d in SITE.get("adding", []))
disc_html = "\n".join(f"<li>{d}</li>" for d in SITE.get("disclaimers", []))
foot_disc = " ".join(SITE.get("disclaimers", [])[:2])

HTML = (HTML.replace("__PAYLOAD__", json.dumps(data, ensure_ascii=False))
            .replace("__TAX__", json.dumps(TAX, ensure_ascii=False))
            .replace("__JALL__", json.dumps(JOURNALS, ensure_ascii=False))
            .replace("__NJALL__", str(len(JOURNALS)))
            .replace("__NT__", str(n_total)).replace("__NJ__", str(n_j))
            .replace("__NA__", str(n_abs)).replace("__NNEW__", str(n_new))
            .replace("__TODAY__", TODAY)
            .replace("__AUTHOR__", SITE.get("author", "Yang Cheng"))
            .replace("__AFFILIATION__", SITE.get("affiliation", ""))
            .replace("__TAGLINE__", SITE.get("tagline", ""))
            .replace("__HOW__", how_html)
            .replace("__HOWBRIEF__", howbrief_html)
            .replace("__USING__", using_html)
            .replace("__READING__", reading_html)
            .replace("__ADDING__", adding_html)
            .replace("__DISCLAIMERS__", disc_html)
            .replace("__FOOTDISC__", foot_disc))
open(os.path.join(BASE, "index.html"), "w").write(HTML)
print(f"wrote index.html: {n_total} papers, {n_abs} abstracts, {n_new} new, {len(TAX)} themes")
