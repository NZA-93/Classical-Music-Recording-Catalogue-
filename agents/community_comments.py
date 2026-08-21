#!/usr/bin/env python3
"""
community_comments.py — public review comments, kept off the editorial layer.

Community notes support authoring (identity hints, discographic tips) but
**never** enter aggregation, statements, or signed editorial entries.

Store: data/community/comments.json

    python3 agents/community_comments.py list
    python3 agents/community_comments.py validate
    python3 agents/community_comments.py add --target bach/brandenburg/0 \
        --author github:alice --body "Check the 1982 Archiv RG, not the later box."

Schema community-comment/1:
  id, target, kind (identity_review|citation_hint|general),
  author (github:<login> or display string), created, body, layer="community"
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
STORE = ROOT / "data" / "community" / "comments.json"
SEED = ROOT / "data" / "seed.json"

MAX_BODY = 500
KINDS = frozenset({"identity_review", "citation_hint", "general"})
# Community must not smuggle score claims into the catalogue path.
SCORE_CLAIM_RE = re.compile(
    r"\b(score|stars?|référence|reference recording|rating)\s*[:=]?\s*\d",
    re.IGNORECASE,
)


def load_store() -> dict:
    if not STORE.exists():
        return {
            "schema": "community-comments/1",
            "layer": "community",
            "note": (
                "Public comments supporting review/authoring. "
                "Never mixed into data/editorial/ or data/statements/."
            ),
            "comments": [],
        }
    return json.loads(STORE.read_text(encoding="utf-8"))


def write_store(doc: dict) -> None:
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")


def candidate_ids(seed: dict) -> set[str]:
    out = set()
    for work in seed.get("works", []):
        for cand in work.get("candidates", []):
            if cand.get("id"):
                out.add(cand["id"])
        if work.get("id"):
            out.add(work["id"])
    return out


def validate_comment(c: dict, known: set[str]) -> list[str]:
    errs = []
    if c.get("layer") != "community":
        errs.append("layer must be 'community' (fence from editorial)")
    if c.get("kind") not in KINDS:
        errs.append(f"kind must be one of {sorted(KINDS)}")
    if not c.get("id"):
        errs.append("missing id")
    if not c.get("target"):
        errs.append("missing target")
    elif known and c["target"] not in known:
        # Allow work-level targets and candidate ids.
        errs.append(f"unknown target `{c['target']}`")
    author = c.get("author") or ""
    if not author:
        errs.append("missing author")
    body = c.get("body") or ""
    if not body.strip():
        errs.append("empty body")
    if len(body) > MAX_BODY:
        errs.append(f"body {len(body)} chars; max {MAX_BODY}")
    if SCORE_CLAIM_RE.search(body):
        errs.append(
            "body looks like a score/rating claim — community comments "
            "cannot set catalogue scores"
        )
    return errs


def validate_store(doc: dict, seed: Optional[dict] = None) -> list[str]:
    errs = []
    if doc.get("schema") != "community-comments/1":
        errs.append("schema must be community-comments/1")
    if doc.get("layer") != "community":
        errs.append("store layer must be community")
    known = candidate_ids(seed or {}) if seed is not None else set()
    for i, c in enumerate(doc.get("comments") or []):
        for e in validate_comment(c, known):
            errs.append(f"comments[{i}]: {e}")
    return errs


def add_comment(*, target: str, author: str, body: str,
                kind: str = "identity_review") -> dict:
    seed = json.loads(SEED.read_text(encoding="utf-8")) if SEED.exists() else {}
    doc = load_store()
    row = {
        "id": str(uuid.uuid4()),
        "schema": "community-comment/1",
        "layer": "community",
        "kind": kind,
        "target": target,
        "author": author,
        "created": datetime.now(timezone.utc).isoformat(),
        "body": body.strip(),
    }
    errs = validate_comment(row, candidate_ids(seed))
    if errs:
        raise ValueError("; ".join(errs))
    doc.setdefault("comments", []).append(row)
    write_store(doc)
    return row


def comments_for(target: str, doc: Optional[dict] = None) -> list[dict]:
    doc = doc or load_store()
    return [c for c in doc.get("comments") or [] if c.get("target") == target]


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="print all community comments")
    sub.add_parser("validate", help="validate the community store")

    add_p = sub.add_parser("add", help="append one community comment")
    add_p.add_argument("--target", required=True)
    add_p.add_argument("--author", required=True,
                       help="github:<login> or display name")
    add_p.add_argument("--body", required=True)
    add_p.add_argument("--kind", default="identity_review", choices=sorted(KINDS))

    args = ap.parse_args(argv)
    if args.cmd == "list":
        doc = load_store()
        for c in doc.get("comments") or []:
            print(f"{c.get('created', '')[:19]}  {c.get('target')}  "
                  f"{c.get('author')}: {c.get('body')}")
        print(f"\n{(len(doc.get('comments') or []))} comments · layer=community")
        return 0

    if args.cmd == "validate":
        seed = json.loads(SEED.read_text(encoding="utf-8")) if SEED.exists() else {}
        errs = validate_store(load_store(), seed)
        for e in errs:
            print(f"  ERROR  {e}")
        print(f"{len(errs)} error{'s' if len(errs) != 1 else ''}")
        return 1 if errs else 0

    if args.cmd == "add":
        try:
            row = add_comment(
                target=args.target, author=args.author,
                body=args.body, kind=args.kind,
            )
        except ValueError as exc:
            print(f"refused: {exc}", file=sys.stderr)
            return 2
        print(f"added {row['id']} on {row['target']}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
