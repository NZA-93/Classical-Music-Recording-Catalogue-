"""On-this-disc couplings: exact release identity only.

A coupling is another work that shares a barcode or a release MBID with one
of this recording's editions. That fact is attached to the recording so a
sealed work page can show it on the card without loading another work.

Never match on title tokens, nicknames, catalogue numbers, producers, or
popularity. A shared "Symphony No. 5" is not a disc. Empty is correct.
"""

from __future__ import annotations

import pathlib
import sys

_SITE = pathlib.Path(__file__).resolve().parent
if str(_SITE) not in sys.path:
    sys.path.insert(0, str(_SITE))

from work_href import composer_id_of, work_anchor  # noqa: E402


def edition_identity_keys(edition: dict) -> list[tuple[str, str]]:
    """Exact disc keys. Barcode digits or a release MBID — nothing else."""
    keys: list[tuple[str, str]] = []
    raw_bc = str(edition.get("barcode") or "")
    digits = "".join(c for c in raw_bc if c.isdigit())
    if len(digits) >= 8:
        keys.append(("barcode", digits))
    mbid = str(edition.get("mbid") or "").strip().lower()
    if mbid:
        keys.append(("mbid", mbid))
    return keys


def _work_meta(work: dict) -> dict:
    wid = work.get("id") or ""
    return {
        "work_id": wid,
        "anchor": work_anchor(wid),
        "title": work.get("title") or "",
        "composer": work.get("composer") or "",
        "composer_id": work.get("composer_id") or composer_id_of(wid),
    }


def _edition_label(edition: dict) -> str:
    label = str(edition.get("label") or "").strip()
    year = str(edition.get("year") or "").strip()
    fmt = str(edition.get("format") or edition.get("fmt") or "").strip()
    return " · ".join(p for p in (label, year, fmt) if p)


def _index_identity(works: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """Map exact disc keys to the works that carry them (once per work+key)."""
    index: dict[tuple[str, str], list[dict]] = {}
    for work in works:
        meta = _work_meta(work)
        seen: set[tuple[str, str]] = set()
        for rec in work.get("recordings") or []:
            for edition in rec.get("editions") or []:
                for key in edition_identity_keys(edition):
                    if key in seen:
                        continue
                    seen.add(key)
                    index.setdefault(key, []).append(meta)
    return index


def couplings_for_recording(
    recording: dict,
    work_id: str,
    index: dict[tuple[str, str], list[dict]],
) -> list[dict]:
    """Other works on a release this recording actually shares. Not a feed."""
    found: dict[tuple[str, str], dict] = {}
    for edition in recording.get("editions") or []:
        ed_id = str(edition.get("id") or "")
        label = _edition_label(edition)
        for key in edition_identity_keys(edition):
            for meta in index.get(key, []):
                if meta["work_id"] == work_id:
                    continue
                slot = (str(meta["work_id"]), ed_id or key[1])
                if slot in found:
                    continue
                found[slot] = {
                    **meta,
                    "via": key[0],
                    "edition_id": ed_id,
                    "edition_label": label,
                }
    out = list(found.values())
    out.sort(key=lambda row: (row.get("title") or "", row.get("work_id") or ""))
    return out


def attach_on_this_disc(cat: dict) -> dict:
    """Copy the catalogue with on_this_disc baked onto each recording.

    Must run on the full catalogue, before a work page is sealed. A sealed
    page cannot see other works, so the card would otherwise stay empty
    even when a shared barcode exists.
    """
    works = list(cat.get("works") or [])
    index = _index_identity(works)
    new_works = []
    for work in works:
        wid = work.get("id") or ""
        recs = []
        for rec in work.get("recordings") or []:
            copy = dict(rec)
            copy["on_this_disc"] = couplings_for_recording(rec, wid, index)
            recs.append(copy)
        new_work = dict(work)
        new_work["recordings"] = recs
        new_works.append(new_work)
    out = dict(cat)
    out["works"] = new_works
    return out
