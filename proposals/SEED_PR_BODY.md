# Seed week 2 (2026-08-09) — Role A

Adds the next five composers from `proposals/composer-queue.json` into the editorial seed.

## Scope

| Composer | Works | Candidate focus (facts only) |
|---|---|---|
| Pyotr Ilyich Tchaikovsky | 12 | Symphonies 4–6, concertos, ballets, Onegin, etc. |
| Richard Wagner | 12 | Ring evenings, Tristan, Meistersinger, Parsifal, etc. |
| Giuseppe Verdi | 12 | Traviata through Nabucco + Requiem |
| Gustav Mahler | 12 | Symphonies 1–9 (selected), Das Lied, song cycles |
| Claude Debussy | 12 | Faune, La mer, Pelléas, piano sets, chamber |

Totals after `make seed`: **15 composers · 179 works · 751 candidate recordings**.

Each new work has ≥4 well-known candidates (performers / label / year only).

## Checklist

- [x] Facts only in seed (performers, label, year) — no scores/stars/statements
- [x] `TestSeedIntegrity` floors: composers ≥ 15, works ≥ 100, candidates ≥ 500
- [x] Queue status `in_progress`, week `2026-08-09` for the five
- [x] `docs/automation/CATALOGUE_TARGETS.md` documents next ceiling **15 · 150 · 750** (current PR exceeds 10 · 100 · 500; `make targets` floor unchanged)
- [x] `python3 -m unittest discover -s tests -q`
- [x] `python3 agents/validate.py`
- [x] `make site`
- [x] `make targets` (still exit 0)
- [ ] Human: confirm candidate identities are the intended recordings (not compilations / wrong decade)

## Base

Rebased onto `main` after #18 (catalogue loop densify) merged.

**Forbidden work not done:** no harvest, no `data/statements/`, no review text, no cover binaries.
