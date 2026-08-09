#!/usr/bin/env python3
"""
review.py — human-readable side-by-side of harvest identity proposals.

Prints each identity proposal: candidate as seeded vs MusicBrainz match.
Flags confidence / match_score < 80, first-release date more than three years
off, or a title containing compilation keywords.

    python3 agents/review.py proposals/proposals-YYYYMMDD.json
    python3 agents/review.py proposals/proposals-YYYYMMDD.json --markdown
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any, Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "seed.json"

COMPILATION_RE = re.compile(
    r"\b(best of|collection|anthology|sampler|highlights)\b",
    re.IGNORECASE,
)

IDENTITY_MIN_CONFIDENCE = 80


def load(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def index_candidates(seed: dict) -> dict[str, tuple[dict, dict]]:
    out = {}
    for work in seed.get("works", []):
        for cand in work.get("candidates", []):
            out[cand["id"]] = (work, cand)
    return out


def _confidence(payload: dict) -> Optional[int]:
    for key in ("confidence", "match_score"):
        if payload.get(key) is not None:
            return int(payload[key])
    return None


def flags_for(cand: dict, payload: dict) -> list[str]:
    # Prefer flags already computed by harvest/1.1+
    embedded = payload.get("review_flags")
    if isinstance(embedded, list) and embedded:
        return list(embedded)

    flags = []
    score = _confidence(payload)
    if score is not None and score < IDENTITY_MIN_CONFIDENCE:
        flags.append(f"match_score {score} < {IDENTITY_MIN_CONFIDENCE}")
    want = str(cand.get("year") or "")[:4]
    got = str(payload.get("mb_first_release") or "")[:4]
    if want.isdigit() and got.isdigit():
        delta = abs(int(want) - int(got))
        if delta > 3:
            flags.append(f"date off by {delta} years ({want} vs {got})")
    title = payload.get("mb_title") or ""
    if COMPILATION_RE.search(title):
        flags.append(f"compilation-like title: {title!r}")
    return flags


def rows(proposals: list[dict], seed: dict) -> list[dict]:
    idx = index_candidates(seed)
    out = []
    for prop in proposals:
        if prop.get("kind") != "identity":
            continue
        target = prop.get("target")
        work, cand = idx.get(target, (None, None))
        payload = prop.get("payload") or {}
        if cand is None:
            out.append({
                "target": target,
                "missing": True,
                "flags": ["target not in seed"],
                "payload": payload,
            })
            continue
        out.append({
            "target": target,
            "missing": False,
            "work": f'{work.get("composer")} — {work.get("title")}',
            "seed": {
                "director": cand.get("director"),
                "ensemble": cand.get("ensemble"),
                "soloists": cand.get("soloists"),
                "label": cand.get("label"),
                "year": cand.get("year"),
            },
            "mb": {
                "mbid": payload.get("mbid"),
                "title": payload.get("mb_title"),
                "first_release": payload.get("mb_first_release"),
                "match_score": _confidence(payload),
                "auto_accept_eligible": payload.get("auto_accept_eligible"),
                "mb_url": payload.get("mb_url"),
            },
            "flags": flags_for(cand, payload),
        })
    return out


def render_text(items: list[dict]) -> str:
    lines = []
    flagged = sum(1 for i in items if i.get("flags"))
    lines.append(f"Identity review · {len(items)} proposals · {flagged} flagged")
    lines.append("")
    for i, row in enumerate(items, 1):
        flag = " FLAG" if row.get("flags") else ""
        lines.append(f"{i}. {row['target']}{flag}")
        if row.get("missing"):
            lines.append(f"   MISSING from seed: {row['flags']}")
            continue
        lines.append(f"   work:  {row['work']}")
        s, m = row["seed"], row["mb"]
        lines.append(
            f"   seed:  {s.get('director') or s.get('soloists') or '—'} / "
            f"{s.get('ensemble') or '—'} · {s.get('label')}, {s.get('year')}"
        )
        lines.append(
            f"   mb:    {m.get('title')!r} · first {m.get('first_release')} · "
            f"score {m.get('match_score')} · {m.get('mbid')}"
        )
        if m.get("auto_accept_eligible") is False:
            lines.append("   auto_accept_eligible: no")
        for f in row["flags"]:
            lines.append(f"   !! {f}")
        lines.append("")
    return "\n".join(lines)


def render_markdown(items: list[dict]) -> str:
    lines = [
        "# Identity review",
        "",
        f"{len(items)} identity proposals · "
        f"{sum(1 for i in items if i.get('flags'))} flagged",
        "",
        "| Target | Seed | MusicBrainz | Score | Eligible | Flags |",
        "|---|---|---|---|---|---|",
    ]
    for row in items:
        if row.get("missing"):
            lines.append(f"| `{row['target']}` | — | — | — | — | missing |")
            continue
        s, m = row["seed"], row["mb"]
        seed = f"{s.get('director') or s.get('soloists') or '—'}; " \
               f"{s.get('label')}, {s.get('year')}"
        mb = f"{m.get('title')} ({m.get('first_release')})"
        flags = "; ".join(row["flags"]) if row["flags"] else ""
        elig = "yes" if m.get("auto_accept_eligible") else "no"
        lines.append(
            f"| `{row['target']}` | {seed} | {mb} | {m.get('match_score')} | "
            f"{elig} | {flags} |"
        )
    lines.append("")
    lines.append(
        f"Reject anything flagged. Do not auto-accept below "
        f"{IDENTITY_MIN_CONFIDENCE}."
    )
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("proposals", type=pathlib.Path)
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args(argv)

    if not args.proposals.exists():
        print(f"not found: {args.proposals}", file=sys.stderr)
        return 2
    proposals = load(args.proposals)
    seed = load(SEED) if SEED.exists() else {"works": []}
    items = rows(proposals if isinstance(proposals, list) else [], seed)
    text = render_markdown(items) if args.markdown else render_text(items)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
