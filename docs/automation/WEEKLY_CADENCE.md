# Weekly cadence — five composers

Policy change relative to Sprint 1–2 “no sixth composer”: the catalogue now
grows by **five well-known composers per week**, facts first. Assessments still
arrive only through cited sources.

## Clock

| Day | Actor | Action |
|---|---|---|
| Mon | Human | Confirm next five ids in `composer-queue.json` (`status: next`) |
| Mon | Orchestrator | `make expand-brief` → launch Role A |
| Tue–Wed | Role A | Seed PR: works + candidates |
| Wed | Role B | Identity + CAA cover proposals (budget 300) |
| Thu | Role C | Award / citation proposals for backlog *and* new works |
| Fri | Human (owner) | Review board `/review/`; set accepts in `review-decisions.json`; `make review-apply` or owner-only Action |
| Fri | Community | Optional notes via **Community review comment** issues → `data/community/` PRs |
| Fri | Human | Merge statement contributions (still owner-ratified); review citation ratio |
| Fri | Role D | Site/rollup green on `main` via PR |
| When a signed entry is ready | **Critic** (Developer may ship) | Land `data/editorial/` on `main` → Pages. No Friday human merge gate |

## Source-coverage target

For each **assessed** recording, drive toward **≥5** independent cited/attributed
sources (stretch **10**), drawn from the Role C list. Coverage is measured by
distinct `source` strings on interpretation statements after ratification — not
by scraped article count.

## Composer score refresh

After any statements merge: `make score && make site`. Composer rollup is null
until `n_strong >= 3` and `n_recordings_assessed >= 2` (see engine). Missing
score is correct behaviour, not a bug.

## Legal

- No publication-site scraping.  
- Diapason print path: [`docs/legal/DIAPASON_INGESTION.md`](../legal/DIAPASON_INGESTION.md).  
- Covers: hotlink Cover Art Archive only.
