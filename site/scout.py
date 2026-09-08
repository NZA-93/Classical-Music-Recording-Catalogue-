"""ADR-004 scout candidate pool — attach to work pages, never to editorial.

Ordinal ranks for “which deserve a Critic cut?”. Never stars, Référence,
matrix, or Dictionnaire text. Never feeds the aggregate. Loader copies an
allowlist of fields so a forbidden key cannot reach the page payload.
"""

from __future__ import annotations

import json
import pathlib
import sys

_SITE = pathlib.Path(__file__).resolve().parent
_ROOT = _SITE.parent
if str(_SITE) not in sys.path:
    sys.path.insert(0, str(_SITE))

from work_href import work_anchor  # noqa: E402

SCOUT_ROW_KEYS = (
    "recording",
    "rank",
    "stance",
    "status",
    "identity",
    "why_in",
    "why_out",
)


def public_scout_row(cand: dict) -> dict:
    """ADR-004 fields only. Crowns cannot hitch a ride onto the page."""
    return {k: cand.get(k) for k in SCOUT_ROW_KEYS}


def load_scout_pools(root: pathlib.Path | None = None) -> dict[str, list]:
    """work_id → ordered scout rows. Files named _* are schema, not pools."""
    data = pathlib.Path(root) if root is not None else _ROOT / "data"
    scout_dir = data / "scout"
    out: dict[str, list] = {}
    if not scout_dir.is_dir():
        return out
    for path in sorted(scout_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        wid = doc.get("work_id")
        rows = doc.get("candidates")
        if not wid or not isinstance(rows, list):
            continue
        ordered = sorted(
            (public_scout_row(c) for c in rows if isinstance(c, dict)),
            key=lambda r: (r.get("rank") is None, r.get("rank") or 0),
        )
        out[wid] = ordered
    return out


def attach_scout_pools(cat: dict, root: pathlib.Path | None = None) -> dict:
    """Hang the pool on the work. Does not merge into recording.editorial."""
    pools = load_scout_pools(root)
    if not pools:
        return cat
    by_anchor = {work_anchor(wid): rows for wid, rows in pools.items()}
    works = []
    changed = False
    for work in cat.get("works") or []:
        wid = work.get("id") or ""
        rows = pools.get(wid) or by_anchor.get(work_anchor(wid))
        if rows:
            w = dict(work)
            w["scout"] = rows
            works.append(w)
            changed = True
        else:
            works.append(work)
    if not changed:
        return cat
    out = dict(cat)
    out["works"] = works
    return out
