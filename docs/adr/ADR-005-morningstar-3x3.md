# ADR-005 — The Morningstar box is a derived 3×3

**Status:** accepted · **Date:** 27 September 2026 · **Decided by:** Nicolò · **Depends on:** ADR-002 · **Amends:** the Morningstar card described in `proposals/MORNINGSTAR_MATRIX.md`

---

## The problem

The card face was a 5×5 square: one cell for each pair of Critic integers.
Five shades on each axis asked the reader to parse a distinction the glance
was not earning. Nicolò decided, on 27 September 2026, to simplify that face
to a 3×3 square — three bands on each axis, nine cells.

## The decision

**The stored axes stay integers 1–5. The cell is derived when the page is drawn.**

Interpretation (the recording) and Sound (the edition) are unchanged as Critic
judgements. Nothing in `data/editorial/` is re-scored. A band name, a cell id,
or an overall is not a field on the entry.

| Stored integer | Interpretation band | Sound band |
|---|---|---|
| 1–2 | Of historical interest | Limited |
| 3 | Solid | Good |
| 4–5 | Outstanding | Excellent |

Each integer lands in exactly one band. The filled cell is that pair. The
caption names the bands (`Interpretation: Outstanding · Sound: Excellent`).
How scored still shows the original integers, which integer sits in which
band, the expand-only overall (`0.6×interpretation + 0.4×sound`), and the
evidence ledger.

**Référence** stays the signed editorial flag. It is not a band and not a cell.
The old English sound-end “Reference” is retired so the two words cannot be
read as the same mark.

A signed recording with no matrix integers renders no style box. The aggregate
score box on engine-scored cards (Tosca, Shostakovich) is a different register
and is not this grid.

Scout pools (ADR-004) are unchanged: ordinal ranks, no stars, no Référence, no
matrix, no Dictionnaire `text`.

## Consequence

Neighbours whose integers were 4 and 5 now share a band, and may share a cell
when the other axis falls in the same band too. That is a display collapse,
not a new judgement. Whether a lost distinction still matters is a question
for the Critic. This note does not move an integer, a star, or a Référence flag.
