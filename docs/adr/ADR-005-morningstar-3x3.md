# ADR-005 — The Morningstar box is a derived 3×3

**Status:** accepted · **Date:** 27 September 2026 · **Amended:** 27 September 2026 (Critic, prose editor, and UX: the band cut below) · **Decided by:** Nicolò · **Depends on:** ADR-002 · **Amends:** the Morningstar card described in `proposals/MORNINGSTAR_MATRIX.md`

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
| 1–3 | With reservations | — |
| 1–2 | — | Limited |
| 3 | — | Good |
| 4 | Strong | Excellent |
| 5 | Outstanding | Excellent |

The two axes do not share a cut. Each integer lands in exactly one band on its
own axis. The filled cell is that pair, taken from the signed integers and
never from the ledger. The card face names every band, and the caption names
the filled cell (`Interpretation: Outstanding · Sound: Excellent`).

How scored shows the original integers, then this sentence once, in plain type:

> Interpretation: 5 is Outstanding, 4 is Strong, 1 to 3 is With reservations. Sound: 4 or 5 is Excellent, 3 is Good, 1 or 2 is Limited.

Then the expand-only overall (`0.6×interpretation + 0.4×sound`) and the
evidence ledger.

**Référence** stays the signed editorial flag. It is not a band and not a cell.
The old English sound-end “Reference” is not a label anywhere on the card.

An assessed recording with no matrix integers shows the words “Not yet scored”.
It does not show an empty grid. The aggregate score box on engine-scored cards
(Tosca, Shostakovich) is a different register and is not this grid.

The word Référence on a card is the signed editorial flag. The aggregate
reference flag stays in the engine data. It is not drawn as a badge on a disc
that has no signed entry.

Scout pools (ADR-004) are unchanged: ordinal ranks, no stars, no Référence, no
matrix, no Dictionnaire `text`.

## Consequence

Interpretation 4 and 5 are different bands (Strong, Outstanding). Sound 4 and 5
still share Excellent. Interpretation 1, 2 and 3 share With reservations. That
is a display grouping, not a new judgement. This note does not move an integer,
a star, or a Référence flag.
