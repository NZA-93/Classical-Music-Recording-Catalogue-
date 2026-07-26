# Development Programme — Agent Harvest
### Critical Discography · round 1 · 26 July 2026

---

## 0. The line this programme does not cross

Agents gather **identity, editions and citations**. They do not write verdicts.

A machine-written assessment with no locator is indistinguishable, three months later, from a real one — and the entire value of this guide is that the distinction stays visible. So the catalogue now contains 47 works and 58 candidate recordings and **not one seeded score**. Every work reads `awaiting sources`, which is the true state of it.

This is also why the round-1 numbers look modest. They are real.

---

## 1. Scope seeded

| Composer | Works | Candidate recordings |
|---|---|---|
| Johann Sebastian Bach | 12 | 16 |
| Ludwig van Beethoven | 12 | 16 |
| Wolfgang Amadeus Mozart | 12 | 15 |
| Giacomo Puccini | 11 | 11 |
| **Total** | **47** | **58** |

Works are facts: catalogue number, date, and a line on why the guide carries it. Candidates are also facts — performers, conductor, ensemble, label, year — held at `verified: false` until MusicBrainz confirms them. Four recordings carry assessments, inherited from the earlier work on the Brandenburgs and Tosca.

---

## 2. The four stages, and why they run in this order

```
identity  →  editions  →  covers  →  citations
```

**1 · Identity.** Resolve each candidate to a MusicBrainz release-group. CC0 data, one request each, exact. Unresolvable candidates are dropped rather than carried forward as guesses. *58 requests.*

**2 · Editions.** Pull every release under the group: label, catalogue number, barcode, format, country. This is the second-hand layer and the reason the barcode lookup works in a shop. *~58 requests, one per resolved recording, 25 releases each.*

**3 · Covers.** Ask the Cover Art Archive whether a front image exists. Misses are re-checked fortnightly because the archive grows. *~58 requests.*

**4 · Citations.** No network at all. For each recording the pipeline emits a task naming the publication, what to look for, and what must come back: a locator, a normalised score, and a one-sentence characterisation *written for this guide*. It never returns copied review text. This is the stage where humans and reading agents work, and it is the only stage that produces a score.

Stages are gated on each other: editions and covers require an mbid, and an mbid only exists once an identity proposal has been reviewed and merged. The pipeline is not permitted to build on its own unreviewed guesses. Round 1 therefore resolves identity; round 2, after the pull request lands, goes deeper.

**Round 1 is 58 requests.** Inside a 300-request budget, well inside MusicBrainz's one-per-second courtesy limit, and finishing in about two minutes.

---

## 3. What the agents may touch

| Source | Licence | Use |
|---|---|---|
| MusicBrainz | CC0 | identity, editions, barcodes, catalogue numbers |
| Cover Art Archive | images owned by rights holders | existence check and hotlink; no rehosting without a decision |
| Wikidata / Wikipedia | CC0 / CC BY-SA | work metadata, premiere dates, notable recordings |
| Gramophone, Diapason, ClassicsToday, Fanfare, MusicWeb, Penguin Guide | **copyrighted** | pointer only — locator, normalised score, own-words characterisation |

Review text is not stored and not republished. Sites whose terms forbid automated access are not scraped; their material enters through a reader or editor citing an issue and page, which is both lawful and better evidence.

A practical finding from building this: `robots.txt` on musicbrainz.org disallows `/ws/`, because that file governs *crawlers* and the endpoint is meant for identified clients under a published rate limit. The client therefore treats declared APIs as a separate category — rate limit strictly honoured, robots gate bypassed — while everything reached as HTML must pass the gate, and anything whose robots file cannot be read is skipped rather than assumed permitted.

---

## 4. Score normalisation

Publications rate differently; the guide stores 0–3. Conversions are fixed and in code: five-star and three-star scales scale linearly, ten-point and percentage likewise, a Diapason d'Or or Gramophone Award enters at 2.90, an Editor's Choice at 2.85, a Penguin rosette at 2.95.

Prose-only sources — Fanfare, most newspaper criticism — return `None` from the converter **by design**. A human assigns the number, and their name goes on it. Guessing here is the most tempting and most corrosive shortcut available.

---

## 5. Cadence and cost

| | When | Cost |
|---|---|---|
| Identity sweep | once, then for new candidates | 58 requests |
| Editions | after identity merges, then quarterly | ~58 |
| Covers | quarterly on hits, fortnightly on misses | ~58 |
| Citation tasks | continuous, human-paced | none |
| Render | every push | none |

Weekly harvest with a 300-request budget and a persisted cursor; a run that hits the cap resumes next week. Every run writes `proposals/*.json` and a `PR_BODY.md` with a review checklist — identity matches are the right recording and not a compilation, barcodes belong to the edition claimed, no review text copied, every score carries a locator or stays `draft`.

---

## 6. Milestones

**M1 — identity complete.** 58 candidates resolved or dropped; MBIDs merged. *One run.*

**M2 — the second-hand layer.** Editions, catalogue numbers and barcodes for all resolved recordings. The barcode lookup becomes genuinely useful somewhere around 300 indexed editions. *Two to three runs.*

**M3 — first citations.** Target the twelve works with the densest literature — the Brandenburgs, the Goldbergs, the Ninth, the Fifth, the Missa Solemnis, Figaro, Don Giovanni, the Requiem, Bohème, Tosca, Butterfly, Turandot. Three cited independent sources per recording is the threshold at which Référence becomes possible at all.

**M4 — the sound axis.** The differentiator, and the thinnest layer. Remastering documentation, engineers' notes, and structured reader A/B comparisons between editions. No other resource has this; it will not arrive by scraping.

**M5 — publish.** GitHub Pages, the catalogue index as the front door, coverage stated honestly on every page.

---

## 7. How to know it is working

- **Citation ratio** — statements at `cited` over all statements. Currently near zero.
- **Editions per recording** — how well the second-hand case is served.
- **Barcode coverage** — the shop feature is only as good as this number.
- **Sound coverage** — editions with a cited sound assessment. The one metric that says whether this guide is different from the ones that already exist.
