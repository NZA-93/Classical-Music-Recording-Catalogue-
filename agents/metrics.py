#!/usr/bin/env python3
"""
metrics.py — citation ratio and coverage into build/metrics.json.

    python3 agents/metrics.py
"""

from __future__ import annotations

import json
import os
import pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
CAT = ROOT / "build" / "catalogue.json"
SEED = ROOT / "data" / "seed.json"
STATEMENTS = ROOT / "data" / "statements"
EDITORIAL = ROOT / "data" / "editorial"
OUT = ROOT / "build" / "metrics.json"


def load(p, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def main() -> int:
    seed = load(SEED, {"works": [], "totals": {}})
    cat = load(CAT, {"works": [], "barcode_index": {}})

    stmts = []
    for path in STATEMENTS.rglob("*.json"):
        if path.name.startswith("_"):
            continue
        data = load(path, [])
        if isinstance(data, list):
            stmts.extend(data)

    interp = [s for s in stmts if s.get("axis") == "interpretation"]
    sound = [s for s in stmts if s.get("axis") == "sound"]
    prov = Counter(s.get("provenance", "draft") for s in interp)
    cited = prov.get("cited", 0)
    citation_ratio = (cited / len(interp)) if interp else 0.0

    n_rec = sum(len(w.get("recordings", [])) for w in cat.get("works", []))
    n_editions = sum(len(r.get("editions", []))
                     for w in cat.get("works", []) for r in w.get("recordings", []))
    n_barcodes = len(cat.get("barcode_index") or {})
    n_sound = sum(
        1 for w in cat.get("works", []) for r in w.get("recordings", [])
        for e in r.get("editions", []) if e.get("sound") is not None
    )
    signed = 0
    for path in EDITORIAL.glob("*.json"):
        if path.name.startswith("_"):
            continue
        doc = load(path, {"entries": []})
        for ent in doc.get("entries", []):
            author = ent.get("author") or {}
            if author.get("id") and ent.get("date") and ent.get("revision") and ent.get("text"):
                signed += 1

    metrics = {
        "works": seed.get("totals", {}).get("works", len(seed.get("works", []))),
        "candidates": seed.get("totals", {}).get("candidates", 0),
        "recordings_assessed": n_rec,
        "interpretation_statements": len(interp),
        "cited_interpretation": cited,
        "citation_ratio": round(citation_ratio, 4),
        "sound_statements": len(sound),
        "editions": n_editions,
        "editions_per_recording": round(n_editions / n_rec, 2) if n_rec else 0,
        "barcodes": n_barcodes,
        "barcode_coverage": round(n_barcodes / n_editions, 4) if n_editions else 0,
        "editions_with_sound": n_sound,
        "sound_coverage": round(n_sound / n_editions, 4) if n_editions else 0,
        "signed_entries": signed,
        "provenance_breakdown": dict(prov),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"wrote {OUT}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        pathlib.Path(summary).write_text(
            "## Catalogue metrics\n\n"
            f"- Citation ratio: **{metrics['citation_ratio']:.0%}** "
            f"({metrics['cited_interpretation']}/{metrics['interpretation_statements']})\n"
            f"- Editions: {metrics['editions']} · barcodes: {metrics['barcodes']}\n"
            f"- Signed entries: {metrics['signed_entries']}\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
