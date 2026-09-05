# Contributing

The unit of contribution is not a review. It is **a claim with a locator**.

## What a good contribution looks like

Copy `contributions/_TEMPLATE.json`, fill it in, open a pull request.

```json
{
  "recording": "puccini/tosca/0",
  "axis": "interpretation",
  "edition": null,
  "source": "Gramophone",
  "locator": "https://… or: issue 1247, p. 84",
  "scale": "stars_5",
  "value": 5,
  "characterisation": "One sentence, in your own words, on what the source claims.",
  "conflict": false,
  "contributor": "your handle"
}
```

Scales: `stars_5` `stars_3` `ten_point` `percent` `award` `editors_choice` `rosette`
`prose`. A prose source carries no number — a human assigns it and signs for it.

**Never paste review text.** The guide stores a score, a locator and its own words. This
is both a legal boundary and a better one: a reader can follow your locator to the
original, which a copied paragraph does not allow.

## Provenance decides weight, so nobody has to argue

| Tier | Meaning | Weight factor |
|---|---|---|
| `cited` | source and locator | 1.00 |
| `attributed` | source named, no locator | 0.70 |
| `draft` | no citation yet | 0.35 |

Uncited claims are welcome and nearly powerless. Promoting one to `cited` is a human act
recorded as a commit.

## The sound axis needs you specifically

Agents cannot listen. If you own two editions of the same recording, this is the single
most valuable contribution available:

Open an **Edition comparison** issue — there is a template for it. Tell us which two
editions, on what equipment, and what specifically changed: level, noise floor, top end,
stage width, compression, edits.

## What agents may do

Find, structure and cite existing published criticism. Resolve identity, editions,
barcodes and cover art from open sources. **Harvest, seed and citation agents may not
generate evaluative opinion** into seed or statements. An uncited machine verdict
enters as `draft` and stays there permanently, which is the correct outcome.

**Signed editorial is Critic’s job.** The Classical Music Recording Critic authors
entries in `data/editorial/` and lands them on `main` / Pages. Developer may ship
that PR. Other agents do not draft the verdict. See
[docs/automation/CRITIC.md](docs/automation/CRITIC.md).

## Conflicts of interest

If you work for a label, retailer, artist management or a publication under review, say
so in the pull request. Your statements are flagged and carry the commercial-interest
penalty like any other. This is not a judgement about you; it is the same rule applied to
Warner's reissue notes.

## Corrections

Facts — catalogue numbers, barcodes, personnel, dates — should simply be fixed, with a
source. Open an issue if you would rather not edit directly.

## The rules are enforced, not just stated

Every pull request runs `agents/validate.py`, which fails the build on:

- a score claiming `cited` with no locator — provenance is derived from evidence, never
  from what the file says about itself
- a sound assessment that names no edition
- a characterisation over 240 characters, or one containing a long quoted run: both are
  usually a paste
- a barcode that fails its own EAN-13 or UPC-A check digit
- a reference to a recording or edition that does not exist

Run it yourself before opening the request:

```bash
python3 agents/validate.py
```
