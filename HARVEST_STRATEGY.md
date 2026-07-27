# Feeding the Algorithm
### Harvest strategy for criticism and cover art · 26 July 2026

---

## Part 1 — Where assessments can actually come from

The bottleneck is not engineering. It is that the material the guide needs — critical judgement — sits in copyrighted prose, much of it paywalled or in print. Scraping Gramophone is not a plan; it is a lawsuit and a reputation, spent on material the guide could not legally display anyway.

Six routes, ranked by what they yield against what they risk.

### A. Facts about criticism, which are not criticism

Awards are facts. *Diapason d'Or*, *Gramophone Award*, *Preis der deutschen Schallplattenkritik*, *Choc de Classica*, BBC *Building a Library* first choices, *Editor's Choice* listings — the fact that a jury chose a recording is not a copyrightable expression, it is a public event, and it maps straight onto the award scale already in the normaliser.

This is the highest-yield, lowest-risk seam in the whole project and it is barely touched. Award lists are published, structured, and cover exactly the historically central recordings the guide wants first. **Start here.** A recording with three independent award citations already clears the evidentiary bar for Référence.

### B. The open historical corpus

Reception history — the layer nobody else has — is largely available for free. Scanned runs of *High Fidelity*, *Stereo Review*, *Audio*, *The Absolute Sound* and similar sit on Internet Archive and the audio-magazine archives, OCR'd and searchable. They cover 1950–1990 in detail: the decades when the Callas *Tosca* was becoming canonical and Harnoncourt was still an argument.

An agent reads them, extracts an assessment, and cites the issue and page. It never republishes the text. Copyright status varies by title, so cite and link rather than mirror — but *reading* to write your own summary is exactly what a scholar does with a library.

### C. Structured numeric sources

ClassicsToday publishes a numeric artistic/sound pair, which is precisely the two-axis shape this guide uses. Presto, Arkiv and similar carry editorial ratings. These are small, structured extractions.

Before touching any of them: read the terms, check robots.txt, and — this is the step people skip — **write and ask**. A short email explaining a non-commercial reference project that cites scores and links back is granted more often than not, and a granted permission is worth more than any scraper, because it survives a change of counsel.

### D. Read-and-extract, with the schema as the guardrail

Where a page may lawfully be fetched, the pattern is:

```
fetch → read → emit (axis, score 0–3, locator, one sentence in the guide's own words)
                                     ↑ source text is never stored
```

The protection is structural, not procedural: **the proposal schema has no field that can hold source text**, and `validate.py` fails any characterisation over 240 characters or containing a long quoted run. A pipeline that cannot physically carry a copied paragraph will not accidentally publish one.

Never bypass a paywall, never ignore robots.txt, never route through residential proxies. If material requires a subscription, the honest path is a contributor who holds one and cites it.

### E. Where a language model is genuinely useful, and where it is poison

**Useful:** converting an attributed review into a normalised score and a one-line characterisation. That is summarisation of a cited source — the same operation a human editor performs, faster.

**Poison:** generating an assessment where no source exists. There is no weighting scheme that makes this safe.

Three controls make the useful case auditable:

1. A `method` field on every statement — `human` or `agent:model@version` — so a later recalibration can isolate machine extractions.
2. **Double extraction.** Two independent passes over the same review; if they disagree by more than 0.4 on the 0–3 scale, the statement is held for a human. Disagreement is the cheap signal that the prose was ambiguous or the model drifted.
3. **A 10% audit.** A human re-reads a random tenth of agent extractions and the agreement rate is published. If it falls, extraction stops. A metric nobody looks at is not a control.

### F. Consensus as evidence

That a recording appears in *N* independent recommendation lists is itself a fact, and a good one. Cross-referencing award lists, library recommendations and survey first-choices produces a defensible signal without a single line of copied prose — and it is exactly what the weighted aggregate was built to handle.

### Sequencing

| Round | Source | Yield |
|---|---|---|
| 1 | Award and first-choice lists | high · negligible risk |
| 2 | Open historical magazine archives | high for reception history |
| 3 | Permissions correspondence | unlocks structured numeric sources |
| 4 | Read-and-extract on permitted pages | steady |
| 5 | Contributors with books and subscriptions | the print sources, unreachable otherwise |

---

## Part 2 — Cover art, and being a good citizen of the commons

MusicBrainz and the Cover Art Archive are the right foundation, and their coverage of historic classical is thin. That was proved on the first four recordings here: Pinnock's Archiv set has fifteen images; the 1964 Harnoncourt has none.

**The resolution ladder**, in order, each step cheaper than the one below:

1. Cover Art Archive, by release — exact edition, exact artwork.
2. Cover Art Archive, by release-group — a different pressing usually carries the same image.
3. Any release in the group with a front image, taken as representative.
4. Wikimedia Commons, where a sleeve has been uploaded under a free licence.
5. The typeset plate already in the interface — label and year, set in Bodoni. Missing art becomes an invitation rather than a hole.

**What not to do.** Discogs has the richest image library and the most restrictive terms: its API requires authentication and its images are not licensed for reuse. Link to Discogs, never fetch from it. The same caution applies to label press images, whose rights are usually unclear and occasionally contested.

**The move that matters.** When a reader photographs a sleeve the guide is missing, the right destination is **MusicBrainz and the Cover Art Archive, not this project's server**. Upload there, then resolve it here through the normal ladder.

That decision does three things at once: it sidesteps the redistribution question permanently, it improves the commons for every other project, and it means the guide's image coverage improves without the guide hosting a single copyrighted file. Being a contributor to the commons rather than a hoarder of it is also, straightforwardly, the right way to use free infrastructure that other people maintain.

**Beyond images, MusicBrainz carries more than the project currently takes.** Release relationships hold producer, engineer and recording-venue credits — the engineering layer that this guide treats as half its judgement, sitting in a CC0 database and unread. Performer relationships give the credit graph that makes the gallery view navigable. At scale, the database dumps and the Live Data Feed replace polling entirely.

---

## Part 3 — Two views, one catalogue

The gallery view borrows what Roon does well: artwork at full scale, credits worth following, calm density, a horizontal rail that makes browsing feel like handling records rather than reading a spreadsheet.

It does not borrow Roon's silence on quality. Roon will show a magnificent page for a mediocre transfer. So the report survives intact inside the richer shell — the same evidence spine, the same editions table, the same visible gaps — and the imagery carries you toward a judgement instead of standing in for one.

The two views are the same JSON rendered twice: `entries.html` for reading and citation, `gallery.html` for browsing and discovery. Neither is a fallback for the other, and a reader can move between them at any point.

The typographic character stays. It is not nostalgia — it is the signal that says this is a reference work rather than a shop, and it is the one thing a streaming service cannot copy without becoming something else.
