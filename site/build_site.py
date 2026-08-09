#!/usr/bin/env python3
"""build_site.py — render the catalogue index from seed.json + catalogue.json.

The index is the hub: A–Z composer groups, find-as-you-type across composers /
works / recordings, and a tiny masthead (no per-composer chrome links).
"""

import json
import pathlib
from collections import defaultdict
from html import escape

seed = json.loads(pathlib.Path("data/seed.json").read_text("utf-8"))
try:
    assessed = json.loads(pathlib.Path("build/catalogue.json").read_text("utf-8"))
except FileNotFoundError:
    assessed = {"works": []}

# map assessed recordings onto seed work ids
done = defaultdict(list)
ALIAS = {"bach_brandenburg": "bach/brandenburg", "puccini_tosca": "puccini/tosca"}
REV_ALIAS = {v: k for k, v in ALIAS.items()}
for w in assessed.get("works", []):
    for r in w["recordings"]:
        done[ALIAS.get(w["id"], w["id"])].append(r)

by_composer = defaultdict(list)
for w in seed["works"]:
    by_composer[(w["composer_id"], w["composer"], w["composer_dates"])].append(w)

# Stable sort by surname, then full name
composers = sorted(
    by_composer.items(),
    key=lambda item: (item[0][1].split()[-1].lower(), item[0][1].lower()),
)


def surname(name: str) -> str:
    return name.split()[-1]


def letter_of(name: str) -> str:
    ch = surname(name)[:1].upper()
    return ch if ch.isalpha() else "#"


def work_anchor(work_id: str) -> str:
    """Entries page currently uses catalogue work ids; seed uses composer/work."""
    return REV_ALIAS.get(work_id, work_id.replace("/", "_"))


n_works = len(seed["works"])
n_cand = seed["totals"]["candidates"]
n_done = sum(len(v) for v in done.values())
n_works_done = len(done)
n_composers = len(by_composer)

CSS = """
:root{--ground:#E7EAE3;--paper:#FBFCF9;--ink:#191D1A;--ink-soft:#5B655D;--hair:#C7CDC2;
--verdigris:#2F6B60;--oxblood:#7A1220}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--ground);color:var(--ink);font-family:"Newsreader",Georgia,serif;
font-size:17px;font-weight:400;line-height:1.6;padding:0 clamp(1rem,3vw,2rem) 5rem}
.wrap{max-width:64rem;margin:0 auto}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace}
.masthead{display:flex;flex-wrap:wrap;gap:.75rem 1.5rem;align-items:baseline;
padding:1.4rem 0 1.1rem;border-bottom:1px solid var(--ink)}
.masthead h1{font-family:"Bodoni Moda",serif;font-weight:500;font-size:1.15rem;margin-right:auto}
.masthead nav{display:flex;gap:1.1rem;font-family:"IBM Plex Mono",monospace;font-size:.66rem;
font-weight:500;letter-spacing:.16em;text-transform:uppercase}
.masthead a{color:var(--ink-soft);text-decoration:none;border-bottom:1px solid transparent}
.masthead a:hover,.masthead a[aria-current="page"]{color:var(--ink);border-bottom-color:var(--ink)}
.find{width:100%;margin-top:.85rem;position:relative}
.find input{
  width:100%;font-family:"IBM Plex Mono",monospace;font-size:.8rem;font-weight:500;
  padding:.55rem .7rem;border:1px solid var(--hair);background:var(--paper);color:var(--ink)}
.find input:focus{outline:2px solid var(--verdigris);outline-offset:2px;border-color:var(--verdigris)}
.find-panel{
  display:none;position:absolute;left:0;right:0;top:calc(100% + 2px);z-index:8;
  background:var(--paper);border:1px solid var(--ink);max-height:22rem;overflow:auto}
.find-panel.open{display:block}
.find-group{padding:.55rem .75rem .25rem;font-family:"IBM Plex Mono",monospace;font-size:.58rem;
  font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft);
  border-top:1px solid var(--hair)}
.find-group:first-child{border-top:0}
.find-hit{
  display:block;width:100%;text-align:left;padding:.55rem .75rem;border:0;background:none;
  color:inherit;font:inherit;cursor:pointer;text-decoration:none}
.find-hit:hover,.find-hit:focus-visible{background:var(--ground)}
.find-hit .lbl{font-weight:500}
.find-hit .sub{display:block;font-family:"IBM Plex Mono",monospace;font-size:.62rem;
  font-weight:500;color:var(--ink-soft);margin-top:.15rem}
.find-empty{padding:.7rem .75rem;font-size:.9rem;color:var(--ink-soft)}
.hero{padding:clamp(2.4rem,7vw,4.2rem) 0 1.4rem;max-width:44rem}
.hero h2{font-family:"Bodoni Moda",serif;font-weight:400;font-size:clamp(2.2rem,7vw,3.8rem);
line-height:.98;letter-spacing:-.015em;margin-bottom:.8rem}
.hero p{color:var(--ink-soft);max-width:36rem}
.tally{display:flex;flex-wrap:wrap;gap:1.6rem;margin-top:2rem;padding-top:1rem;border-top:1px solid var(--ink)}
.tally div{font-family:"IBM Plex Mono",monospace}
.tally b{display:block;font-family:"Bodoni Moda",serif;font-weight:400;font-size:2rem;line-height:1}
.tally span{font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft)}
.bar{height:.5rem;background:var(--hair);margin-top:1.6rem;display:flex}
.bar i{display:block;height:100%}
.bar .b-done{background:var(--verdigris)}
.bar .b-cand{background:var(--ink-soft);opacity:.45}
.barkey{display:flex;gap:1.2rem;margin-top:.5rem;font-family:"IBM Plex Mono",monospace;
font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-soft)}
.az{display:flex;flex-wrap:wrap;gap:.35rem .55rem;margin:2rem 0 0;padding:1rem 0 0;
  border-top:1px solid var(--hair);font-family:"IBM Plex Mono",monospace;font-size:.72rem;font-weight:600}
.az a{color:var(--ink);text-decoration:none;min-width:1.2rem;text-align:center}
.az a:hover{color:var(--verdigris)}
.az .dim{color:var(--hair);pointer-events:none}
.letter{padding-top:clamp(2.2rem,5vw,3.4rem)}
.letter > h2{font-family:"Bodoni Moda",serif;font-weight:500;font-size:1.35rem;
  border-bottom:1px solid var(--ink);padding-bottom:.35rem;margin-bottom:1.2rem}
.composer{padding:1.3rem 0 1.6rem;border-bottom:1px solid var(--hair)}
.composer:last-child{border-bottom:0}
.composer h3{font-family:"Bodoni Moda",serif;font-weight:400;font-size:1.7rem;margin-bottom:.15rem}
.composer .dates{font-family:"IBM Plex Mono",monospace;font-size:.66rem;font-weight:500;
  letter-spacing:.12em;color:var(--ink-soft);text-transform:uppercase;margin-bottom:.85rem}
table{width:100%;border-collapse:collapse;font-size:.9rem}
th{text-align:left;font-family:"IBM Plex Mono",monospace;font-weight:500;font-size:.58rem;
letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft);
padding:.4rem .5rem .4rem 0;border-bottom:1px solid var(--ink)}
td{padding:.55rem .5rem;border-bottom:1px solid var(--hair);vertical-align:top}
td:first-child{padding-left:0}
.w-title{font-family:"Bodoni Moda",serif;font-size:1.02rem}
.w-cat{font-family:"IBM Plex Mono",monospace;font-size:.62rem;font-weight:500;color:var(--ink-soft)}
.w-note{color:var(--ink-soft);font-size:.85rem}
.chip{font-family:"IBM Plex Mono",monospace;font-size:.56rem;font-weight:500;letter-spacing:.08em;
text-transform:uppercase;padding:.15rem .4rem;white-space:nowrap;border:1px solid currentColor}
.c-done{color:var(--verdigris)}
.c-cand{color:var(--ink-soft)}
.c-none{color:var(--oxblood);border-style:dashed}
a.entry{color:var(--verdigris);font-weight:500}
footer{margin-top:4rem;padding-top:1.2rem;border-top:1px solid var(--ink);font-size:.82rem;
color:var(--ink-soft);max-width:44rem;display:grid;gap:.5rem}
footer .mono{font-size:.68rem;letter-spacing:.04em}
@media(max-width:680px){body{font-size:16px}.w-note{display:none}td,th{padding-right:.3rem}}
"""


def row(w):
    d = done.get(w["id"], [])
    if d:
        chip = f'<span class="chip c-done">{len(d)} assessed</span>'
        link = (
            f' <a class="entry" href="entries.html#{escape(work_anchor(w["id"]))}">read</a>'
        )
    elif w["candidates"]:
        chip = f'<span class="chip c-cand">{len(w["candidates"])} queued</span>'
        link = ""
    else:
        chip = '<span class="chip c-none">no candidates</span>'
        link = ""
    return f"""<tr data-work="{escape(w['id'])}">
      <td><span class="w-title">{escape(w['title'])}</span><br>
        <span class="w-cat">{escape(w['catalogue'])} · {escape(w['year'])}</span></td>
      <td class="w-note">{escape(w['note'])}</td>
      <td>{chip}{link}</td>
    </tr>"""


composer_scores = {c["id"]: c for c in assessed.get("composers", [])}


def composer_rollup_line(cid: str) -> str:
    c = composer_scores.get(cid)
    if not c:
        return ""
    if c.get("interpretation") is None:
        return (
            f'<p class="dates">Composer rollup: withheld '
            f'({c.get("n_strong", 0)} strong sources · '
            f'{c.get("n_recordings_assessed", 0)} recordings assessed)</p>'
        )
    classes = c.get("sources_by_class") or {}
    origin = ", ".join(f"{k} ×{v}" for k, v in sorted(classes.items())) or "—"
    return (
        f'<p class="dates">Composer rollup {c["interpretation"]:.3f} '
        f'(confidence {c["confidence"]:.3f}) · origin mix: {escape(origin)}</p>'
    )


# ---- search index (composers, works, assessed recordings) ----
search_index = []
for (cid, name, dates), works in composers:
    search_index.append({
        "kind": "composer",
        "label": name,
        "sub": f"{surname(name)} · {len(works)} works",
        "href": f"#{cid}",
        "keys": f"{name} {surname(name)} {cid}".lower(),
    })
    for w in works:
        d = done.get(w["id"], [])
        href = (
            f"entries.html#{work_anchor(w['id'])}"
            if d else f"#{cid}"
        )
        state = (
            f"{len(d)} assessed" if d
            else (f"{len(w['candidates'])} queued" if w["candidates"] else "unstarted")
        )
        search_index.append({
            "kind": "work",
            "label": w["title"],
            "sub": f"{name} · {w['catalogue']} · {state}",
            "href": href,
            "keys": f"{w['title']} {w['catalogue']} {name} {surname(name)}".lower(),
        })
        for r in d:
            who = " / ".join(
                x for x in (r.get("director"), r.get("ensemble"), r.get("soloists")) if x
            )
            search_index.append({
                "kind": "recording",
                "label": who or r["id"],
                "sub": f"{name} · {w['title']} · {r.get('published', '')}",
                "href": f"entries.html#{r['id']}",
                "keys": (
                    f"{who} {r.get('published','')} {w['title']} {name} "
                    f"{r.get('director','')} {r.get('ensemble','')} {r.get('soloists','')}"
                ).lower(),
            })

# ---- A–Z groups ----
by_letter = defaultdict(list)
for item in composers:
    by_letter[letter_of(item[0][1])].append(item)

active_letters = sorted(by_letter)
az = []
for code in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    if code in by_letter:
        az.append(f'<a href="#letter-{code}">{code}</a>')
    else:
        az.append(f'<span class="dim">{code}</span>')

letter_sections = []
for code in active_letters:
    blocks = []
    for (cid, name, dates), works in by_letter[code]:
        rows = "".join(row(w) for w in works)
        dn = sum(1 for w in works if done.get(w["id"]))
        blocks.append(f"""<article class="composer" id="{escape(cid)}">
      <h3>{escape(name)}</h3>
      <p class="dates">{escape(dates)} · {len(works)} works · {dn} with assessments</p>
      {composer_rollup_line(cid)}
      <table><thead><tr><th>Work</th><th>Why it is in the guide</th><th>State</th></tr></thead>
      <tbody>{rows}</tbody></table>
    </article>""")
    letter_sections.append(
        f'<section class="letter" id="letter-{escape(code)}">'
        f"<h2>{escape(code)}</h2>{''.join(blocks)}</section>"
    )

pct_done = n_works_done / n_works * 100
pct_cand = (
    sum(1 for w in seed["works"] if w["candidates"] and not done.get(w["id"]))
    / n_works * 100
)

JS = r"""
const INDEX = __INDEX__;
const esc = s => String(s??"").replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const input = document.getElementById("q");
const panel = document.getElementById("q-panel");
const KIND_ORDER = {composer:0, work:1, recording:2};
const KIND_LABEL = {composer:"Composers", work:"Works", recording:"Recordings"};

function search(q){
  q = q.trim().toLowerCase().replace(/\s+/g," ");
  if(q.length < 2) return [];
  const tokens = q.split(" ");
  return INDEX.filter(item => tokens.every(t => item.keys.includes(t)))
    .sort((a,b) => KIND_ORDER[a.kind]-KIND_ORDER[b.kind] || a.label.localeCompare(b.label))
    .slice(0, 24);
}

function render(hits){
  if(!input.value.trim()){ panel.classList.remove("open"); panel.innerHTML=""; return; }
  if(!hits.length){
    panel.classList.add("open");
    panel.innerHTML = `<p class="find-empty">No composers, works or recordings match.</p>`;
    return;
  }
  let html = "", kind = null;
  for(const h of hits){
    if(h.kind !== kind){
      kind = h.kind;
      html += `<p class="find-group">${KIND_LABEL[kind]}</p>`;
    }
    html += `<a class="find-hit" href="${esc(h.href)}"><span class="lbl">${esc(h.label)}</span>
      <span class="sub">${esc(h.sub)}</span></a>`;
  }
  panel.classList.add("open");
  panel.innerHTML = html;
}

input.addEventListener("input", () => render(search(input.value)));
input.addEventListener("keydown", e => {
  if(e.key === "Escape"){ panel.classList.remove("open"); input.blur(); }
  if(e.key === "Enter"){
    const first = panel.querySelector(".find-hit");
    if(first){ e.preventDefault(); first.click(); }
  }
});
document.addEventListener("click", e => {
  if(!e.target.closest(".find")) panel.classList.remove("open");
});
"""

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Critical Discography — Catalogue</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,500;6..96,600&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><div class="wrap">
<header class="masthead">
  <h1>Critical Discography</h1>
  <nav>
    <a href="index.html" aria-current="page">Catalogue</a>
    <a href="entries.html">Entries</a>
    <a href="gallery.html">Gallery</a>
  </nav>
  <div class="find">
    <input id="q" type="search" autocomplete="off" spellcheck="false"
      placeholder="Find a composer, work or recording — try brah, tosca, pinnock"
      aria-label="Find a composer, work or recording" aria-controls="q-panel">
    <div class="find-panel" id="q-panel" role="listbox" aria-label="Search results"></div>
  </div>
</header>

<div class="hero">
  <h2>{n_works} works,<br>and an honest ledger.</h2>
  <p>{n_composers} composers in the seed. Browse A–Z below, or type to jump.
  Assessments appear only when a source with a locator supplies one.</p>
  <div class="tally">
    <div><b>{n_works}</b><span>works</span></div>
    <div><b>{n_cand}</b><span>candidates queued</span></div>
    <div><b>{n_done}</b><span>recordings assessed</span></div>
    <div><b>{pct_done:.0f}%</b><span>works with any assessment</span></div>
  </div>
  <div class="bar"><i class="b-done" style="width:{pct_done:.1f}%"></i><i class="b-cand" style="width:{pct_cand:.1f}%"></i></div>
  <div class="barkey"><span>assessed</span><span>candidates awaiting sources</span><span>unstarted</span></div>
  <nav class="az" aria-label="Composers by letter">{''.join(az)}</nav>
</div>

{''.join(letter_sections)}

<footer>
  <p>Cover images from the <a href="https://coverartarchive.org">Cover Art Archive</a> via
  <a href="https://musicbrainz.org">MusicBrainz</a>. Catalogue data is CC0.
  No advertising, no affiliate links.</p>
  <p class="mono">SEED SCHEMA {escape(seed['schema'])} · {n_composers} COMPOSERS · {n_works} WORKS · NO AFFILIATE LINKS</p>
</footer>
</div>
<script>{JS.replace("__INDEX__", json.dumps(search_index, ensure_ascii=False))}</script>
</body></html>"""

pathlib.Path("docs/index.html").write_text(html, "utf-8")
print(
    f"docs/index.html · {n_composers} composers · {n_works} works · "
    f"{n_done} assessed · {len(search_index)} search rows"
)
