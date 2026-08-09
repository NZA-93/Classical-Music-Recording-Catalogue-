#!/usr/bin/env python3
"""
apply.py — merge accepted harvest proposals into seed and recordings data.

Reads proposals/*.json written by harvest.py. Writes only to data/seed.json
and data/recordings/. Never touches data/statements/ or data/editorial/.

    python3 agents/apply.py --proposals proposals/proposals-YYYYMMDD.json --dry-run
    python3 agents/apply.py --proposals proposals/proposals-YYYYMMDD.json
    python3 agents/apply.py --proposals PATH --only identity,editions
    python3 agents/apply.py --proposals PATH --force "reason for overwriting verified"
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Optional

# Reuse the barcode check already enforced on contributions.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from validate import check_digit_ok  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "data" / "seed.json"
RECORDINGS = ROOT / "data" / "recordings"
PROPOSALS_DIR = ROOT / "proposals"

KINDS = {"identity", "editions", "cover"}


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def find_candidate(seed: dict, target: str) -> Optional[dict]:
    for work in seed.get("works", []):
        for cand in work.get("candidates", []):
            if cand.get("id") == target:
                return cand
    return None


def work_id_of(target: str) -> str:
    """bach/brandenburg/0 → bach/brandenburg."""
    parts = target.rsplit("/", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() else target


def recordings_path(work_id: str) -> pathlib.Path:
    return RECORDINGS / f"{work_id}.json"


def find_recording_by_mbid(doc: dict, mbid: str) -> Optional[dict]:
    if not mbid:
        return None
    for rec in doc.get("recordings", []):
        for ed in rec.get("editions", []):
            if ed.get("mbid") == mbid:
                return rec
        # Some recordings may carry the release-group mbid at top level later.
        if rec.get("mbid") == mbid:
            return rec
    return None


def guard_verified(obj: dict, field: str, new_value: Any,
                   force: bool, reason: str, log: list) -> bool:
    """Return True if the write is allowed. verified:true fields need --force."""
    if not obj.get("verified"):
        return True
    old = obj.get(field)
    if old == new_value:
        return True
    if not force:
        log.append({
            "action": "skipped_verified",
            "field": field,
            "old": old,
            "new": new_value,
            "id": obj.get("id"),
        })
        return False
    if not reason:
        log.append({
            "action": "force_refused",
            "field": field,
            "id": obj.get("id"),
            "note": "--force requires a reason",
        })
        return False
    log.append({
        "action": "force_overwrite",
        "field": field,
        "old": old,
        "new": new_value,
        "id": obj.get("id"),
        "reason": reason,
    })
    return True


def apply_identity(cand: dict, payload: dict, force: bool, reason: str,
                   log: list) -> bool:
    mbid = payload.get("mbid")
    if not mbid:
        log.append({"action": "skip", "kind": "identity", "id": cand["id"],
                    "note": "no mbid in payload"})
        return False
    changed = False
    if cand.get("mbid") == mbid and cand.get("verified") is False:
        # Already applied; still refresh match metadata if missing.
        for k in ("mb_title", "mb_first_release", "match_score"):
            if k in payload and cand.get(k) != payload[k]:
                cand[k] = payload[k]
                changed = True
        if not changed:
            log.append({"action": "noop", "kind": "identity", "id": cand["id"]})
        return changed

    if not guard_verified(cand, "mbid", mbid, force, reason, log):
        return False

    if cand.get("mbid") != mbid:
        cand["mbid"] = mbid
        changed = True
    # A machine match is not a verification.
    if cand.get("verified") is not False:
        cand["verified"] = False
        changed = True
    for k in ("mb_title", "mb_first_release", "match_score"):
        if k in payload and cand.get(k) != payload[k]:
            cand[k] = payload[k]
            changed = True
    if changed:
        log.append({"action": "identity", "id": cand["id"], "mbid": mbid,
                    "match_score": payload.get("match_score")})
    return changed


def edition_key(ed: dict) -> tuple:
    return (ed.get("mbid") or "", ed.get("barcode") or "",
            ed.get("catno") or "", ed.get("year") or "")


def filter_editions(raw: list[dict], log: list, target: str) -> list[dict]:
    kept = []
    for ed in raw:
        code = ed.get("barcode")
        if code:
            if not check_digit_ok(str(code)):
                log.append({
                    "action": "dropped_barcode",
                    "id": target,
                    "barcode": code,
                    "note": "check digit failed; never stored",
                })
                ed = {**ed, "barcode": None}
        kept.append(ed)
    return kept


def apply_editions(cand: dict, payload: dict, seed: dict, force: bool,
                   reason: str, log: list,
                   recordings_cache: dict) -> bool:
    incoming = filter_editions(list(payload.get("editions") or []), log, cand["id"])
    if not incoming:
        log.append({"action": "noop", "kind": "editions", "id": cand["id"],
                    "note": "nothing left after barcode filter"})
        return False

    cand.setdefault("editions", [])
    existing = {edition_key(e) for e in cand["editions"]}
    added = 0
    for ed in incoming:
        key = edition_key(ed)
        if key in existing:
            continue
        # Do not overwrite a verified edition's fields via append-merge.
        cand["editions"].append({**ed, "verified": False})
        existing.add(key)
        added += 1

    # Mirror into data/recordings when a file exists for the work and we can
    # attach by release-group mbid already on the candidate.
    wid = work_id_of(cand["id"])
    rpath = recordings_path(wid)
    if rpath.exists() and cand.get("mbid"):
        if str(rpath) not in recordings_cache:
            recordings_cache[str(rpath)] = load_json(rpath)
        doc = recordings_cache[str(rpath)]
        rec = find_recording_by_mbid(doc, cand["mbid"])
        if rec is None:
            # Match by director string as a soft attach for known catalogue rows.
            director = (cand.get("director") or "").lower()
            for r in doc.get("recordings", []):
                if director and director in (r.get("director") or "").lower():
                    rec = r
                    break
        if rec is not None:
            rec.setdefault("editions", [])
            rexisting = {edition_key(e) for e in rec["editions"]}
            for ed in incoming:
                key = edition_key(ed)
                if key in rexisting:
                    continue
                # Never overwrite a verified:true edition in place.
                clash = next((e for e in rec["editions"]
                              if e.get("mbid") and e.get("mbid") == ed.get("mbid")
                              and e.get("verified")), None)
                if clash and not force:
                    log.append({"action": "skipped_verified", "kind": "editions",
                                "id": rec["id"], "mbid": ed.get("mbid")})
                    continue
                rec["editions"].append({
                    "id": ed.get("mbid") or f"mb_{ed.get('catno') or 'unk'}",
                    "label": ed.get("label") or "",
                    "catno": ed.get("catno") or "",
                    "year": ed.get("year") or "",
                    "fmt": ed.get("format") or "",
                    "transfer": ed.get("transfer") or "MusicBrainz harvest; transfer not yet assessed.",
                    "barcode": ed.get("barcode"),
                    "mbid": ed.get("mbid"),
                    "verified": False,
                })
                rexisting.add(key)
                added += 1

    if added:
        log.append({"action": "editions", "id": cand["id"], "added": added})
        return True
    log.append({"action": "noop", "kind": "editions", "id": cand["id"]})
    return False


def cover_hotlink_ok(image: Any) -> bool:
    """Covers are CAA/MB hotlinks (or an explicit miss). Never store binaries."""
    if image is None:
        return True
    if not isinstance(image, str):
        return False
    if image.startswith(("data:", "file:")):
        return False
    lowered = image.lower()
    # Cover Art Archive hotlink (what harvest.py emits).
    if lowered.startswith("https://coverartarchive.org/"):
        return True
    # Bare release / release-group MBID is enough to build a CAA hotlink later.
    if len(image) == 36 and image.count("-") == 4:
        hex_ok = all(c in "0123456789abcdef-" for c in lowered)
        return hex_ok
    return False


def apply_cover(cand: dict, payload: dict, force: bool, reason: str,
                log: list) -> bool:
    # may be null — that is a recorded miss (no front at CAA)
    if "image" not in payload:
        log.append({"action": "skip", "kind": "cover", "id": cand["id"],
                    "note": "no image key"})
        return False
    image = payload.get("image")
    if not cover_hotlink_ok(image):
        log.append({
            "action": "skip",
            "kind": "cover",
            "id": cand["id"],
            "note": "cover must be a CAA/MB hotlink or null; binaries refused",
        })
        return False
    # Optional release-group / release mbid for hotlinking without a full URL.
    cover_mbid = payload.get("mbid") or payload.get("release_mbid")
    if cover_mbid is not None and not cover_hotlink_ok(cover_mbid):
        log.append({
            "action": "skip",
            "kind": "cover",
            "id": cand["id"],
            "note": "cover mbid is not a plausible MusicBrainz identifier",
        })
        return False

    changed = False
    if cand.get("image") != image:
        if not guard_verified(cand, "image", image, force, reason, log):
            return False
        cand["image"] = image
        changed = True
    if cover_mbid and cand.get("cover_mbid") != cover_mbid:
        cand["cover_mbid"] = cover_mbid
        changed = True
    if not changed:
        log.append({"action": "noop", "kind": "cover", "id": cand["id"]})
        return False
    log.append({"action": "cover", "id": cand["id"], "image": image,
                "cover_mbid": cover_mbid})
    return True


def apply_proposals(proposals: list[dict], seed: dict, *,
                    only: Optional[set[str]] = None,
                    dry_run: bool = False,
                    force: bool = False,
                    reason: str = "") -> tuple[dict, dict, list]:
    """Return (new_seed, recordings_cache, log)."""
    seed = deepcopy(seed)
    only = only or KINDS
    log: list = []
    recordings_cache: dict = {}
    changed = False

    for prop in proposals:
        kind = prop.get("kind")
        if kind not in KINDS:
            continue
        if kind not in only:
            continue
        target = prop.get("target")
        cand = find_candidate(seed, target) if target else None
        if cand is None:
            log.append({"action": "missing_target", "kind": kind, "target": target})
            continue
        payload = prop.get("payload") or {}
        if kind == "identity":
            changed = apply_identity(cand, payload, force, reason, log) or changed
        elif kind == "editions":
            changed = apply_editions(cand, payload, seed, force, reason, log,
                                     recordings_cache) or changed
        elif kind == "cover":
            changed = apply_cover(cand, payload, force, reason, log) or changed

    return seed, recordings_cache, log


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--proposals", required=True, type=pathlib.Path,
                    help="Path to a proposals JSON array")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report changes without writing")
    ap.add_argument("--only", default="",
                    help="Comma list: identity,editions,cover")
    ap.add_argument("--force", metavar="REASON", default="",
                    help="Allow overwriting verified:true fields; reason is logged")
    args = ap.parse_args(argv)

    if not args.proposals.exists():
        print(f"proposals file not found: {args.proposals}", file=sys.stderr)
        return 2

    only = {k.strip() for k in args.only.split(",") if k.strip()} or None
    if only and not only <= KINDS:
        print(f"--only must be subset of {sorted(KINDS)}", file=sys.stderr)
        return 2

    proposals = load_json(args.proposals)
    if not isinstance(proposals, list):
        print("proposals file must be a JSON array", file=sys.stderr)
        return 2

    seed = load_json(SEED_PATH)
    force = bool(args.force)
    new_seed, recordings_cache, log = apply_proposals(
        proposals, seed, only=only, dry_run=args.dry_run,
        force=force, reason=args.force,
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    applied_path = PROPOSALS_DIR / f"applied-{stamp}.json"
    report = {
        "schema": "applied/1",
        "source": str(args.proposals),
        "dry_run": args.dry_run,
        "force_reason": args.force or None,
        "created": datetime.now(timezone.utc).isoformat(),
        "log": log,
        "changes": sum(1 for e in log if e.get("action") not in
                       ("noop", "skip", "skipped_verified", "missing_target",
                        "force_refused")),
    }

    print(f"{len(log)} log entries · {report['changes']} changes"
          f"{' (dry-run)' if args.dry_run else ''}")
    for entry in log:
        print(f"  {entry.get('action')}: {entry}")

    if args.dry_run:
        # Still write the applied report for reviewability of the dry run.
        write_json(applied_path, report)
        print(f"wrote {applied_path} (dry-run; seed/recordings untouched)")
        return 0

    # Hard fence: this tool writes seed + recordings (+ applied log) only.
    forbidden = (ROOT / "data" / "statements", ROOT / "data" / "editorial")
    for path, doc in list(recordings_cache.items()) + [(SEED_PATH, new_seed)]:
        resolved = pathlib.Path(path).resolve()
        for fence in forbidden:
            try:
                resolved.relative_to(fence.resolve())
            except ValueError:
                continue
            print(f"refusing to write under {fence}: {resolved}", file=sys.stderr)
            return 3

    write_json(SEED_PATH, new_seed)
    for path, doc in recordings_cache.items():
        write_json(pathlib.Path(path), doc)
    write_json(applied_path, report)
    print(f"wrote {SEED_PATH}")
    for path in recordings_cache:
        print(f"wrote {path}")
    print(f"wrote {applied_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
