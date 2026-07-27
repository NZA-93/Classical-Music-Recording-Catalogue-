#!/usr/bin/env python3
"""
covers_report.py — record Cover Art Archive hits and misses.

Misses are contribution prompts, not failures. Images are never downloaded;
readers who photograph a sleeve should contribute upstream to MusicBrainz /
the Cover Art Archive.

    python3 agents/covers_report.py
"""

from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "seed.json"
OUT = ROOT / "build" / "covers.json"


def main() -> int:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    hits, misses = [], []
    for w in seed.get("works", []):
        for c in w.get("candidates", []):
            row = {
                "id": c["id"],
                "work_id": w["id"],
                "mbid": c.get("mbid"),
                "image": c.get("image"),
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }
            if c.get("image"):
                hits.append(row)
            elif c.get("mbid"):
                misses.append({
                    **row,
                    "prompt": (
                        "No front cover in the Cover Art Archive for this "
                        "release-group. Photograph the sleeve and add it at "
                        "https://musicbrainz.org — not in this repository."
                    ),
                })
            else:
                misses.append({**row, "prompt": "Resolve identity (mbid) before asking for a cover."})

    doc = {
        "hits": hits,
        "misses": misses,
        "totals": {"hits": len(hits), "misses": len(misses)},
        "policy": "Hotlink Cover Art Archive only. Never download or commit images.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"covers: {len(hits)} hits · {len(misses)} misses · wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
