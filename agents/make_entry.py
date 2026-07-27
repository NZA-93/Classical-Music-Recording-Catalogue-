#!/usr/bin/env python3
"""
make_entry.py — scaffold a signed-entry stub and print a facts-only brief.

ADR-002: the brief contains no draft prose, no suggested rating, and no
sentence the author might keep. The agent assembles the ground; the author
arrives at a blank page.

    make entry
    python3 agents/make_entry.py --work shostakovich/sym5
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parents[1]
CAT = ROOT / "build" / "catalogue.json"
SEED = ROOT / "data" / "seed.json"
EDITORIAL = ROOT / "data" / "editorial"


def load(p, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def top_work(cat: dict, seed: dict) -> str:
    """Reuse editorial_queue ranking without importing its CLI."""
    sys.path.insert(0, str(ROOT / "agents"))
    import editorial_queue as eq  # noqa: E402
    recs_by_work: dict[str, list] = {}
    for w in cat.get("works", []):
        recs_by_work.setdefault(w["id"], []).extend(w["recordings"])
    best, best_need = None, -1.0
    for w in seed.get("works", []):
        need, _ = eq.score_need(w, recs_by_work.get(w["id"], []),
                                len(w.get("candidates") or []))
        if need > best_need:
            best_need, best = need, w["id"]
    return best or "shostakovich/sym5"


def brief(work_id: str, cat: dict, seed: dict) -> str:
    lines = [f"# Editorial brief — {work_id}", ""]
    lines.append("Facts only. No draft prose. No suggested stars. (ADR-002)")
    lines.append("")

    seed_work = next((w for w in seed.get("works", []) if w["id"] == work_id), None)
    cat_work = next((w for w in cat.get("works", []) if w["id"] == work_id), None)

    if seed_work:
        lines.append(f"**Work:** {seed_work['composer']} — {seed_work['title']}")
        lines.append(f"**Catalogue:** {seed_work.get('catalogue')} · {seed_work.get('year')}")
        lines.append(f"**Note:** {seed_work.get('note')}")
        lines.append("")
        lines.append("## Candidates in seed")
        for c in seed_work.get("candidates", []):
            lines.append(
                f"- `{c['id']}` · {c.get('director') or c.get('soloists')} / "
                f"{c.get('ensemble')} · {c.get('label')}, {c.get('year')} · "
                f"mbid={c.get('mbid')}"
            )
        lines.append("")

    if cat_work:
        lines.append("## Assessed recordings")
        for r in cat_work.get("recordings", []):
            lines.append(f"### `{r['id']}`")
            lines.append(f"- Director: {r.get('director')}")
            lines.append(f"- Ensemble: {r.get('ensemble')}")
            lines.append(f"- Soloists: {r.get('soloists')}")
            lines.append(f"- Published: {r.get('published')}")
            eng = r.get("engineering") or {}
            lines.append(
                f"- Credits: venue={eng.get('venue')}; sessions={eng.get('sessions')}; "
                f"producer={eng.get('producer')}; engineer={eng.get('engineer')}; "
                f"status={eng.get('status')}"
            )
            if r.get("interpretation") is not None:
                lines.append(
                    f"- Aggregate: interpretation={r['interpretation']}, "
                    f"confidence={r.get('confidence')}, stars={r.get('stars')}, "
                    f"reference={r.get('reference')}"
                )
            else:
                lines.append("- Aggregate: awaiting sources")
            lines.append("- Sources the aggregate rests on:")
            for s in r.get("sources") or []:
                lines.append(
                    f"  - {s.get('source')} · {s.get('class')} · "
                    f"{s.get('provenance')} · score={s.get('score')} · "
                    f"weight={s.get('weight')}"
                )
            lines.append("- Editions:")
            for e in r.get("editions") or []:
                lines.append(
                    f"  - `{e.get('id')}` · {e.get('label')} {e.get('catno')} "
                    f"({e.get('year')}) · barcode={e.get('barcode')} · "
                    f"verified={e.get('verified')}"
                )
            if r.get("editorial"):
                lines.append(f"- Signed entry already present: {r['editorial'].get('author')}")
            lines.append("")
        competitors = [r["id"] for r in cat_work.get("recordings", [])]
        lines.append(f"## Competing recordings on file: {', '.join(competitors) or 'none'}")
    else:
        lines.append("No assessed recordings in catalogue.json for this work yet.")

    lines.append("")
    lines.append("---")
    lines.append("Write the entry in the stub JSON. Leave `text` and `stars` blank "
                 "until you have listened. Do not ask an agent to draft them.")
    return "\n".join(lines)


def stub_path(work_id: str) -> pathlib.Path:
    return EDITORIAL / f"{work_id.replace('/', '_')}.json"


def ensure_stub(work_id: str, cat: dict) -> pathlib.Path:
    path = stub_path(work_id)
    if path.exists():
        doc = load(path, {"work_id": work_id, "entries": []})
    else:
        doc = {"work_id": work_id, "entries": []}

    # Pick top recording without a signed entry for the stub target.
    cat_work = next((w for w in cat.get("works", []) if w["id"] == work_id), None)
    target = None
    if cat_work:
        for r in cat_work["recordings"]:
            if not r.get("editorial"):
                target = r["id"]
                break
        if target is None and cat_work["recordings"]:
            target = cat_work["recordings"][0]["id"]
    if target is None:
        target = f"{work_id.replace('/', '_')}_PENDING"

    already = {e.get("recording") for e in doc.get("entries", [])}
    already |= {e.get("recording") for e in doc.get("_stubs", [])}
    if target not in already:
        doc.setdefault("_stubs", []).append({
            "recording": target,
            "author": {"id": "", "name": ""},
            "date": "",
            "revision": 1,
            "stars": None,
            "reference": False,
            "compared_with": [],
            "text": "",
            "quotes": [],
            "_created": date.today().isoformat(),
            "_note": "Fill author/date/text/stars then move into entries[]. ADR-002.",
        })
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", default=None, help="composer/work id")
    args = ap.parse_args(argv)

    cat = load(CAT, {"works": []})
    seed = load(SEED, {"works": []})
    work_id = args.work or top_work(cat, seed)
    path = ensure_stub(work_id, cat)
    print(brief(work_id, cat, seed))
    print(f"\nstub: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
