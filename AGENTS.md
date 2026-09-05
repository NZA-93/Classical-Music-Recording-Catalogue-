# AGENTS.md — rules for automated contributors

This file governs any autonomous or semi-autonomous agent working in this
repository, including Cursor loops, CI agents and scripted assistants. It is
binding in the same way tests are: a change that violates it is a defect,
regardless of how good it looks.

Read this before touching anything. If a task appears to require breaking a
rule here, **stop and ask a human**. That is not a failure state; it is the
system working.

---

## 1. The one rule everything else serves

**An agent never invents a critical judgement into the seed, the statements,
or the aggregate.**

No score. No star. No Référence flag. No sound assessment. No commentary that
evaluates a performance or a transfer — not in `data/seed.json`, not in
`data/statements/`, not as a draft, not as a placeholder, not "to be replaced
later", not even clearly marked as provisional.

The reason is not caution. A machine-written verdict with no source is
indistinguishable from a sourced one three months later, and the only thing
this guide has that a streaming service does not is that the distinction stays
visible. One convincing fabrication in the catalogue costs more than a year of
correct work.

If a harvest, seed, citation or apply task's definition of done includes
"assess", "rate", "score" or "judge" a recording *into those layers*, the task
is misdrafted. Stop and say so.

**Amendment (ADR-002).** Judgement does legitimately exist in this guide, in
exactly one place: the *signed editorial entry*, written in the named editorial
voice and closed with initials and a date.

**Amendment (Critic role).** That register is the job of the **Classical Music
Recording Critic** — the named editorial role, including the Critic agent
acting in that role. Critic may author the verdict (prose, stars, Référence)
and **must land it on `main` and live Pages**. There is no human merge babysit
on this path. The Developer role may merge or push a Critic editorial PR so it
ships. An entry still does not publish without an author id, a date and a
revision. See [`docs/automation/CRITIC.md`](docs/automation/CRITIC.md).

Other agents (seed, harvest, identity, citation, apply, rollup) may compute
the editorial queue, assemble the brief, check facts inside a signed entry
and publish an already-signed one. They may **not** draft a sentence of the
verdict, suggest a rating, complete a half-written entry, generate an entry
"for the author to edit", or write stars / Référence into seed or statements.
An unsigned entry is not a signed entry, whatever the byline says.

---

## 2. What agents may do

- Write and refactor code in `engine/`, `agents/`, `site/`, `tests/`
- Write and improve documentation
- Write to `proposals/` — machine output awaiting human review
- Correct **facts** (catalogue numbers, barcodes, dates, personnel, venues)
  when a source is cited in the commit message
- Add tests, fix failing tests, improve error messages
- Open pull requests, and respond to review comments on them
- **Critic:** write signed entries in `data/editorial/` and land them on `main`
  so Pages updates
- **Developer:** merge or push Critic editorial PRs so that content reaches
  `main` and live Pages — without inventing or rewriting the verdict

## 3. What agents must never do

- Write to `data/statements/` — the assessment layer is human-ratified
- Invent scores, stars, `reference` flags or confidence values in the seed,
  statements or aggregate, or invent any of those without a citation basis.
  Critic may set stars and Référence on a signed entry in `data/editorial/`
  only. The four Brandenburg / Tosca regression anchors must not move except
  through a deliberate, reviewed algorithm-version bump
- Merge a pull request, approve one, or push directly to `main` — **except**
  Critic editorial landings and the Developer path that ships that Critic
  content. Harvest proposals, identity applies, statement ingest and seed
  expansion still wait for a human merge. This exception is not a licence to
  land unsigned prose or invented aggregate scores
- Add a runtime dependency. Standard library only, in every language used here
- Store, paste or commit text copied from a review, sleeve note or article
  except inside a Critic-signed editorial entry, bounded by ADR-003. Other
  agents may not write, choose or place a quotation
- Bypass a paywall, ignore `robots.txt`, or route requests through proxies
- Perform automated collection against any publication's site without checking
  its terms, or OCR a copyrighted volume for paraphrase at scale. Print criticism
  enters through a human with the book and a page number — see
  `docs/legal/DIAPASON_INGESTION.md`
- Rehost cover images. Link to the Cover Art Archive; contribute new scans
  upstream to MusicBrainz instead
- Widen a harvest budget beyond what the task specifies
- Rewrite git history on a shared branch

## 4. Before every commit

```bash
python3 -m unittest discover -s tests -q     # must pass
python3 agents/validate.py                   # must exit 0
make site                                    # must produce all three pages
```

A commit that leaves any of these failing is not ready, even if the feature
works. The loop's most valuable property is that `main` is always publishable.

## 5. Working protocol

1. Take the **next unblocked task** from `SPRINTS.md`, in order. Do not
   reorder tasks to pick easier ones.
2. One task per branch: `task/S1-04-identity-review`.
3. Small commits with real messages. State what changed and why, and cite a
   source for any factual change.
4. Open a pull request using the template. Fill in the checklist honestly —
   an unchecked box with an explanation is worth more than a checked lie.
5. **Harvest / identity / citation / seed:** stop. Do not begin the next task
   while a human review is pending, unless the next task is genuinely
   independent. **Critic editorial:** do not wait for a human merge gate.
   Land on `main` (Critic merges, or Developer ships the Critic PR) so live
   Pages updates.

## 6. When to stop and ask

Stop, do not guess, if:

- A task seems to require judging musical or sonic quality **and you are not
  the Critic role writing a signed entry**
- A source's terms are unclear, or `robots.txt` cannot be read
- An identity match is ambiguous (a compilation, a sampler, a wrong decade)
- A change would alter existing **aggregate** scores as a side effect
- A test fails in a way you do not understand
- The task's acceptance criteria are ambiguous

Write the question in the pull request and stop. Twenty minutes of a human's
attention is cheaper than a silent corruption of the catalogue.

## 7. Regression guards you must not weaken

These four aggregate scores are fixed by test and must not change except
through a deliberate, reviewed algorithm-version bump:

| Recording | Interpretation | Référence |
|---|---|---|
| Pinnock — Brandenburgs | 2.853 | No |
| Harnoncourt — Brandenburgs | 2.814 | No |
| Callas / de Sabata — Tosca | 2.955 | **Yes** |
| Price / Karajan — Tosca | 2.848 | No |

If a refactor changes any of these, the refactor is wrong. Do not update the
test to match the new output.

## 8. Provenance is derived, never declared

A statement's tier comes from its evidence: a locator makes it `cited`, a named
source without one makes it `attributed`, neither makes it `draft`. Code that
lets a contribution assert its own tier is a bug. `agents/validate.py` enforces
this; do not add a bypass.
