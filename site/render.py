#!/usr/bin/env python3
"""render.py — sealed work pages + an entries directory. No network."""

from __future__ import annotations

import json
import pathlib
import shutil
import sys
from html import escape

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from work_href import work_anchor  # noqa: E402

ROOT = pathlib.Path(".")
DOCS = ROOT / "docs"

CATALOGUE_MARKER = "/*__CATALOGUE__*/{}"
WORK_INDEX_MARKER = "/*__WORK_INDEX__*/[]"
TITLE_MARKER = "{{TITLE}}"
BASE_MARKER = "{{BASE}}"


def work_index_row(work: dict) -> dict:
    return {
        "id": work["id"],
        "anchor": work_anchor(work["id"]),
        "title": work.get("title") or "",
        "composer": work.get("composer") or "",
        "dates": work.get("dates") or "",
        "cat": work.get("cat") or "",
        "recordings": [r["id"] for r in work.get("recordings") or []],
    }


def seal_catalogue(cat: dict, work: dict) -> dict:
    """One work, barcodes for that work only. No sibling-work payload."""
    rec_ids = {r["id"] for r in work.get("recordings") or []}
    ed_ids = {
        e["id"]
        for r in work.get("recordings") or []
        for e in r.get("editions") or []
        if e.get("id")
    }
    idx = {}
    for bc, hit in (cat.get("barcode_index") or {}).items():
        if not isinstance(hit, dict):
            continue
        if hit.get("recording") in rec_ids or hit.get("edition") in ed_ids:
            idx[bc] = hit
    drop = ("works", "barcode_index", "composers")
    out = {k: v for k, v in cat.items() if k not in drop}
    out["works"] = [work]
    out["barcode_index"] = idx
    return out


def directory_catalogue(cat: dict) -> dict:
    """Entries index: no work bodies, so it cannot feed another work."""
    drop = ("works", "barcode_index", "composers")
    out = {k: v for k, v in cat.items() if k not in drop}
    out["works"] = []
    out["barcode_index"] = {}
    return out


def apply_template(tpl: str, cat_obj: dict, index: list, *, base: str, title: str) -> str:
    if CATALOGUE_MARKER not in tpl:
        raise SystemExit("template is missing the catalogue marker")
    if WORK_INDEX_MARKER not in tpl:
        raise SystemExit("template is missing the work-index marker")
    if TITLE_MARKER not in tpl or BASE_MARKER not in tpl:
        raise SystemExit("template is missing {{TITLE}} / {{BASE}} markers")
    html = tpl.replace(CATALOGUE_MARKER, json.dumps(cat_obj, ensure_ascii=False))
    html = html.replace(WORK_INDEX_MARKER, json.dumps(index, ensure_ascii=False))
    html = html.replace(TITLE_MARKER, escape(title))
    html = html.replace(BASE_MARKER, base)
    return html


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path} ({path.stat().st_size / 1024:.0f} KB)")


def main() -> None:
    tpl_path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site/template.html")
    cat_path = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "build/catalogue.json")
    tpl = tpl_path.read_text(encoding="utf-8")
    cat = json.loads(cat_path.read_text(encoding="utf-8"))
    works = list(cat.get("works") or [])
    index = [work_index_row(w) for w in works]

    docs_works = DOCS / "works"
    if docs_works.exists():
        shutil.rmtree(docs_works)
    docs_works.mkdir(parents=True)

    for work in works:
        anchor = work_anchor(work["id"])
        title = f"{work.get('title') or anchor} — {work.get('composer') or ''}".strip(" —")
        html = apply_template(
            tpl,
            seal_catalogue(cat, work),
            [],  # sealed: no cross-work directory, no related feed
            base="../",
            title=title,
        )
        write(docs_works / f"{anchor}.html", html)

    entries = apply_template(
        tpl,
        directory_catalogue(cat),
        index,
        base="",
        title="Entries",
    )
    write(DOCS / "entries.html", entries)

    root_works = ROOT / "works"
    if root_works.exists():
        shutil.rmtree(root_works)
    shutil.copytree(docs_works, root_works)


if __name__ == "__main__":
    main()
