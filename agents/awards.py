#!/usr/bin/env python3
"""
awards.py — turn data/awards/*.json into proposals for human confirmation.

Awards are public facts (not copyrighted criticism). This adapter matches
covers_works + performers against catalogue recordings and emits a proposal
per match. It never writes data/statements/.

ADR-001: album awards carry covers_works on every proposal so a three-work
Grammy cannot be mistaken for three independent endorsements.

    python3 agents/awards.py
    python3 agents/awards.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from datetime import datetime, timezone
from typing import Any, Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
AWARDS = ROOT / "data" / "awards"
SEED = ROOT / "data" / "seed.json"
RECORDINGS = ROOT / "data" / "recordings"
OUT = ROOT / "proposals"

# Short own-words characterisations. Never paste promotional copy from locators.
CHAR = (
    "Award recorded as a public fact for this recording; "
    "see locator. Album coverage listed in covers_works (ADR-001)."
)


def load(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def tokens(s: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", (s or "").lower()) if len(t) > 2}


def performer_match(award_performers: str, director: str, ensemble: str,
                    soloists: str = "") -> bool:
    """Require the award string to share a substantial token with director or
    ensemble. 'Karajan, Tosca' alone is not an identification — year/label are
    checked by the caller when available."""
    want = tokens(award_performers)
    have = tokens(director) | tokens(ensemble) | tokens(soloists)
    if not want or not have:
        return False
    # Prefer surnames / distinctive tokens over stopwords like orchestra.
    stop = {"orchestra", "philharmonic", "symphony", "ensemble", "the", "and",
            "opera", "choir", "chorus", "radio"}
    want_core = want - stop
    have_core = have - stop
    if not want_core:
        want_core = want
    return bool(want_core & have_core)


def catalogue_recordings() -> list[dict]:
    """Recordings from data/recordings plus seed candidates (for works not yet
    migrated). Each item: id, work_id, director, ensemble, soloists, label, year."""
    out: list[dict] = []
    for path in sorted(RECORDINGS.glob("*/*.json")):
        doc = load(path)
        wid = doc["work_id"]
        for rec in doc.get("recordings", []):
            pub = rec.get("published") or ""
            year = ""
            m = re.search(r"(19|20)\d{2}", pub)
            if m:
                year = m.group(0)
            label = pub.split(",")[0].strip() if pub else ""
            out.append({
                "id": rec["id"],
                "work_id": wid,
                "director": rec.get("director") or "",
                "ensemble": rec.get("ensemble") or "",
                "soloists": rec.get("soloists") or "",
                "label": label,
                "year": year,
                "source": "recordings",
            })
    if SEED.exists():
        seed = load(SEED)
        known = {r["id"] for r in out}
        for work in seed.get("works", []):
            for cand in work.get("candidates", []):
                # Prefer catalogue rows when both exist for the same artists.
                cid = cand["id"]
                if cid in known:
                    continue
                out.append({
                    "id": cid,
                    "work_id": work["id"],
                    "director": cand.get("director") or "",
                    "ensemble": cand.get("ensemble") or "",
                    "soloists": cand.get("soloists") or "",
                    "label": cand.get("label") or "",
                    "year": str(cand.get("year") or ""),
                    "source": "seed",
                })
    return out


def load_awards() -> list[dict]:
    rows = []
    for path in sorted(AWARDS.glob("*.json")):
        for row in load(path):
            rows.append({**row, "_file": path.name})
    return rows


def match_award(award: dict, recordings: list[dict]) -> list[dict]:
    """Return candidate matches. Ambiguous sets are flagged, not auto-picked.
    Prefer data/recordings rows over seed candidates for the same artists."""
    works = set(award.get("covers_works") or [])
    if not works:
        return []
    year = str(award.get("year") or "")
    label = (award.get("label") or "").lower()
    hits = []
    for rec in recordings:
        if rec["work_id"] not in works:
            continue
        if not performer_match(award.get("performers") or "",
                               rec["director"], rec["ensemble"], rec["soloists"]):
            continue
        year_ok = True
        if year and rec["year"]:
            # Allow award year == release year or award year == release+1 (common).
            try:
                ry, ay = int(rec["year"][:4]), int(year[:4])
                year_ok = abs(ry - ay) <= 2
            except ValueError:
                year_ok = True
        label_ok = True
        if label and rec["label"]:
            label_ok = label.split()[0] in rec["label"].lower() or \
                       rec["label"].lower().split()[0] in label
        hits.append({
            "recording": rec,
            "year_ok": year_ok,
            "label_ok": label_ok,
            "ambiguous_risk": not (year_ok and label_ok),
        })
    # Drop seed candidates when a catalogue recording already covers the same
    # work_id + director token overlap.
    catalogue_keys = {
        (h["recording"]["work_id"],
         frozenset(tokens(h["recording"]["director"]) &
                   tokens(award.get("performers") or "")))
        for h in hits if h["recording"]["source"] == "recordings"
    }
    pruned = []
    for h in hits:
        rec = h["recording"]
        if rec["source"] == "seed":
            key = (rec["work_id"],
                   frozenset(tokens(rec["director"]) &
                             tokens(award.get("performers") or "")))
            if key in catalogue_keys:
                continue
        pruned.append(h)
    return pruned


def proposal_for(award: dict, hit: dict) -> dict:
    rec = hit["recording"]
    covers = list(award.get("covers_works") or [])
    album = len(covers) > 1
    char = CHAR
    if album:
        char = (
            f"Album award covering {len(covers)} works; recorded once per "
            f"matched recording as a shared benchmark signal (ADR-001)."
        )
    caveat = award.get("locator_caveat")
    note = award.get("note") or ""
    if caveat:
        note = (note + " " if note else "") + caveat
    return {
        "target": rec["id"],
        "kind": "award",
        "payload": {
            "recording": rec["id"],
            "work_id": rec["work_id"],
            "award": award.get("award"),
            "year": award.get("year"),
            "album": award.get("album"),
            "performers": award.get("performers"),
            "label": award.get("label"),
            "scale": "award",
            "provenance": "cited",
            "class": "major_award",
            "conflict": False,
            "axis": "interpretation",
            "locator": award.get("locator"),
            "covers_works": covers,
            "characterisation": char,
            "note": note.strip() or None,
            "needs_human_confirmation": True,
            "ambiguous_risk": hit["ambiguous_risk"],
            "match": {
                "director": rec["director"],
                "ensemble": rec["ensemble"],
                "label": rec["label"],
                "year": rec["year"],
                "year_ok": hit["year_ok"],
                "label_ok": hit["label_ok"],
            },
        },
        "source": award.get("award") or "award",
        "provenance": "cited",
        "created": datetime.now(timezone.utc).isoformat(),
    }


def run(dry_run: bool = False) -> list[dict]:
    awards = load_awards()
    recordings = catalogue_recordings()
    proposals = []
    for award in awards:
        if not award.get("locator"):
            print(f"  skip (no locator): {award.get('award')} {award.get('year')}")
            continue
        hits = match_award(award, recordings)
        if not hits:
            print(f"  no match: {award.get('award')} {award.get('year')} "
                  f"({award.get('performers')})")
            continue
        # Group by work — one proposal per (award, recording).
        for hit in hits:
            prop = proposal_for(award, hit)
            proposals.append(prop)
            flag = " AMBIGUOUS" if hit["ambiguous_risk"] else ""
            print(f"  match{flag}: {prop['target']} ← {award.get('award')} "
                  f"{award.get('year')}")
    return proposals


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", type=pathlib.Path, default=None)
    args = ap.parse_args(argv)

    proposals = run(dry_run=args.dry_run)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    out = args.out or (OUT / f"awards-{stamp}.json")
    print(f"{len(proposals)} award proposals")
    if args.dry_run:
        print(json.dumps(proposals, indent=2, ensure_ascii=False)[:2000])
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proposals, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
