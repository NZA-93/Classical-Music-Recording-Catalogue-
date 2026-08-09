#!/usr/bin/env python3
"""
harvest.py — the agent pipeline for the Critical Discography.

Round 1 does four things, in this order, and stops:

    1. IDENTITY    resolve every candidate recording to a MusicBrainz
                   release-group. Unresolvable candidates are dropped, not kept.
    2. EDITIONS    pull the releases under each group — catalogue number,
                   barcode, year, format. This is the second-hand layer.
    3. COVERS      ask the Cover Art Archive whether a front image exists.
    4. CITATIONS   for every recording, emit a task naming what a human or a
                   reading agent must find. It does not invent the answer.

WHAT THE AGENTS ARE ALLOWED TO DO
---------------------------------
Harvest open, licensed data (MusicBrainz CC0, Wikidata CC0, Wikipedia CC BY-SA),
and record *pointers* to everything else. Critical writing in Gramophone,
Diapason, ClassicsToday, Fanfare and the rest is copyrighted: the guide stores
a normalised score, a short characterisation in the guide's own words, and a
locator. It does not store or republish review text, and it does not scrape
sites whose terms forbid it. A citation a reader can follow is worth more than
a paragraph the guide cannot legally show.

Nothing here writes to the catalogue. It writes proposals, which become a pull
request, which a human merges.

    python harvest.py seed.json --contact you@example.org --budget 300
    python harvest.py seed.json --contact you@example.org --dry-run
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable, Optional

VERSION = "harvest/1.1"
CACHE = pathlib.Path(".cache")
OUT = pathlib.Path("proposals")

# MusicBrainz search score 0–100. Below this, never treat a match as eligible
# for auto-accept; leave it for human identity review (SPRINTS S1-06).
IDENTITY_MIN_CONFIDENCE = 80

COMPILATION_RE = re.compile(
    r"\b(best of|collection|anthology|sampler|highlights)\b",
    re.IGNORECASE,
)

STALE = {"identity": timedelta(days=365), "editions": timedelta(days=90),
         "cover": timedelta(days=90), "cover_miss": timedelta(days=14),
         "citation": timedelta(days=180)}


# ------------------------------------------------------------------ transport

class Http:
    """One polite client. Per-host rate limiting, on-disk cache, robots gate."""

    LIMITS = {"musicbrainz.org": 1.05, "coverartarchive.org": 0.6,
              "www.wikidata.org": 0.3, "en.wikipedia.org": 0.3}

    # Documented APIs, used as their operators intend. robots.txt governs
    # crawling; MusicBrainz disallows /ws/ there precisely to keep crawlers out
    # of an endpoint meant for identified clients under a published rate limit.
    # Honouring the rate limit is the obligation that matters. Everything not on
    # this list is treated as HTML and goes through the robots gate.
    APIS = ("https://musicbrainz.org/ws/",
            "https://coverartarchive.org/",
            "https://www.wikidata.org/w/api.php",
            "https://en.wikipedia.org/api/")

    def __init__(self, contact: str, budget: int, dry: bool = False):
        self.ua = f"CriticalDiscography/2.0 ({contact})"
        self.budget = budget
        self.spent = 0
        self.dry = dry
        self.last: dict[str, float] = {}
        self.robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        # ok | empty | error | robots | dry — so the queue does not apply a
        # multi-day backoff after a 503/timeout.
        self.last_status: str = "ok"
        CACHE.mkdir(exist_ok=True)

    def allowed(self, url: str) -> bool:
        if url.startswith(self.APIS):
            return True
        host = urllib.parse.urlparse(url).netloc
        if host not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"https://{host}/robots.txt")
            try:
                rp.read()
            except Exception:
                rp = None
            self.robots[host] = rp
        rp = self.robots[host]
        if rp is None:
            print(f"    robots.txt unreachable for {host} — skipping (not an API)")
            return False          # cannot verify permission: do not scrape
        return rp.can_fetch(self.ua, url)

    def get(self, url: str) -> Optional[dict | bytes]:
        if self.spent >= self.budget:
            raise BudgetExhausted()
        if not self.allowed(url):
            print(f"    robots.txt disallows {url}")
            self.last_status = "robots"
            return None
        if self.dry:
            self.spent += 1
            self.last_status = "dry"
            return None

        host = urllib.parse.urlparse(url).netloc
        gap = self.LIMITS.get(host, 1.0) - (time.monotonic() - self.last.get(host, 0))
        if gap > 0:
            time.sleep(gap)
        self.last[host] = time.monotonic()

        req = urllib.request.Request(url, headers={"User-Agent": self.ua, "Accept": "application/json"})
        self.spent += 1
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                body = r.read()
                if "json" in r.headers.get("Content-Type", ""):
                    self.last_status = "ok"
                    return json.loads(body)
                self.last_status = "ok"
                return body
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.last_status = "empty"
                return None
            print(f"    HTTP {e.code} {url}")
            self.last_status = "error"
            return None
        except Exception as e:
            print(f"    {type(e).__name__} {url}")
            self.last_status = "error"
            return None


class BudgetExhausted(Exception):
    """Stop cleanly and resume next run. The queue keeps its cursor."""


# ------------------------------------------------------------------ proposals

@dataclass
class Proposal:
    target: str                  # "work/candidate" path this concerns
    kind: str                    # identity | editions | cover | citation_task
    payload: dict
    source: str
    provenance: str              # cited | attributed | draft
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ------------------------------------------------------------------ score maps

def normalise(scale: str, value) -> Optional[float]:
    """Map a publication's own scale onto 0–3. Prose-only sources return None,
    which routes them to a human rather than to a guess."""
    try:
        if scale == "stars_5":       return round(float(value) / 5 * 3, 2)
        if scale == "stars_3":       return round(float(value), 2)
        if scale == "ten_point":     return round(float(value) / 10 * 3, 2)
        if scale == "percent":       return round(float(value) / 100 * 3, 2)
        if scale == "award":         return 2.90     # Diapason d'Or, Gramophone Award
        if scale == "editors_choice":return 2.85
        if scale == "rosette":       return 2.95     # Penguin Guide rosette
    except (TypeError, ValueError):
        return None
    return None


# ------------------------------------------------------------------ adapters

def identity_review_flags(rec: dict, mb_title: str, mb_first_release: Optional[str],
                          confidence: Optional[int]) -> list[str]:
    """Flags that block auto-accept. Humans still review clean matches too."""
    flags: list[str] = []
    if confidence is None:
        flags.append("missing MusicBrainz confidence score")
    elif confidence < IDENTITY_MIN_CONFIDENCE:
        flags.append(f"confidence {confidence} < {IDENTITY_MIN_CONFIDENCE}")
    want = str(rec.get("year") or "")[:4]
    got = str(mb_first_release or "")[:4]
    if want.isdigit() and got.isdigit():
        delta = abs(int(want) - int(got))
        if delta > 3:
            flags.append(f"date off by {delta} years ({want} vs {got})")
    if mb_title and COMPILATION_RE.search(mb_title):
        flags.append(f"compilation-like title: {mb_title!r}")
    return flags


def adapter_identity(rec: dict, work: dict, http: Http) -> list[Proposal]:
    """Resolve a candidate to a MusicBrainz release-group. CC0 data.

    Emits confidence and review flags. Matches below IDENTITY_MIN_CONFIDENCE
    are never auto_accept_eligible — a human must decide.
    """
    if rec.get("mbid"):
        return []
    artist = rec.get("director") or rec.get("ensemble") or rec.get("soloists") or ""
    terms = f'{work["title"]} AND artist:"{artist}"' if artist else work["title"]
    q = urllib.parse.urlencode({"query": terms, "fmt": "json", "limit": 5})
    data = http.get(f"https://musicbrainz.org/ws/2/release-group/?{q}")
    if not data:
        return []
    groups = data.get("release-groups", [])
    if not groups:
        return []

    want = str(rec.get("year", ""))[:4]

    def rank(g):
        d = (g.get("first-release-date") or "")[:4]
        near = abs(int(d) - int(want)) if d.isdigit() and want.isdigit() else 999
        return (near, -g.get("score", 0))

    ranked = sorted(groups, key=rank)
    best = ranked[0]
    confidence = best.get("score")
    if confidence is not None:
        confidence = int(confidence)
    mb_title = best.get("title") or ""
    mb_first = best.get("first-release-date")
    flags = identity_review_flags(rec, mb_title, mb_first, confidence)
    eligible = confidence is not None and confidence >= IDENTITY_MIN_CONFIDENCE and not flags

    alternatives = []
    for g in ranked[1:]:
        alternatives.append({
            "mbid": g["id"],
            "mb_title": g.get("title"),
            "mb_first_release": g.get("first-release-date"),
            "confidence": g.get("score"),
            "mb_url": f"https://musicbrainz.org/release-group/{g['id']}",
        })

    return [Proposal(rec["id"], "identity", {
        "mbid": best["id"],
        "mb_title": mb_title,
        "mb_first_release": mb_first,
        "match_score": confidence,          # alias kept for agents/review.py
        "confidence": confidence,
        "auto_accept_eligible": eligible,
        "needs_human_review": True,         # identity always merges via human PR
        "uncertain": not eligible,
        "review_flags": flags,
        "mb_url": f"https://musicbrainz.org/release-group/{best['id']}",
        "query": terms,
        "seed": {
            "work": f'{work.get("composer")} — {work.get("title")}',
            "director": rec.get("director"),
            "ensemble": rec.get("ensemble"),
            "soloists": rec.get("soloists"),
            "label": rec.get("label"),
            "year": rec.get("year"),
        },
        "alternatives": alternatives,
    }, "MusicBrainz", "cited")]


def adapter_editions(rec: dict, work: dict, http: Http) -> list[Proposal]:
    """Every physical release under the group: catno, barcode, format, year."""
    if not rec.get("mbid"):
        return []
    q = urllib.parse.urlencode({"release-group": rec["mbid"], "fmt": "json",
                                "inc": "labels+media", "limit": 25})
    data = http.get(f"https://musicbrainz.org/ws/2/release?{q}")
    if not data:
        return []
    editions = []
    for r in data.get("releases", []):
        li = (r.get("label-info") or [{}])[0]
        editions.append({
            "mbid": r["id"], "year": (r.get("date") or "")[:4],
            "catno": li.get("catalog-number"),
            "label": (li.get("label") or {}).get("name"),
            "barcode": r.get("barcode") or None,
            "format": (r.get("media") or [{}])[0].get("format"),
            "country": r.get("country"),
            "verified": False,
        })
    return [Proposal(rec["id"], "editions", {"editions": editions}, "MusicBrainz", "cited")] if editions else []


def _caa_front_from_meta(meta: dict) -> Optional[str]:
    """Pick a front-image hotlink from CAA JSON. Never download binary bytes."""
    for img in meta.get("images") or []:
        if not img.get("front"):
            continue
        thumbs = img.get("thumbnails") or {}
        # Prefer the 500px thumb URL; fall back to declared image URL.
        return thumbs.get("500") or thumbs.get("large") or img.get("image")
    return None


def adapter_cover(rec: dict, work: dict, http: Http) -> list[Proposal]:
    """Cover Art Archive existence check via JSON metadata (hotlink only).

    Resolution ladder (HARVEST_STRATEGY Part 2), stopping at the first hit:
      1. CAA by release (when a release mbid is already known)
      2. CAA by release-group (identity mbid)
    Misses are proposals too — a contribution prompt, not a failure.
    Images are never downloaded or committed; Discogs is never fetched.
    """
    if not rec.get("mbid"):
        return []

    release_mbid = rec.get("release_mbid")
    rg_mbid = rec["mbid"]
    image = None
    step = None
    checked = []

    if release_mbid:
        url = f"https://coverartarchive.org/release/{release_mbid}"
        checked.append(url)
        meta = http.get(url)
        if isinstance(meta, dict):
            image = _caa_front_from_meta(meta)
            if image:
                step = "caa-release"

    if image is None:
        url = f"https://coverartarchive.org/release-group/{rg_mbid}"
        checked.append(url)
        meta = http.get(url)
        if isinstance(meta, dict):
            image = _caa_front_from_meta(meta)
            if image:
                step = "caa-release-group"

    hit = image is not None
    # Stable hotlink shape for the site/render path (release-group front-500).
    hotlink = (
        f"https://coverartarchive.org/release-group/{rg_mbid}/front-500"
        if hit and step == "caa-release-group"
        else image
    )
    payload = {
        "image": hotlink if hit else None,
        "image_url": image,
        "status": "hit" if hit else "miss",
        "resolution_step": step,
        "release_group_mbid": rg_mbid,
        "release_mbid": release_mbid,
        "checked_urls": checked,
        "source": "Cover Art Archive",
        "rehost": False,
        "note": (
            "Hotlink only — do not download or commit image binaries. "
            "Missing sleeves should be uploaded upstream to MusicBrainz / CAA."
        ),
    }
    if not hit:
        payload["contribution_prompt"] = {
            "action": "photograph_sleeve_and_upload_to_musicbrainz",
            "musicbrainz_rg": f"https://musicbrainz.org/release-group/{rg_mbid}",
            "why": "CAA has no front image yet; the archive grows — re-check fortnightly.",
        }
    return [Proposal(rec["id"], "cover", payload, "Cover Art Archive", "cited")]


CITATION_TARGETS = [
    ("Gramophone", "review or Collection survey", "interpretation"),
    ("Diapason", "review, d'Or award, or guide entry", "interpretation"),
    ("Penguin Guide", "entry, any edition", "interpretation"),
    ("ClassicsToday", "review with numeric artistic/sound pair", "both"),
    ("Fanfare / MusicWeb", "review", "interpretation"),
    ("Remastering documentation", "engineer's notes, label technical sheet", "sound"),
]


def adapter_citation(rec: dict, work: dict, http: Http) -> list[Proposal]:
    """No network. Emits the work that a reading agent or a human must do,
    with the exact question, so nobody is asked to 'find some reviews'."""
    label = " — ".join(x for x in (rec.get("soloists"), rec.get("director"),
                                   rec.get("ensemble")) if x)
    tasks = [{
        "publication": pub, "looking_for": what, "axis": axis,
        "must_return": ["locator (URL, issue, or page)", "normalised score 0–3",
                        "one-sentence characterisation in the guide's own words"],
        "must_not_return": ["copied review text"],
    } for pub, what, axis in CITATION_TARGETS]
    return [Proposal(rec["id"], "citation_task",
                     {"recording": f"{label} ({rec.get('label')}, {rec.get('year')})",
                      "work": f'{work["composer"]} — {work["title"]}',
                      "sound_axis_note": "Sound must be attached to a specific edition, not the recording.",
                      "tasks": tasks},
                     VERSION, "draft")]


ADAPTERS: dict[str, Callable] = {
    "identity": adapter_identity,
    "editions": adapter_editions,
    "cover": adapter_cover,
    "citation": adapter_citation,
}

# Order matters: editions and covers need an mbid that identity supplies.
STAGES = ["identity", "editions", "cover", "citation"]


# ------------------------------------------------------------------ queue

def prominence(work: dict, rec: dict) -> int:
    """Cheap priority. Works with no assessment at all come first, then
    recordings whose year suggests they are the historically central ones."""
    p = 0
    if not work.get("assessed"):
        p += 10
    if rec.get("year", "").isdigit() and int(rec["year"]) < 1975:
        p += 3
    return p


def queue(seed: dict, state: dict) -> Iterable[tuple[str, dict, dict]]:
    items = []
    for work in seed["works"]:
        for rec in work["candidates"]:
            done = state.get(rec["id"], {})
            for stage in STAGES:
                # Preconditions. editions and cover need an mbid, which only
                # arrives when an identity proposal has been reviewed and
                # merged. A run therefore resolves identity; the next run,
                # after the pull request lands, goes deeper. The pipeline is
                # deliberately not allowed to build on unreviewed guesses.
                if stage in ("editions", "cover") and not rec.get("mbid"):
                    continue
                last = done.get(stage)
                if last:
                    age = datetime.now(timezone.utc) - datetime.fromisoformat(last["at"])
                    if last.get("hit"):
                        wait = STALE["cover_miss" if stage == "cover" else stage]
                    else:
                        # A miss may be a genuine absence or a bad day on the
                        # network. Back off rather than hammering either way.
                        wait = timedelta(days=min(7 * last.get("attempts", 1), 60))
                    if age < wait:
                        continue
                items.append((prominence(work, rec), stage, work, rec))
                break                       # one stage per recording per run
    items.sort(key=lambda x: -x[0])
    for _, stage, work, rec in items:
        yield stage, work, rec


# ------------------------------------------------------------------ reporting

def _seed_counts(seed: dict) -> tuple[int, int, int]:
    n_works = len(seed.get("works", []))
    n_cands = sum(len(w.get("candidates") or []) for w in seed.get("works", []))
    n_mbid = sum(1 for w in seed.get("works", [])
                 for r in (w.get("candidates") or []) if r.get("mbid"))
    return n_works, n_cands, n_mbid


def write_pr_body(path: pathlib.Path, *, stamp: str, version: str, contact: str,
                  budget: int, spent: int, planned: dict[str, int],
                  proposals: list[Proposal], seed: dict, dry: bool) -> None:
    n_works, n_cands, n_mbid = _seed_counts(seed)
    identities = [p for p in proposals if p.kind == "identity"]
    covers = [p for p in proposals if p.kind == "cover"]
    eligible = sum(1 for p in identities if p.payload.get("auto_accept_eligible"))
    uncertain = sum(1 for p in identities if p.payload.get("uncertain"))
    cover_hits = sum(1 for p in covers if p.payload.get("status") == "hit")
    cover_miss = sum(1 for p in covers if p.payload.get("status") == "miss")
    have_ids = {p.target for p in identities}
    unresolved = [
        c["id"]
        for w in seed.get("works", [])
        for c in (w.get("candidates") or [])
        if c["id"] not in have_ids and not c.get("mbid")
    ]

    title = f"# Harvest {stamp}" + (" · DRY RUN (plan only)" if dry else "")
    body = [
        title, "",
        f"`{version}` · contact `{contact}` · budget **{budget}** · "
        f"{'planned ' if dry else ''}**{spent}** requests · "
        f"**{len(proposals)}** proposals",
        "",
        "## Expected cost",
        "",
        f"- Seed: **{n_works}** works · **{n_cands}** candidates · "
        f"**{n_mbid}** already have an mbid",
        f"- Budget cap: **{budget}** requests (MusicBrainz ~1 req/s; CAA ~0.6s gap)",
        f"- This run: **{spent}** network request{'s' if spent != 1 else ''}"
        + (" (not sent — dry-run)" if dry else ""),
        f"- Wall-clock if live: ~{max(spent, 1)}–{spent + 30}s under polite rate limits",
        "",
        "| Stage | Planned |",
        "|---|---|",
    ]
    body += [f"| {k} | {v} |" for k, v in sorted(planned.items())] or ["| — | 0 |"]

    if dry:
        body += [
            "",
            "## Dry-run notes",
            "",
            "- No MusicBrainz / CAA requests were made.",
            "- Editions and covers stay gated on a human-merged mbid "
            "(pipeline does not build on unreviewed identity guesses).",
            "- After this plan is accepted, re-run without `--dry-run` with the "
            "same budget.",
        ]
    else:
        body += [
            "",
            "## Identity confidence",
            "",
            f"- Identity proposals: **{len(identities)}** / {n_cands} candidates",
            f"- `auto_accept_eligible` (confidence ≥ {IDENTITY_MIN_CONFIDENCE}, "
            f"no compilation/date flags): **{eligible}**",
            f"- Uncertain / must stay for human review: **{uncertain}**",
            f"- Unresolved (no MusicBrainz hit this run): **{len(unresolved)}**",
            "- **Do not auto-accept below 80.** Reject compilations, samplers, "
            "wrong-decade matches.",
            "",
            "## Covers (Cover Art Archive only)",
            "",
            f"- Cover proposals: **{len(covers)}** · hits **{cover_hits}** · "
            f"misses **{cover_miss}**",
            "- Cover stage stays gated until identity mbids are human-merged "
            "(pipeline does not build on unreviewed guesses).",
            "- When covers run: CAA JSON hotlinks only — no image binaries, "
            "no Discogs. Misses include an upstream upload prompt.",
        ]
        if unresolved:
            body += ["", "### Unresolved candidates", ""]
            body += [f"- `{u}`" for u in unresolved]

        if identities:
            body += ["", "### Identity review table", "",
                     "| Target | Seed | MusicBrainz | Conf. | Eligible | Flags |",
                     "|---|---|---|---|---|---|"]
            for p in identities:
                s = p.payload.get("seed") or {}
                seed_s = f"{s.get('director') or s.get('soloists') or '—'}; " \
                         f"{s.get('label')}, {s.get('year')}"
                mb = f"{p.payload.get('mb_title')} ({p.payload.get('mb_first_release')})"
                flags = "; ".join(p.payload.get("review_flags") or []) or ""
                elig = "yes" if p.payload.get("auto_accept_eligible") else "**no**"
                body.append(
                    f"| `{p.target}` | {seed_s} | {mb} | "
                    f"{p.payload.get('confidence')} | {elig} | {flags} |"
                )

        if covers:
            body += ["", "### Cover proposals", "",
                     "| Target | Status | Step | Hotlink |",
                     "|---|---|---|---|"]
            for p in covers:
                body.append(
                    f"| `{p.target}` | {p.payload.get('status')} | "
                    f"{p.payload.get('resolution_step') or '—'} | "
                    f"{p.payload.get('image') or '—'} |"
                )

    body += [
        "",
        "## Review checklist",
        "",
        "- [ ] Identity matches are the right recording, not a compilation / sampler",
        f"- [ ] No identity with confidence < {IDENTITY_MIN_CONFIDENCE} is treated "
        "as auto-accept",
        "- [ ] Uncertain rows reviewed against MusicBrainz (`mb_url`) before merge",
        "- [ ] Cover payloads are CAA / MusicBrainz hotlinks only (no binaries, "
        "no Discogs)",
        "- [ ] Barcodes belong to the edition claimed (editions stage)",
        "- [ ] No review text has been copied into any payload",
        "- [ ] Every score carries a locator, or it stays `draft`",
        "",
        "## Stop",
        "",
        "Human identity review gate. Do not begin editions/covers apply until "
        "mbids are ratified.",
    ]
    path.write_text("\n".join(body) + "\n", "utf-8")


# ------------------------------------------------------------------ main

def merge_proposals(existing: list[dict], new: list[Proposal]) -> list[dict]:
    """Upsert by (target, kind) so a resume run does not erase earlier work."""
    by_key: dict[tuple[str, str], dict] = {}
    for raw in existing:
        by_key[(raw.get("target", ""), raw.get("kind", ""))] = raw
    for p in new:
        by_key[(p.target, p.kind)] = asdict(p)
    return list(by_key.values())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", type=pathlib.Path)
    ap.add_argument("--contact", default="maintainer@example.org")
    ap.add_argument("--budget", type=int, default=300)
    ap.add_argument("--dry-run", action="store_true",
                    help="plan the run and count requests without making them")
    ap.add_argument("--only", default="",
                    help="comma-separated stages to run (default: all). "
                         "Example: --only identity,cover")
    args = ap.parse_args()

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    if only and not only.issubset(set(STAGES)):
        ap.error(f"--only entries must be in {STAGES}")

    seed = json.loads(args.seed.read_text("utf-8"))
    state_path = CACHE / "harvest_state.json"
    state = json.loads(state_path.read_text("utf-8")) if state_path.exists() else {}

    http = Http(args.contact, args.budget, dry=args.dry_run)
    proposals: list[Proposal] = []
    planned: dict[str, int] = {}

    n_works, n_cands, _ = _seed_counts(seed)
    print(f"{VERSION} · {n_works} works · {n_cands} candidates · "
          f"budget {args.budget} requests"
          + (" · DRY RUN" if args.dry_run else "")
          + (f" · only {','.join(sorted(only))}" if only else ""))

    try:
        for stage, work, rec in queue(seed, state):
            if only and stage not in only:
                continue
            planned[stage] = planned.get(stage, 0) + 1
            if args.dry_run and stage != "citation":
                http.spent += 1
                if http.spent >= http.budget:
                    raise BudgetExhausted()
                continue
            print(f"  [{stage}] {rec['id']}")
            got = ADAPTERS[stage](rec, work, http)
            # Transient transport failures must not advance the cursor into a
            # week-long backoff — retry next run (or later in this budget).
            if not got and http.last_status == "error":
                print("    transient failure — cursor not advanced")
                continue
            proposals.extend(got)
            prev = state.setdefault(rec["id"], {}).get(stage, {})
            state[rec["id"]][stage] = {
                "at": datetime.now(timezone.utc).isoformat(),
                "hit": bool(got),
                "attempts": 0 if got else prev.get("attempts", 0) + 1,
            }
    except BudgetExhausted:
        print("  budget reached — stopping cleanly, cursor kept")

    OUT.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_path = OUT / f"proposals-{stamp}.json"

    if not args.dry_run:
        CACHE.mkdir(exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2), "utf-8")
        existing: list[dict] = []
        if out_path.exists():
            try:
                prev = json.loads(out_path.read_text("utf-8"))
                if isinstance(prev, list):
                    existing = prev
            except json.JSONDecodeError:
                existing = []
        merged = merge_proposals(existing, proposals)
        out_path.write_text(
            json.dumps(merged, indent=2, ensure_ascii=False), "utf-8")
        # Report on the merged set so PR_BODY reflects the full day file.
        report_props = [
            Proposal(
                target=m["target"], kind=m["kind"], payload=m["payload"],
                source=m["source"], provenance=m["provenance"],
                created=m.get("created") or datetime.now(timezone.utc).isoformat(),
            )
            for m in merged
        ]
    else:
        report_props = proposals

    write_pr_body(
        OUT / "PR_BODY.md",
        stamp=stamp, version=VERSION, contact=args.contact,
        budget=args.budget, spent=http.spent, planned=planned,
        proposals=report_props, seed=seed, dry=args.dry_run,
    )

    n_wrote = len(report_props) if not args.dry_run else len(proposals)
    print(f"\n{http.spent} requests · {len(proposals)} new / {n_wrote} in file")
    for k, v in sorted(planned.items()):
        print(f"  {k:<10} {v:>4} queued")
    if args.dry_run:
        print(f"wrote {OUT}/PR_BODY.md (plan only — no proposals file, state untouched)")
    else:
        print(f"wrote {out_path} and PR_BODY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
