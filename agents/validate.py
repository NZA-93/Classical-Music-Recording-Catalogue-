#!/usr/bin/env python3
"""
validate.py — the gate on every incoming contribution.

The guide's rules are only real if a machine enforces them on every pull
request. This checks contributions/*.json and fails the build on anything that
would quietly damage the catalogue:

  · a score with no locator claiming to be `cited`
  · a sound assessment that names no edition
  · a characterisation long enough to be a copied paragraph
  · quoted review text
  · a barcode that fails its own check digit
  · a reference to a recording or edition that does not exist

Stdlib only. Runs in about a second.

    python agents/validate.py
    python agents/validate.py --strict     # warnings become failures
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

CONTRIB = pathlib.Path("contributions")
SEED = pathlib.Path("data/seed.json")
CATALOGUE = pathlib.Path("build/catalogue.json")

SCALES = {"stars_5", "stars_3", "ten_point", "percent", "award",
          "editors_choice", "rosette", "prose"}
AXES = {"interpretation", "sound"}
TIERS = {"cited", "attributed", "draft"}

# A characterisation is one sentence in the contributor's own words. Anything
# much longer is either an essay or, more often, a paste.
MAX_CHARACTERISATION = 240
QUOTE_RUN = re.compile(r'["“”«»]\s*(?:\S+\s+){8,}')


def load(path: pathlib.Path, default):
    try:
        return json.loads(path.read_text("utf-8"))
    except FileNotFoundError:
        return default


def known_ids() -> tuple[set[str], set[str]]:
    """Recording and edition ids the catalogue actually contains."""
    recordings, editions = set(), set()
    seed = load(SEED, {"works": []})
    for w in seed.get("works", []):
        for c in w.get("candidates", []):
            recordings.add(c["id"])
    cat = load(CATALOGUE, {"works": []})
    for w in cat.get("works", []):
        for r in w.get("recordings", []):
            recordings.add(r["id"])
            for e in r.get("editions", []):
                editions.add(e["id"])
    return recordings, editions


def check_digit_ok(code: str) -> bool:
    """EAN-13 and UPC-A carry their own checksum. Typos are common and silent."""
    if not code.isdigit() or len(code) not in (12, 13):
        return False
    digits = [int(d) for d in code]
    body, check = digits[:-1], digits[-1]
    if len(code) == 13:                      # EAN-13: weights 1,3 from the left
        weights = [1 if i % 2 == 0 else 3 for i in range(12)]
    else:                                    # UPC-A: weights 3,1 from the left
        weights = [3 if i % 2 == 0 else 1 for i in range(11)]
    total = sum(d * w for d, w in zip(body, weights))
    return (10 - total % 10) % 10 == check


def earned_tier(c: dict) -> str:
    """Provenance is derived from evidence, never from what the file claims."""
    if c.get("locator"):
        return "cited"
    if c.get("source"):
        return "attributed"
    return "draft"


def validate(c: dict, path: pathlib.Path, recs: set[str], eds: set[str]):
    errs, warns = [], []
    def e(m): errs.append(f"{path.name}: {m}")
    def w(m): warns.append(f"{path.name}: {m}")

    for field in ("recording", "axis", "source", "characterisation"):
        if not c.get(field):
            e(f"missing required field `{field}`")
    if errs:
        return errs, warns

    if c["axis"] not in AXES:
        e(f"axis must be one of {sorted(AXES)}")

    if c["recording"] not in recs:
        e(f"unknown recording `{c['recording']}`")

    # Sound belongs to an edition. This is the guide's central distinction and
    # the one mistake that would quietly undo it.
    if c["axis"] == "sound":
        if not c.get("edition"):
            e("a sound assessment must name the edition it describes")
        elif c["edition"] not in eds:
            e(f"unknown edition `{c['edition']}`")
    elif c.get("edition"):
        w("an interpretation assessment should not name an edition")

    scale = c.get("scale")
    if scale not in SCALES:
        e(f"scale must be one of {sorted(SCALES)}")
    elif scale == "prose":
        if c.get("value") is not None:
            e("a prose source carries no number; a human assigns it, and signs for it")
    else:
        v = c.get("value")
        if v is None and scale not in ("award", "editors_choice", "rosette"):
            e(f"scale `{scale}` requires a value")
        elif v is not None and not isinstance(v, (int, float)):
            e("value must be numeric")

    claimed = c.get("provenance")
    earned = earned_tier(c)
    if claimed and claimed not in TIERS:
        e(f"provenance must be one of {sorted(TIERS)}")
    elif claimed and TIERS and claimed != earned:
        order = {"draft": 0, "attributed": 1, "cited": 2}
        if order[claimed] > order[earned]:
            e(f"claims `{claimed}` but the evidence supports `{earned}`"
              + (" — add a locator" if earned != "cited" else ""))
        else:
            w(f"claims `{claimed}` though it has earned `{earned}`")

    text = c["characterisation"].strip()
    if len(text) > MAX_CHARACTERISATION:
        e(f"characterisation is {len(text)} characters; the limit is "
          f"{MAX_CHARACTERISATION}. One sentence, in your own words.")
    if QUOTE_RUN.search(text):
        e("looks like quoted review text. Store a locator and your own words, "
          "not the publication's.")

    if "conflict" not in c:
        w("no `conflict` field. State whether you have a commercial interest.")
    elif not isinstance(c["conflict"], bool):
        e("`conflict` must be true or false")

    bc = c.get("barcode")
    if bc:
        clean = re.sub(r"\D", "", str(bc))
        if not check_digit_ok(clean):
            e(f"barcode {bc} fails its check digit — likely a transcription error")

    return errs, warns


# --------------------------------------------------------------- editorial

MAX_QUOTES = 2
MAX_QUOTE_WORDS = 25
MAX_QUOTE_PROPORTION = 0.20


def validate_editorial(entry: dict, path: pathlib.Path, recs: set[str]):
    """ADR-002 and ADR-003. Signed entries are the only place judgement and
    quotation legitimately live, so they are the only place worth checking hard."""
    errs, warns = [], []
    def e(m): errs.append(f"{path.name}: {m}")
    def w(m): warns.append(f"{path.name}: {m}")

    for field in ("recording", "author", "date", "revision", "text"):
        if not entry.get(field):
            e(f"unsigned or incomplete: missing `{field}`. Unsigned prose does not publish.")
    if errs:
        return errs, warns

    if entry["recording"] not in recs:
        e(f"unknown recording `{entry['recording']}`")
    if not isinstance(entry.get("author"), dict) or not entry["author"].get("id"):
        e("author must carry an id; a byline is the whole point")

    quotes = entry.get("quotes", [])
    if len(quotes) > MAX_QUOTES:
        e(f"{len(quotes)} quotations; the limit is {MAX_QUOTES} per entry (ADR-003)")

    for i, q in enumerate(quotes, 1):
        where = f"quote {i}"
        for field in ("text", "quoted_author", "publication", "locator"):
            if not q.get(field):
                e(f"{where}: missing `{field}` — courte citation requires author and source")
        words = len(str(q.get("text", "")).split())
        if words > MAX_QUOTE_WORDS:
            e(f"{where}: {words} words; the limit is {MAX_QUOTE_WORDS}")
        src = q.get("source_length_words")
        if src:
            share = words / float(src)
            if share > MAX_QUOTE_PROPORTION:
                e(f"{where}: {share:.0%} of a {src}-word notice; the limit is "
                  f"{MAX_QUOTE_PROPORTION:.0%}. Brevity is relative to the source.")
        else:
            w(f"{where}: no `source_length_words`, so proportion cannot be checked")

    return errs, warns


# --------------------------------------------------------------- data/ prose scan
# S1-05: contributions and editorial already go through validate(); the catalogue
# data layer itself had no mechanical check. A pasted paragraph in a statement
# file must fail the build.

DATA_ROOT = pathlib.Path("data")
PROSE_KEYS = frozenset({
    "characterisation", "characterization", "characterization_en",
})
# Long free-text keys that may legitimately exceed 240 chars (facts, not
# contribution characterisations) — still scanned for quoted review runs.
LONG_OK_KEYS = frozenset({
    "note", "listen_for", "standfirst", "transfer", "text", "album",
    "locator_caveat", "description",
})


def _walk_strings(obj, path="$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def scan_data_file(path: pathlib.Path) -> list[str]:
    """Return error strings for one JSON file under data/."""
    errs = []
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        return [f"{path}: not valid JSON — {err}"]

    rel = path.as_posix()
    for keypath, text in _walk_strings(doc):
        key = keypath.rsplit(".", 1)[-1]
        if key in PROSE_KEYS:
            if len(text) > MAX_CHARACTERISATION:
                errs.append(
                    f"{rel}: `{key}` is {len(text)} characters; limit is "
                    f"{MAX_CHARACTERISATION} (S1-05 source-text guard)"
                )
            if QUOTE_RUN.search(text):
                errs.append(
                    f"{rel}: `{key}` looks like quoted review text (S1-05)"
                )
        elif key in LONG_OK_KEYS or key.endswith("_note"):
            if QUOTE_RUN.search(text):
                errs.append(
                    f"{rel}: `{key}` contains a quoted run that reads as "
                    f"reproduced prose (S1-05)"
                )
        elif len(text) > MAX_CHARACTERISATION and QUOTE_RUN.search(text):
            errs.append(
                f"{rel}: long field `{key}` looks like pasted review prose (S1-05)"
            )
    return errs


def scan_data_tree(root: pathlib.Path = DATA_ROOT) -> list[str]:
    errs = []
    if not root.exists():
        return errs
    for path in sorted(root.rglob("*.json")):
        if path.name.startswith("_"):
            continue
        errs.extend(scan_data_file(path))
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--skip-data", action="store_true",
                    help="skip the data/ source-text scan (emergency only)")
    args = ap.parse_args()

    recs, eds = known_ids()
    files = sorted(f for f in CONTRIB.glob("*.json")
             if not f.name.startswith("_")) if CONTRIB.exists() else []

    all_errs, all_warns = [], []
    for path in files:
        try:
            data = json.loads(path.read_text("utf-8"))
        except json.JSONDecodeError as err:
            all_errs.append(f"{path.name}: not valid JSON — {err}")
            continue
        for item in (data if isinstance(data, list) else [data]):
            e, w = validate(item, path, recs, eds)
            all_errs += e
            all_warns += w

    ed_dir = pathlib.Path("data/editorial")
    ed_files = sorted(f for f in ed_dir.glob("*.json")
                      if not f.name.startswith("_")) if ed_dir.exists() else []
    for path in ed_files:
        try:
            doc = json.loads(path.read_text("utf-8"))
        except json.JSONDecodeError as err:
            all_errs.append(f"{path.name}: not valid JSON — {err}")
            continue
        for ent in doc.get("entries", []):
            e, w = validate_editorial(ent, path, recs)
            all_errs += e
            all_warns += w
    files = files + ed_files

    data_errs = [] if args.skip_data else scan_data_tree()
    all_errs += data_errs

    for w in all_warns:
        print(f"  warning  {w}")
    for e in all_errs:
        print(f"  ERROR    {e}")

    n = len(files)
    print(f"\n{n} file{'s' if n != 1 else ''} checked · "
          f"{len(all_errs)} error{'s' if len(all_errs) != 1 else ''} · "
          f"{len(all_warns)} warning{'s' if len(all_warns) != 1 else ''}"
          f" · data/ scan {'skipped' if args.skip_data else 'on'}")
    return 1 if all_errs or (args.strict and all_warns) else 0


if __name__ == "__main__":
    raise SystemExit(main())
