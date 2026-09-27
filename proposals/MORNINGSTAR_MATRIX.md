# Morningstar matrix — Critic rubric (plumbing + visual box)

Schema, validate, and card UI. **No scores are invented here.** Critic integers
already signed on the assessed set stay 1–5 in `data/editorial/`. This note
does not alter them.

Shape: `data/editorial/_SCHEMA.json`. Gate: `agents/validate.py`.
Display decision: [`docs/adr/ADR-005-morningstar-3x3.md`](../docs/adr/ADR-005-morningstar-3x3.md)
(Nicolò, 27 September 2026).

## Card (three-second scan)

- Dictionnaire signed prose first; stars / Référence stay the editorial headline.
- When `editorial.matrix` has both integers: a **3×3 Morningstar-style box**
  under the prose (not inside it). The cell is **derived at render from those
  integers only**, never from the ledger. One filled cell. Every band name is
  readable on the face. Caption names the filled cell:
  `Interpretation: Outstanding · Sound: Excellent`.
- **No overall badge on the card.**
- No integers: the words **Not yet scored**. No empty grid. Engine-scored cards
  with no Critic matrix (Tosca, Shostakovich 5) keep their aggregate score box
  and show those words instead of a style box. The aggregate reference flag
  stays in the data and is not drawn as a badge until that disc has a signed
  entry. A signed Référence badge stays on the signed entry.
- “How scored” expands to the original integers, then this sentence once, in
  plain type: “Interpretation: 5 is Outstanding, 4 is Strong, 1 to 3 is With
  reservations. Sound: 4 or 5 is Excellent, 3 is Good, 1 or 2 is Limited.”
  Then optional overall and the evidence ledger.
- The box is drawn on the sealed work page (the card a composer hub links to).
  Composer hubs list assessed recordings; they do not draw a second box.
  Candidates considered (ADR-004) stays a rank list with no style box.

## Visual box (UX + Prose SIGN)

X = Sound band, left→right. Y = Interpretation band, bottom→top.

**Every band is named on the face** (row labels top→bottom, column labels left→right):

- Interpretation: Outstanding, Strong, With reservations
- Sound: Limited, Good, Excellent

**Bands (derived from the integers; not stored; not taken from the ledger):**

| Stored integer | Interpretation | Sound |
|---|---|---|
| 1–3 | With reservations | — |
| 1–2 | — | Limited |
| 3 | — | Good |
| 4 | Strong | Excellent |
| 5 | Outstanding | Excellent |

**Référence** remains only the signed editorial flag. It is not a band and not
a cell. The sound axis has no end-label “Reference”.

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
