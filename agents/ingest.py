#!/usr/bin/env python3
"""
ingest.py — validated contributions into data/statements/.

Human-run only. Derives provenance from evidence (never the declared field),
stamps method and ingested_at, refuses anything validate.py rejects, and
dedupes on (recording, source, locator).

Prose contributions (value null) are kept visible and unscored — correct.

    python3 agents/ingest.py contributions/nza93-noseda-sym5.json --dry-run
    python3 agents/ingest.py contributions/nza93-noseda-sym5.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Optional

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from validate import (  # noqa: E402
    earned_tier, known_ids, validate, CONTRIB,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATEMENTS = ROOT / "data" / "statements"
SEED = ROOT / "data" / "seed.json"


def load(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def work_id_for(recording: str, seed: dict) -> Optional[str]:
    """Map a recording id to composer/work for the statements path."""
    # Catalogue ids: shostakovich_sym5_noseda → look up via catalogue or seed.
    cat = ROOT / "build" / "catalogue.json"
    if cat.exists():
        doc = load(cat)
        for w in doc.get("works", []):
            for r in w.get("recordings", []):
                if r["id"] == recording:
                    return w["id"]
    # Seed candidate ids: composer/work/N
    parts = recording.rsplit("/", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0]
    # Heuristic: shostakovich_sym5_* → shostakovich/sym5 from seed works
    for w in seed.get("works", []):
        wid = w["id"]  # composer/work
        slug = wid.replace("/", "_")
        if recording.startswith(slug + "_") or recording == slug:
            return wid
    return None


def dedupe_key(st: dict) -> tuple:
    return (st.get("recording"), st.get("source"), st.get("locator"))


def statement_path(work_id: str) -> pathlib.Path:
    return STATEMENTS / f"{work_id}.json"


def ingest_one(c: dict, path: pathlib.Path, seed: dict, recs: set, eds: set,
               dry_run: bool, log: list) -> bool:
    errs, warns = validate(c, path, recs, eds)
    if errs:
        for e in errs:
            log.append({"action": "rejected", "error": e})
        return False

    recording = c["recording"]
    wid = work_id_for(recording, seed)
    if not wid:
        log.append({"action": "rejected", "error": f"cannot map {recording} to a work"})
        return False

    tier = earned_tier(c)
    row = {
        "recording": recording,
        "axis": c["axis"],
        "edition": c.get("edition"),
        "source": c["source"],
        "locator": c.get("locator"),
        "scale": c.get("scale"),
        "value": c.get("value"),
        "class": c.get("class") or (
            "reader contribution" if c.get("method") == "human" else "independent critic"
        ),
        "provenance": tier,
        "method": c.get("method") or "human",
        "conflict": bool(c.get("conflict", False)),
        "characterisation": c["characterisation"],
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "covers_works": c.get("covers_works"),
    }
    # Drop null covers_works for cleanliness
    if not row["covers_works"]:
        row.pop("covers_works", None)

    sp = statement_path(wid)
    existing = load(sp) if sp.exists() else []
    if not isinstance(existing, list):
        log.append({"action": "rejected", "error": f"{sp} is not a list"})
        return False

    key = dedupe_key(row)
    if any(dedupe_key(e) == key for e in existing):
        log.append({"action": "duplicate", "recording": recording,
                    "source": row["source"], "locator": row.get("locator")})
        return False

    unscored = row.get("scale") == "prose" or row.get("value") is None and \
        row.get("scale") not in ("award", "editors_choice", "rosette")
    existing.append(row)
    if not dry_run:
        write(sp, existing)
    log.append({
        "action": "ingested" if not dry_run else "would_ingest",
        "path": str(sp),
        "recording": recording,
        "provenance": tier,
        "unscored_prose": bool(unscored and row.get("scale") == "prose"),
    })
    return True


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("contributions", nargs="+", type=pathlib.Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    seed = load(SEED) if SEED.exists() else {"works": []}
    recs, eds = known_ids()
    log: list = []
    n_ok = 0
    for path in args.contributions:
        data = load(path)
        items = data if isinstance(data, list) else [data]
        for item in items:
            if ingest_one(item, path, seed, recs, eds, args.dry_run, log):
                n_ok += 1

    for entry in log:
        print(f"  {entry['action']}: {entry}")
    print(f"{n_ok} statements {'would be ' if args.dry_run else ''}ingested · "
          f"{sum(1 for e in log if e['action']=='duplicate')} duplicates · "
          f"{sum(1 for e in log if e['action']=='rejected')} rejected")
    # Surface unscored prose clearly
    for entry in log:
        if entry.get("unscored_prose"):
            print(f"  note: {entry['recording']} prose kept unscored until a human assigns a number")
    return 0 if not any(e["action"] == "rejected" for e in log) else 1


if __name__ == "__main__":
    raise SystemExit(main())
