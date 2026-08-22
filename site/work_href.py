"""Shared work-page identifiers. Standard library only.

A work page is sealed: one work, no global related / recommended /
trending payload. Cross-composer nickname matches ("Symphony No. 5")
are not a reason to put another work on the page.
"""

from __future__ import annotations

# Historical ids in catalogue.json vs seed.json.
ALIAS = {"bach_brandenburg": "bach/brandenburg", "puccini_tosca": "puccini/tosca"}
REV_ALIAS = {v: k for k, v in ALIAS.items()}


def work_anchor(work_id: str) -> str:
    return REV_ALIAS.get(work_id, str(work_id).replace("/", "_"))


def work_page_href(work_id: str, *, depth: int = 0, recording_id: str | None = None) -> str:
    prefix = "../" * depth
    href = f"{prefix}works/{work_anchor(work_id)}.html"
    if recording_id:
        href += f"#{recording_id}"
    return href
