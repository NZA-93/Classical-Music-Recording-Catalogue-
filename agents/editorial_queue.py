#!/usr/bin/env python3
"""
editorial_queue.py — where one paragraph is worth the most.

The machine cannot write the entry (ADR-002). It can decide where the entry is
worth writing, which in a catalogue of this size is most of the editorial
labour. A work where the sources disagree, where a dozen versions compete and
where nobody has yet said anything decisive is exactly where one listener's
paragraph outweighs fifty citations.

    python3 agents/editorial_queue.py            # top 12
    python3 agents/editorial_queue.py --all --markdown
"""

from __future__ import annotations

import argparse
import json
import pathlib

CAT = pathlib.Path("build/catalogue.json")
SEED = pathlib.Path("data/seed.json")


def load(p, default):
    try:
        return json.loads(p.read_text("utf-8"))
    except FileNotFoundError:
        return default


def score_need(work: dict, recs: list[dict], candidates: int) -> tuple[float, list[str]]:
    """Higher means: write here first. Reasons are returned so the ranking can
    be argued with rather than trusted."""
    need, why = 0.0, []

    signed = sum(1 for r in recs if r.get("editorial"))
    if signed == 0:
        need += 4.0
        why.append("nothing signed")

    assessed = [r for r in recs if r.get("interpretation") is not None]
    if not assessed:
        need += 3.0
        why.append("no aggregate either — the guide currently says nothing")
    else:
        conf = sum(r["confidence"] for r in assessed) / len(assessed)
        if conf < 0.55:
            need += 3.0
            why.append(f"weak consensus (confidence {conf:.2f})")
        elif conf < 0.70:
            need += 1.5
            why.append(f"middling consensus (confidence {conf:.2f})")

        spread = [r["interpretation"] for r in assessed]
        if len(spread) > 1 and (max(spread) - min(spread)) < 0.12:
            need += 2.0
            why.append("scores bunched — the algorithm cannot separate them, a listener can")

    if candidates >= 6:
        need += 2.0
        why.append(f"{candidates} versions competing")
    elif candidates >= 3:
        need += 1.0
        why.append(f"{candidates} versions competing")

    diverging = [r for r in recs if r.get("divergence")]
    if diverging:
        need += 2.5
        why.append("signed and aggregate already disagree — worth extending")

    return need, why


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=12)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args()

    cat, seed = load(CAT, {"works": []}), load(SEED, {"works": []})
    # The hardcoded entries predate the data loader and use underscored ids.
    # Until S2-01 completes, map them; otherwise assessed works look unassessed
    # and the queue sends the author somewhere already covered.
    ALIAS = {"bach_brandenburg": "bach/brandenburg", "puccini_tosca": "puccini/tosca"}
    recs_by_work: dict[str, list] = {}
    titles: dict[str, str] = {}
    for w in cat["works"]:
        wid = ALIAS.get(w["id"], w["id"])
        recs_by_work.setdefault(wid, []).extend(w["recordings"])
        titles[wid] = f'{w["composer"]} — {w["title"]}'

    rows = []
    for w in seed["works"]:
        wid = w["id"]
        recs = recs_by_work.get(wid, [])
        need, why = score_need(w, recs, len(w["candidates"]) or len(recs))
        rows.append((need, titles.get(wid, f'{w["composer"]} — {w["title"]}'), wid, why))
    rows.sort(key=lambda r: -r[0])

    rows = rows if args.all else rows[: args.n]

    if args.markdown:
        print("| # | Work | Need | Why |")
        print("|---|---|---|---|")
        for i, (need, title, wid, why) in enumerate(rows, 1):
            print(f"| {i} | {title} | {need:.1f} | {'; '.join(why)} |")
    else:
        print("Where a signed entry is worth the most\n")
        for i, (need, title, wid, why) in enumerate(rows, 1):
            print(f"{i:>2}. {title}   [{need:.1f}]")
            for reason in why:
                print(f"      · {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
