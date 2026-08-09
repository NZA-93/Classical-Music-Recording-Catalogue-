#!/usr/bin/env python3
"""catalogue_loop.py — measure progress toward 10 composers · 100 works · 500 recordings.

Facts-only seed metrics. Exit 0 when all floors are met; exit 1 with a gap
report otherwise. Used by `make targets` to drive the expansion loop.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "seed.json"

TARGETS = {
    "composers": 10,
    "works": 100,
    "recordings": 500,  # seed candidates (identity queue), not assessed rows
}


def load_seed() -> dict:
    return json.loads(SEED.read_text(encoding="utf-8"))


def measure(seed: dict) -> dict:
    n_comp = len(seed.get("composers") or [])
    totals = seed.get("totals") or {}
    n_works = int(totals.get("works") or len(seed.get("works") or []))
    n_rec = int(totals.get("candidates") or 0)
    if not n_rec:
        n_rec = sum(len(w.get("candidates") or []) for w in seed.get("works") or [])
    empty = sum(1 for w in seed.get("works") or [] if not w.get("candidates"))
    thin = sum(1 for w in seed.get("works") or [] if len(w.get("candidates") or []) < 3)
    mbid = sum(
        1
        for w in seed.get("works") or []
        for c in w.get("candidates") or []
        if c.get("mbid")
    )
    return {
        "composers": n_comp,
        "works": n_works,
        "recordings": n_rec,
        "works_without_candidates": empty,
        "works_with_under_3_candidates": thin,
        "candidates_with_mbid": mbid,
    }


def gaps(m: dict) -> dict:
    return {k: max(0, TARGETS[k] - m[k]) for k in TARGETS}


def met(m: dict) -> bool:
    return all(m[k] >= TARGETS[k] for k in TARGETS)


def render(m: dict) -> str:
    g = gaps(m)
    lines = [
        "# Catalogue targets",
        "",
        f"| Metric | Have | Target | Gap |",
        f"|---|---:|---:|---:|",
        f"| Composers | {m['composers']} | {TARGETS['composers']} | {g['composers']} |",
        f"| Works | {m['works']} | {TARGETS['works']} | {g['works']} |",
        f"| Candidate recordings | {m['recordings']} | {TARGETS['recordings']} | {g['recordings']} |",
        "",
        f"Works with 0 candidates: {m['works_without_candidates']}",
        f"Works with <3 candidates: {m['works_with_under_3_candidates']}",
        f"Candidates with MusicBrainz mbid: {m['candidates_with_mbid']}",
        "",
    ]
    if met(m):
        lines += [
            "**Floor met.** Run identity harvest + human review; keep densifying "
            "and citing toward coverage quality.",
            "",
        ]
    else:
        lines += [
            "**Floor not met.** Next actions:",
            "",
        ]
        if g["composers"]:
            lines.append(
                f"- Add {g['composers']} composer(s) from "
                "`proposals/composer-queue.json` (Role A)."
            )
        if g["works"]:
            lines.append(
                f"- Add {g['works']} work(s) to reach ≥{TARGETS['works']} "
                "(~10–12 per new composer)."
            )
        if g["recordings"]:
            lines.append(
                f"- Densify candidates by {g['recordings']} "
                "(prefer `engine/seed_candidates_dense.py`; facts only)."
            )
        lines.append("- Then: `make seed && make test && make site`.")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="machine-readable status")
    ap.add_argument("--write", type=pathlib.Path,
                    help="write the markdown report to this path")
    args = ap.parse_args(argv)

    seed = load_seed()
    m = measure(seed)
    ok = met(m)
    if args.json:
        print(json.dumps({"targets": TARGETS, "have": m, "gaps": gaps(m),
                          "met": ok}, indent=2))
    else:
        text = render(m)
        print(text)
        if args.write:
            args.write.write_text(text, encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
