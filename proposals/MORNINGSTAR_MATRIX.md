# Morningstar matrix — Critic rubric (plumbing + visual box)

Schema, validate, and card UI. **No scores are invented here.** Critic integers
already signed on the assessed set stay 1–5 in `data/editorial/`. This note
does not alter them.

Shape: `data/editorial/_SCHEMA.json`. Gate: `agents/validate.py`.
Display decision: [`docs/adr/ADR-005-morningstar-3x3.md`](../docs/adr/ADR-005-morningstar-3x3.md)
(Nicolò, 27 September 2026).

## Card (three-second scan)

- Dictionnaire signed prose first; stars / Référence stay the editorial headline.
- When `editorial.matrix` is present: a **3×3 Morningstar-style box** under the
  prose (not inside it). The cell is **derived at render** from the stored
  integers. One filled cell at (sound band, interpretation band). Caption names
  the bands: `Interpretation: Outstanding · Sound: Excellent`.
- **No overall badge on the card.**
- Empty matrix stays invisible (no hollow box). Engine-scored cards with no
  Critic matrix (Tosca, Shostakovich 5) keep their aggregate score box and do
  not gain a style box.
- “How scored” expands to the original 1–5 integers, the band each integer
  belongs to, optional overall, and the evidence ledger.
- The box is drawn on the sealed work page (the card a composer hub links to).
  Composer hubs list assessed recordings; they do not draw a second box.
  Candidates considered (ADR-004) stays a rank list with no style box.

## Visual box (UX + Prose SIGN)

X = Sound band, left→right. Y = Interpretation band, bottom→top.

**Axis ends on the box face:**

- Sound: Limited → Excellent
- Interpretation: Of historical interest → Outstanding

The middle bands (Good, Solid) appear in the caption when that is the cell,
and in How scored for every integer.

**Bands (derived; not stored; not 9 cell essays):**

| Stored integer | Interpretation | Sound |
|---|---|---|
| 1–2 | Of historical interest | Limited |
| 3 | Solid | Good |
| 4–5 | Outstanding | Excellent |

**Référence** remains only the signed editorial flag. It is not a band and not
a cell. Do not conflate it with a sound or interpretation label.

## Axes (Critic integers, never derived from the ledger)

| Field | Value |
|---|---|
| `interpretation` | integer 1–5, stored |
| `sound` | integer 1–5, stored |
| 3×3 cell | derived at render, never stored |
| overall (expand only) | `0.6×interpretation + 0.4×sound`, one decimal |

Overall is computed at render for the expand panel. It is not stored on the
entry, not shown on the card face, and not written into seed, statements, or
the aggregate.

## Evidence ledger (optional)

Rows are evidence, not a calculator. Validate does **not** auto-compute axis
scores from the ledger.

```json
{
  "axis": "interpretation | sound",
  "tier": "A | B | C",
  "title": "string",
  "url": "https://…",
  "note": "short why-this-score, ≤200 characters"
}
```

### Tiers (Critic rule)

- **A** — cited, locatable primary.
- **B** — named / attributed source.
- **C** — secondary or thin. **Tier C alone cannot raise an axis.**

That last line is a Critic rule. The UI states it. The validator does not
raise or lower integers from ledger rows.

Consulted **References** (already shipped) stay a separate block from the ledger.
