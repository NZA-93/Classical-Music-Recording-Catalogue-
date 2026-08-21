# Identity board — harvest payload gaps

Generated for the needs-review identity board. **Never fill a blank with a guess.**

For each field: **payload present** (shown on the board) or **payload absent** (blank — honest omit).

| Field | Status | Source | Board behaviour |
|---|---|---|---|
| `work_title` | payload present (shown) | seed.work + proposal.payload.mb_title | shown side-by-side |
| `catalogue` | payload present (shown) | seed.catalogue | shown (seed only; MB has no catalogue field) |
| `fassung` | payload absent (blank) | neither seed nor proposal.payload | blank — payload-absent |
| `completeness` | payload absent (blank) | neither seed nor proposal.payload | blank — payload-absent |
| `conductor` | payload present (shown) | seed.director | shown (seed only; MB artist-credit not in payload) |
| `orchestra` | payload present (shown) | seed.ensemble | shown (seed only) |
| `soloists_roles` | payload absent (blank) | seed.soloists is a flat string; no role tags; MB artists not in payload | seed soloists string shown when present; roles blank |
| `session_year` | payload absent (blank) | neither seed nor proposal has session_year | blank — seed.year and mb_first_release shown as release-year proxies only |
| `seed_year` | payload present (shown) | seed.year | shown (not labelled session year) |
| `mb_first_release` | payload present (shown) | proposal.payload.mb_first_release | shown |
| `venue` | payload absent (blank) | neither seed nor proposal.payload | blank — payload-absent |
| `live_studio` | payload absent (blank) | neither seed nor proposal.payload | blank — payload-absent |
| `seed_label` | payload present (shown) | seed.label | shown |
| `seed_catno` | payload absent (blank) | seed has no catno field | blank — payload-absent |
| `mb_label` | payload absent (blank) | proposal.payload has no label | blank — payload-absent |
| `mb_catno` | payload absent (blank) | proposal.payload has no catno | blank — payload-absent |
| `mb_barcode` | payload absent (blank) | proposal.payload has no barcode | blank — payload-absent |
| `release_group_mbid` | payload present (shown) | proposal.payload.mbid | shown + MusicBrainz link (this is a release-group id) |
| `release_mbid` | payload absent (blank) | harvest stores release-group MBID only | blank — payload-absent |
| `why_it_missed` | derived from present fields (shown) | review_flags + seed.year vs mb_first_release + title string compare | shown — only from actual mismatches; never invented |
| `remake_siblings` | derived from present fields (shown) | other seed candidates with same forces, different year | shown when present |
| `community_notes` | payload present (shown) | data/community/comments.json | amber when present |
| `pack_id` | payload present (shown) | review queue pack_id | shown |

## Five critic-required fields

| Field | If harvest/seed can supply | If not |
|---|---|---|
| Fassung | surface it | payload-absent — blank |
| completeness | surface it | payload-absent — blank |
| session year | surface it | payload-absent — blank (show seed.year / mb_first_release as proxies only, labelled as such) |
| live/studio | surface it | payload-absent — blank |
| why-it-missed / conflicting-field | derive from actual mismatched fields / review_flags | list needs_human_review_bucket only — never invent |

Absent required-looking fields make **defer** the honest human default for that row. This document does not write defer into `review-decisions.json`.

Citation tasks stay off identity rows.
