# Morningstar matrix — Critic rubric (plumbing contract)

Schema and card UI only. **No scores are invented here.** Critic fills
Goldberg / Fournier (and later entries) after this lands. Live Bach editorial
JSON stays without `matrix` until then.

Shape: `data/editorial/_SCHEMA.json`. Gate: `agents/validate.py`.

## Card (three-second scan)

- Dictionnaire signed prose first; stars / Référence stay the editorial headline.
- When `editorial.matrix` is present: two integers only — Interpretation 1–5 ·
  Sound 1–5 — under the prose, not inside it.
- **No overall badge on the card.**
- “How scored” expands to the evidence ledger.

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
