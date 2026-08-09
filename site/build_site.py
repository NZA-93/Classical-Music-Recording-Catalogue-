#!/usr/bin/env python3
"""build_site.py — render the catalogue index from seed.json + catalogue.json.

Shows the whole scope and, honestly, how little of it is done. A guide that
hides its gaps cannot ask anyone to fill them.
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
for w in assessed.get("works", []):
    for r in w["recordings"]:
        done[ALIAS.get(w["id"], w["id"])].append(r)

by_composer = defaultdict(list)
for w in seed["works"]:
    by_composer[(w["composer_id"], w["composer"], w["composer_dates"])].append(w)

n_works = len(seed["works"])
n_cand = seed["totals"]["candidates"]
n_done = sum(len(v) for v in done.values())
n_works_done = len(done)

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
letter-spacing:.16em;text-transform:uppercase}
.masthead a{color:var(--ink-soft);text-decoration:none;border-bottom:1px solid transparent}
.masthead a:hover{color:var(--ink);border-bottom-color:var(--ink)}
.hero{padding:clamp(3rem,8vw,5rem) 0 2rem;max-width:44rem}
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
section{padding-top:clamp(2.5rem,6vw,4rem)}
section h3{font-family:"Bodoni Moda",serif;font-weight:400;font-size:1.9rem;margin-bottom:.15rem}
section .dates{font-family:"IBM Plex Mono",monospace;font-size:.66rem;letter-spacing:.12em;
color:var(--ink-soft);text-transform:uppercase;margin-bottom:1rem}
table{width:100%;border-collapse:collapse;font-size:.9rem}
th{text-align:left;font-family:"IBM Plex Mono",monospace;font-weight:500;font-size:.58rem;
letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft);
padding:.4rem .5rem .4rem 0;border-bottom:1px solid var(--ink)}
td{padding:.55rem .5rem;border-bottom:1px solid var(--hair);vertical-align:top}
td:first-child{padding-left:0}
.w-title{font-family:"Bodoni Moda",serif;font-size:1.02rem}
.w-cat{font-family:"IBM Plex Mono",monospace;font-size:.62rem;color:var(--ink-soft)}
.w-note{color:var(--ink-soft);font-size:.85rem}
.chip{font-family:"IBM Plex Mono",monospace;font-size:.56rem;letter-spacing:.08em;
text-transform:uppercase;padding:.15rem .4rem;white-space:nowrap;border:1px solid currentColor}
.c-done{color:var(--verdigris)}
.c-cand{color:var(--ink-soft)}
.c-none{color:var(--oxblood);border-style:dashed}
a.entry{color:var(--verdigris)}
footer{margin-top:4rem;padding-top:1.2rem;border-top:1px solid var(--ink);font-size:.82rem;
color:var(--ink-soft);max-width:44rem;display:grid;gap:.5rem}
footer .mono{font-size:.68rem;letter-spacing:.04em}
@media(max-width:680px){body{font-size:16px}.w-note{display:none}td,th{padding-right:.3rem}}
"""


def row(w):
    d = done.get(w["id"], [])
    if d:
        chip = f'<span class="chip c-done">{len(d)} assessed</span>'
        link = f' <a class="entry" href="entries.html#{escape(w["id"].replace("/", "_"))}">read</a>'
    elif w["candidates"]:
        chip = f'<span class="chip c-cand">{len(w["candidates"])} queued</span>'
        link = ""
    else:
        chip = '<span class="chip c-none">no candidates</span>'
        link = ""
    return f"""<tr>
      <td><span class="w-title">{escape(w['title'])}</span><br>
        <span class="w-cat">{escape(w['catalogue'])} · {escape(w['year'])}</span></td>
      <td class="w-note">{escape(w['note'])}</td>
      <td>{chip}{link}</td>
    </tr>"""


sections = []
for (cid, name, dates), works in by_composer.items():
    rows = "".join(row(w) for w in works)
    dn = sum(1 for w in works if done.get(w["id"]))
    sections.append(f"""<section id="{cid}">
      <h3>{escape(name)}</h3>
      <p class="dates">{escape(dates)} · {len(works)} works · {dn} with assessments</p>
      <table><thead><tr><th>Work</th><th>Why it is in the guide</th><th>State</th></tr></thead>
      <tbody>{rows}</tbody></table>
    </section>""")

pct_done = n_works_done / n_works * 100
pct_cand = sum(1 for w in seed["works"] if w["candidates"] and not done.get(w["id"])) / n_works * 100

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Critical Discography — Catalogue</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,500;6..96,600&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><div class="wrap">
<header class="masthead"><h1>Critical Discography</h1>
<nav><a href="#bach">Bach</a><a href="#beethoven">Beethoven</a><a href="#mozart">Mozart</a>
<a href="#puccini">Puccini</a><a href="entries.html">Entries</a><a href="gallery.html">Gallery</a></nav></header>

<div class="hero">
  <h2>Forty-seven works,<br>and an honest ledger.</h2>
  <p>Four composers seeded for round one. The works are settled; the assessments are not.
  Nothing here carries a score until a source with a locator supplies one, which is why
  most of this page reads as work still to do rather than work already done.</p>
  <div class="tally">
    <div><b>{n_works}</b><span>works</span></div>
    <div><b>{n_cand}</b><span>candidates queued</span></div>
    <div><b>{n_done}</b><span>recordings assessed</span></div>
    <div><b>{pct_done:.0f}%</b><span>works with any assessment</span></div>
  </div>
  <div class="bar"><i class="b-done" style="width:{pct_done:.1f}%"></i><i class="b-cand" style="width:{pct_cand:.1f}%"></i></div>
  <div class="barkey"><span>assessed</span><span>candidates awaiting sources</span><span>unstarted</span></div>
</div>

{''.join(sections)}

<footer>
  <p>Round one resolves identity for every candidate against MusicBrainz, then pulls editions,
  barcodes and cover art. Critical assessments follow only as citations arrive: a locator, a
  normalised score, and a characterisation written here rather than copied from a review.</p>
  <p class="mono">SEED SCHEMA {escape(seed['schema'])} · {n_works} WORKS · NO SCORES SEEDED · NO AFFILIATE LINKS</p>
</footer>
</div></body></html>"""

pathlib.Path("docs/index.html").write_text(html, "utf-8")
print(f"docs/index.html · {n_works} works · {n_cand} candidates · {n_done} assessed "
      f"({pct_done:.0f}% of works)")
