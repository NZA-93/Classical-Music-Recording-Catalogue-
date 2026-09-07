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

# Emerson Quartet Art of Fugue — only this MusicBrainz release (CAA front).
EMERSON_ID = "bach/art_of_fugue/3"
EMERSON_MBID = "1d748095-0c33-4fd7-b925-9e50849f101d"

# Identity editions carry catalogue facts for the cover plate. Never copy
# sound, verdict, or transfer — those are judgements, not identity.
_EDITION_KEYS = (
    "id", "label", "year", "catno", "format", "mbid",
    "verified", "barcode", "release_group_mbid",
)
# Critic-internal notes stay off the public card.
_FACT_STRIP_SKIP = frozenset({"seed_year_note", "cover_face"})


def identity_editions(candidate: dict) -> list[dict]:
    """Preferred release(s) already on the seed candidate, for CAA fronts."""
    out = []
    rid = candidate.get("id") or ""
    for ed in candidate.get("editions") or []:
        if not isinstance(ed, dict):
            continue
        item = {k: ed[k] for k in _EDITION_KEYS if ed.get(k) not in (None, "")}
        mbid = str(item.get("mbid") or "")
        if rid == EMERSON_ID and mbid and mbid != EMERSON_MBID:
            raise ValueError(
                f"{EMERSON_ID}: edition.mbid must be {EMERSON_MBID}"
            )
        if item.get("mbid") or item.get("id"):
            out.append(item)
    return out


def identity_fact_strip(candidate: dict) -> dict | None:
    """Brandenburg-lite facts from the seed. Empty keys are omitted."""
    raw = candidate.get("fact_strip")
    if not isinstance(raw, dict) or not raw:
        return None
    out = {
        k: v for k, v in raw.items()
        if k not in _FACT_STRIP_SKIP and v not in (None, "")
    }
    return out or None


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
        "editions": identity_editions(candidate),
        "fact_strip": identity_fact_strip(candidate),
        "anchors": [],
        "reception": [],
        "sources": [],
        "editorial": editorial,
        "divergence": None,  # no aggregate on an identity card
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
