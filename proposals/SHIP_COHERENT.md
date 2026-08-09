# Coherent ship — consolidate open work

## Scheme

| Layer | Source | Status |
|---|---|---|
| Catalogue floor 10·100·500 | `#18` on `main` | Live (511) |
| Composer directory pages | `#20` on `main` | Live |
| Week-2 seed (15·179·751) | `cursor/seed-week2-5458` | Merged here |
| `derive_prov` / locator through engine | score-matrix (was missing on main) | Ported — AGENTS §8 |
| Harvest title matching (equiv groups, keys) | `cursor/identity-harvest-511-5458` | Ported |
| Identity/citation proposals (densest) | `cursor/identity-harvest-local-5458` | Included |

## Superseded — close without merging

| PR / branch | Why |
|---|---|
| `#2` s1-02 apply | Already on `main` via ship-all |
| `#3` s1-03 awards | Already on `main` via ship-all |
| `#4` s1-05 source-text | Already on `main` |
| `#19` seed week 2 | Contained in this ship |
| `#21` local harvest | Contained in this ship |
| `cursor/seed-week-20260809-5458` | Week-1 composers already on `main` |
| `cursor/score-matrix-covers-4193` | Site superseded by `#20`; engine bits ported |
| `cursor/catalogue-composer-pages-4193` | Merged as `#20` |
| Older `cursor/*-5458` tooling branches | Already landed or empty vs `main` |

## Human gates still open

- Identity review of `proposals/IDENTITY_REVIEW.md` before `apply.py`
- Never apply `wrong work:` rows
- Week-2 composers (Tchaikovsky…Debussy) still need a harvest round after this merges
