# Sprint 1 close — human checklist (S1-07 · S1-08)

Agent work for Sprint 1 tooling is in open PRs. These steps are **human only**.

## S1-00 remainder (still blocking loop safety)

- [ ] Pages → Source: GitHub Actions (not legacy branch deploy)
- [ ] Variable `HARVEST_CONTACT` set
- [ ] Protect `main`: require PR; require `validate` + `Build and publish`; disallow self-approval
- [ ] Confirm direct push to `main` is rejected

## S1-07 · Send the letters

- [ ] Send [docs/legal/lettre-editis.md](../docs/legal/lettre-editis.md) — ratings with links only
- [ ] Send [docs/legal/lettre-reworld.md](../docs/legal/lettre-reworld.md) — same ask; quotation is later (ADR-003)
- [ ] One approach to a conservatoire / university music library (DSM Arts 8–11)

Do **not** open with a quotation request.

## S1-04 · Confirm award statements

- [ ] Work [proposals/S1-04-HUMAN-REVIEW.md](S1-04-HUMAN-REVIEW.md)
- [ ] Move confirmed drafts from `proposals/pending-statements/` into `data/statements/`
- [ ] Citation ratio > 50% and ≥ 30 cited statements

## S1-06 · Identity round

- [ ] Live harvest with `HARVEST_CONTACT`
- [ ] `python3 agents/review.py … --markdown`
- [ ] Reject flagged rows; `apply.py` accepted ones

## S1-08 · Sprint close

Verify before tagging:

```bash
python3 -m unittest discover -s tests -q
python3 agents/validate.py
make site
```

Regression scores must still be:

| Recording | Interpretation | Référence |
|---|---|---|
| Pinnock — Brandenburgs | 2.853 | No |
| Harnoncourt — Brandenburgs | 2.814 | No |
| Callas / de Sabata — Tosca | 2.955 | Yes |
| Price / Karajan — Tosca | 2.848 | No |

- [ ] Four scores untouched
- [ ] No source text entered `data/` (S1-05 guard green)
- [ ] Tag `v0.2-live`
