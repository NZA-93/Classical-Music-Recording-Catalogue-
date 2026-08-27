"""Identity-only public pages from seed.works[].assessed.

The critic-signed assessed IDs are who may appear on a public card. Engine
scores and the harvest candidate queue are not. A first-slice enable list
gates which assessed works get a Pages file, so later apply PRs can turn
more works on without new plumbing.

No scores, stars, Référence, statements, or editorial belong here.
"""

from __future__ import annotations

import pathlib
import sys

_SITE = pathlib.Path(__file__).resolve().parent
if str(_SITE) not in sys.path:
    sys.path.insert(0, str(_SITE))

from work_href import composer_id_of, work_anchor  # noqa: E402

# Works that may emit identity-only public pages this slice. Content is
# always the work's assessed IDs; add a work id here to publish it.
FIRST_SLICE_WORKS = frozenset({"bach/goldberg"})


def published_line(candidate: dict) -> str:
    label = str(candidate.get("label") or "").strip()
    year = str(candidate.get("year") or "").strip()
    if label and year:
        return f"{label}, {year}"
    return label or year


def identity_recording(work_id: str, candidate: dict) -> dict:
    """Facts already on the seed candidate. Nothing scored."""
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
        "editorial": None,
    }


def _work_payload(work: dict) -> dict | None:
    assessed = list(work.get("assessed") or [])
    if not assessed:
        return None
    by_id = {c.get("id"): c for c in work.get("candidates") or [] if c.get("id")}
    recs = []
    for rid in assessed:
        cand = by_id.get(rid)
        if not cand:
            continue
        recs.append(identity_recording(work["id"], cand))
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


def public_identity_works(seed: dict) -> list[dict]:
    """First-slice works whose public cards are the signed assessed IDs."""
    out = []
    for work in seed.get("works") or []:
        wid = work.get("id") or ""
        if wid not in FIRST_SLICE_WORKS:
            continue
        payload = _work_payload(work)
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
