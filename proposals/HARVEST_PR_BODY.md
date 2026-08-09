# Local harvest pass — 511-candidate seed (Role B)

Ran `make loop` then MusicBrainz identity/citation harvest against `main` (10 · 119 · **511**).

## Already live

The **≥500** seed floor is already on `main` and GitHub Pages (511 candidates queued). This PR does **not** change `data/seed.json` scores or statements.

## This PR

| | Count |
|---|---:|
| Proposals in `proposals/proposals-20260809.json` | 902 |
| Identity matches proposed | 392 |
| `auto_accept_eligible` (≥80, clean flags) | 102 |
| Citation tasks queued | 510 |
| Cover proposals | 0 (gated until mbids ratified) |

## Human gate (required)

- [ ] Review `proposals/IDENTITY_REVIEW.md` — reject `wrong work:`, compilations, wrong decade
- [ ] Apply only eligible rows via `python3 agents/apply.py` (never force wrong-work)
- [ ] Covers run only after mbids land in seed

## Gates

- [x] `python3 -m unittest discover -s tests -q`
- [x] `python3 agents/validate.py`
- [x] `make targets` (floor still met)

**Forbidden work not done:** no writes to `data/statements/`, no review prose, no cover binaries, no score edits.
