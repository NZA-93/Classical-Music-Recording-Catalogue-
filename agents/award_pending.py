#!/usr/bin/env python3
"""
Emit statement-shaped drafts from award proposals into
proposals/pending-statements/. Humans move confirmed rows into
data/statements/. Agents never write that tree (AGENTS.md §3).

    python3 agents/award_pending.py proposals/awards-YYYYMMDD.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "proposals" / "pending-statements"


def statement_from(prop: dict) -> dict:
    p = prop["payload"]
    return {
        "recording": p["recording"],
        "axis": "interpretation",
        "edition": None,
        "source": f"{p.get('award')}, {p.get('year')}",
        "locator": p.get("locator"),
        "scale": "award",
        "value": None,
        "class": "major_award",
        "provenance": "cited",
        "method": "human",
        "conflict": False,
        "characterisation": p.get("characterisation") or "Award recorded as a public fact.",
        "covers_works": p.get("covers_works") or [],
        "note": p.get("note"),
        "_pending": {
            "needs_human_confirmation": True,
            "ambiguous_risk": p.get("ambiguous_risk"),
            "match": p.get("match"),
            "work_id": p.get("work_id"),
        },
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("proposals", type=pathlib.Path)
    args = ap.parse_args(argv)
    props = json.loads(args.proposals.read_text(encoding="utf-8"))
    by_work: dict[str, list] = defaultdict(list)
    for prop in props:
        if prop.get("kind") != "award":
            continue
        st = statement_from(prop)
        wid = prop["payload"]["work_id"]
        by_work[wid].append(st)

    OUT.mkdir(parents=True, exist_ok=True)
    # Clear previous drafts for a clean round.
    for old in OUT.glob("*.json"):
        old.unlink()
    n = 0
    for wid, stmts in sorted(by_work.items()):
        path = OUT / (wid.replace("/", "_") + ".json")
        path.write_text(json.dumps(stmts, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        n += len(stmts)
        print(f"  {path.name}: {len(stmts)} pending")
    print(f"{n} pending statements in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
