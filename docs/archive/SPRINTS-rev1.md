> **Superseded by SPRINTS.md revision 2, 26 July 2026.** Kept for the record:
> awards were buried at S2-03 here, which was the wrong order.

# Sprints 1 and 2
### Two weeks, task by task · prepared 26 July 2026

Every task below is written to be executed by an agent loop and reviewed by a
human. Read `AGENTS.md` first; it overrides anything here that appears to
conflict with it.

**Conventions.** `[H]` human only · `[A]` agent may execute · `[A→H]` agent
prepares, human decides. Every task states what "done" means and the exact
command that proves it. Tasks run in ID order unless marked independent.

**Sprint rhythm.** One branch per task. Pull request, review, merge, next. The
loop stops when it reaches a `[H]` task and waits.

---

## Day 0 — preconditions

Nothing in Sprint 1 can start until these are true. Fifteen minutes of work.

### S1-00 · Push and configure `[H]`

```bash
cd Classical-Music-Recording-Catalogue-
git remote add origin https://github.com/NZA-93/Classical-Music-Recording-Catalogue-.git
git push -u origin main
```

Then, in repository settings:

- **Pages** → Source: *GitHub Actions* (not "deploy from a branch")
- **Variables** → `HARVEST_CONTACT` = an email you are willing to publish
- **Branches** → protect `main`: require a pull request, require the
  `validate` and `Build and publish` checks, **disallow self-approval**

That last switch is what makes the agent loop safe. Without it, `AGENTS.md`
§3 is a suggestion rather than a constraint.

**Done when:** the site is live at
`https://nza-93.github.io/Classical-Music-Recording-Catalogue-/` and a direct
push to `main` is refused.

---

# Sprint 1 — Live, verified, guarded
**Goal:** the site is published, all 58 candidates are resolved to real
MusicBrainz identities, editions and barcodes are populated, and the loop
cannot damage anything.

**Sprint is done when:** `make site` publishes three pages from data that has
been through a review, the barcode index holds more than 200 entries, and the
test suite guards every rule in `AGENTS.md` that can be tested.

---

### S1-01 · Tests in CI and in the loop `[A]`
**Depends on:** S1-00 · **Effort:** small

`tests/test_engine.py` exists with 24 tests and passes. It is not yet wired
into anything, which means nothing enforces it.

**Do:**
1. Add to `Makefile`:
   ```make
   test:            ## run the test suite
   	python3 -m unittest discover -s tests -q
   ```
2. Add a `test` step to `.github/workflows/validate.yml`, before the build
   check.
3. Add `.githooks/pre-commit` running `make test && make validate`, and
   document `git config core.hooksPath .githooks` in `README.md`.

**Done when:** `make test` passes; a deliberately broken assertion fails CI.
**Verify:** `make test && make validate && make site`
**Do not:** weaken or delete any regression assertion to make CI green.

---

### S1-02 · `agents/apply.py` — proposals into data `[A]`
**Depends on:** S1-01 · **Effort:** medium · **This is the missing link**

The harvest writes `proposals/*.json`. Nothing reads them. Until this exists,
every harvest round is theatre.

**Do:** write `agents/apply.py` that takes a proposals file and merges accepted
proposals into `data/seed.json`.

- `--proposals PATH` (required), `--dry-run`, `--only identity,editions,cover`
- Merge by `target` id. Never overwrite a field where `verified: true` unless
  `--force` is given with a reason recorded in the run log
- `identity` sets `mbid` and leaves `verified: false` — a machine match is not
  a verification
- `editions` appends edition records, **validating every barcode check digit
  before writing**; a failing barcode is dropped and reported, never stored
- `cover` records the resolved image URL or `null`
- Write `proposals/applied-<date>.json` recording exactly what changed, so the
  diff is reviewable
- Idempotent: applying the same file twice changes nothing the second time

**Done when:** applying the round-1 proposals populates mbids and the diff on
`data/seed.json` is human-readable.
**Verify:** `python3 agents/apply.py --proposals proposals/<file> --dry-run`
then apply, then `make test && make site`
**Do not:** apply anything to `data/statements/` (it does not exist yet, and
when it does it is out of bounds — `AGENTS.md` §3).

---

### S1-03 · `agents/review.py` — make the identity round reviewable `[A]`
**Depends on:** S1-02 · **Effort:** small

58 identity matches are about to need human judgement. A JSON blob is the wrong
surface for that.

**Do:** a script that prints, per proposal, side by side: the candidate as
seeded (performers, label, year) against the MusicBrainz match (title, artist,
first release date, match score), with a flag on anything suspicious —
`match_score < 80`, a date more than three years off, or a title containing
*best of*, *greatest*, *collection*, *anthology*, *sampler*, *highlights*.

Output plain text by default, `--markdown` for pasting into a pull request.

**Done when:** reviewing 58 matches takes under fifteen minutes.
**Verify:** `python3 agents/review.py proposals/<file> --markdown`

---

### S1-04 · First live identity round `[A→H]`
**Depends on:** S1-03 · **Effort:** small to run, real to review

**Do:**
```bash
make plan                                    # confirm 58 requests
python3 agents/harvest.py data/seed.json --contact "$CONTACT" --budget 300
python3 agents/review.py proposals/<file> --markdown > /tmp/review.md
```
Open a pull request with the review table in the body. **The agent stops here.**

**Human:** work the table. Reject anything that looks like a compilation. Expect
a real rejection rate — MusicBrainz search will happily return a 2011 budget box
for a 1962 Decca set. Delete rejected entries from the proposals file, note the
count in the PR, then merge and run `apply.py`.

**Done when:** every candidate has an mbid or has been struck from the seed.
**Do not:** auto-accept low-scoring matches. An identity error propagates into
editions, barcodes and covers, and is expensive to unpick later.

---

### S1-05 · Editions and barcodes `[A→H]`
**Depends on:** S1-04 · **Effort:** medium

Run the harvest again; with mbids present it advances to the `editions` stage.
Up to 25 releases per recording.

**Human review focuses on one thing:** that the releases genuinely belong to
this recording and not to a coupling that happens to share a release group.

**Done when:** the barcode index exceeds 200 entries and every stored barcode
passes its check digit.
**Verify:** `make site` — the build line on `entries.html` reports the count.

---

### S1-06 · Covers `[A]`
**Depends on:** S1-05 · **Effort:** small · *independent of S1-07*

Third harvest stage. Record hits and misses; misses are re-checked fortnightly
and are not failures — they are contribution prompts.

**Done when:** every resolved recording has a cover URL or an explicit `null`,
and the typeset plate renders wherever `null` appears.
**Do not:** download or commit any image (`AGENTS.md` §3).

---

### S1-07 · Barcode index as its own artefact `[A]`
**Depends on:** S1-05 · **Effort:** small

The index is currently embedded in `catalogue.json`, which the shop lookup
loads in full. Split it: `docs/barcodes.json`, `{barcode: {recording, edition}}`,
fetched on demand by the lookup, cached by the service worker.

**Done when:** the identification field works with `catalogue.json` unloaded,
and `docs/barcodes.json` is under 100 KB for 1000 entries.

---

### S1-08 · Coverage metrics `[A]`
**Depends on:** S1-05 · **Effort:** small

`agents/metrics.py` computing the four numbers from `PROGRAM.md` §7: citation
ratio, editions per recording, barcode coverage, sound coverage. Write
`build/metrics.json`; surface them on the catalogue index, replacing the
hand-computed tally.

**Done when:** the numbers on the index page are generated, not typed, and CI
prints them in the job summary.

---

### S1-09 · Sprint close `[H]`
Read the week's diffs. Confirm the four regression scores are untouched. Tag
`v0.2-identity`.

---

# Sprint 2 — First cited scores
**Goal:** the assessment layer moves out of code into reviewable data, and the
first genuinely cited statements enter the catalogue — from award lists, which
are facts rather than prose.

**Sprint is done when:** at least 30 statements carry `provenance: cited`, at
least 12 works have any assessment, and no score in the repository originates
from a model.

---

### S2-01 · Statements out of code `[A]`
**Depends on:** S1-09 · **Effort:** large · **Blocking for everything else**

Assessments are currently hardcoded in `catalogue()` inside
`engine/aggregation_engine_v2.py`. No contributor can add one without editing
Python, and no review can be about data alone.

**Do:**
1. Define `data/statements/<composer>/<work>.json` — a list of statement
   objects matching the contribution schema, plus `edition` and `method`.
2. Move `data/recordings/<composer>/<work>.json` for the recording-level facts
   (personnel, venue, sessions, credits, anchors, reception, editions).
3. Rewrite the engine to read these directories. `catalogue()` becomes a loader.
4. **The four regression scores must be identical to three decimal places.**

**Done when:** `make test` passes unchanged and `git diff build/catalogue.json`
shows no change in any score.
**Verify:** `make test && make site && git diff --stat build/catalogue.json`
**Do not:** adjust a single score to make the migration come out even. If a
score moves, the loader is wrong.
**Stop and ask if:** the reception and anchor fields resist a clean schema.

---

### S2-02 · `agents/ingest.py` — contributions into statements `[A]`
**Depends on:** S2-01 · **Effort:** medium

`contributions/*.json` are validated and then go nowhere.

**Do:** ingest validated contributions into `data/statements/`, deriving
provenance from evidence (never from the declared field), stamping `method`
(`human` or `agent:<model>@<version>`) and `ingested_at`. Refuse to ingest
anything `validate.py` rejects. Duplicate detection on
`(recording, source, locator)`.

**Done when:** the example contribution ingests, the engine picks it up, and
the site shows it in the source table with the right tier.
**Do not:** let ingest run automatically on merge. A human runs it.

---

### S2-03 · Awards adapter `[A→H]`
**Depends on:** S2-02 · **Effort:** medium · **Highest-yield task in the fortnight**

Awards are facts, and facts can be gathered without a copyright question. See
`HARVEST_STRATEGY.md` §A.

**Do:**
1. `data/awards/<award>.json` — `{award, year, category, recording_hint, url}`.
2. `agents/adapters/awards.py` matching an award record to a recording in the
   catalogue, emitting a proposal with `scale: award`, `provenance: cited`
   (the citation is the award announcement URL), `conflict: false`.
3. Seed with *Gramophone Award* and *Diapason d'Or* entries touching the 47
   works. **The agent may gather candidates; a human confirms each match**,
   because "Karajan, Tosca" in an award list is not by itself an identification.

**Done when:** at least 30 cited award statements are in `data/statements/`
and at least one recording earns Référence on award evidence alone.
**Do not:** infer an award. If the list does not say it, it did not happen.

---

### S2-04 · Extraction controls `[A]`
**Depends on:** S2-02 · **Effort:** medium

Before any model reads a review, the controls from `HARVEST_STRATEGY.md` §E
must exist.

**Do:**
- `method` recorded on every statement and displayed in the source table
- **Double extraction:** two independent passes; a disagreement over 0.4 on
  the 0–3 scale holds the statement for a human instead of ingesting it
- `agents/audit.py` sampling 10% of machine extractions for human re-reading
  and reporting the agreement rate into `build/metrics.json`

**Done when:** a statement with `method: agent:*` cannot enter
`data/statements/` without having passed double extraction.
**Do not:** implement any extraction that emits a score without a locator.

---

### S2-05 · Credits from MusicBrainz `[A]`
**Depends on:** S2-01 · **Effort:** medium · *independent of S2-03*

Producer, engineer and venue sit in MusicBrainz release relationships, CC0,
unread. That is half of the guide's stated judgement arriving free.

**Do:** an adapter reading release and recording relationships, proposing
`engineering.producer`, `engineering.engineer`, `engineering.venue` with
`credits_status: cited` and the MusicBrainz URL as locator.

**Done when:** at least half the resolved recordings carry a cited producer or
engineer, and the "not established — contribute" prompt appears only where the
data genuinely does not exist.

---

### S2-06 · Sound-axis intake `[A]`
**Depends on:** S2-02 · **Effort:** medium

The edition-comparison issue template collects the one thing agents cannot
produce. Nothing converts those issues into statements.

**Do:** a script turning a completed comparison issue into a `sound` statement
against a named edition, `method: human`, `provenance: attributed` (the
contributor is the source; there is no external locator), with the comparison
recorded in full.

**Done when:** one real comparison completes the round trip from issue to
rendered edition verdict.
**Stop and ask if:** a comparison names editions not in the catalogue — that is
an editions gap, not a contribution to reject.

---

### S2-07 · The twelve `[H]` with `[A]` support
**Depends on:** S2-03 · **Effort:** the week's real work

Push the twelve densest works to three cited statements each: Brandenburgs,
Goldbergs, Cello Suites, Ninth, Fifth, Missa Solemnis, Figaro, Don Giovanni,
Requiem, Bohème, Tosca, Butterfly. Three independent high-weight sources is
the threshold at which Référence becomes possible at all.

**Done when:** twelve works have assessments and the coverage bar on the index
moves from 4% to roughly 26%.

---

### S2-08 · Sprint close `[H]`
Review every statement that entered this fortnight. Confirm no score originates
from a model without a locator. Tag `v0.3-cited`.

---

## Explicitly out of scope for both sprints

Cover OCR and perceptual hashing · the interactive service (Strategy B) ·
composers beyond the four · Discogs integration of any kind · rehosting images ·
service worker and offline mode beyond S1-07 · any change to the four
regression scores.

## Risk register

| Risk | Watch for | Response |
|---|---|---|
| Identity errors propagate | Editions that do not fit the recording | Reject at S1-04; never auto-accept below score 80 |
| Loop merges its own work | A PR approved by the same actor that opened it | Branch protection, S1-00. Verify it actually blocks |
| Score drift during S2-01 | Any regression test failure | Stop. The loader is wrong, not the test |
| Model-written assessment enters | A statement with no locator | S2-04 controls; audit sample every sprint |
| Award match ambiguity | "Karajan, Tosca" with no year or label | Human confirms every award match |
| Scope creep into composer five | New works appearing in the seed | Out of scope until citation ratio is healthy |

## What I would watch after two weeks

The citation ratio is the only number that matters. Identity, editions,
barcodes and covers are all tractable engineering, and an agent loop will grind
through them. Assessments will not arrive that way — they arrive from award
lists, from libraries, and from people who own the records. If the ratio is
still near zero at the end of Sprint 2, the constraint is editorial, not
technical, and no amount of pipeline will fix it.
