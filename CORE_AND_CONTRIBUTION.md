# The Core, and How It Gets Filled
### Critical Discography — design note, algorithm v2.0, 25 July 2026

---

## 1. The core, stated once

Two judgements, and they belong to different objects:

- **Interpretation** belongs to the *recording*. Pinnock in 1982 played what he played; no reissue changes it. This is where musical expertise lives — style, structure, rhetoric, what the players understood the piece to be.
- **Sound** belongs to the *edition*. The 1992 Teldec remaster and the original Telefunken LP are different sonic objects made from the same performance.

Every other resource conflates these, which is why none of them can help someone holding a disc. The v2 engine scores them separately and never lets one contaminate the other: sound cannot buy a Référence, and a celebrated interpretation cannot rescue a bad transfer's verdict.

This split is the project. Everything below serves it.

**What this demands editorially.** The engineering axis needs real technical writing — venue, microphone philosophy, what a remastering actually did — and the interpretation axis needs real musical writing. Both are scarce and neither can be faked convincingly. The guide's credibility rests on refusing to pretend otherwise: in the current build every sound assessment carries `provenance: draft`, weighs about a third of a cited claim, and says so on the page.

---

## 2. Photo recognition: right instinct, wrong photograph

Vivino works because a wine label is a near-unique key to a product. **A CD cover is not.** The same Archiv artwork appears on the 1983 CD, the 1990s twofer and the box-set reissue. A photo of the front cover identifies the interpretation — which the buyer in the shop already knows — and says nothing about the edition, which is the only thing they don't know.

The marks that *do* disambiguate are printed elsewhere:

| Mark | Where | Useful from |
|---|---|---|
| EAN / UPC barcode | back of case | c. 1983 |
| Catalogue number | spine, back, disc face | always |
| Matrix / runout | etched in the inner ring | always, and decisive for LPs |

So the camera feature is worth building, but it should read the barcode, not the picture. That is exact rather than probabilistic, needs no model, runs entirely in the browser (`BarcodeDetector`, or ZXing where unsupported), and matches against a prebuilt index shipped as static JSON — which means it works on a phone with no signal, in a basement record shop, which is exactly where it is needed. **This is implemented in the current draft.** Type or scan a barcode and the matching edition row highlights with its verdict.

Sequenced properly:

1. **Barcode → edition.** Built. Costs nothing, works offline, exact.
2. **OCR of the catalogue number.** Covers pre-barcode CDs and every LP spine. Text detection is now good enough in-browser; the matching is a string lookup.
3. **Perceptual hash of the cover.** The one case where the picture is the right input: a buyer who has no idea what they are looking at. A pHash against Cover Art Archive thumbnails narrows to a release-group, then the guide asks which edition. A few thousand hashes is a small JSON and a nearest-neighbour search — still no server.
4. **Runout matching.** Genuinely hard, and the deepest collector need. Later, if ever.

Reversing this order — cover matching first, because it looks like Vivino — would ship the least useful version of the feature.

---

## 3. Filling it: harvest proposes, humans ratify; Critic signs

The wiki instinct is right, but an open catalogue of *opinions* degrades. What does not degrade is a catalogue of **claims with locators**. So the unit of contribution is not a review; it is a statement plus where it came from.

The algorithm already enforces this. Provenance is a weight multiplier:

| Tier | Meaning | Factor |
|---|---|---|
| `cited` | source and locator — URL, issue, page | 1.00 |
| `attributed` | source named, no locator | 0.70 |
| `draft` | no citation yet | 0.35 |

An uncited claim is therefore welcome and nearly powerless. Promoting it to `cited` is a human act, recorded as a commit. Nobody has to argue about whether to let material in; the arithmetic already handles it.

**What harvest agents may and may not do.** They find, structure and cite existing published criticism: locating reviews, extracting the assessment, normalising it to the 0–3 scale, attaching the locator, filing a pull request. They do **not** generate evaluative opinion into seed or statements. A machine-written aggregate verdict with no source is the one input that would destroy the guide's only real asset, and no weighting scheme can make it safe — it enters as `draft` and stays there permanently, which is the correct outcome.

**Signed editorial is a different register.** The Classical Music Recording Critic authors the Dictionnaire-style entry and lands it on `main` / Pages. There is no human merge babysit on that path. Developer may ship the Critic PR. Other agents still must not invent verdicts into the aggregate. See `docs/automation/CRITIC.md` and ADR-002.

**What readers are best at** is the thing agents cannot do: listening. The sound axis in particular needs structured comparison reports — which two editions, on what equipment, what specifically changed. That is a short form, not an essay box, and it produces data rather than prose.

**Anti-capture.** No advertising, no affiliate links, ever — a guide whose method discounts commercial interest cannot take a share of the sale, and the second-hand audience is precisely where that temptation appears. Contributors with a label or retailer affiliation are flagged and their statements carry the commercial-interest penalty like any other.

---

## 4. What v2 adds, concretely

- Two-axis scoring, with sound assessed per edition.
- Provenance tiers as weight multipliers.
- Editions carrying catalogue number, barcode and MusicBrainz identifier, so a physical disc resolves to a verdict.
- Listening anchors — the passages that reward attention — as a first-class field rather than a sentence in the commentary.
- Reception by period, so a reader can see that a reputation was *made* and not found.
- Production credits (venue, producer, engineer) with their own sourcing state.
- Backwards compatibility: v1 interpretation scores are reproduced exactly (2.853 / 2.814 / 2.955 Référence / 2.848).

## 5. Immediate gaps, in priority order

1. **Sound assessments need citations.** Fourteen of the current edition rows are draft or unassessed. This is the guide's differentiator and currently its thinnest layer.
2. **Barcodes.** Two indexed out of thirteen editions. Each one added makes the shop feature work for one more disc.
3. **Engineer credits.** Known for the Decca set, unestablished for two others.
4. **Timings on listening anchors**, which turn the guide into something you can follow while playing the record.
