"""Shared work-page and composer-hub identifiers. Standard library only.

A work page is sealed: one work (composer + catalogue / work_id), no global
related / recommended / trending payload. Cross-composer nickname matches
("Symphony No. 5") are not a reason to put another work on the page.

C: other works on the same disc live on the recording as `on_this_disc`,
keyed by barcode or release MBID — never by title tokens. They are not a
work-page feed.

Navigation is catalogue → composer hub → sealed work page. Sibling works of
the same composer live on the hub, not on the work page.
"""

from __future__ import annotations

# Historical ids in catalogue.json vs seed.json.
ALIAS = {"bach_brandenburg": "bach/brandenburg", "puccini_tosca": "puccini/tosca"}
REV_ALIAS = {v: k for k, v in ALIAS.items()}


def work_anchor(work_id: str) -> str:
    return REV_ALIAS.get(work_id, str(work_id).replace("/", "_"))


def composer_id_of(work_id: str) -> str:
    """Composer slug from a work id. Never inferred from a title token."""
    wid = ALIAS.get(work_id, str(work_id))
    if "/" in wid:
        return wid.split("/", 1)[0]
    return wid.split("_", 1)[0]


def work_page_href(work_id: str, *, depth: int = 0, recording_id: str | None = None) -> str:
    prefix = "../" * depth
    href = f"{prefix}works/{work_anchor(work_id)}.html"
    if recording_id:
        href += f"#{recording_id}"
    return href


def composer_page_href(composer_id: str, *, depth: int = 0) -> str:
    prefix = "../" * depth
    return f"{prefix}composers/{composer_id}.html"
