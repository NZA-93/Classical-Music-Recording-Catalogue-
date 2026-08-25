#!/usr/bin/env python3
"""build_site.py — catalogue hub + one composer hub per composer.

Index is a professional directory (A–Z + find-as-you-type). Each composer
gets composers/<id>.html listing only that composer's works, with assessed
titles linking into sealed work pages. Navigation: catalogue → composer
hub → sealed work page. No per-composer links in the global masthead.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import sys
from collections import defaultdict
from html import escape

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from work_href import ALIAS, work_anchor, work_page_href  # noqa: E402

ROOT = pathlib.Path(".")
DOCS = ROOT / "docs"
COMP_DIR = DOCS / "composers"

seed = json.loads((ROOT / "data/seed.json").read_text("utf-8"))
try:
    assessed = json.loads((ROOT / "build/catalogue.json").read_text("utf-8"))
except FileNotFoundError:
    assessed = {"works": []}

done: dict[str, list] = defaultdict(list)
for w in assessed.get("works", []):
    for r in w["recordings"]:
        done[ALIAS.get(w["id"], w["id"])].append(r)

by_composer: dict[tuple, list] = defaultdict(list)
for w in seed["works"]:
    by_composer[(w["composer_id"], w["composer"], w["composer_dates"])].append(w)

composers = sorted(
    by_composer.items(),
    key=lambda item: (item[0][1].split()[-1].lower(), item[0][1].lower()),
)
composer_scores = {c["id"]: c for c in assessed.get("composers", [])}

n_works = len(seed["works"])
n_composers = len(by_composer)
n_done = sum(len(v) for v in done.values())


def surname(name: str) -> str:
    return name.split()[-1]


def letter_of(name: str) -> str:
    ch = surname(name)[:1].upper()
    return ch if ch.isalpha() else "#"


def entries_href(work_id: str, *, depth: int = 0, recording_id: str | None = None) -> str:
    return work_page_href(work_id, depth=depth, recording_id=recording_id)


SHARED_CSS = """
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
.masthead h1 a{color:inherit;text-decoration:none}
.masthead nav{display:flex;gap:1.1rem;font-family:"IBM Plex Mono",monospace;font-size:.66rem;
font-weight:500;letter-spacing:.16em;text-transform:uppercase}
.masthead a{color:var(--ink-soft);text-decoration:none;border-bottom:1px solid transparent}
.masthead nav a:hover,.masthead nav a[aria-current="page"]{color:var(--ink);border-bottom-color:var(--ink)}
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
.find-hit{display:block;padding:.55rem .75rem;color:inherit;text-decoration:none}
.find-hit:hover,.find-hit:focus-visible{background:var(--ground)}
.find-hit .lbl{font-weight:500}
.find-hit .sub{display:block;font-family:"IBM Plex Mono",monospace;font-size:.62rem;
  font-weight:500;color:var(--ink-soft);margin-top:.15rem}
.find-empty{padding:.7rem .75rem;font-size:.9rem;color:var(--ink-soft)}
.page-head{padding:1.6rem 0 1.1rem;border-bottom:1px solid var(--hair);margin-bottom:1.6rem}
.page-head h2{font-family:"Bodoni Moda",serif;font-weight:500;font-size:clamp(1.6rem,4vw,2.2rem);
  line-height:1.1;letter-spacing:-.01em}
.page-head .meta{font-family:"IBM Plex Mono",monospace;font-size:.66rem;font-weight:500;
  letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft);margin-top:.45rem}
.crumb{font-family:"IBM Plex Mono",monospace;font-size:.62rem;font-weight:500;letter-spacing:.08em;
  text-transform:uppercase;color:var(--ink-soft);margin-bottom:.7rem}
.crumb a{color:var(--ink-soft);text-decoration:none;border-bottom:1px solid transparent}
.crumb a:hover{color:var(--ink);border-bottom-color:var(--ink)}
.az{display:flex;flex-wrap:wrap;gap:.35rem .55rem;margin:0 0 1.6rem;
  font-family:"IBM Plex Mono",monospace;font-size:.72rem;font-weight:600}
.az a{color:var(--ink);text-decoration:none;min-width:1.2rem;text-align:center}
.az a:hover{color:var(--verdigris)}
.az .dim{color:var(--hair);pointer-events:none}
.letter{padding-top:1.4rem}
.letter > h2{font-family:"IBM Plex Mono",monospace;font-size:.7rem;font-weight:600;
  letter-spacing:.14em;text-transform:uppercase;color:var(--ink-soft);
  border-bottom:1px solid var(--hair);padding-bottom:.35rem;margin-bottom:.2rem}
.dir-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.6rem 1.2rem;
  align-items:baseline;padding:.85rem 0;border-bottom:1px solid var(--hair);text-decoration:none;color:inherit}
.dir-row:hover .name{color:var(--verdigris)}
.dir-row .name{font-family:"Bodoni Moda",serif;font-size:1.25rem;font-weight:500}
.dir-row .dates{font-family:"IBM Plex Mono",monospace;font-size:.68rem;font-weight:500;color:var(--ink-soft)}
.dir-row .stats{font-family:"IBM Plex Mono",monospace;font-size:.62rem;font-weight:500;
  letter-spacing:.06em;text-transform:uppercase;color:var(--ink-soft);text-align:right}
table{width:100%;border-collapse:collapse;font-size:.9rem}
th{text-align:left;font-family:"IBM Plex Mono",monospace;font-weight:500;font-size:.58rem;
letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft);
padding:.4rem .5rem .4rem 0;border-bottom:1px solid var(--ink)}
td{padding:.55rem .5rem;border-bottom:1px solid var(--hair);vertical-align:top}
td:first-child{padding-left:0}
.w-title{font-family:"Bodoni Moda",serif;font-size:1.02rem}
a.w-title{color:inherit;text-decoration:none}
a.w-title:hover,a.w-title:focus-visible{color:var(--verdigris)}
.w-cat{font-family:"IBM Plex Mono",monospace;font-size:.62rem;font-weight:500;color:var(--ink-soft)}
.w-note{color:var(--ink-soft);font-size:.85rem}
.chip{font-family:"IBM Plex Mono",monospace;font-size:.56rem;font-weight:500;letter-spacing:.08em;
text-transform:uppercase;padding:.15rem .4rem;white-space:nowrap;border:1px solid currentColor}
.c-done{color:var(--verdigris)}
.c-cand{color:var(--ink-soft)}
.c-none{color:var(--oxblood);border-style:dashed}
a.entry{color:var(--verdigris);font-weight:500}
.rec-list{list-style:none;margin:1.4rem 0 0;display:grid;gap:.7rem}
.rec-list li{padding-left:.85rem;border-left:1px solid var(--verdigris)}
.rec-list a{color:var(--ink);font-weight:500;text-decoration:none}
.rec-list a:hover{color:var(--verdigris)}
.rec-list .sub{display:block;font-family:"IBM Plex Mono",monospace;font-size:.62rem;
  font-weight:500;color:var(--ink-soft);margin-top:.15rem}
.modlabel{font-family:"IBM Plex Mono",monospace;font-size:.62rem;font-weight:600;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink-soft);margin:2rem 0 .6rem}
footer{margin-top:4rem;padding-top:1.2rem;border-top:1px solid var(--ink);font-size:.82rem;
color:var(--ink-soft);max-width:44rem;display:grid;gap:.5rem}
footer .mono{font-size:.68rem;letter-spacing:.04em}
@media(max-width:680px){body{font-size:16px}.w-note{display:none}td,th{padding-right:.3rem}
.dir-row{grid-template-columns:1fr}.dir-row .stats{text-align:left}}
"""

FIND_JS = r"""
const INDEX = __INDEX__;
const SCOPE = __SCOPE__;
const CATALOGUE_HREF = __CATALOGUE_HREF__;
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
    panel.innerHTML = SCOPE === "composer"
      ? `<p class="find-empty">Nothing by this composer matches. Try the <a href="${esc(CATALOGUE_HREF)}">catalogue</a>.</p>`
      : `<p class="find-empty">No composers, works or recordings match.</p>`;
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


def shell(title: str, body: str, index_json: list, *, depth: int = 0,
          current: str = "catalogue", scope: str = "catalogue") -> str:
    prefix = "../" * depth
    nav = {
        "catalogue": f'{prefix}index.html',
        "entries": f'{prefix}entries.html',
        "gallery": f'{prefix}gallery.html',
        "review": f'{prefix}review/index.html',
    }
    def link(key, label):
        cur = ' aria-current="page"' if current == key else ""
        return f'<a href="{nav[key]}"{cur}>{label}</a>'
    find_placeholder = (
        "Find a work or recording by this composer"
        if scope == "composer"
        else "Find a composer, work or recording"
    )
    js = (
        FIND_JS
        .replace("__INDEX__", json.dumps(index_json, ensure_ascii=False))
        .replace("__SCOPE__", json.dumps(scope))
        .replace("__CATALOGUE_HREF__", json.dumps(nav["catalogue"]))
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)} — Critical Discography</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,500;6..96,600&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{SHARED_CSS}</style></head><body><div class="wrap">
<header class="masthead">
  <h1><a href="{nav['catalogue']}">Critical Discography</a></h1>
  <nav>
    {link("catalogue", "Catalogue")}
    {link("entries", "Entries")}
    {link("gallery", "Gallery")}
    {link("review", "Review")}
  </nav>
  <div class="find">
    <input id="q" type="search" autocomplete="off" spellcheck="false"
      placeholder="{escape(find_placeholder)}"
      aria-label="{escape(find_placeholder)}" aria-controls="q-panel">
    <div class="find-panel" id="q-panel" role="listbox" aria-label="Search results"></div>
  </div>
</header>
{body}
<footer>
  <p>Cover images from the <a href="https://coverartarchive.org">Cover Art Archive</a> via
  <a href="https://musicbrainz.org">MusicBrainz</a>. Catalogue data is CC0.
  No advertising, no affiliate links.</p>
  <p class="mono">SEED SCHEMA {escape(seed['schema'])} · {n_composers} COMPOSERS · {n_works} WORKS</p>
</footer>
</div>
<script>{js}</script>
</body></html>"""


def work_row(w, *, depth: int = 0) -> str:
    d = done.get(w["id"], [])
    title = escape(w["title"])
    if d:
        href = escape(entries_href(w["id"], depth=depth))
        title_cell = f'<a class="w-title" href="{href}">{title}</a>'
        chip = f'<span class="chip c-done">{len(d)} assessed</span>'
        link = f' <a class="entry" href="{href}">open work</a>'
    elif w["candidates"]:
        title_cell = f'<span class="w-title">{title}</span>'
        chip = f'<span class="chip c-cand">{len(w["candidates"])} queued</span>'
        link = ""
    else:
        title_cell = f'<span class="w-title">{title}</span>'
        chip = '<span class="chip c-none">no candidates</span>'
        link = ""
    return f"""<tr id="{escape(work_anchor(w['id']))}">
      <td>{title_cell}<br>
        <span class="w-cat">{escape(w['catalogue'])} · {escape(w['year'])}</span></td>
      <td class="w-note">{escape(w['note'])}</td>
      <td>{chip}{link}</td>
    </tr>"""


def rollup_line(cid: str) -> str:
    c = composer_scores.get(cid)
    if not c:
        return ""
    if c.get("interpretation") is None:
        return (
            f'<p class="meta">Rollup withheld · {c.get("n_strong", 0)} strong sources · '
            f'{c.get("n_recordings_assessed", 0)} recordings assessed</p>'
        )
    return (
        f'<p class="meta">Composer rollup {c["interpretation"]:.3f} · '
        f'confidence {c["confidence"]:.3f}</p>'
    )


# ---- global search index (paths from docs/ root) ----
def build_index(*, depth: int = 0, composer_id: str | None = None) -> list:
    """Find index. Catalogue is global; a composer hub is that composer only."""
    prefix = "../" * depth
    out = []
    for (cid, name, dates), works in composers:
        if composer_id and cid != composer_id:
            continue
        out.append({
            "kind": "composer",
            "label": name,
            "sub": f"{dates} · {len(works)} works",
            "href": f"{prefix}composers/{cid}.html",
            "keys": f"{name} {surname(name)} {cid}".lower(),
        })
        for w in works:
            d = done.get(w["id"], [])
            if d:
                href = work_page_href(w["id"], depth=depth)
                state = f"{len(d)} assessed"
            else:
                href = f"{prefix}composers/{cid}.html#{work_anchor(w['id'])}"
                state = (
                    f"{len(w['candidates'])} queued" if w["candidates"] else "unstarted"
                )
            out.append({
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
                out.append({
                    "kind": "recording",
                    "label": who or r["id"],
                    "sub": f"{name} · {w['title']} · {r.get('published', '')}",
                    "href": work_page_href(w["id"], depth=depth, recording_id=r["id"]),
                    "keys": (
                        f"{who} {r.get('published','')} {w['title']} {name} "
                        f"{r.get('director','')} {r.get('ensemble','')} {r.get('soloists','')}"
                    ).lower(),
                })
    return out


# ---- index: professional directory ----
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
    rows = []
    for (cid, name, dates), works in by_letter[code]:
        dn = sum(1 for w in works if done.get(w["id"]))
        rows.append(
            f'<a class="dir-row" href="composers/{escape(cid)}.html">'
            f'<span><span class="name">{escape(name)}</span><br>'
            f'<span class="dates">{escape(dates)}</span></span>'
            f'<span class="stats">{len(works)} works · {dn} assessed</span></a>'
        )
    letter_sections.append(
        f'<section class="letter" id="letter-{escape(code)}">'
        f"<h2>{escape(code)}</h2>{''.join(rows)}</section>"
    )

index_body = f"""
<div class="page-head">
  <h2>Catalogue</h2>
  <p class="meta">{n_composers} composers · {n_works} works · {n_done} recordings assessed</p>
</div>
<nav class="az" aria-label="Composers by letter">{''.join(az)}</nav>
{''.join(letter_sections)}
"""


def composer_hub(cid: str, name: str, dates: str, works: list) -> str:
    """One composer: that composer's works only, linking into sealed work pages."""
    dn = sum(1 for w in works if done.get(w["id"]))
    rows = "".join(work_row(w, depth=1) for w in works)
    rec_items = []
    for w in works:
        for r in done.get(w["id"], []):
            who = " — ".join(
                x for x in (r.get("director"), r.get("ensemble")) if x
            ) or r["id"]
            rec_items.append(
                f'<li><a href="{escape(work_page_href(w["id"], depth=1, recording_id=r["id"]))}">{escape(who)}</a>'
                f'<span class="sub">{escape(w["title"])} · {escape(r.get("published") or "")}</span></li>'
            )
    assessed_block = ""
    if rec_items:
        assessed_block = (
            '<p class="modlabel">Assessed recordings</p>'
            f'<ul class="rec-list">{"".join(rec_items)}</ul>'
        )
    body = f"""
<p class="crumb"><a href="../index.html">Catalogue</a> / {escape(surname(name))}</p>
<div class="page-head">
  <h2>{escape(name)}</h2>
  <p class="meta">{escape(dates)} · {len(works)} works · {dn} with assessments</p>
  {rollup_line(cid)}
</div>
<table><thead><tr><th>Work</th><th>Why it is in the guide</th><th>State</th></tr></thead>
<tbody>{rows}</tbody></table>
{assessed_block}
"""
    return shell(
        name,
        body,
        build_index(depth=1, composer_id=cid),
        depth=1,
        current="catalogue",
        scope="composer",
    )


def composer_by_id(cid: str) -> tuple[str, str, str, list]:
    for (id_, name, dates), works in composers:
        if id_ == cid:
            return id_, name, dates, works
    raise KeyError(cid)


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    if COMP_DIR.exists():
        shutil.rmtree(COMP_DIR)
    COMP_DIR.mkdir(parents=True)

    (DOCS / "index.html").write_text(
        shell(
            "Catalogue",
            index_body,
            build_index(depth=0),
            depth=0,
            current="catalogue",
            scope="catalogue",
        ),
        "utf-8",
    )

    for (cid, name, dates), works in composers:
        (COMP_DIR / f"{cid}.html").write_text(
            composer_hub(cid, name, dates, works),
            "utf-8",
        )

    root_comp = ROOT / "composers"
    if root_comp.exists():
        shutil.rmtree(root_comp)
    shutil.copytree(COMP_DIR, root_comp)

    print(
        f"docs/index.html · {n_composers} composer pages in docs/composers/ · "
        f"{n_works} works · {n_done} assessed"
    )


if __name__ == "__main__":
    main()
