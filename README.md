# Classical Music Recording Catalogue

A work-first critical guide to classical recordings, in the tradition of the
*Dictionnaire des disques Diapason* — with two differences that decide everything else.

**Two judgements, kept apart.** *Interpretation* belongs to the recording and never
changes. *Sound* belongs to the edition — the pressing, the transfer, the remastering —
and changes every time a label reissues it. Stars and Référence describe the
interpretation only. The sound figure describes one specific disc, which is the thing
you are holding in a shop.

**Two registers, never blended.** Where someone has listened, you get a *signed entry*
— named, dated, opinionated, in the tradition of the *Dictionnaire des disques Diapason*.
Everywhere else you get the *aggregate*: the weighted consensus of published sources.
Neither feeds the other. When they disagree, the guide says so, because that disagreement
is the most interesting thing on the page.

**Every claim shows its receipt.** Source class sets a base weight; independence and
citation scale it. A cited statement counts fully, a named source without a locator
about seven-tenths, an uncited draft about a third. Commercial interest in a recording
cuts the weight outright. Nothing is hidden: each entry displays who its verdict rests on.

No advertising. No affiliate links. A guide that discounts commercial interest cannot
take a share of the sale.

---

## State of the catalogue

| | |
|---|---|
| Composers | 5 — Bach, Beethoven, Mozart, Puccini, Shostakovich |
| Works | 59 |
| Candidate recordings | 72, awaiting identity verification |
| Recordings assessed | 7 |
| Growth plan | +5 well-known composers / week (`proposals/composer-queue.json`) |

That coverage figure is the honest one. A guide that hides its gaps cannot ask anyone to
fill them. Agent coordination lives in [`docs/automation/`](docs/automation/README.md).

---

## Layout

```
data/seed.json          editorial truth: works and candidate recordings. No scores.
engine/                 seed generator and the aggregation engine (algorithm v2.0)
agents/                 the harvest pipeline and the cover-art resolver
site/                   templates and renderers
build/catalogue.json    machine-written results, committed so diffs are reviewable
docs/                   the published site: catalogue index, report view, gallery
```

## Build

Python 3.11+, standard library only. No dependencies to install.

```bash
make                        # seed, score, render
make plan                   # cost a harvest round without making requests
make harvest CONTACT=you@example.org
python3 agents/validate.py  # check contributions before opening a pull request
```

## How the pipeline works

```
identity  →  editions  →  covers  →  citations
```

Agents resolve recordings against MusicBrainz, pull editions and barcodes, check the
Cover Art Archive, and emit citation *tasks*. **Harvest, seed and citation agents never
write a verdict into the seed or the aggregate.** A machine-written assessment with no
locator is indistinguishable from a real one three months later, and that distinction is
the only thing this guide has. Those proposals arrive as pull requests; a human merges
them. Stages are gated on merged proposals, so the harvest pipeline cannot build on its
own unreviewed guesses.

**Signed editorial is a different path.** The Classical Music Recording Critic authors
Dictionnaire-style entries in `data/editorial/` and lands them on `main` so live Pages
updates. There is no human merge babysit on that path. Developer may merge or push a
Critic editorial PR. See [`docs/automation/CRITIC.md`](docs/automation/CRITIC.md).

## Contributing

Readers are better than agents at the one thing that matters most here: listening. The
sound axis needs structured A/B comparisons between editions — which two, on what
equipment, what specifically changed. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licences

Code MIT · factual catalogue data CC0 · editorial prose CC BY-SA 4.0.
Cover images belong to their rights holders and are hotlinked, never rehosted.
Published criticism is referenced by locator and normalised score; review text is never
stored here. See [LICENSE-CONTENT](LICENSE-CONTENT).

## Working on this

Automated contributors: read [AGENTS.md](AGENTS.md) first — it is binding.
Current work is planned in [SPRINTS.md](SPRINTS.md).

```bash
git config core.hooksPath .githooks   # run tests and validation before each commit
make test
```

## Documents

- [docs/legal/DIAPASON_INGESTION.md](docs/legal/DIAPASON_INGESTION.md) — how print criticism enters lawfully
- [docs/adr/ADR-003-quotation.md](docs/adr/ADR-003-quotation.md) — why this is not Wikipedia
- [docs/adr/](docs/adr/) — architecture decisions, including the editorial voice
- [docs/automation/CRITIC.md](docs/automation/CRITIC.md) — Critic signed-entry path to `main` / Pages
- [SPRINTS.md](SPRINTS.md) — the next two weeks, task by task
- [AGENTS.md](AGENTS.md) — rules for automated contributors
- [HARVEST_STRATEGY.md](HARVEST_STRATEGY.md) — where assessments can lawfully come from, and the cover-art ladder
- [PROGRAM.md](PROGRAM.md) — the harvest programme and its milestones
- [CORE_AND_CONTRIBUTION.md](CORE_AND_CONTRIBUTION.md) — the two-axis model, disc identification, contribution governance
- [DEPLOYMENT_AND_REFRESH.md](DEPLOYMENT_AND_REFRESH.md) — hosting, refresh cadence, resource budgets
