# Sprints 1 and 2 — revision 2
### Two weeks to a live guide that says something · revised 26 July 2026

Supersedes revision 1. Rewritten after ADR-002 (the signed entry), ADR-003
(quotation) and the legal note on print sources, all of which changed what is
worth doing first.

Read `AGENTS.md` before executing anything here. It is binding and overrides
this document wherever the two appear to conflict.

**Conventions.** `[H]` human only · `[A]` agent may execute · `[A→H]` agent
prepares, human decides · `[C]` Critic authors and lands on `main`. Every task
states what "done" means and the command that proves it. One branch per task,
in ID order. The harvest loop stops at a `[H]` task and waits. **Critic
editorial (`[C]`) does not wait for a human merge gate** — see
[`docs/automation/CRITIC.md`](docs/automation/CRITIC.md).

---

## State on the day this was written

| | |
|---|---|
| Composers · works · candidate recordings | 5 · 59 · 72 |
| Recordings in the catalogue | 7, of which 5 carry any assessment |
| Statements | 19, of which **1 is `cited`** — 5% |
| Editions tracked · with a verified barcode | 21 · 6 |
| Signed editorial entries | **0** |
| Tests · commits | 33 passing · 12 |
| Published | **not yet** |

Two numbers govern the fortnight. **The guide is not online.** And **95% of what
it says rests on statements nobody can check.** Everything below serves those.

---

## What changed from revision 1, and why

**Awards moved from Sprint 2 into Sprint 1.** They are the only source of
criticism that is legally clean, publicly verifiable and available without
anyone's permission, because an award is a fact rather than an expression. In
revision 1 they sat at S2-03 while the plan spent a week on plumbing. That was
the wrong order: the guide currently has almost nothing to say, and awards are
the cheapest way to change it.

**Editorial work is now a first-class sprint item.** ADR-002 made the signed
entry the thing that gives this guide its value. A plan that never schedules one
is a plan for a nicer aggregator.

**Print sources are handled by a human with a book and a page number.** No
scraping task appears anywhere in this plan. See
`docs/legal/DIAPASON_INGESTION.md`.

**S1-01 is already done** — tests, hooks and CI wiring landed while revision 1
was being written. It is struck through below rather than deleted, so the loop
does not redo it.

---

# Sprint 1 — Live, and speaking

**Goal:** the site is published, every claim it makes is checkable, and `cited`
statements go from one to at least thirty.

**Done when:** the guide answers at its public URL, the citation ratio is above
50%, and the coverage figure on the index is generated rather than typed.

---

### S1-00 · Go live `[H]` · blocks everything

```bash
git remote add origin https://github.com/NZA-93/Classical-Music-Recording-Catalogue-.git
git push -u origin main
```

Then in settings:

- **Pages** → Source: *GitHub Actions*
- **Variables** → `HARVEST_CONTACT` = a publishable email address
- **Branches** → protect `main`: require a pull request, require the `validate`
  and `Build and publish` checks, **disallow self-approval**

That last switch is what makes the **harvest** loop safe. Test it by attempting
a direct push of harvest or statement work to `main` and confirming refusal.

> **Amendment (Critic landing).** Branch protection and the "disallow
> self-approval" rule remain for harvest, identity, seed and statements.
> They do **not** gate Critic signed-editorial landings. Critic (or Developer
> shipping Critic content) may merge those PRs or push that path to `main`
> so Pages updates. See `docs/automation/CRITIC.md`.

**Done when:** the site answers at
`nza-93.github.io/Classical-Music-Recording-Catalogue-/` and a direct harvest
push to `main` is rejected.

---

### ~~S1-01 · Tests in CI and in the loop~~ `[done]`

33 tests, wired into `validate.yml`, the `Makefile` and `.githooks/pre-commit`.
Enable the hook locally: `git config core.hooksPath .githooks`.

---

### S1-02 · `agents/apply.py` — proposals into data `[A]`
**Depends on:** S1-00 · **Effort:** medium · **Still the missing link**

The harvest writes `proposals/*.json`. Nothing reads them, so every harvest to
date has been theatre.

**Do:** merge accepted proposals into `data/seed.json` and `data/recordings/`.

- `--proposals PATH`, `--dry-run`, `--only identity,editions,cover`
- merge by `target` id; never overwrite a `verified: true` field without
  `--force` and a reason written to the run log
- `identity` sets `mbid` and leaves `verified: false` — a machine match is not a
  verification
- `editions` appends records, **validating every barcode check digit before
  writing**; a failing barcode is dropped and reported, never stored
- write `proposals/applied-<date>.json` so the change is reviewable
- idempotent: applying the same file twice changes nothing the second time

**Verify:** `python3 agents/apply.py --proposals proposals/<file> --dry-run`,
then apply, then `make test && make site`
**Do not:** write to `data/statements/` or `data/editorial/` from this script,
ever. Those layers are human-ratified.

---

### S1-03 · `agents/awards.py` — the citation engine `[A]`
**Depends on:** S1-02 · **Effort:** medium · **Highest yield in the fortnight**

`data/awards/grammy.json` and `gramophone.json` exist as a worked shape. The
adapter that consumes them does not.

**Do:**

1. Read `data/awards/*.json`; match `covers_works` and `performers` to
   recordings. Emit a **proposal** per match, never a direct ingest.
2. Emit `scale: award`, `provenance: cited`, `class: major_award`,
   `conflict: false`, locator = the announcement URL.
3. **Implement ADR-001.** An award covering *n* works carries `covers_works` and
   counts as **one shared benchmark signal**, not one per work. A three-symphony
   album award must never read as three independent endorsements.
4. Flag every match for human confirmation. "Karajan, Tosca" in an award list is
   not an identification.

**Done when:** running it over the current award files produces correct
proposals and ADR-001 is enforced by a test.
**Do not:** infer an award. If the list does not say it, it did not happen.
**Note:** the Petrenko 2011 record is sourced from Naxos's own announcement. The
award is a public fact; the praise on that page is label promotion and must not
be ingested as criticism.

---

### S1-04 · Award harvest across 59 works `[A→H]`
**Depends on:** S1-03 · **Effort:** the week's real work

Gather records for **Diapason d'Or** and **Diapason d'Or de l'Année**,
**Gramophone Awards**, **Grammy** (Best Orchestral, Opera, Choral), **BBC
Building a Library** first choices, **Choc de Classica**, **Preis der deutschen
Schallplattenkritik**.

The agent gathers candidates with locators. **A human confirms every match**
before anything enters `data/statements/`.

**Done when:** at least 30 `cited` statements exist and the citation ratio is
above 50%.
**Stop and ask if:** a list names a conductor and a work but no year or label,
and more than one recording fits.

---

### S1-05 · No-source-text CI guard `[A]`
**Depends on:** S1-03 · **Effort:** small · *independent*

`validate.py` enforces the 240-character limit and the quoted-run check on
contributions, and ADR-003 limits on editorial entries. Nothing checks `data/`
itself.

**Do:** a CI step scanning every JSON under `data/` for characterisations over
the limit, quoted runs, or any field that reads as reproduced prose. Fail the
build. This is the mechanical half of the legal posture and it should not depend
on anyone remembering.

**Done when:** planting a 400-character pasted paragraph in a statement file
fails CI.

---

### S1-06 · Identity round `[A→H]`
**Depends on:** S1-02 · **Effort:** small to run, real to review

```bash
make plan
python3 agents/harvest.py data/seed.json --contact "$CONTACT" --budget 300
python3 agents/review.py proposals/<file> --markdown > /tmp/review.md
```

`agents/review.py` does not exist yet — build it here. It prints each proposal
side by side, candidate as seeded against the MusicBrainz match, flagging
`match_score < 80`, a date more than three years off, or a title containing
*best of*, *collection*, *anthology*, *sampler*, *highlights*.

**Human:** work the table. Expect real rejections. Delete rejected entries,
record the count in the pull request, merge, run `apply.py`.

**Done when:** every candidate has an mbid or has been struck from the seed.
**Do not:** auto-accept low-scoring matches. Identity errors propagate into
editions, barcodes and covers and are expensive to unpick later.

---

### S1-07 · Send the letters `[H]`
**Depends on:** S1-00, so they can link to a live site · **Effort:** an hour

- `docs/legal/lettre-editis.md` → Éditions Robert Laffont / Editis, rights and
  permissions, for the 1991 *Dictionnaire*
- `docs/legal/lettre-reworld.md` → Reworld Media, for the magazine and the
  *Diapason d'Or*

Ask for **ratings with links only**. Quotation is a later, narrower, separate
request (ADR-003). Opening with the larger ask risks a documented refusal, which
is materially worse than no answer.

**Also this week:** one approach to a conservatoire or university music library
about the out-of-commerce works route (DSM Arts 8–11). The institution can be
the beneficiary; a private project cannot.

---

### S1-08 · Sprint close `[H]`

Read the week's diffs. Confirm the four regression scores are untouched and that
no source text entered `data/`. Tag `v0.2-live`.

---

# Sprint 2 — The voice

**Goal:** the guide acquires the thing that makes it worth reading, and the
migration that lets contributors work in data rather than Python is finished.

**Done when:** three signed entries are published, the divergence view exists,
and `catalogue()` holds no hardcoded assessment.

---

### S2-01 · Finish the migration out of code `[A]`
**Depends on:** S1-08 · **Effort:** large · **Blocking**

`load_from_data()` exists and Shostakovich uses it. The four original recordings
are still hardcoded in `catalogue()`, so the identifier schemes are inconsistent
(`bach_brandenburg` against `bach/brandenburg`, already patched around in
`editorial_queue.py`) and no contributor can touch them without editing Python.

**Do:** move all four into `data/recordings/` and `data/statements/`, unify the
identifiers, delete `catalogue()`, remove the `ALIAS` workarounds in
`build_site.py` and `editorial_queue.py`.

**The four published scores must be identical to three decimal places.**

**Verify:** `make test && make site && git diff --stat build/catalogue.json`
**Do not:** adjust a score to make the migration come out even. If one moves,
the loader is wrong, not the test.

---

### S2-02 · `agents/ingest.py` — contributions into statements `[A]`
**Depends on:** S2-01 · **Effort:** medium

Validated contributions currently go nowhere. Ingest them into
`data/statements/`, deriving provenance from evidence rather than the declared
field, stamping `method` and `ingested_at`, refusing anything `validate.py`
rejects, and detecting duplicates on `(recording, source, locator)`.

Two contributions are already waiting: the maintainer's Noseda notes, filed at
`scale: prose, value: null`. They stay unscored until a human assigns a number
and signs for it. That is correct behaviour and should be **visible in the
output**, not silently skipped.

**Do not:** run ingest automatically on merge. A human runs it.

---

### S2-03 · The editorial workflow `[A]`
**Depends on:** S2-01 · **Effort:** medium

Writing a signed entry currently means hand-editing JSON. Make it a command.

- `make entry` takes the top of `editorial_queue.py`, scaffolds a stub in
  `data/editorial/`, and prints a **brief**: the recording's facts, editions,
  credits, what the aggregate says, which sources it rests on, and which
  competing recordings exist.
- Validate on save through `validate_editorial()`.
- **The brief contains no draft prose, no suggested rating and no sentence the
  Critic might keep.** ADR-002. Roles A–E assemble the ground; Critic writes
  the entry. Do not generate an entry "for the author to edit".

**Done when:** the round trip from `make entry` to a rendered signed block costs
under a minute of tool friction.

---

### S2-04 · Write the first signed entries `[C]` · Critic lands to main
**Depends on:** S2-03 · **First target:** Bach assessed set on work pages

Nicolò’s mandate: Dictionnaire-style signed entries on work pages, **Bach
assessed set first** (the critic-signed IDs already on public cards). The old
queue ranking (Shostakovich 5, Tosca) still describes later need; it is not
the first cut.

**Do:** Critic authors signed entries in `data/editorial/` (author, date,
revision, stars, comparative prose). Land on `main` / Pages — no human merge
babysit. Developer may ship the Critic PR.

**Do not:** invent aggregate or statement scores; weaken the four regression
anchors; have Roles A–E draft verdict prose. This sprint item does not ask a
non-Critic agent to invent Bach review text.

**Done when:** Bach assessed-set work pages carry Critic-signed entries (or
the first of that set has landed), each with author, date, revision and stars.

---

### S2-05 · The divergence view `[A]`
**Depends on:** S2-04 · **Effort:** small · **The feature nobody else has**

A page ranking recordings by the gap between the signed verdict and the
aggregate, showing both figures and linking into the entry. Consensus against a
named person who listened, with the disagreement stated rather than resolved.

**Done when:** it renders from `divergence`, which the engine already computes,
and reads as an invitation rather than an erratum.

---

### S2-06 · Editions and barcodes `[A→H]`
**Depends on:** S1-06 · **Effort:** medium

Second harvest stage; with mbids present it advances automatically. Human review
focuses on one thing: that the releases belong to this recording and not to a
coupling that shares a release group.

**Done when:** the barcode index exceeds 200 entries and every stored barcode
passes its check digit.

---

### S2-07 · Covers `[A]`
**Depends on:** S2-06 · **Effort:** small · *independent*

Record hits and misses. Misses are contribution prompts, not failures. Where a
reader photographs a missing sleeve, the destination is **MusicBrainz and the
Cover Art Archive**, not this repository.

**Do not:** download or commit any image.

---

### S2-08 · Metrics `[A]`
**Depends on:** S2-01 · **Effort:** small

`agents/metrics.py` computing citation ratio, editions per recording, barcode
coverage, sound coverage and signed-entry count into `build/metrics.json`, shown
on the index and printed into the CI job summary. Replaces the hand-computed
tally.

**Done when:** the numbers on the index are generated, not typed.

---

### S2-09 · Sprint close `[H]`

Review every statement that entered. Confirm no aggregate score originates
from a model without a locator, and that every signed entry was authored by
the Critic role (not by a harvest or seed agent). Tag `v0.3-voice`.

---

## Out of scope for both sprints

Cover OCR and perceptual hashing · the interactive service ·
Discogs integration of any kind · rehosting images · **any scraping of a
publication's site** · any change to the four regression scores.

> **Amendment (automation track).** Adding composers beyond the original five is
> no longer forbidden. Growth is paced at **five well-known composers per week**
> via `proposals/composer-queue.json` and `docs/automation/`. Seed expansion
> remains facts-only; assessments still require cited sources. Scraping
> publication sites remains forbidden.

---

# Sprint 3 — Weekly expansion & origin-weighted composer rollup

**Goal:** the catalogue grows by five composers each week, cover art resolves
through the Cover Art Archive, and each assessed recording accumulates citations
toward ≥5 independent sources. A composer-level figure exists only as a rollup
of ratified statements weighted by review origin (class × provenance).

**Orchestration:** [`docs/automation/README.md`](docs/automation/README.md).

### S3-00 · Automation structure `[A]` · this track
Docs, composer queue, `agents/weekly_expand.py`, `aggregate_composer()`, site
display of rollups. **Done when:** `make expand-brief && make test && make site`.

### S3-01 · Week batch seed `[A]`
Role A implements the next five composers from the queue into
`engine/seed_catalogue.py`. No scores.

### S3-02 · Identity + covers for the new batch `[A]`
Role B harvest → proposals only. CAA hotlinks; never rehost images.

### S3-03 · Citation drive to ≥5 sources `[A→H]`
Role C emits award/citation proposals for assessed recordings. Human ratifies
into `data/statements/`. Stretch target: 10 sources.

### S3-04 · Apply / review tooling land `[A]`
Merge or re-implement `apply.py` / `review.py` from prior `cursor/s1-*` branches
so proposals become seed/recording facts without touching statements.

### S3-05 · Catalogue floor 10 · 100 · 500 `[A]`
**Done when:** `make targets` exits 0 (≥10 composers, ≥100 works, ≥500
candidate recordings). Densify via `engine/seed_candidates_dense.py`; facts
only. Then Role B harvest in budgeted rounds until identity coverage rises;
humans ratify; never apply `wrong work:` rows.

---

# Ongoing loop (after the floor)

Raise the ceiling in `docs/automation/CATALOGUE_TARGETS.md` and keep the same
Roles A→D cycle. Citation ratio remains the aggregate bottleneck — densifying
candidates does not invent assessments. Signed entries are Critic’s path
(`[C]`, `docs/automation/CRITIC.md`) and land on `main` / Pages without a
human merge gate.

## Risk register

| Risk | Watch for | Response |
|---|---|---|
| Harvest loop merges its own work | A harvest/identity PR approved by the actor that opened it | Branch protection, S1-00. Does **not** apply to Critic editorial landings |
| Identity errors propagate | Editions that do not fit the recording | Reject at S1-06; never auto-accept below 80 |
| Score drift in S2-01 | Any regression failure | Stop. The loader is wrong, not the test |
| Album awards over-counted | A three-work award reading as three signals | ADR-001, enforced by test in S1-03 |
| Source text enters `data/` | Long characterisations, quoted runs | S1-05 CI guard |
| An unauthorised agent drafts a signed entry | Prose in `data/editorial/` with no Critic author / unsigned | `validate_editorial()`; unsigned does not publish. Only Critic authors |
| Trademark drift | "Diapason" migrating toward the product name | Nominative use only, never in branding |
| Documented refusal | Asking for quotation before ratings | S1-07 order: the small ask first |

## The number to watch

**Citation ratio.** It is 5% today. Identity, editions, barcodes and covers are
tractable engineering and the loop will grind through them, and none of it makes
the guide worth reading. If the ratio is not above 50% by the end of Sprint 1,
the constraint is editorial rather than technical, and no further pipeline will
fix it.
