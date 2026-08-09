# S1-03 · Award → proposal citation engine (Role C)

Restores `agents/awards.py` so `data/awards/*.json` emit **proposals** for human
confirmation. Does **not** write `data/statements/` or `data/editorial/`.

## What changed

- `agents/awards.py` — match `covers_works` + performers to catalogue/seed;
  emit `scale: award`, `provenance: cited`, origin-aware `class`, locator,
  `covers_works`, `needs_human_confirmation`
- ADR-001 in `engine/aggregation_engine_v2.py` — album awards collapse to one
  benchmark signal via `Statement.signal_key()` / `covers_works`
- `data/awards/public_lists.json` — two further public Grammy facts with
  Wikipedia locators (Haitink Sym. 4; Bernstein Sym. 1 & 7)
- `proposals/awards-20260809.json` — six proposals from the current award files

## Proposals produced (6)

| Target | Award | Year | Notes |
|---|---|---|---|
| `shostakovich_sym5_nelsons` | Grammy Best Orchestral | 2017 | Album award; ADR-001 `covers_works` = sym5/8/9 |
| `shostakovich/sym8/1` | Grammy Best Orchestral | 2017 | Same album award (shared signal) |
| `shostakovich/sym10/2` | Grammy Best Orchestral | 2016 | Nelsons / BSO |
| `shostakovich/sym10/2` | Gramophone Award Orchestral | 2016 | Nelsons / BSO |
| `shostakovich/sym10/1` | Gramophone Award Orchestral | 2011 | Petrenko; Naxos locator (label promo caveat on row) |
| `shostakovich/sym7/0` | Grammy Best Orchestral | 1991 | Bernstein/CSO; **ambiguous_risk** (year gap) |

Unmatched (no catalogue candidate yet): 2018 Nelsons Grammy (sym4/11), 2009
Haitink Grammy (sym4), sym9 half of the 2017 album award.

## Review checklist

- [x] No review / sleeve / promotional body text stored
- [x] Characterisations ≤ 240 chars, guide's own words
- [x] Every proposal has a locator (no inferred awards)
- [x] `class` reflects origin (`major_award` / `specialist survey`)
- [x] ADR-001: album awards carry shared `covers_works`
- [x] `make test` / `validate` / `make site` pass
- [ ] **[H]** Human confirms each identity match before apply into statements
- [ ] **[H]** Bernstein 1991 / Sym. 7 candidate: confirm correct album (ambiguous_risk)
- [ ] **[H]** Do not merge Petrenko Naxos locator praise as criticism

## Stop

Human ratification gate. Agents must not apply these into `data/statements/`.
