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
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable, Optional

VERSION = "harvest/1.0"
CACHE = pathlib.Path(".cache")
OUT = pathlib.Path("proposals")

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
            return None
        if self.dry:
            self.spent += 1
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
                    return json.loads(body)
                return body
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            print(f"    HTTP {e.code} {url}")
            return None
        except Exception as e:
            print(f"    {type(e).__name__} {url}")
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

def adapter_identity(rec: dict, work: dict, http: Http) -> list[Proposal]:
    """Resolve a candidate to a MusicBrainz release-group. CC0 data."""
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

    best = sorted(groups, key=rank)[0]
    return [Proposal(rec["id"], "identity",
                     {"mbid": best["id"], "mb_title": best.get("title"),
                      "mb_first_release": best.get("first-release-date"),
                      "match_score": best.get("score")},
                     "MusicBrainz", "cited")]


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


def adapter_cover(rec: dict, work: dict, http: Http) -> list[Proposal]:
    if not rec.get("mbid"):
        return []
    url = f"https://coverartarchive.org/release-group/{rec['mbid']}/front-500"
    got = http.get(url)
    return [Proposal(rec["id"], "cover",
                     {"image": url if got is not None else None},
                     "Cover Art Archive", "cited")]


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


# ------------------------------------------------------------------ main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", type=pathlib.Path)
    ap.add_argument("--contact", default="maintainer@example.org")
    ap.add_argument("--budget", type=int, default=300)
    ap.add_argument("--dry-run", action="store_true",
                    help="plan the run and count requests without making them")
    args = ap.parse_args()

    seed = json.loads(args.seed.read_text("utf-8"))
    state_path = CACHE / "harvest_state.json"
    state = json.loads(state_path.read_text("utf-8")) if state_path.exists() else {}

    http = Http(args.contact, args.budget, dry=args.dry_run)
    proposals: list[Proposal] = []
    planned: dict[str, int] = {}

    print(f"{VERSION} · {len(seed['works'])} works · budget {args.budget} requests"
          + (" · DRY RUN" if args.dry_run else ""))

    try:
        for stage, work, rec in queue(seed, state):
            planned[stage] = planned.get(stage, 0) + 1
            if args.dry_run and stage != "citation":
                http.spent += 1
                if http.spent >= http.budget:
                    raise BudgetExhausted()
                continue
            print(f"  [{stage}] {rec['id']}")
            got = ADAPTERS[stage](rec, work, http)
            proposals.extend(got)
            prev = state.setdefault(rec["id"], {}).get(stage, {})
            state[rec["id"]][stage] = {
                "at": datetime.now(timezone.utc).isoformat(),
                "hit": bool(got),
                "attempts": 0 if got else prev.get("attempts", 0) + 1,
            }
    except BudgetExhausted:
        print("  budget reached — stopping cleanly, cursor kept")

    CACHE.mkdir(exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2), "utf-8")

    OUT.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    (OUT / f"proposals-{stamp}.json").write_text(
        json.dumps([asdict(p) for p in proposals], indent=2, ensure_ascii=False), "utf-8")

    body = [f"# Harvest {stamp}", "",
            f"`{VERSION}` · {http.spent} requests · {len(proposals)} proposals", "",
            "| Stage | Planned |", "|---|---|"]
    body += [f"| {k} | {v} |" for k, v in sorted(planned.items())]
    body += ["", "## Review checklist", "",
             "- [ ] Identity matches are the right recording, not a compilation",
             "- [ ] Barcodes belong to the edition claimed",
             "- [ ] No review text has been copied into any payload",
             "- [ ] Every score carries a locator, or it stays `draft`"]
    (OUT / "PR_BODY.md").write_text("\n".join(body), "utf-8")

    print(f"\n{http.spent} requests · {len(proposals)} proposals")
    for k, v in sorted(planned.items()):
        print(f"  {k:<10} {v:>4} queued")
    print(f"wrote {OUT}/proposals-{stamp}.json and PR_BODY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
