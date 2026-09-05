# Agent automation — Critical Discography

Coordinates Cursor agents for catalogue growth without inventing aggregate
judgements. Signed editorial is Role Critic ([`CRITIC.md`](CRITIC.md)).
Binding rules remain in [`AGENTS.md`](../../AGENTS.md). This directory only
describes **who does what**, **in what order**, and **what each agent may write**.

## Non-negotiables

| Allowed | Forbidden |
|---|---|
| MusicBrainz identity / editions / barcodes → `proposals/` | Scraping a publication’s review site |
| Cover Art Archive existence + hotlink (never rehost) | Committing cover image binaries |
| Award / rating **facts** with locators → proposals | Writing scores into `data/statements/` |
| Own-words characterisation ≤240 chars + locator | Pasting review prose into `data/` |
| Composer **rollup** from already-ratified statements | Roles A–E drafting signed editorial `text` / stars / Référence |
| Seed expansion: works + candidates (facts only) | Inventing assessments where no source exists |
| **Critic** signed entries in `data/editorial/`, landed on `main` | Inventing seed / statement / aggregate scores without a citation |

Short quotations (ADR-003) belong only in a **Critic-signed** editorial entry.
Harvest and citation agents may emit citation *tasks* and structured proposals;
they never place quotes. Critic may place quotes inside the entry, bounded.

## How a composer score is produced

The guide already weights every statement by **origin class × provenance**
(`Cls` × `Prov` in `engine/aggregation_engine_v2.py`). A composer score is not a
new judgement layer: it is the same weighted mean, re-run across that composer’s
interpretation statements after humans have ratified them.

```
online review / award list
        │
        ▼
 agent extract → proposal {axis, score, class, locator, characterisation≤240}
        │
        ▼
 human ratify → data/statements/   (agents never write here)
        │
        ▼
 aggregate() per recording  →  aggregate_composer() rollup
        │
        ▼
 build/catalogue.json  +  site index
```

Origin classes (highest first among serious sources): independent critic and
major award (0.90), engineering literature (0.88), specialist survey (0.85),
secondary (0.75). Promo / retail / reader sit far lower. Provenance multiplies:
`cited` 1.00 · `attributed` 0.70 · `draft` 0.35.

## Roles (one Cursor agent each)

See [`AGENT_ROLES.md`](AGENT_ROLES.md). Launch one cloud agent per role per
week; do not ask a harvest or seed agent to invent assessments. Signed
editorial is Role Critic — see [`CRITIC.md`](CRITIC.md).

## Weekly cadence

See [`WEEKLY_CADENCE.md`](WEEKLY_CADENCE.md). Each week:

1. Human confirms next five composers from [`proposals/composer-queue.json`](../../proposals/composer-queue.json).
2. **Seed agent** adds works + candidate recordings (no scores).
3. **Identity / covers agent** runs harvest → proposals (MB + CAA).
4. **Citation agent** emits citation tasks / award proposals for ≥5 named sources per assessed entry over time.
5. Humans ratify statements; composer rollup updates on `make site`.
6. **Critic** authors signed entries (Bach assessed set first) and lands them
   on `main` / Pages. Developer may ship that PR. No human merge babysit.

## Catalogue floor (10 · 100 · 500)

See [`CATALOGUE_TARGETS.md`](CATALOGUE_TARGETS.md). Drive with:

```bash
make targets             # exit 0 only when floors met
make loop                # targets + next week brief
```

## Human review (online)

See [`HUMAN_REVIEW.md`](HUMAN_REVIEW.md). Public board after publish:
`/review/` on GitHub Pages. Owner (`NZA-93`) alone applies **identity**
decisions; community comments land in `data/community/` and never mix with
editorial. Signed editorial is Critic’s path ([`CRITIC.md`](CRITIC.md)), not
this board.

```bash
make review-queue        # packs + review-decisions.json template
make review-apply-dry    # preview accepts
make review-apply        # owner applies mbids (facts only)
```

## Makefile entry points

```bash
make targets             # 10 composers · 100 works · 500 candidates
make queue-week          # print next 5 composers + agent brief
make expand-brief        # write proposals/WEEK_BRIEF.md for Cursor agents
make score && make site  # includes composers[] rollup + /review/ board
make review-queue        # human review packs for the current proposals file
```
