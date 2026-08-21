#!/usr/bin/env python3
"""
ingest_community_issue.py — turn a GitHub issue form into a community comment.

Reads the issue body (GitHub issue-form markdown) from a file or stdin,
appends to data/community/comments.json. Never touches editorial/statements.

    python3 agents/ingest_community_issue.py --body-file /tmp/issue.md
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Optional

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import community_comments as cc  # noqa: E402


FIELD_RE = re.compile(
    r"###\s+(?P<name>[^\n]+)\s*\n\s*(?P<value>.*?)(?=\n###|\Z)",
    re.DOTALL,
)


def parse_issue_body(text: str) -> dict[str, str]:
    fields = {}
    for m in FIELD_RE.finditer(text or ""):
        name = m.group("name").strip().lower()
        value = m.group("value").strip()
        if value == "_No response_":
            value = ""
        fields[name] = value
    return fields


def map_fields(fields: dict[str, str]) -> dict[str, str]:
    target = fields.get("target id") or fields.get("target") or ""
    kind = fields.get("kind") or "identity_review"
    body = fields.get("comment") or fields.get("body") or ""
    login = fields.get("your github login") or fields.get("github login") or ""
    author = f"github:{login.lstrip('@')}" if login else ""
    return {
        "target": target.strip(),
        "kind": kind.strip(),
        "body": body.strip(),
        "author": author,
    }


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--body-file", type=pathlib.Path, required=True)
    ap.add_argument("--author-fallback", default="",
                    help="github login if the form field is empty")
    args = ap.parse_args(argv)

    text = args.body_file.read_text(encoding="utf-8")
    mapped = map_fields(parse_issue_body(text))
    if not mapped["author"] and args.author_fallback:
        mapped["author"] = f"github:{args.author_fallback.lstrip('@')}"
    try:
        row = cc.add_comment(
            target=mapped["target"],
            author=mapped["author"],
            body=mapped["body"],
            kind=mapped["kind"] or "identity_review",
        )
    except ValueError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    print(row["id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
