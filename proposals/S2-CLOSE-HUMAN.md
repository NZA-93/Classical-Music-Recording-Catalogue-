# Sprint 2 close — human checklist (S2-04 · S2-09)

## S2-04 · Write the first three signed entries `[H]`

```bash
make entry                    # facts-only brief + stub (ADR-002)
# edit data/editorial/<work>.json — author, date, revision, stars, text
python3 agents/validate.py
make site
```

Queue today (recompute after awards land):

1. Shostakovich, Symphony No. 5
2. Puccini, Tosca
3. Whatever `make queue` says after Sprint 1 awards

Done when three entries carry author, date, revision and stars, and at least
one disagrees with the aggregate.

**Agents must not draft `text`, `stars`, or `reference`.**

## S2-06 · Editions / barcodes `[A→H]`

After identity mbids are applied:

```bash
python3 agents/harvest.py data/seed.json --contact "$HARVEST_CONTACT" --budget 300
python3 agents/review.py proposals/<file> --markdown   # review editions
python3 agents/apply.py --proposals proposals/<file> --only editions
```

Done when barcode index > 200 and every stored barcode passes its check digit.

## S2-07 · Covers

```bash
python3 agents/covers_report.py
```

Misses are prompts for MusicBrainz/CAA — never commit images.

## S2-09 · Sprint close

```bash
python3 -m unittest discover -s tests -q
python3 agents/validate.py
make site
```

- [ ] No score originates from a model without a locator
- [ ] No signed entry was machine-assisted
- [ ] Tag `v0.3-voice`
