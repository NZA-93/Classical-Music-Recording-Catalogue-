#!/usr/bin/env python3
"""build_review.py — online human-review board (GitHub Pages).

Read-only UI over the harvest review queue + community comments.
Owner decisions stay in proposals/review-decisions.json (git); community
comments live in data/community/ and are labeled as non-editorial.

No runtime dependencies. No scores invented here.
"""

from __future__ import annotations

import json
import pathlib
from collections import defaultdict
from html import escape
from typing import Any

ROOT = pathlib.Path(".")
DOCS = ROOT / "docs" / "review"
QUEUE = ROOT / "proposals" / "review-queue.json"
DECISIONS = ROOT / "proposals" / "review-decisions.json"
COMMUNITY = ROOT / "data" / "community" / "comments.json"
SEED = ROOT / "data" / "seed.json"
PROPOSALS = ROOT / "proposals" / "proposals-20260809.json"
OWNER = "NZA-93"
REPO = "Classical-Music-Recording-Catalogue-"
PAGES = f"https://{OWNER.lower()}.github.io/{REPO}/"
ISSUE_NEW = (
    f"https://github.com/{OWNER}/{REPO}/issues/new"
    f"?template=community-review-comment.yml"
)


def load(path: pathlib.Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def index_seed(seed: dict) -> dict[str, dict]:
    out = {}
    for work in seed.get("works", []):
        for cand in work.get("candidates", []):
            out[cand["id"]] = {
                "work": f'{work.get("composer")} — {work.get("title")}',
                "director": cand.get("director"),
                "ensemble": cand.get("ensemble"),
                "soloists": cand.get("soloists"),
                "label": cand.get("label"),
                "year": cand.get("year"),
                "mbid": cand.get("mbid"),
            }
    return out


def proposal_by_target(proposals: list) -> dict[str, dict]:
    out = {}
    for prop in proposals:
        if prop.get("kind") != "identity":
            continue
        out[prop["target"]] = prop.get("payload") or {}
    return out


def decision_map(doc: dict) -> dict[str, dict]:
    out = {}
    for row in doc.get("decisions") or []:
        if row.get("kind", "identity") == "identity" and row.get("target"):
            out[row["target"]] = row
    return out


CSS = """
:root{--ground:#E7EAE3;--paper:#FBFCF9;--ink:#191D1A;--ink-soft:#5B655D;--hair:#C7CDC2;
--verdigris:#2F6B60;--oxblood:#7A1220;--amber:#8A5A12}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--ground);color:var(--ink);font-family:"Newsreader",Georgia,serif;
font-size:17px;line-height:1.55;padding:0 clamp(1rem,3vw,2rem) 4rem}
.wrap{max-width:72rem;margin:0 auto}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace}
.masthead{display:flex;flex-wrap:wrap;gap:.75rem 1.5rem;align-items:baseline;
padding:1.4rem 0 1.1rem;border-bottom:1px solid var(--ink)}
.masthead h1{font-family:"Bodoni Moda",serif;font-weight:500;font-size:1.15rem;margin-right:auto}
.masthead h1 a{color:inherit;text-decoration:none}
.masthead nav{display:flex;gap:1.1rem;font-family:"IBM Plex Mono",monospace;font-size:.66rem;
letter-spacing:.16em;text-transform:uppercase}
.masthead a{color:var(--ink-soft);text-decoration:none;border-bottom:1px solid transparent}
.masthead a:hover,.masthead a[aria-current="page"]{color:var(--ink);border-bottom-color:var(--ink)}
.hero{padding:2rem 0 1.4rem;max-width:44rem}
.hero h2{font-family:"Bodoni Moda",serif;font-weight:400;font-size:clamp(1.8rem,5vw,2.6rem);
line-height:1.05;margin-bottom:.6rem}
.hero p{color:var(--ink-soft)}
.banner{margin:1rem 0 1.6rem;padding:.85rem 1rem;border:1px solid var(--ink);
background:var(--paper);font-size:.92rem}
.banner strong{font-family:"IBM Plex Mono",monospace;font-size:.72rem;letter-spacing:.08em;
text-transform:uppercase}
.banner.community{border-color:var(--amber)}
.banner.owner{border-color:var(--verdigris)}
.tally{display:flex;flex-wrap:wrap;gap:1.2rem;margin-top:1.2rem}
.tally div{font-family:"IBM Plex Mono",monospace}
.tally b{display:block;font-family:"Bodoni Moda",serif;font-size:1.7rem;font-weight:400}
.tally span{font-size:.58rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft)}
.filters{display:flex;flex-wrap:wrap;gap:.5rem;margin:1.5rem 0 1rem}
.filters button{font-family:"IBM Plex Mono",monospace;font-size:.62rem;letter-spacing:.08em;
text-transform:uppercase;padding:.35rem .6rem;border:1px solid var(--hair);background:var(--paper);
color:var(--ink);cursor:pointer}
.filters button[aria-pressed="true"]{border-color:var(--ink);background:var(--ink);color:var(--paper)}
.row{border-top:1px solid var(--hair);padding:1rem 0;display:grid;
grid-template-columns:1fr;gap:.55rem}
@media(min-width:820px){.row{grid-template-columns:1.1fr 1fr;gap:1.2rem}}
.row h3{font-family:"Bodoni Moda",serif;font-weight:500;font-size:1.05rem}
.meta{font-family:"IBM Plex Mono",monospace;font-size:.62rem;letter-spacing:.06em;
color:var(--ink-soft);text-transform:uppercase}
.chip{display:inline-block;font-family:"IBM Plex Mono",monospace;font-size:.56rem;
letter-spacing:.08em;text-transform:uppercase;padding:.12rem .4rem;border:1px solid currentColor;
margin-right:.35rem}
.chip.accept{color:var(--verdigris)}
.chip.pending{color:var(--ink-soft)}
.chip.reject{color:var(--oxblood)}
.chip.defer{color:var(--amber)}
.chip.wrong{color:var(--oxblood);border-style:dashed}
.flags{color:var(--oxblood);font-size:.88rem}
.comments{margin-top:.4rem;padding:.65rem .75rem;background:var(--paper);border-left:3px solid var(--amber)}
.comments h4{font-family:"IBM Plex Mono",monospace;font-size:.58rem;letter-spacing:.1em;
text-transform:uppercase;color:var(--amber);margin-bottom:.35rem}
.comments li{margin:.35rem 0;font-size:.92rem;list-style:none}
.comments .who{font-family:"IBM Plex Mono",monospace;font-size:.62rem;color:var(--ink-soft)}
.actions a{font-family:"IBM Plex Mono",monospace;font-size:.62rem;letter-spacing:.08em;
text-transform:uppercase;color:var(--verdigris);margin-right:1rem}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--ink);color:var(--ink-soft);
font-size:.85rem;max-width:40rem}
"""


def chip(decision: str, wrong: bool = False) -> str:
    if wrong:
        return '<span class="chip wrong">wrong work</span>'
    d = decision or "pending"
    return f'<span class="chip {escape(d)}">{escape(d)}</span>'


def render_row(target: str, seed_row: dict, payload: dict, decision: dict,
               comments: list[dict], bucket: str) -> str:
    flags = list(payload.get("review_flags") or [])
    wrong = any(f.startswith("wrong work:") for f in flags)
    mb_url = payload.get("mb_url") or (
        f"https://musicbrainz.org/release-group/{payload['mbid']}"
        if payload.get("mbid") else ""
    )
    seed_line = (
        f"{seed_row.get('director') or seed_row.get('soloists') or '—'} / "
        f"{seed_row.get('ensemble') or '—'} · "
        f"{seed_row.get('label')}, {seed_row.get('year')}"
    )
    mb_line = (
        f"{payload.get('mb_title') or '—'} · first {payload.get('mb_first_release') or '—'} · "
        f"score {payload.get('match_score') if payload.get('match_score') is not None else '—'}"
    )
    flag_html = ""
    if flags:
        flag_html = '<p class="flags">' + "<br>".join(
            escape(f) for f in flags
        ) + "</p>"
    chtml = ""
    if comments:
        items = "".join(
            f'<li><span class="who">{escape(c.get("author") or "?")} · '
            f'community</span><br>{escape(c.get("body") or "")}</li>'
            for c in comments
        )
        chtml = (
            f'<div class="comments"><h4>Community notes '
            f'(not editorial)</h4><ul>{items}</ul></div>'
        )
    issue = (
        f"{ISSUE_NEW}&title={escape(target)}&target={escape(target)}"
    )
    mb_link = (
        f'<a href="{escape(mb_url)}" rel="noopener">MusicBrainz</a>'
        if mb_url else ""
    )
    return f"""
<article class="row" data-bucket="{escape(bucket)}" data-decision="{escape(decision.get('decision') or 'pending')}">
  <div>
    <p class="meta">{escape(target)}</p>
    <h3>{escape(seed_row.get('work') or target)}</h3>
    <p>{escape(seed_line)}</p>
    {chip(decision.get('decision') or 'pending', wrong=wrong)}
    <span class="meta">{escape(bucket.replace('_', ' '))}</span>
    {flag_html}
    {chtml}
  </div>
  <div>
    <p class="meta">MusicBrainz match</p>
    <p>{escape(mb_line)}</p>
    <p class="actions">{mb_link}
      <a href="{issue}">Add community comment</a>
    </p>
  </div>
</article>
"""


def main() -> None:
    queue = load(QUEUE, {})
    decisions = decision_map(load(DECISIONS, {}))
    community = load(COMMUNITY, {"comments": []})
    seed = load(SEED, {"works": []})
    proposals = load(PROPOSALS, [])
    if not isinstance(proposals, list):
        proposals = []

    by_seed = index_seed(seed)
    by_prop = proposal_by_target(proposals)
    by_comments: dict[str, list] = defaultdict(list)
    for c in community.get("comments") or []:
        if c.get("layer") == "community" and c.get("target"):
            by_comments[c["target"]].append(c)

    buckets = queue.get("buckets") or {}
    counts = queue.get("counts") or {}

    # Prefer queue bucket membership; fall back to all identity proposals.
    ordered: list[tuple[str, str]] = []
    for name in ("accept_eligible", "needs_review", "reject_wrong_work"):
        for t in buckets.get(name) or []:
            ordered.append((t, name))
    if not ordered:
        for t in by_prop:
            ordered.append((t, "needs_review"))

    rows_html = []
    for target, bucket in ordered:
        seed_row = by_seed.get(target) or {"work": target}
        payload = by_prop.get(target) or {}
        rows_html.append(
            render_row(
                target, seed_row, payload,
                decisions.get(target) or {},
                by_comments.get(target) or [],
                bucket,
            )
        )

    tally = "".join(
        f"<div><b>{counts.get(k, 0)}</b><span>{label}</span></div>"
        for k, label in (
            ("accept_eligible", "accept-eligible"),
            ("needs_review", "needs review"),
            ("reject_wrong_work", "wrong work"),
            ("citation_tasks", "citation tasks"),
            ("without_identity_proposal", "unharvested"),
        )
    )

    body = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Review board — Critical Discography</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,500&family=Newsreader:opsz,wght@6..72,400;6..72,500&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head><body><div class="wrap">
<header class="masthead">
  <h1><a href="../index.html">Critical Discography</a></h1>
  <nav>
    <a href="../index.html">Catalogue</a>
    <a href="../entries.html">Entries</a>
    <a href="../gallery.html">Gallery</a>
    <a href="index.html" aria-current="page">Review</a>
  </nav>
</header>

<div class="hero">
  <h2>Human review board</h2>
  <p>Queued identity matches and citation tasks for the seed. Community notes
  help authoring; they stay on a separate layer from the owner’s editorial voice.</p>
  <div class="tally">{tally}</div>
</div>

<div class="banner owner">
  <strong>Owner only ({escape(OWNER)})</strong><br>
  Accept / reject decisions live in <span class="mono">proposals/review-decisions.json</span>.
  Apply them with your GitHub login via
  <span class="mono">make review-apply</span> or the
  <a href="https://github.com/{OWNER}/{REPO}/actions/workflows/review-apply.yml">Review apply</a>
  workflow (repository owner actor required). Agents never write scores or
  <span class="mono">data/statements/</span>.
</div>

<div class="banner community">
  <strong>Community layer</strong><br>
  Anyone signed into GitHub can
  <a href="{ISSUE_NEW}">open a community review comment</a>.
  Comments render here with an amber label and are stored under
  <span class="mono">data/community/</span> — never merged into
  <span class="mono">data/editorial/</span> or assessment statements.
</div>

<div class="filters" role="group" aria-label="Filter queue">
  <button type="button" data-filter="all" aria-pressed="true">All</button>
  <button type="button" data-filter="accept_eligible" aria-pressed="false">Accept-eligible</button>
  <button type="button" data-filter="needs_review" aria-pressed="false">Needs review</button>
  <button type="button" data-filter="reject_wrong_work" aria-pressed="false">Wrong work</button>
</div>

<section id="queue">
{''.join(rows_html) if rows_html else '<p class="meta">No review queue yet — run <span class="mono">make review-queue</span>.</p>'}
</section>

<footer>
  <p>Public board: {escape(PAGES)}review/</p>
  <p class="mono">Community ≠ editorial · Wrong-work never applies · No scraped review prose</p>
</footer>
</div>
<script>
const buttons=[...document.querySelectorAll('.filters button')];
const rows=[...document.querySelectorAll('.row')];
buttons.forEach(btn=>btn.addEventListener('click',()=>{{
  buttons.forEach(b=>b.setAttribute('aria-pressed', b===btn ? 'true':'false'));
  const f=btn.dataset.filter;
  rows.forEach(r=>{{
    r.style.display = (f==='all' || r.dataset.bucket===f) ? '' : 'none';
  }});
}}));
</script>
</body></html>
"""
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "index.html").write_text(body, encoding="utf-8")
    # Legacy Pages root mirror
    root_review = ROOT / "review"
    root_review.mkdir(parents=True, exist_ok=True)
    (root_review / "index.html").write_text(body, encoding="utf-8")
    print(f"docs/review/index.html · {len(ordered)} identity rows · "
          f"{sum(len(v) for v in by_comments.values())} community comments")


if __name__ == "__main__":
    main()
