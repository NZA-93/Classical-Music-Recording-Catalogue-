# Catalogue targets loop — 10 · 100 · 500

Hard floor for usefulness of the seed (facts only — no scores):

| Metric | Target | How it grows |
|---|---|---|
| Composers | **≥ 10** | `proposals/composer-queue.json` → Role A seed PRs |
| Works | **≥ 100** | ~10–12 core works per composer in `seed_catalogue.py` |
| Candidate recordings | **≥ 500** | Densify `CANDIDATES` / `seed_candidates_dense.py` |

Current progress: `make targets` (or `python3 agents/catalogue_loop.py`).

The live seed already exceeds this floor (week-2 Role A: Tchaikovsky, Wagner,
Verdi, Mahler, Debussy → **15 · 179 · 751**). Keep `agents/catalogue_loop.py`
targets at 10 · 100 · 500 so `make targets` still exits 0; raise the enforced
floor only when identity/citation catch up.

## Quality bar (non-negotiable)

1. **Facts only** in the seed: performers, director, ensemble, label, year.  
2. **No scores, stars, statements, or review text** in seed expansion.  
3. Prefer canonically discussed recordings (not random discogs dumps).  
4. Identity still goes through MusicBrainz harvest → human review; `wrong work:` never applies.  
5. Covers = Cover Art Archive hotlinks only.  
6. Assessments only via cited proposals after human ratification.

## Loop (repeat until `make targets` exits 0)

```
make targets                  # print gap; exit 1 until floors met
make expand-brief             # next composer batch if composers < 10
# Role A: add composers/works OR densify candidates
make seed && make test && make site
# Role B: make plan && make harvest CONTACT=…  (budget 300)
# Human: identity review → apply eligible matches
# Role C: awards/citations toward ≥5 sources on assessed rows
```

Exit code of `catalogue_loop.py`: **0** only when all three floors are met.
Until then agents keep opening densify / seed PRs — never inventing judgements to “look done”.

## Next ceiling

| Metric | Next floor |
|---|---|
| Composers | **≥ 15** |
| Works | **≥ 150** |
| Candidate recordings | **≥ 750** |

Continue the same loop. Citation ratio and signed entries remain the editorial
bottleneck — see `SPRINTS.md`.
