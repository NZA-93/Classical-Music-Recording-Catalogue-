#!/usr/bin/env python3
"""build_review.py — online human-review board (GitHub Pages).

Read-only UI over the harvest review queue + community comments.
Owner decisions stay in proposals/review-decisions.json (git); community
comments live in data/community/ and are labeled as non-editorial.

Needs-review rows are identity-enriched (side-by-side seed vs MB, why-it-missed
from actual mismatches only, remake siblings). Empty harvest fields stay blank —
never invented. Citation tasks stay off identity rows.

No runtime dependencies. No scores invented here.
"""

from __future__ import annotations

import json
import pathlib
import sys
from collections import defaultdict
from html import escape
from typing import Any

ROOT = pathlib.Path(".")
sys.path.insert(0, str(ROOT / "agents"))

import identity_board as ib  # noqa: E402
from harvest import refresh_identity_eligibility  # noqa: E402
import review as rv  # noqa: E402
import review_queue as rq  # noqa: E402

DOCS = ROOT / "docs" / "review"
QUEUE = ROOT / "proposals" / "review-queue.json"
DECISIONS = ROOT / "proposals" / "review-decisions.json"
COMMUNITY = ROOT / "data" / "community" / "comments.json"
SEED = ROOT / "data" / "seed.json"
PROPOSALS = ROOT / "proposals" / "proposals-20260809.json"
GAPS_MD = ROOT / "proposals" / "review" / "PAYLOAD_GAPS.md"
OWNER = "NZA-93"
REPO = "Classical-Music-Recording-Catalogue-"
PAGES = f"https://{OWNER.lower()}.github.io/{REPO}/"
ISSUE_NEW = (
    f"https://github.com/{OWNER}/{REPO}/issues/new"
    f"?template=community-review-comment.yml"
)
DECISIONS_URL = (
    f"https://github.com/{OWNER}/{REPO}/blob/main/proposals/review-decisions.json"
)
APPLY_URL = (
    f"https://github.com/{OWNER}/{REPO}/actions/workflows/review-apply.yml"
)

PACK_LABEL = {
    "accept_eligible": "ACCEPT_ELIGIBLE",
    "needs_review": "NEEDS_REVIEW",
    "reject_wrong_work": "REJECT_WRONG_WORK",
}


def load(path: pathlib.Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def index_seed(seed: dict) -> tuple[dict[str, dict], list[dict], dict[str, int]]:
    """Return (by_id, all_candidates, work_order) with honest field presence."""
    out: dict[str, dict] = {}
    all_cands: list[dict] = []
    work_order: dict[str, int] = {}
    for wi, work in enumerate(seed.get("works", [])):
        wid = str(work.get("id") or "")
        work_order[wid] = wi
        title = work.get("title") or ""
        composer = work.get("composer") or ""
        catalogue = work.get("catalogue") or ""
        display = f"{composer} — {title}" if composer and title else (title or composer)
        for cand in work.get("candidates", []):
            row = {
                "id": cand.get("id"),
                "work": display,
                "work_title": title,
                "composer": composer,
                "catalogue": catalogue,
                "work_id": wid,
                "director": cand.get("director") or "",
                "ensemble": cand.get("ensemble") or "",
                "soloists": cand.get("soloists") or "",
                "label": cand.get("label") or "",
                "year": cand.get("year"),
                "mbid": cand.get("mbid"),
                # Honest absents — never invent. Board omits these unless harvest
                # payload actually carries a token.
                "fassung": cand.get("fassung"),
                "completeness": cand.get("completeness"),
                "session_year": cand.get("session_year"),
                "live_studio": cand.get("live_studio"),
                "venue": None,
                "catno": None,
            }
            out[cand["id"]] = row
            all_cands.append(row)
    return out, all_cands, work_order


def proposal_by_target(proposals: list) -> dict[str, dict]:
    out = {}
    for prop in proposals:
        if prop.get("kind") != "identity":
            continue
        out[prop["target"]] = prop
    return out


def decision_map(doc: dict) -> dict[str, dict]:
    out = {}
    for row in doc.get("decisions") or []:
        if row.get("kind", "identity") == "identity" and row.get("target"):
            out[row["target"]] = row
    return out


def blank(label: str) -> str:
    return (
        f'<span class="blank" title="payload absent — honest omit">'
        f'{escape(label)}: —</span>'
    )


def shown(label: str, value: Any) -> str:
    if value is None or value == "":
        return blank(label)
    return f'<span class="shown"><span class="k">{escape(label)}</span> {escape(str(value))}</span>'


def shown_if(label: str, value: Any) -> str:
    """Present fields only. Absent critic fields stay off the row (not boilerplate)."""
    if value is None or value == "":
        return ""
    return shown(label, value)


CSS = """
:root{--ground:#E7EAE3;--paper:#FBFCF9;--ink:#191D1A;--ink-soft:#5B655D;--hair:#C7CDC2;
--verdigris:#2F6B60;--oxblood:#7A1220;--amber:#8A5A12}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--ground);color:var(--ink);font-family:"Newsreader",Georgia,serif;
font-size:17px;line-height:1.55;padding:0 clamp(1rem,3vw,2rem) 4rem}
.wrap{max-width:78rem;margin:0 auto}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace}
.masthead{display:flex;flex-wrap:wrap;gap:.75rem 1.5rem;align-items:baseline;
padding:1.4rem 0 1.1rem;border-bottom:1px solid var(--ink)}
.masthead h1{font-family:"Bodoni Moda",serif;font-weight:500;font-size:1.15rem;margin-right:auto}
.masthead h1 a{color:inherit;text-decoration:none}
.masthead nav{display:flex;gap:1.1rem;font-family:"IBM Plex Mono",monospace;font-size:.66rem;
letter-spacing:.16em;text-transform:uppercase}
.masthead a{color:var(--ink-soft);text-decoration:none;border-bottom:1px solid transparent}
.masthead a:hover,.masthead a[aria-current="page"]{color:var(--ink);border-bottom-color:var(--ink)}
.hero{padding:2rem 0 1.4rem;max-width:48rem}
.hero h2{font-family:"Bodoni Moda",serif;font-weight:400;font-size:clamp(1.8rem,5vw,2.6rem);
line-height:1.05;margin-bottom:.6rem}
.hero p{color:var(--ink-soft)}
.banner{margin:1rem 0 1.6rem;padding:.85rem 1rem;border:1px solid var(--ink);
background:var(--paper);font-size:.92rem}
.banner strong{font-family:"IBM Plex Mono",monospace;font-size:.72rem;letter-spacing:.08em;
text-transform:uppercase}
.banner.community{border-color:var(--amber)}
.banner.owner{border-color:var(--verdigris)}
.banner.gaps{border-color:var(--ink-soft)}
.tally{display:flex;flex-wrap:wrap;gap:1.2rem;margin-top:1.2rem}
.tally div{font-family:"IBM Plex Mono",monospace}
.tally b{display:block;font-family:"Bodoni Moda",serif;font-size:1.7rem;font-weight:400}
.tally span{font-size:.58rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-soft)}
.filters{display:flex;flex-wrap:wrap;gap:.5rem;margin:1.5rem 0 1rem}
.filters button{font-family:"IBM Plex Mono",monospace;font-size:.62rem;letter-spacing:.08em;
text-transform:uppercase;padding:.35rem .6rem;border:1px solid var(--hair);background:var(--paper);
color:var(--ink);cursor:pointer}
.filters button[aria-pressed="true"]{border-color:var(--ink);background:var(--ink);color:var(--paper)}
.find{flex:1 1 14rem;min-width:12rem}
.find input{width:100%;font-family:"IBM Plex Mono",monospace;font-size:.72rem;
padding:.35rem .6rem;border:1px solid var(--hair);background:var(--paper);color:var(--ink)}
.row{border-top:1px solid var(--hair);padding:1.15rem 0;display:grid;
grid-template-columns:1fr;gap:.75rem}
@media(min-width:900px){.row{grid-template-columns:1fr 1fr;gap:1.4rem}
.row.identity-rich{grid-template-columns:1fr 1fr;}}
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
.chip.absent{color:var(--ink-soft);border-style:dashed}
.chip.conflict{color:var(--oxblood)}
.chip.pass{color:var(--verdigris)}
.why{margin:.55rem 0;padding:.65rem .75rem;background:var(--paper);border-left:3px solid var(--oxblood)}
.why h4{font-family:"IBM Plex Mono",monospace;font-size:.58rem;letter-spacing:.1em;
text-transform:uppercase;color:var(--oxblood);margin-bottom:.35rem}
.why li{margin:.25rem 0;font-size:.92rem;list-style:none}
.why .fields{font-family:"IBM Plex Mono",monospace;font-size:.58rem;color:var(--ink-soft)}
.criteria{margin:.45rem 0;font-size:.88rem}
.criteria li{list-style:none;margin:.2rem 0}
.pair{display:grid;gap:.35rem;font-size:.92rem}
.pair .col-h{font-family:"IBM Plex Mono",monospace;font-size:.58rem;letter-spacing:.1em;
text-transform:uppercase;color:var(--ink-soft);margin-bottom:.15rem}
.blank{color:var(--ink-soft);font-style:italic}
.shown .k{font-family:"IBM Plex Mono",monospace;font-size:.58rem;letter-spacing:.06em;
text-transform:uppercase;color:var(--ink-soft);margin-right:.25rem}
.siblings{margin-top:.4rem;font-size:.88rem;color:var(--ink-soft)}
.comments{margin-top:.4rem;padding:.65rem .75rem;background:var(--paper);border-left:3px solid var(--amber)}
.comments h4{font-family:"IBM Plex Mono",monospace;font-size:.58rem;letter-spacing:.1em;
text-transform:uppercase;color:var(--amber);margin-bottom:.35rem}
.comments li{margin:.35rem 0;font-size:.92rem;list-style:none}
.comments .who{font-family:"IBM Plex Mono",monospace;font-size:.62rem;color:var(--ink-soft)}
.actions a{font-family:"IBM Plex Mono",monospace;font-size:.62rem;letter-spacing:.08em;
text-transform:uppercase;color:var(--verdigris);margin-right:1rem}
.defer-hint{font-family:"IBM Plex Mono",monospace;font-size:.58rem;letter-spacing:.06em;
text-transform:uppercase;color:var(--amber);margin-top:.35rem}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--ink);color:var(--ink-soft);
font-size:.85rem;max-width:44rem}
"""


def chip(decision: str, wrong: bool = False, bucket: str = "") -> str:
    """Chip must agree with bucket membership.

    Wrong-work is always the wrong-work chip. Accept-eligible never shows a
    stale template `reject` — that chip/count disagreement is how wrong-work
    rows sat in the 103 while displaying REJECT.
    """
    if wrong or bucket == "reject_wrong_work":
        return '<span class="chip wrong">wrong work</span>'
    d = decision or "pending"
    if bucket == "accept_eligible" and d == "reject":
        d = "pending"
    return f'<span class="chip {escape(d)}">{escape(d)}</span>'


def render_why(reasons: list[dict[str, str]]) -> str:
    items = "".join(
        f'<li>{escape(r["detail"])} '
        f'<span class="fields">[{escape(r["fields"])}]</span></li>'
        for r in reasons
    )
    return (
        f'<div class="why"><h4>Why it missed auto-accept</h4><ul>{items}</ul></div>'
    )


def render_criteria(checks: list[dict[str, str]]) -> str:
    items = "".join(
        f'<li><span class="chip {escape(c["status"])}">{escape(c["status"])}</span> '
        f'{escape(c["criterion"])} — {escape(c["note"])}</li>'
        for c in checks
    )
    return f'<ul class="criteria">{items}</ul>'


def render_siblings(siblings: list[dict[str, Any]]) -> str:
    if not siblings:
        return '<p class="siblings">Remake siblings: <span class="blank">none in seed</span></p>'
    bits = "; ".join(
        f'{escape(s["id"])} ({escape(str(s.get("year") or "—"))}, '
        f'{escape(s.get("label") or "—")})'
        for s in siblings
    )
    return f'<p class="siblings">Remake siblings (same forces, different year): {bits}</p>'


def render_comments(comments: list[dict]) -> str:
    if not comments:
        return ""
    items = "".join(
        f'<li><span class="who">{escape(c.get("author") or "?")} · '
        f'community</span><br>{escape(c.get("body") or "")}</li>'
        for c in comments
    )
    return (
        f'<div class="comments"><h4>Community notes '
        f'(not editorial)</h4><ul>{items}</ul></div>'
    )




def render_identity_rich(
    target: str,
    seed_row: dict,
    proposal: dict,
    decision: dict,
    comments: list[dict],
    bucket: str,
    enrich: dict[str, Any],
) -> str:
    payload = proposal.get("payload") or {}
    work = {
        "title": seed_row.get("work_title") or "",
        "catalogue": seed_row.get("catalogue") or "",
        "composer": seed_row.get("composer") or "",
    }
    rec = {
        "director": seed_row.get("director"),
        "ensemble": seed_row.get("ensemble"),
        "soloists": seed_row.get("soloists"),
        "year": seed_row.get("year"),
    }
    flags, _eligible = refresh_identity_eligibility(payload, rec, work)
    wrong = any(str(f).startswith("wrong work:") for f in flags)
    mb_url = payload.get("mb_url") or (
        f"https://musicbrainz.org/release-group/{payload['mbid']}"
        if payload.get("mbid") else ""
    )
    pack = PACK_LABEL.get(bucket, bucket)
    conf = payload.get("confidence", payload.get("match_score"))

    fp = enrich.get("field_presence") or {}
    seed_col = f"""
    <div class="pair">
      <p class="col-h">Seed</p>
      {shown("work", seed_row.get("work_title") or seed_row.get("work"))}
      {shown("catalogue", seed_row.get("catalogue"))}
      {shown_if("Fassung", seed_row.get("fassung"))}
      {shown_if("completeness", seed_row.get("completeness"))}
      {shown("conductor", seed_row.get("director"))}
      {shown("orchestra", seed_row.get("ensemble"))}
      {shown("soloists", seed_row.get("soloists"))}
      {shown_if("session year", seed_row.get("session_year"))}
      {shown("seed year (release proxy, not session)", seed_row.get("year"))}
      {shown_if("live/studio", seed_row.get("live_studio"))}
      {shown("label", seed_row.get("label"))}
    </div>
    """

    rg = payload.get("mbid")
    mb_col = f"""
    <div class="pair">
      <p class="col-h">MusicBrainz (harvest)</p>
      {shown("mb_title", payload.get("mb_title"))}
      {shown_if("Fassung", fp.get("fassung"))}
      {shown_if("completeness", fp.get("completeness"))}
      {shown_if("session year", fp.get("session_year"))}
      {shown("first release (release proxy, not session)", payload.get("mb_first_release"))}
      {shown_if("live/studio", fp.get("live_studio"))}
      {shown("release-group MBID", rg)}
      {shown("match confidence (not a verdict)", conf)}
    </div>
    """

    decisions_url = DECISIONS_URL
    apply_url = APPLY_URL
    issue = f"{ISSUE_NEW}&title={escape(target)}&target={escape(target)}"
    mb_link = (
        f'<a href="{escape(mb_url)}" rel="noopener">Open release-group</a>'
        if mb_url else ""
    )

    return f"""
<article class="row identity-rich" data-bucket="{escape(bucket)}"
  data-decision="{escape(decision.get('decision') or 'pending')}">
  <div>
    <p class="meta">{escape(target)} · pack {escape(pack)}</p>
    <h3>{escape(seed_row.get("work") or target)}</h3>
    {chip(decision.get("decision") or "pending", wrong=wrong, bucket=bucket)}
    <span class="meta">{escape(bucket.replace("_", " "))}</span>
    {render_why(enrich["why_missed"])}
    {render_criteria(enrich["criteria"])}
    {render_siblings(enrich["remake_siblings"])}
    {render_comments(comments)}
  </div>
  <div>
    {seed_col}
    {mb_col}
    <p class="actions">{mb_link}
      <a href="{escape(decisions_url)}">Owner: decisions file</a>
      <a href="{escape(apply_url)}">Owner: Review apply</a>
      <a href="{issue}">Add community comment</a>
    </p>
  </div>
</article>
"""


def render_simple_row(
    target: str,
    seed_row: dict,
    payload: dict,
    decision: dict,
    comments: list[dict],
    bucket: str,
) -> str:
    """Compact row for accept-eligible / wrong-work (not the 244 enrichment)."""
    work = {
        "title": seed_row.get("work_title") or "",
        "catalogue": seed_row.get("catalogue") or "",
        "composer": seed_row.get("composer") or "",
    }
    rec = {
        "director": seed_row.get("director"),
        "ensemble": seed_row.get("ensemble"),
        "soloists": seed_row.get("soloists"),
        "year": seed_row.get("year"),
    }
    flags, _eligible = refresh_identity_eligibility(payload, rec, work)
    wrong = any(str(f).startswith("wrong work:") for f in flags)
    mb_url = payload.get("mb_url") or (
        f"https://musicbrainz.org/release-group/{payload['mbid']}"
        if payload.get("mbid") else ""
    )
    seed_line = (
        f"{seed_row.get('director') or seed_row.get('soloists') or '—'} / "
        f"{seed_row.get('ensemble') or '—'} · "
        f"{seed_row.get('label')}, {seed_row.get('year')}"
    )
    conf = payload.get("confidence", payload.get("match_score"))
    mb_line = (
        f"{payload.get('mb_title') or '—'} · first {payload.get('mb_first_release') or '—'} · "
        f"match {conf if conf is not None else '—'}"
    )
    flag_html = ""
    if flags:
        flag_html = '<p class="flags" style="color:var(--oxblood);font-size:.88rem">' + "<br>".join(
            escape(f) for f in flags
        ) + "</p>"
    issue = f"{ISSUE_NEW}&title={escape(target)}&target={escape(target)}"
    mb_link = (
        f'<a href="{escape(mb_url)}" rel="noopener">MusicBrainz</a>'
        if mb_url else ""
    )
    decisions_url = DECISIONS_URL
    apply_url = APPLY_URL
    pack = PACK_LABEL.get(bucket, bucket)
    return f"""
<article class="row" data-bucket="{escape(bucket)}" data-decision="{escape(decision.get('decision') or 'pending')}">
  <div>
    <p class="meta">{escape(target)} · pack {escape(pack)}</p>
    <h3>{escape(seed_row.get('work') or target)}</h3>
    <p>{escape(seed_line)}</p>
    {chip(decision.get('decision') or 'pending', wrong=wrong, bucket=bucket)}
    <span class="meta">{escape(bucket.replace('_', ' '))}</span>
    {flag_html}
    {render_comments(comments)}
  </div>
  <div>
    <p class="meta">MusicBrainz match (confidence, not a verdict)</p>
    <p>{escape(mb_line)}</p>
    <p class="actions">{mb_link}
      <a href="{escape(decisions_url)}">Owner: decisions file</a>
      <a href="{escape(apply_url)}">Owner: Review apply</a>
      <a href="{issue}">Add community comment</a>
    </p>
  </div>
</article>
"""


def sort_needs_review(
    targets: list[str],
    by_seed: dict[str, dict],
    by_prop: dict[str, dict],
    all_cands: list[dict],
    work_order: dict[str, int],
) -> list[tuple[str, dict]]:
    """why-missed first, then work prominence (seed order)."""
    scored: list[tuple[tuple, str, dict]] = []
    for t in targets:
        seed_row = by_seed.get(t) or {"id": t, "work": t, "work_title": t}
        prop = by_prop.get(t) or {"target": t, "payload": {}}
        enrich = ib.enrichment_for_row(seed_row, prop, all_cands)
        wid = seed_row.get("work_id") or ""
        prominence = work_order.get(str(wid), 10_000)
        key = (enrich["why_missed_sort"][0], enrich["why_missed_sort"][1], prominence, t)
        scored.append((key, t, enrich))
    scored.sort(key=lambda x: x[0])
    return [(t, e) for _, t, e in scored]


def main() -> None:
    queue = load(QUEUE, {})
    decisions = decision_map(load(DECISIONS, {}))
    community = load(COMMUNITY, {"comments": []})
    seed = load(SEED, {"works": []})
    proposals = load(PROPOSALS, [])
    if not isinstance(proposals, list):
        proposals = []

    by_seed, all_cands, work_order = index_seed(seed)
    by_prop = proposal_by_target(proposals)
    by_comments: dict[str, list] = defaultdict(list)
    for c in community.get("comments") or []:
        if c.get("layer") == "community" and c.get("target"):
            by_comments[c["target"]].append(c)

    buckets = queue.get("buckets") or {}
    counts = dict(queue.get("counts") or {})

    # Recompute identity membership from the live matcher. Stale
    # review-queue.json auto_accept_eligible lists must not keep a reject /
    # wrong-work chip inside the accept-eligible tally.
    if proposals:
        live = rq.live_identity_buckets(proposals, seed)
        buckets = {
            "accept_eligible": [r["target"] for r in live["accept_eligible"]],
            "needs_review": [r["target"] for r in live["needs_review"]],
            "reject_wrong_work": [r["target"] for r in live["reject_wrong_work"]],
        }
        counts["accept_eligible"] = len(buckets["accept_eligible"])
        counts["needs_review"] = len(buckets["needs_review"])
        counts["reject_wrong_work"] = len(buckets["reject_wrong_work"])
        counts["identity_total"] = (
            counts["accept_eligible"]
            + counts["needs_review"]
            + counts["reject_wrong_work"]
        )

    # Sort needs-review; keep other buckets in queue order.
    needs_sorted = sort_needs_review(
        list(buckets.get("needs_review") or []),
        by_seed, by_prop, all_cands, work_order,
    )
    enrich_by_target = {t: e for t, e in needs_sorted}

    ordered: list[tuple[str, str]] = []
    for t in buckets.get("accept_eligible") or []:
        ordered.append((t, "accept_eligible"))
    for t, _ in needs_sorted:
        ordered.append((t, "needs_review"))
    for t in buckets.get("reject_wrong_work") or []:
        ordered.append((t, "reject_wrong_work"))
    if not ordered:
        for t in by_prop:
            ordered.append((t, "needs_review"))

    rows_html = []
    for target, bucket in ordered:
        seed_row = by_seed.get(target) or {"work": target, "work_title": target, "id": target}
        prop = by_prop.get(target) or {"target": target, "payload": {}}
        payload = prop.get("payload") or {}
        if bucket == "needs_review":
            enrich = enrich_by_target.get(target) or ib.enrichment_for_row(
                seed_row, prop, all_cands
            )
            rows_html.append(
                render_identity_rich(
                    target, seed_row, prop,
                    decisions.get(target) or {},
                    by_comments.get(target) or [],
                    bucket,
                    enrich,
                )
            )
        else:
            rows_html.append(
                render_simple_row(
                    target, seed_row, payload,
                    decisions.get(target) or {},
                    by_comments.get(target) or [],
                    bucket,
                )
            )

    ib.write_payload_gaps_markdown(str(GAPS_MD))

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
  <p>Queued identity matches for the seed. Needs-review rows show seed vs harvest
  side by side; empty fields stay blank. Community notes help authoring; they stay
  on a separate layer from the owner’s editorial voice. Citation tasks are listed
  in the tally only — not on identity rows.</p>
  <div class="tally">{tally}</div>
</div>

<div class="banner owner">
  <strong>Owner only ({escape(OWNER)})</strong><br>
  There are no public accept / reject / defer buttons on this page — community
  cannot apply MBIDs. The owner records decisions in
  <a href="{DECISIONS_URL}"><span class="mono">proposals/review-decisions.json</span></a>
  (fill <span class="mono">by</span> + <span class="mono">date</span> on each accept),
  then runs <span class="mono">make review-apply</span> or the
  <a href="{APPLY_URL}">Review apply</a>
  workflow (repository owner actor required). Identity apply writes the
  release-group MBID only. Agents never write scores or
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

<div class="banner gaps">
  <strong>Honest omit</strong><br>
  Fassung, completeness, session year and live/studio appear on a row only when
  MusicBrainz actually supplied a token. They are not repeated as empty
  “absent Fassung” paragraphs. seed.year and MB first-release stay labelled as
  <em>release-year proxies</em>, never as session year. Match figures are
  MusicBrainz search confidence, not critical verdicts and never stars.
  Inventory:
  <a href="../../proposals/review/PAYLOAD_GAPS.md"><span class="mono">PAYLOAD_GAPS.md</span></a>.
</div>

<div class="filters" role="group" aria-label="Filter queue">
  <button type="button" data-filter="all" aria-pressed="true">All</button>
  <button type="button" data-filter="accept_eligible" aria-pressed="false">Accept-eligible</button>
  <button type="button" data-filter="needs_review" aria-pressed="false">Needs review</button>
  <button type="button" data-filter="reject_wrong_work" aria-pressed="false">Wrong work</button>
  <label class="find">Find
    <input id="find" type="search" placeholder="Kleiber, Beethoven 5, bach/john…">
  </label>
</div>

<section id="queue">
{''.join(rows_html) if rows_html else '<p class="meta">No review queue yet — run <span class="mono">make review-queue</span>.</p>'}
</section>

<footer>
  <p>Public board: {escape(PAGES)}review/</p>
  <p class="mono">Community ≠ editorial · Wrong-work never applies · No invented musicology · Citation tasks off identity rows</p>
</footer>
</div>
<script>
const buttons=[...document.querySelectorAll('.filters button')];
const rows=[...document.querySelectorAll('.row')];
const find=document.getElementById('find');
function applyFilters(){{
  const f=buttons.find(b=>b.getAttribute('aria-pressed')==='true')?.dataset.filter || 'all';
  const q=(find?.value || '').trim().toLowerCase();
  rows.forEach(r=>{{
    const bucketOk = (f==='all' || r.dataset.bucket===f);
    const textOk = !q || r.textContent.toLowerCase().includes(q);
    r.style.display = (bucketOk && textOk) ? '' : 'none';
  }});
}}
buttons.forEach(btn=>btn.addEventListener('click',()=>{{
  buttons.forEach(b=>b.setAttribute('aria-pressed', b===btn ? 'true':'false'));
  applyFilters();
}}));
if(find) find.addEventListener('input', applyFilters);
</script>
</body></html>
"""
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "index.html").write_text(body, encoding="utf-8")
    root_review = ROOT / "review"
    root_review.mkdir(parents=True, exist_ok=True)
    (root_review / "index.html").write_text(body, encoding="utf-8")
    print(
        f"docs/review/index.html · {len(ordered)} identity rows · "
        f"{counts.get('needs_review', 0)} needs-review enriched · "
        f"{sum(len(v) for v in by_comments.values())} community comments · "
        f"gaps → {GAPS_MD}"
    )


if __name__ == "__main__":
    main()
