# Seed week 2026-08-09 — Role A

Adds five composers from `proposals/composer-queue.json` into the editorial seed.

## Scope

| Composer | Works | Candidates (facts only) |
|---|---|---|
| Johannes Brahms | 12 | Symphonies 1 & 4, concertos, Requiem, chamber, overtures |
| Joseph Haydn | 12 | London / Surprise / Trauer / Farewell, Creation, Op. 76, etc. |
| Franz Schubert | 12 | Unfinished / Great, song cycles, chamber, D.960, etc. |
| George Frideric Handel | 12 | Messiah, Water Music, Fireworks, operas, Op. 6, etc. |
| Frédéric Chopin | 12 | Ballades, Études, Preludes, sonatas, concertos, etc. |

Totals after `make seed`: **10 composers · 119 works · 193 candidates**.

## Checklist

- [x] Facts only in seed (performers, label, year) — no scores/stars/statements
- [x] `TestSeedIntegrity` expects 10 composers / 119 works
- [x] Queue status `in_progress`, week `2026-08-09` for the five
- [x] `python3 -m unittest discover -s tests -q`
- [x] `python3 agents/validate.py`
- [x] `make site` (dynamic nav already present)
- [ ] Human: confirm candidate identities are the intended recordings (not compilations / wrong decade)

## Base

Branched from `cursor/composer-automation-5458` (weekly automation + dynamic nav). Prefer merge after that lands, or review as stacked on top of it.

**Forbidden work not done:** no harvest, no `data/statements/`, no review text.
