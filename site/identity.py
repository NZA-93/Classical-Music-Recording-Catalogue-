"""Identity-only public pages from seed.works[].assessed.

The critic-signed assessed IDs are who may appear on a public card. Engine
scores and the harvest candidate queue are not. A first-slice enable list
gates which assessed works get a Pages file, so later apply PRs can turn
more works on without new plumbing.

No aggregate scores, engine stars, Référence, or statements belong here.
A Critic-signed entry from data/editorial/ attaches when present (ADR-002).
"""

from __future__ import annotations

import json
import pathlib
import sys

_SITE = pathlib.Path(__file__).resolve().parent
_ROOT = _SITE.parent
if str(_SITE) not in sys.path:
    sys.path.insert(0, str(_SITE))

from work_href import composer_id_of, work_anchor  # noqa: E402

# Works that may emit identity-only public pages this slice. Content is
# always the work's assessed IDs; add a work id here to publish it.
# Goldberg stays on ( /0, /1, /4 — seed.assessed excludes /3 Perahia ).
FIRST_SLICE_WORKS = frozenset({
    "bach/goldberg",
    "bach/cello_suites",
    "bach/violin_concertos",
    "bach/sonatas_partitas",
    "bach/matthew",
    "bach/john",
    "bach/mass_b_minor",
    "bach/art_of_fugue",
})


def published_line(candidate: dict) -> str:
    label = str(candidate.get("label") or "").strip()
    year = str(candidate.get("year") or "").strip()
    if label and year:
        return f"{label}, {year}"
    return label or year


def load_signed_editorial(root: pathlib.Path | None = None) -> dict[str, dict]:
    """Signed entries keyed by recording id. Unsigned prose does not publish."""
    data = pathlib.Path(root) if root is not None else _ROOT / "data"
    out: dict[str, dict] = {}
    ed_dir = data / "editorial"
    if not ed_dir.is_dir():
        return out
    for path in sorted(ed_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        for ent in doc.get("entries") or []:
            if not (ent.get("author") and ent.get("date") and ent.get("revision")):
                continue
            rid = ent.get("recording")
            if rid:
                out[rid] = ent
    return out


def identity_recording(
    work_id: str, candidate: dict, editorial: dict | None = None
) -> dict:
    """Facts already on the seed candidate. Nothing scored by the engine."""
    return {
        "id": candidate["id"],
        "work": work_id,
        "card": "identity",
        "soloists": candidate.get("soloists") or "",
        "director": candidate.get("director") or "",
        "ensemble": candidate.get("ensemble") or "",
        "published": published_line(candidate),
        "editions": [],
        "anchors": [],
        "reception": [],
        "sources": [],
        "editorial": editorial,
    }


def _work_payload(work: dict, editorial: dict[str, dict] | None = None) -> dict | None:
    assessed = list(work.get("assessed") or [])
    if not assessed:
        return None
    signed = editorial if editorial is not None else {}
    by_id = {c.get("id"): c for c in work.get("candidates") or [] if c.get("id")}
    recs = []
    for rid in assessed:
        cand = by_id.get(rid)
        if not cand:
            continue
        recs.append(identity_recording(work["id"], cand, signed.get(rid)))
    if not recs:
        return None
    cat = " · ".join(
        p for p in (work.get("catalogue") or "", work.get("year") or "") if p
    )
    return {
        "id": work["id"],
        "composer_id": work.get("composer_id") or composer_id_of(work["id"]),
        "composer": work.get("composer") or "",
        "dates": work.get("composer_dates") or "",
        "title": work.get("title") or "",
        "cat": cat,
        "standfirst": work.get("note") or "",
        "recordings": recs,
    }


def public_identity_works(
    seed: dict, editorial: dict[str, dict] | None = None
) -> list[dict]:
    """First-slice works whose public cards are the signed assessed IDs."""
    signed = editorial if editorial is not None else load_signed_editorial()
    out = []
    for work in seed.get("works") or []:
        wid = work.get("id") or ""
        if wid not in FIRST_SLICE_WORKS:
            continue
        payload = _work_payload(work, signed)
        if payload:
            out.append(payload)
    return out


def merge_identity_works(cat: dict, seed: dict) -> dict:
    """Append first-slice identity works that the engine catalogue does not already carry."""
    existing = {w.get("id") for w in cat.get("works") or []}
    existing_anchors = {work_anchor(i) for i in existing if i}
    extra = []
    for work in public_identity_works(seed):
        if work["id"] in existing or work_anchor(work["id"]) in existing_anchors:
            continue
        extra.append(work)
    if not extra:
        return cat
    out = dict(cat)
    out["works"] = list(cat.get("works") or []) + extra
    return out
