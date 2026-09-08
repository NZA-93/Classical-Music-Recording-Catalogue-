# Morningstar matrix — Critic rubric (plumbing + visual box)

Schema, validate, and card UI. **No scores are invented here.** Critic integers
already signed on Goldberg / Fournier are mapped onto the 5×5 box; this change
does not alter them.

Shape: `data/editorial/_SCHEMA.json`. Gate: `agents/validate.py`.

## Card (three-second scan)

- Dictionnaire signed prose first; stars / Référence stay the editorial headline.
- When `editorial.matrix` is present: a **5×5 Morningstar-style box** under the
  prose (not inside it), mapping the Critic integers. One filled cell at
  (sound, interpretation). Caption keeps the numbers:
  `Interpretation {n} · Sound {m}`.
- **No overall badge on the card.**
- Empty matrix stays invisible (no hollow box).
- “How scored” expands to band-name ticks, optional overall, and the evidence ledger.

## Visual box (UX + Prose SIGN)

X = Sound, left→right (1→5). Y = Interpretation, bottom→top (1→5).

**Axis ends on the box face only:**

- Sound: Hard listen → Reference
- Interpretation: Documentary → Landmark

**Band names (ticks / How scored only — not 25 cell essays):**

| Axis | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Sound | Hard listen | Serviceable | Clean | Excellent | **Reference** |
| Interpretation | Documentary | Competent | Solid | Outstanding | Landmark |

**Reference** (English) is the Sound-axis end. **Référence** remains only the
signed editorial flag. Do not conflate.

## Axes (Critic integers, never derived from the ledger)

| Field | Value |
|---|---|
| `interpretation` | integer 1–5 |
| `sound` | integer 1–5 |
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
