import json, html, sys, os
from datetime import date

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
papers = json.load(open(os.path.join(BASE, "data", "papers.json")))
OV = json.load(open(os.path.join(BASE, "data", "overview.json")))
TODAY = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
LATEST = max(p.get("added","") for p in papers)


DEEP = set(OV.get("deep_dois", []))
DEEP_TITLES = set(OV.get("deep_titles", []))

def link_for(p):
    url = p.get("url") or ("https://doi.org/" + p["doi"] if p.get("doi") else "")
    disp = p.get("doi") or (url.split("/pii/")[-1] and "ScienceDirect: " + url.split("/pii/")[-1] if "/pii/" in url else url)
    return url, disp

ORDER = ["Journal of Regional Science","Papers in Regional Science","Annals of Regional Science",
 "Regional Science and Urban Economics","Regional Studies","Spatial Economic Analysis",
 "International Regional Science Review","Regional Science Policy & Practice",
 "Journal of Urban Economics","Journal of Economic Geography","Economic Geography",
 "Environment and Planning A","Journal of Rural Studies","Land Use Policy","Growth and Change"]

def ptype(t):
    tl=t.lower()
    if tl.startswith("corrigendum") or tl.startswith("erratum"): return "Corrigendum"
    if tl.startswith("book review") or tl=="book review": return "Book review"
    return "Research"

data=[]
for p in papers:
    url,doidisp=link_for(p)
    is_deep = (p.get("doi") in DEEP) or (p["title"] in DEEP_TITLES)
    data.append({
        "journal":p["journal"],"group":p["group"],"date":p.get("date",""),
        "title":p["title"],"authors":p["authors"],"type":ptype(p["title"]),
        "keywords":[k.strip() for k in p["keywords"].split(";") if k.strip()],
        "abstract":p["abstract"],"url":url,"doi":doidisp,"deep":is_deep,"new":p.get("added","")==LATEST,"added":p.get("added",""),
        "jorder":ORDER.index(p["journal"]) if p["journal"] in ORDER else 99,
    })
data.sort(key=lambda d:(d["jorder"], d["date"]))

n_total=len(data); n_abs=sum(1 for d in data if d["abstract"]); n_j=len(set(d["journal"] for d in data))

THEMES = OV["themes"]
PICKS = OV["picks"]

payload = json.dumps(data, ensure_ascii=False)
themes_json = json.dumps(THEMES, ensure_ascii=False)
picks_json = json.dumps(PICKS, ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Regional Science Briefing — Jul 2026</title>
<style>
:root{
 --bg:#0e1626; --panel:#152238; --panel2:#1b2b46; --line:#26385a; --ink:#e8eefb;
 --mut:#9fb0cf; --accent:#5b9bff; --accent2:#8ad0a8; --gold:#f2c14e; --chip:#22375c;
}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
 background:linear-gradient(180deg,#0b1220,#0e1626 240px);color:var(--ink);line-height:1.5}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1080px;margin:0 auto;padding:20px 16px 80px}
header h1{font-size:26px;margin:0 0 4px;letter-spacing:-.02em}
header .sub{color:var(--mut);font-size:14px;margin-bottom:16px}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 6px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px 14px;min-width:96px}
.stat b{display:block;font-size:22px}
.stat span{color:var(--mut);font-size:12px}
details.ov{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin:16px 0;padding:4px 16px}
details.ov summary{cursor:pointer;font-weight:600;font-size:16px;padding:12px 0;list-style:none}
details.ov summary::-webkit-details-marker{display:none}
details.ov summary::before{content:"▸ ";color:var(--accent)}
details.ov[open] summary::before{content:"▾ "}
.theme{margin:10px 0;padding-left:2px}
.theme h4{margin:0 0 2px;font-size:14px;color:var(--accent2)}
.theme p{margin:0 0 6px;color:var(--mut);font-size:13px}
.pick{margin:8px 0;padding:8px 12px;background:var(--panel2);border-left:3px solid var(--gold);border-radius:8px}
.pick .t{font-weight:600;font-size:13.5px}
.pick .a{color:var(--mut);font-size:12.5px}
.pick .w{font-size:12.5px;margin-top:2px}
.controls{position:sticky;top:0;z-index:5;background:rgba(14,22,38,.96);
 backdrop-filter:blur(8px);padding:12px 0;border-bottom:1px solid var(--line);margin-bottom:8px}
#q{width:100%;padding:12px 14px;font-size:15px;border-radius:12px;border:1px solid var(--line);
 background:var(--panel);color:var(--ink);outline:none}
#q:focus{border-color:var(--accent)}
.row{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;align-items:center}
select{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:10px;
 padding:8px 10px;font-size:13px}
.toggle{display:flex;align-items:center;gap:6px;color:var(--mut);font-size:13px;cursor:pointer;user-select:none}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.chip{background:var(--chip);border:1px solid var(--line);color:var(--ink);font-size:12px;
 padding:5px 10px;border-radius:999px;cursor:pointer;white-space:nowrap}
.chip.active{background:var(--accent);border-color:var(--accent);color:#06122a;font-weight:600}
.count{color:var(--mut);font-size:13px;margin:12px 2px 6px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin:10px 0}
.card.deep{border-color:var(--gold);box-shadow:0 0 0 1px rgba(242,193,78,.25)}
.meta{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:6px}
.jpill{font-size:11px;font-weight:700;padding:3px 9px;border-radius:999px;color:#06122a}
.date{color:var(--mut);font-size:12px}
.badge{font-size:10.5px;padding:2px 7px;border-radius:6px;background:#2a2130;color:#e6c07a;border:1px solid #4a3a24}
.badge.res{background:#1a2b22;color:#8ad0a8;border-color:#274634}
.star{color:var(--gold);font-size:12px;font-weight:700}\n.newb{font-size:10.5px;padding:2px 7px;border-radius:6px;background:#14324a;color:#7cc7ff;border:1px solid #2b5f8a;font-weight:700}
.title{font-size:16px;font-weight:650;margin:2px 0 4px;letter-spacing:-.01em}
.auth{color:var(--mut);font-size:13px;margin-bottom:8px}
.kw{display:flex;gap:5px;flex-wrap:wrap;margin:6px 0}
.kw span{font-size:11px;background:#1d2c48;border:1px solid var(--line);color:#bcd0f2;padding:2px 8px;border-radius:6px;cursor:pointer}
.abs{font-size:13.5px;color:#d6e0f2;margin:8px 0 10px}
.noabs{font-size:13px;color:var(--mut);font-style:italic;margin:8px 0 10px;
 background:var(--panel2);border:1px dashed var(--line);border-radius:8px;padding:8px 10px}
.links{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.btn{display:inline-block;background:var(--accent);color:#06122a;font-weight:650;font-size:12.5px;
 padding:7px 12px;border-radius:9px}
.btn.ghost{background:transparent;color:var(--accent);border:1px solid var(--accent)}
.doi{color:var(--mut);font-size:11.5px;word-break:break-all}
.empty{text-align:center;color:var(--mut);padding:40px}
footer{color:var(--mut);font-size:12px;margin-top:24px;border-top:1px solid var(--line);padding-top:14px}
</style></head><body><div class="wrap">
<header>
<h1>Regional Science &amp; Regional Economics — Research Briefing</h1>
<div class="sub">Rolling archive across 15 journals · last updated __TODAY__ · __NNEW__ added in latest update</div>
<div class="stats">
 <div class="stat"><b>__NT__</b><span>papers indexed</span></div>
 <div class="stat"><b>__NJ__</b><span>journals</span></div>
 <div class="stat"><b>__NA__</b><span>abstracts inline</span></div>
 <div class="stat"><b>__NNEW__</b><span>new this update</span></div>
</div>
</header>

<details class="ov"><summary>Overview — themes &amp; what to deep-read</summary>
<div id="themes"></div>
<h3 style="margin:14px 0 4px;font-size:15px">★ Deep-read shortlist</h3>
<div id="picks"></div>
</details>

<div class="controls">
 <input id="q" placeholder="Search titles, authors, abstracts, keywords…" autocomplete="off">
 <div class="row">
   <select id="sort">
     <option value="jorder">Sort: by journal</option>
     <option value="date_desc">Sort: newest first</option>
     <option value="date_asc">Sort: oldest first</option>
     <option value="title">Sort: title A–Z</option>
   </select>
   <label class="toggle"><input type="checkbox" id="onlyabs"> abstract available</label>
   <label class="toggle"><input type="checkbox" id="onlydeep"> ★ deep-read only</label>
   <label class="toggle"><input type="checkbox" id="research" checked> research only</label>
 </div>
 <div class="chips" id="jchips"></div>
</div>

<div class="count" id="count"></div>
<div id="list"></div>
<footer>
Titles, authors &amp; DOIs verified for all __NT__ items; abstracts shown inline for all Wiley, Springer,
SAGE, Oxford &amp; Land Use Policy papers (retrieved via publisher pages, IDEAS/RePEc and the OUCI Crossref mirror).
Abstracts for Papers in Regional Science, Reg. Sci. Policy &amp; Practice, RSUE (in-press), J. Rural Studies,
Regional Studies, Spatial Economic Analysis &amp; Economic Geography are not openly mirrored anywhere —
one tap on the DOI button opens them via your UW–Madison library access. High-volume journals capped at ~12–15 items.
</footer>
</div>
<script>
const DATA=__PAYLOAD__, THEMES=__THEMES__, PICKS=__PICKS__;
const JCOLORS={};
const PALETTE=["#5b9bff","#8ad0a8","#f2c14e","#e88fb0","#b79bff","#67d3d9","#f4a259",
 "#9ac96a","#ff9b85","#7aa2f7","#c3a6ff","#5bd1a6","#e6b450","#f28ca0","#88c0d0"];
[...new Set(DATA.map(d=>d.journal))].forEach((j,i)=>JCOLORS[j]=PALETTE[i%PALETTE.length]);

document.getElementById("themes").innerHTML=THEMES.map(t=>
 `<div class="theme"><h4>${t[0]}</h4><p>${t[1]}</p></div>`).join("");
document.getElementById("picks").innerHTML=PICKS.map((p,i)=>
 `<div class="pick"><div class="t">${i+1}. ${p[0]}</div><div class="a">${p[1]}</div><div class="w">${p[2]}</div></div>`).join("");

const esc=s=>(s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
let jfilter="", state={q:"",sort:"jorder",onlyabs:false,onlydeep:false,research:true};

const jchips=document.getElementById("jchips");
const journals=[...new Set(DATA.map(d=>d.journal))];
jchips.innerHTML=`<div class="chip active" data-j="">All journals</div>`+
 journals.map(j=>`<div class="chip" data-j="${esc(j)}">${esc(j)} (${DATA.filter(d=>d.journal===j).length})</div>`).join("");
jchips.addEventListener("click",e=>{const c=e.target.closest(".chip");if(!c)return;
 jfilter=c.dataset.j;[...jchips.children].forEach(x=>x.classList.toggle("active",x===c));render();});

document.getElementById("q").addEventListener("input",e=>{state.q=e.target.value.toLowerCase();render();});
document.getElementById("sort").addEventListener("change",e=>{state.sort=e.target.value;render();});
document.getElementById("onlyabs").addEventListener("change",e=>{state.onlyabs=e.target.checked;render();});
document.getElementById("onlydeep").addEventListener("change",e=>{state.onlydeep=e.target.checked;render();});
document.getElementById("research").addEventListener("change",e=>{state.research=e.target.checked;render();});

function matches(d){
 if(jfilter&&d.journal!==jfilter)return false;
 if(state.onlyabs&&!d.abstract)return false;
 if(state.onlydeep&&!d.deep)return false;
 if(state.research&&d.type!=="Research")return false;
 if(state.q){const hay=(d.title+" "+d.authors+" "+d.abstract+" "+d.keywords.join(" ")+" "+d.journal).toLowerCase();
   return state.q.split(/\\s+/).every(w=>hay.includes(w));}
 return true;
}
function sortFn(a,b){
 if(state.sort==="date_desc")return (b.date||"").localeCompare(a.date||"");
 if(state.sort==="date_asc")return (a.date||"").localeCompare(b.date||"");
 if(state.sort==="title")return a.title.localeCompare(b.title);
 return a.jorder-b.jorder || (a.date||"").localeCompare(b.date||"");
}
function render(){
 const list=document.getElementById("list");
 const rows=DATA.filter(matches).sort(sortFn);
 document.getElementById("count").textContent=rows.length+" of "+DATA.length+" papers";
 if(!rows.length){list.innerHTML=`<div class="empty">No papers match your filters.</div>`;return;}
 list.innerHTML=rows.map(d=>{
  const col=JCOLORS[d.journal];
  const badge=d.type==="Research"?`<span class="badge res">Research</span>`:`<span class="badge">${d.type}</span>`;
  const star=d.deep?`<span class="star">★ deep-read</span>`:"";const newb=d.new?`<span class="newb">NEW</span>`:"";
  const kw=d.keywords.length?`<div class="kw">${d.keywords.map(k=>`<span data-k="${esc(k)}">${esc(k)}</span>`).join("")}</div>`:"";
  const abs=d.abstract?`<div class="abs">${esc(d.abstract)}</div>`
      :`<div class="noabs">Abstract not shown here (publisher blocks automated access). Open it on the publisher page →</div>`;
  const link=d.url?`<a class="btn" href="${d.url}" target="_blank" rel="noopener">Open abstract ↗</a>
       <span class="doi">${esc(d.doi)}</span>`:`<span class="doi">no link available</span>`;
  return `<div class="card ${d.deep?'deep':''}">
   <div class="meta"><span class="jpill" style="background:${col}">${esc(d.journal)}</span>
     <span class="date">${esc(d.date)}</span>${badge}${star}${newb}</div>
   <div class="title">${esc(d.title)}</div>
   <div class="auth">${esc(d.authors)||"—"}</div>
   ${kw}${abs}<div class="links">${link}</div></div>`;
 }).join("");
 list.querySelectorAll(".kw span").forEach(s=>s.addEventListener("click",()=>{
   document.getElementById("q").value=s.dataset.k;state.q=s.dataset.k.toLowerCase();render();
   window.scrollTo({top:0,behavior:"smooth"});}));
}
render();
</script></body></html>"""

n_new = sum(1 for d in data if d["new"])
HTML = (HTML.replace("__PAYLOAD__",payload).replace("__THEMES__",themes_json)
            .replace("__PICKS__",picks_json).replace("__NT__",str(n_total))
            .replace("__NJ__",str(n_j)).replace("__NA__",str(n_abs))
            .replace("__NNEW__",str(n_new)).replace("__TODAY__",TODAY))
open(os.path.join(BASE, "index.html"),"w").write(HTML)
print("wrote index.html:",n_total,"papers,",n_abs,"abstracts,",n_new,"new")
