"""Identity-board enrichment for human review of harvest proposals.

Pure helpers: derive why-it-missed from actual seed vs proposal mismatches,
surface remake siblings, and report field presence honestly. Never invent
musicological values for empty harvest fields.
"""

from __future__ import annotations

from typing import Any

# Fields the critic requires on every needs-review row. Values are either
# shown from payload or listed as payload-absent — never synthesized.
REQUIRED_IDENTITY_FIELDS = (
    "fassung",
    "completeness",
    "session_year",
    "live_studio",
    "why_it_missed",
)

# Full inventory of board columns vs what current harvest/seed JSON holds.
# status: "present" | "absent" | "derived"
FIELD_INVENTORY: list[dict[str, str]] = [
    {
        "field": "work_title",
        "status": "present",
        "source": "seed.work + proposal.payload.mb_title",
        "board": "shown side-by-side",
    },
    {
        "field": "catalogue",
        "status": "present",
        "source": "seed.catalogue",
        "board": "shown (seed only; MB has no catalogue field)",
    },
    {
        "field": "fassung",
        "status": "absent",
        "source": "neither seed nor proposal.payload",
        "board": "blank — payload-absent",
    },
    {
        "field": "completeness",
        "status": "absent",
        "source": "neither seed nor proposal.payload",
        "board": "blank — payload-absent",
    },
    {
        "field": "conductor",
        "status": "present",
        "source": "seed.director",
        "board": "shown (seed only; MB artist-credit not in payload)",
    },
    {
        "field": "orchestra",
        "status": "present",
        "source": "seed.ensemble",
        "board": "shown (seed only)",
    },
    {
        "field": "soloists_roles",
        "status": "absent",
        "source": "seed.soloists is a flat string; no role tags; MB artists not in payload",
        "board": "seed soloists string shown when present; roles blank",
    },
    {
        "field": "session_year",
        "status": "absent",
        "source": "neither seed nor proposal has session_year",
        "board": "blank — seed.year and mb_first_release shown as release-year proxies only",
    },
    {
        "field": "seed_year",
        "status": "present",
        "source": "seed.year",
        "board": "shown (not labelled session year)",
    },
    {
        "field": "mb_first_release",
        "status": "present",
        "source": "proposal.payload.mb_first_release",
        "board": "shown",
    },
    {
        "field": "venue",
        "status": "absent",
        "source": "neither seed nor proposal.payload",
        "board": "blank — payload-absent",
    },
    {
        "field": "live_studio",
        "status": "absent",
        "source": "neither seed nor proposal.payload",
        "board": "blank — payload-absent",
    },
    {
        "field": "seed_label",
        "status": "present",
        "source": "seed.label",
        "board": "shown",
    },
    {
        "field": "seed_catno",
        "status": "absent",
        "source": "seed has no catno field",
        "board": "blank — payload-absent",
    },
    {
        "field": "mb_label",
        "status": "absent",
        "source": "proposal.payload has no label",
        "board": "blank — payload-absent",
    },
    {
        "field": "mb_catno",
        "status": "absent",
        "source": "proposal.payload has no catno",
        "board": "blank — payload-absent",
    },
    {
        "field": "mb_barcode",
        "status": "absent",
        "source": "proposal.payload has no barcode",
        "board": "blank — payload-absent",
    },
    {
        "field": "release_group_mbid",
        "status": "present",
        "source": "proposal.payload.mbid",
        "board": "shown + MusicBrainz link (this is a release-group id)",
    },
    {
        "field": "release_mbid",
        "status": "absent",
        "source": "harvest stores release-group MBID only",
        "board": "blank — payload-absent",
    },
    {
        "field": "why_it_missed",
        "status": "derived",
        "source": "review_flags + seed.year vs mb_first_release + title string compare",
        "board": "shown — only from actual mismatches; never invented",
    },
    {
        "field": "remake_siblings",
        "status": "derived",
        "source": "other seed candidates with same forces, different year",
        "board": "shown when present",
    },
    {
        "field": "community_notes",
        "status": "present",
        "source": "data/community/comments.json",
        "board": "amber when present",
    },
    {
        "field": "pack_id",
        "status": "present",
        "source": "review queue pack_id",
        "board": "shown",
    },
]


def _norm(s: Any) -> str:
    return " ".join(str(s or "").lower().split())


def _year_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(str(value)[:4])
    except (TypeError, ValueError):
        return None


def _classify_flag(flag: str) -> tuple[str, str] | None:
    """Map a harvest review_flags string to (code, fields). None if unknown."""
    fl = flag.lower().strip()
    if fl.startswith("wrong work:"):
        return ("wrong_work", "review_flags")
    if fl.startswith("date off"):
        return ("date_mismatch", "seed.year,payload.mb_first_release,review_flags")
    if fl.startswith("confidence") or "missing musicbrainz confidence" in fl:
        return ("low_confidence", "payload.confidence,review_flags")
    if fl.startswith("compilation-like"):
        return ("compilation_or_box", "review_flags,payload.mb_title")
    return None


def why_it_missed(seed: dict[str, Any], proposal: dict[str, Any]) -> list[dict[str, str]]:
    """Return concrete mismatch reasons from flags and comparable fields.

    Only reports differences that exist in the data. Does not invent
    musicological explanations. Parses harvest flag strings as emitted by
    agents/harvest.py (e.g. ``date off by N years``, ``confidence N < 80``).
    """
    payload = proposal.get("payload") or {}
    flags = [str(f) for f in (payload.get("review_flags") or [])]
    reasons: list[dict[str, str]] = []
    seen: set[str] = set()

    def add(code: str, detail: str, fields: str) -> None:
        if code in seen:
            return
        seen.add(code)
        reasons.append({"code": code, "detail": detail, "fields": fields})

    for flag in flags:
        classified = _classify_flag(flag)
        if classified is None:
            add("review_flag", flag, "review_flags")
            continue
        code, fields = classified
        add(code, flag, fields)

    seed_year = _year_int(seed.get("year"))
    mb_year = _year_int(payload.get("mb_first_release"))
    if (
        seed_year is not None
        and mb_year is not None
        and abs(seed_year - mb_year) > 0
        and "date_mismatch" not in seen
    ):
        add(
            "year_differs",
            f"Seed year {seed_year} ≠ MB first-release {mb_year} "
            f"(within 3 years — still a conflicting field for human eyes).",
            "seed.year,payload.mb_first_release",
        )

    # Prefer bare work title for comparison; fall back to composer — title.
    seed_title_raw = seed.get("work_title") or seed.get("work") or ""
    seed_title = _norm(seed_title_raw)
    mb_title = _norm(payload.get("mb_title"))
    if seed_title and mb_title and seed_title != mb_title:
        if seed_title not in mb_title and mb_title not in seed_title:
            add(
                "title_string_differs",
                f"Seed work {seed_title_raw!r} vs MB title {payload.get('mb_title')!r}.",
                "seed.work,payload.mb_title",
            )
        else:
            add(
                "title_string_partial",
                f"Seed work {seed_title_raw!r} only partially overlaps MB title "
                f"{payload.get('mb_title')!r}.",
                "seed.work,payload.mb_title",
            )

    if not reasons:
        add(
            "needs_human_review_bucket",
            "In needs-review queue without a more specific conflicting field in payload "
            "(no inventable musicological reason).",
            "queue.bucket",
        )
    return reasons


def remake_siblings(
    seed: dict[str, Any],
    all_candidates: list[dict[str, Any]],
    *,
    exclude_id: str | None = None,
) -> list[dict[str, Any]]:
    """Other seed rows with same principal forces and different year."""
    director = _norm(seed.get("director"))
    ensemble = _norm(seed.get("ensemble"))
    work = _norm(seed.get("work_title") or seed.get("work"))
    year = _year_int(seed.get("year"))
    if not director and not ensemble:
        return []
    out: list[dict[str, Any]] = []
    for cand in all_candidates:
        cid = str(cand.get("id") or "")
        if exclude_id and cid == exclude_id:
            continue
        cand_work = _norm(cand.get("work_title") or cand.get("work"))
        if cand_work != work:
            continue
        if director and _norm(cand.get("director")) != director:
            continue
        if ensemble and _norm(cand.get("ensemble")) != ensemble:
            continue
        cy = _year_int(cand.get("year"))
        if year is not None and cy is not None and cy == year:
            continue
        out.append(
            {
                "id": cid,
                "year": cand.get("year"),
                "label": cand.get("label") or "",
                "director": cand.get("director") or "",
                "ensemble": cand.get("ensemble") or "",
            }
        )
    out.sort(key=lambda r: (str(r.get("year") or ""), r.get("id") or ""))
    return out


def criterion_status(seed: dict[str, Any], proposal: dict[str, Any]) -> list[dict[str, str]]:
    """Visible accept-criteria checks. Values: pass | conflict | absent.

    absent = field missing in payload (human should lean defer).
    conflict = comparable fields disagree.
    pass = comparable fields agree where both present.
    Never synthesizes missing musicology.
    """
    payload = proposal.get("payload") or {}
    flag_codes: set[str] = set()
    for f in payload.get("review_flags") or []:
        classified = _classify_flag(str(f))
        if classified is not None:
            flag_codes.add(classified[0])
    reasons = why_it_missed(seed, proposal)
    reason_codes = {r["code"] for r in reasons}

    def row(name: str, status: str, note: str) -> dict[str, str]:
        return {"criterion": name, "status": status, "note": note}

    checks: list[dict[str, str]] = []

    st = _norm(seed.get("work_title") or seed.get("work"))
    mt = _norm(payload.get("mb_title"))
    if not st or not mt:
        checks.append(row("same_work", "absent", "work title missing on seed or MB payload"))
    elif st == mt or st in mt or mt in st:
        checks.append(row("same_work", "pass", "seed work overlaps MB title string"))
    else:
        checks.append(row("same_work", "conflict", "seed work vs MB title string diverge"))

    checks.append(
        row(
            "same_fassung",
            "absent",
            "Fassung not in seed or harvest payload — blank; defer is honest default",
        )
    )
    checks.append(
        row(
            "same_completeness",
            "absent",
            "completeness not in seed or harvest payload — blank; defer is honest default",
        )
    )

    if seed.get("director") or seed.get("ensemble") or seed.get("soloists"):
        checks.append(
            row(
                "same_principal_artists",
                "absent",
                "seed forces shown; MB artist-credit not in harvest payload — cannot verify match",
            )
        )
    else:
        checks.append(
            row("same_principal_artists", "absent", "no seed forces and no MB artists in payload")
        )

    seed_year = _year_int(seed.get("year"))
    mb_year = _year_int(payload.get("mb_first_release"))
    if seed_year is None and mb_year is None:
        checks.append(row("same_session_year", "absent", "no year on seed or MB payload"))
    else:
        checks.append(
            row(
                "session_year_field",
                "absent",
                "session_year not in payload; seed.year / mb_first_release are release-year proxies only",
            )
        )
        if seed_year is not None and mb_year is not None:
            if seed_year == mb_year:
                checks.append(
                    row(
                        "release_year_proxy",
                        "pass",
                        f"seed year {seed_year} equals MB first-release {mb_year}",
                    )
                )
            else:
                checks.append(
                    row(
                        "release_year_proxy",
                        "conflict",
                        f"seed year {seed_year} ≠ MB first-release {mb_year}",
                    )
                )

    if "compilation_or_box" in flag_codes:
        checks.append(
            row("not_excerpt_or_sampler", "conflict", "compilation-like title flag set")
        )
    else:
        checks.append(
            row(
                "not_excerpt_or_sampler",
                "absent",
                "no excerpt/sampler field in payload — cannot confirm",
            )
        )
    checks.append(
        row(
            "live_vs_studio",
            "absent",
            "live/studio not in seed or harvest payload — blank; defer is honest default",
        )
    )

    mbid = str(payload.get("mbid") or "").strip()
    if not mbid:
        checks.append(row("mbid_is_this_performance", "absent", "no MBID in payload"))
    elif "compilation_or_box" in flag_codes:
        checks.append(
            row(
                "mbid_is_this_performance",
                "conflict",
                "MBID present but compilation-like title flag — may be VA box not this performance",
            )
        )
    else:
        checks.append(
            row(
                "mbid_is_this_performance",
                "absent",
                "release-group MBID present; release MBID and artist-credit absent — human must open MB",
            )
        )

    if "low_confidence" in reason_codes or "low_confidence" in flag_codes:
        checks.append(
            row("confidence_threshold", "conflict", "low_confidence flag set")
        )

    return checks


def why_missed_sort_key(reasons: list[dict[str, str]]) -> tuple[int, str]:
    """Sort needs-review: work mismatch → remake/compilation → date → confidence → other."""
    codes = {r["code"] for r in reasons}
    if "title_string_differs" in codes:
        return (0, "title")
    if "compilation_or_box" in codes:
        return (1, "compilation")
    if "date_mismatch" in codes:
        return (2, "date")
    if "year_differs" in codes:
        return (3, "year")
    if "title_string_partial" in codes:
        return (4, "title_partial")
    if "low_confidence" in codes:
        return (5, "confidence")
    return (9, "other")


def enrichment_for_row(
    seed: dict[str, Any],
    proposal: dict[str, Any],
    all_candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    """Bundle everything the board needs for one needs-review identity row."""
    payload = proposal.get("payload") or {}
    reasons = why_it_missed(seed, proposal)
    siblings = remake_siblings(seed, all_candidates, exclude_id=str(seed.get("id") or ""))
    return {
        "why_missed": reasons,
        "why_missed_sort": why_missed_sort_key(reasons),
        "criteria": criterion_status(seed, proposal),
        "remake_siblings": siblings,
        "field_presence": {
            "fassung": None,
            "completeness": None,
            "session_year": None,
            "live_studio": None,
            "venue": None,
            "seed_year": seed.get("year"),
            "mb_first_release": payload.get("mb_first_release"),
            "release_group_mbid": payload.get("mbid"),
            "release_mbid": None,
            "mb_label": None,
            "mb_catno": None,
            "mb_barcode": None,
            "seed_catno": None,
        },
    }


def write_payload_gaps_markdown(path: str) -> None:
    """Write the explicit field-by-field gap list for the 244 board."""
    lines = [
        "# Identity board — harvest payload gaps",
        "",
        "Generated for the needs-review identity board. "
        "**Never fill a blank with a guess.**",
        "",
        "For each field: **payload present** (shown on the board) or "
        "**payload absent** (blank — honest omit).",
        "",
        "| Field | Status | Source | Board behaviour |",
        "|---|---|---|---|",
    ]
    for row in FIELD_INVENTORY:
        status = row["status"]
        label = {
            "present": "payload present (shown)",
            "absent": "payload absent (blank)",
            "derived": "derived from present fields (shown)",
        }.get(status, status)
        lines.append(
            f"| `{row['field']}` | {label} | {row['source']} | {row['board']} |"
        )
    lines.extend(
        [
            "",
            "## Five critic-required fields",
            "",
            "| Field | If harvest/seed can supply | If not |",
            "|---|---|---|",
            "| Fassung | surface it | payload-absent — blank |",
            "| completeness | surface it | payload-absent — blank |",
            "| session year | surface it | payload-absent — blank "
            "(show seed.year / mb_first_release as proxies only, labelled as such) |",
            "| live/studio | surface it | payload-absent — blank |",
            "| why-it-missed / conflicting-field | derive from actual mismatched "
            "fields / review_flags | list needs_human_review_bucket only — never invent |",
            "",
            "Absent required-looking fields make **defer** the honest human default "
            "for that row. This document does not write defer into "
            "`review-decisions.json`.",
            "",
            "Citation tasks stay off identity rows.",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
