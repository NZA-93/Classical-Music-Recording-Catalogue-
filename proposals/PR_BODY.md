# Harvest 20260822 · identity facts (`harvest/1.9`)

Lookup of **existing** identity release-group MBIDs for session year and live/studio. **No identity search.** Unmatched seeds stay unmatched. first-release-date is never copied as session year. Identity apply still writes the release-group MBID only.

Contact: `https://github.com/nza-93/classical-music-recording-catalogue-` · budget **300 per run** (four resume passes; MusicBrainz 1 req/s, backoff on 503).

## Cumulative facts (392 identity rows)

| Field | Present | Blank (honest omit) |
|---|---:|---:|
| session_year | **11** | **381** |
| live_studio | **61** (32 live · 29 studio) | **331** |
| fassung | **2** | **390** |
| completeness | **7** | **385** |
| WS/2 lookup stored (`mb_primary_type`) | **390** | **2** (Handel Water Music /0, Dixit Dominus /0 — repeated timeouts) |

Blank means MusicBrainz had no disambiguation / secondary-type / recording-year token. seed.year and first-release-date stay labelled as release-year proxies.

Example of the session-year rule: Gould Goldberg (`bach/goldberg/0`) stores session **1955** from disambiguation `1955 recording`; first-release-date is **1956-03-01** and is not copied. Year-range tokens (`1976-1981 recordings` on Haydn London) are omitted as ambiguous.

## Identity buckets (unchanged from #25)

| Bucket | Count |
|---|---:|
| accept-eligible | **90** (same 90 targets as after #25) |
| needs-review | **194** |
| reject_wrong_work | **108** |
| identity proposals | **392** (no rows added or dropped) |
| unmatched seeds left unmatched | **359** |

`review-decisions.json` was not written (`--no-init`). No accepts added. The signed 90 were not bulk-applied.

Gardiner Archiv/1990s Brandenburg (`bach/brandenburg/5`) still carries the existing 2009 date-flagged hit; this run did not search for or attach SDG 707 or any other release-group.

## Locks honoured

- No scores, stars, Référence, sound assessments, or editorial prose
- No writes to `data/statements/` or `data/editorial/`
- Identity apply still writes release-group MBID only
- Wrong-work matcher from #25 unchanged
- Stdlib only; budget not raised above 300 per run
- Regression scores unchanged: Pinnock 2.853, Harnoncourt 2.814, Callas/de Sabata 2.955 Référence, Price/Karajan 2.848

## Stop

Do not merge. Human identity review gate. Do not treat accept-eligible as a bulk apply.
