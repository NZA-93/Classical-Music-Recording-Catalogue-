#!/usr/bin/env python3
"""
review_queue.py — build a human review queue from harvest proposals.

Buckets the current proposals file into actionable packs for a human:

  accept_eligible  — identity, auto_accept_eligible, no wrong-work flag
  needs_review     — identity with flags / low confidence (human eyes)
  reject_wrong_work — identity with wrong work: (never apply)
  citation_tasks   — citation_task rows (backlog for Role C / humans)
  awards           — award proposals if present in a separate file

Writes:
  proposals/review-queue.json          machine summary + buckets
  proposals/review/ACCEPT_ELIGIBLE.md  short list for fast pass
  proposals/review/NEEDS_REVIEW.md     flagged identity rows
  proposals/review/REJECT_WRONG_WORK.md
  proposals/review/CITATION_TASKS.md
  proposals/review-decisions.json      decision template (unless --no-init)

Decisions schema (human edits this file):

  {
    "schema": "review-decisions/1",
    "proposals": "proposals/proposals-YYYYMMDD.json",
    "decisions": [
      {"target": "bach/brandenburg/0", "kind": "identity",
       "decision": "pending"|"accept"|"reject"|"defer",
       "note": "", "by": "", "date": ""}
    ]
  }

Then apply only accepts:

  python3 agents/apply.py --proposals … --decisions proposals/review-decisions.json --dry-run
  python3 agents/apply.py --proposals … --decisions proposals/review-decisions.json

    python3 agents/review_queue.py
    python3 agents/review_queue.py --proposals proposals/proposals-20260809.json
    python3 agents/review_queue.py --no-init   # refresh packs; leave decisions alone
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone
from typing import Any, Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents"))

import review as rv  # noqa: E402

DEFAULT_PROPOSALS = ROOT / "proposals" / "proposals-20260809.json"
QUEUE_JSON = ROOT / "proposals" / "review-queue.json"
DECISIONS = ROOT / "proposals" / "review-decisions.json"
REVIEW_DIR = ROOT / "proposals" / "review"
SEED = ROOT / "data" / "seed.json"
WRONG_PREFIX = "wrong work:"

DECISION_VALUES = frozenset({"pending", "accept", "reject", "defer"})


def load(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def _is_wrong_work(flags: list[str]) -> bool:
    return any(f.startswith(WRONG_PREFIX) for f in flags)


def bucket_identity(items: list[dict]) -> dict[str, list[dict]]:
    """Assign each identity row to one pack.

    Wrong-work flags always win, including when a stale harvest payload still
    has auto_accept_eligible true. Incomplete / date / confidence flags go to
    needs-review, never accept-eligible.
    """
    accept_eligible: list[dict] = []
    needs_review: list[dict] = []
    reject_wrong: list[dict] = []
    for row in items:
        flags = list(row.get("flags") or [])
        if _is_wrong_work(flags):
            reject_wrong.append(row)
            continue
        mb = row.get("mb") or {}
        if mb.get("auto_accept_eligible") and not flags:
            accept_eligible.append(row)
            continue
        needs_review.append(row)
    return {
        "accept_eligible": accept_eligible,
        "needs_review": needs_review,
        "reject_wrong_work": reject_wrong,
    }


def live_identity_buckets(proposals: list[dict], seed: dict) -> dict[str, list[dict]]:
    """Recompute membership from the current matcher. Do not trust queue JSON."""
    return bucket_identity(rv.rows(proposals, seed))


def citation_rows(proposals: list[dict]) -> list[dict]:
    out = []
    for prop in proposals:
        if prop.get("kind") != "citation_task":
            continue
        payload = prop.get("payload") or {}
        out.append({
            "target": prop.get("target"),
            "source_hint": payload.get("source") or payload.get("suggested_source"),
            "locator_hint": payload.get("locator"),
            "note": payload.get("note") or payload.get("task") or "",
        })
    return out


def award_rows(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    data = load(path)
    if not isinstance(data, list):
        return []
    out = []
    for prop in data:
        if prop.get("kind") != "award":
            continue
        payload = prop.get("payload") or {}
        out.append({
            "target": prop.get("target"),
            "source": payload.get("source") or prop.get("source"),
            "locator": payload.get("locator") or prop.get("locator"),
            "axis": payload.get("axis") or prop.get("axis"),
        })
    return out


def render_identity_md(title: str, blurb: str, items: list[dict]) -> str:
    lines = [
        f"# {title}",
        "",
        blurb,
        "",
        f"**Count:** {len(items)}",
        "",
        "| Decision | Target | Seed | MusicBrainz | Match | Flags | MB URL |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in items:
        if row.get("missing"):
            lines.append(
                f"| pending | `{row['target']}` | — | — | — | missing | — |"
            )
            continue
        s, m = row["seed"], row["mb"]
        seed = f"{s.get('director') or s.get('soloists') or '—'}; " \
               f"{s.get('label')}, {s.get('year')}"
        mb = f"{m.get('title')} ({m.get('first_release')})"
        extras = []
        if m.get("session_year"):
            extras.append(f"session {m['session_year']}")
        if m.get("live_studio"):
            extras.append(str(m["live_studio"]))
        if extras:
            mb = f"{mb}; {'; '.join(extras)}"
        flags = "; ".join(row["flags"]) if row["flags"] else ""
        url = m.get("mb_url") or ""
        link = f"[open]({url})" if url else "—"
        lines.append(
            f"| pending | `{row['target']}` | {seed} | {mb} | "
            f"{m.get('match_score')} | {flags} | {link} |"
        )
    lines.append("")
    lines.append(
        "Edit `proposals/review-decisions.json`: set `decision` to "
        "`accept`, `reject`, or `defer`. Fill `by` (initials) and `date`."
    )
    lines.append("")
    return "\n".join(lines)


def render_citations_md(items: list[dict]) -> str:
    lines = [
        "# Citation tasks (queued)",
        "",
        "These are **tasks**, not statements. A human (or Role C with a "
        "locator) turns each into a ratified contribution — agents still "
        "must not write `data/statements/`.",
        "",
        f"**Count:** {len(items)}",
        "",
        "| Target | Source hint | Note |",
        "|---|---|---|",
    ]
    for row in items:
        note = (row.get("note") or "").replace("|", "/")
        lines.append(
            f"| `{row.get('target')}` | {row.get('source_hint') or '—'} | "
            f"{note[:120]} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_decisions_template(
    proposals_rel: str,
    buckets: dict[str, list[dict]],
    existing: Optional[dict] = None,
) -> dict:
    """Merge prior human decisions; default new rows to pending / reject."""
    prior: dict[tuple[str, str], dict] = {}
    if existing and isinstance(existing.get("decisions"), list):
        for d in existing["decisions"]:
            key = (d.get("target") or "", d.get("kind") or "identity")
            prior[key] = d

    decisions = []
    for row in buckets["reject_wrong_work"]:
        key = (row["target"], "identity")
        if key in prior and prior[key].get("decision") in DECISION_VALUES:
            decisions.append(prior[key])
        else:
            decisions.append({
                "target": row["target"],
                "kind": "identity",
                "decision": "reject",
                "note": "wrong work: pre-rejected by review_queue",
                "by": "",
                "date": "",
            })
    for row in buckets["accept_eligible"] + buckets["needs_review"]:
        key = (row["target"], "identity")
        if key in prior and prior[key].get("decision") in DECISION_VALUES:
            decisions.append(prior[key])
        else:
            decisions.append({
                "target": row["target"],
                "kind": "identity",
                "decision": "pending",
                "note": "",
                "by": "",
                "date": "",
            })
    return {
        "schema": "review-decisions/1",
        "proposals": proposals_rel,
        "updated": datetime.now(timezone.utc).isoformat(),
        "decisions": decisions,
    }


def seed_gaps(seed: dict, identity_targets: set[str]) -> dict[str, int]:
    """How much of the seed still has no identity proposal."""
    n_cand = 0
    n_with_mbid = 0
    n_proposed = 0
    for work in seed.get("works", []):
        for cand in work.get("candidates", []):
            n_cand += 1
            if cand.get("mbid"):
                n_with_mbid += 1
            if cand.get("id") in identity_targets:
                n_proposed += 1
    return {
        "candidates": n_cand,
        "with_mbid": n_with_mbid,
        "with_identity_proposal": n_proposed,
        "without_identity_proposal": n_cand - n_proposed,
    }


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--proposals", type=pathlib.Path, default=DEFAULT_PROPOSALS,
        help="Harvest proposals JSON (default: proposals/proposals-20260809.json)",
    )
    ap.add_argument(
        "--awards", type=pathlib.Path,
        default=ROOT / "proposals" / "awards-20260809.json",
        help="Optional awards proposals file",
    )
    ap.add_argument(
        "--no-init", action="store_true",
        help="Refresh markdown/JSON packs but do not write review-decisions.json",
    )
    ap.add_argument(
        "--merge-decisions", action="store_true", default=True,
        help="Preserve existing accept/reject/defer when re-initing (default)",
    )
    args = ap.parse_args(argv)

    if not args.proposals.exists():
        print(f"not found: {args.proposals}", file=sys.stderr)
        return 2

    proposals = load(args.proposals)
    if not isinstance(proposals, list):
        print("proposals file must be a JSON array", file=sys.stderr)
        return 2

    seed = load(SEED) if SEED.exists() else {"works": []}
    identity_items = rv.rows(proposals, seed)
    buckets = bucket_identity(identity_items)
    citations = citation_rows(proposals)
    awards = award_rows(args.awards)

    identity_targets = {r["target"] for r in identity_items if r.get("target")}
    gaps = seed_gaps(seed, identity_targets)

    try:
        proposals_rel = str(args.proposals.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        proposals_rel = str(args.proposals)

    summary = {
        "schema": "review-queue/1",
        "created": datetime.now(timezone.utc).isoformat(),
        "proposals": proposals_rel,
        "counts": {
            "identity_total": len(identity_items),
            "accept_eligible": len(buckets["accept_eligible"]),
            "needs_review": len(buckets["needs_review"]),
            "reject_wrong_work": len(buckets["reject_wrong_work"]),
            "citation_tasks": len(citations),
            "awards": len(awards),
            **gaps,
        },
        "buckets": {
            name: [r["target"] for r in rows_]
            for name, rows_ in buckets.items()
        },
        "citation_targets": [c["target"] for c in citations if c.get("target")],
    }
    write_json(QUEUE_JSON, summary)

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    (REVIEW_DIR / "ACCEPT_ELIGIBLE.md").write_text(
        render_identity_md(
            "Accept-eligible identity matches",
            "High-confidence MusicBrainz matches with no review flags. "
            "Still require a human `accept` in `review-decisions.json` "
            "before `apply.py` — the machine does not write mbids alone.",
            buckets["accept_eligible"],
        ),
        encoding="utf-8",
    )
    (REVIEW_DIR / "NEEDS_REVIEW.md").write_text(
        render_identity_md(
            "Identity matches needing human review",
            "Flagged rows (date drift, low confidence, compilation-like "
            "titles, etc.). Open the MusicBrainz URL before accepting. "
            "Never accept a wrong-work match.",
            buckets["needs_review"],
        ),
        encoding="utf-8",
    )
    (REVIEW_DIR / "REJECT_WRONG_WORK.md").write_text(
        render_identity_md(
            "Wrong-work matches (never apply)",
            "Pre-marked `reject` in the decisions file. `apply.py` refuses "
            "these even with `--force`.",
            buckets["reject_wrong_work"],
        ),
        encoding="utf-8",
    )
    (REVIEW_DIR / "CITATION_TASKS.md").write_text(
        render_citations_md(citations),
        encoding="utf-8",
    )

    # Full identity table for the existing path humans already open.
    (ROOT / "proposals" / "IDENTITY_REVIEW.md").write_text(
        rv.render_markdown(identity_items) + "\n",
        encoding="utf-8",
    )

    if not args.no_init:
        existing = load(DECISIONS) if DECISIONS.exists() else None
        tmpl = build_decisions_template(proposals_rel, buckets, existing)
        write_json(DECISIONS, tmpl)

    c = summary["counts"]
    print("# Review queue")
    print()
    print(f"Proposals: `{proposals_rel}`")
    print()
    print("| Bucket | Count |")
    print("|---|---:|")
    for key in (
        "accept_eligible", "needs_review", "reject_wrong_work",
        "citation_tasks", "awards", "candidates", "with_mbid",
        "with_identity_proposal", "without_identity_proposal",
    ):
        print(f"| {key} | {c[key]} |")
    print()
    print(f"Wrote `{QUEUE_JSON.relative_to(ROOT)}`")
    print(f"Wrote packs under `{REVIEW_DIR.relative_to(ROOT)}/`")
    if not args.no_init:
        print(f"Wrote `{DECISIONS.relative_to(ROOT)}` "
              f"({len(load(DECISIONS)['decisions'])} decisions)")
    print()
    print("Next: edit decisions → `make review-apply-dry` → `make review-apply`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
