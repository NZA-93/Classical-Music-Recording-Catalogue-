# Harvest 20260809 · DRY RUN (plan only)

`harvest/1.1` · contact `harvest@example.invalid` · budget **300** · planned **72** requests · **0** proposals

## Expected cost

- Seed: **59** works · **72** candidates · **0** already have an mbid
- Budget cap: **300** requests (MusicBrainz ~1 req/s; CAA ~0.6s gap)
- This run: **72** network requests (not sent — dry-run)
- Wall-clock if live: ~72–102s under polite rate limits

| Stage | Planned |
|---|---|
| identity | 72 |

## Dry-run notes

- No MusicBrainz / CAA requests were made.
- Editions and covers stay gated on a human-merged mbid (pipeline does not build on unreviewed identity guesses).
- After this plan is accepted, re-run without `--dry-run` with the same budget.

## Review checklist

- [ ] Identity matches are the right recording, not a compilation / sampler
- [ ] No identity with confidence < 80 is treated as auto-accept
- [ ] Uncertain rows reviewed against MusicBrainz (`mb_url`) before merge
- [ ] Cover payloads are CAA / MusicBrainz hotlinks only (no binaries, no Discogs)
- [ ] Barcodes belong to the edition claimed (editions stage)
- [ ] No review text has been copied into any payload
- [ ] Every score carries a locator, or it stays `draft`

## Stop

Human identity review gate. Do not begin editions/covers apply until mbids are ratified.
