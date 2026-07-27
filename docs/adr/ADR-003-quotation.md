# ADR-003 — Quotation: never in the aggregate, sparingly in a signed entry

**Status:** accepted · **Date:** 26 July 2026 · **Depends on:** ADR-002

---

## The question

Wikipedia quotes critics all the time, with attribution, and nobody sues. Why
can this guide not do the same?

## Why the comparison does not hold

Four differences, in rising order of importance.

### 1. There is no fair use here

Wikipedia is hosted in the United States and leans on fair use — a flexible
four-factor test weighing purpose, nature, amount and market effect. French and
EU law has nothing of the kind. It has a closed list of exceptions, and the
relevant one is *courte citation* (CPI L122-5, 3°a), which requires **all** of:
brevity, incorporation into a work of one's own, a critical, polemical,
pedagogical, scientific or informational purpose, and attribution of both author
and source.

"Short and attributed" satisfies two of four conditions. French courts have not
been generous about the others.

### 2. Brevity is relative to the source, not absolute

This is the technical point people miss. Twenty-five words taken from a
five-thousand-word feature is a fragment. Twenty-five words taken from a
hundred-word Diapason notice is **a quarter of the work**.

Diapason notices are short. That makes them disproportionately dangerous to
quote — the shorter the source, the smaller a "short quotation" has to be.

### 3. The quote would not illustrate this guide. It would be this guide.

Wikipedia quotes a review inside an article *about* an album — the quote
illustrates reception within a wider discussion of composition, personnel,
history. Remove the quotes and an article remains.

Here, the aggregated critical verdict **is the product**. Quotes would not
support the entry; they would constitute it. A reader who has the quotes has no
reason to consult the source. Under the French test that fails "incorporation
into a work of one's own"; under the American one it fails market effect. Both
roads arrive at the same place.

Add systematicity — ten thousand notices through a pipeline rather than one
editor quoting one review — and even if each individual act were defensible, the
aggregate reconstructs the book. French law reaches that through *parasitisme*
without needing copyright at all.

### 4. Licence contamination, which is the practical killer

This guide publishes factual data as CC0 and prose as CC BY-SA. **Quoted review
text cannot be relicensed, because it is not ours to license.** The moment a
quotation is embedded in `data/`, the dataset stops being cleanly licensed, and
anyone downstream who reuses it under CC0 redistributes someone else's
copyrighted text believing it free.

Wikipedia manages this with explicit non-free content tagging and a policy
apparatus built over twenty years. Building that here would poison the open-data
claim that is part of the project's point. It is not worth it.

## The decision

**In the aggregate layer: no quotation, ever.** A normalised score, a locator,
and a characterisation in the guide's own words under 240 characters. This is
already enforced by `agents/validate.py` and by a schema with no field for
source text.

**In a signed editorial entry (ADR-002): quotation is permitted, bounded.**

| Rule | Limit |
|---|---|
| Quotes per entry | 2 |
| Words per quote | 25 |
| Proportion of the source notice, where known | 20% |
| Structured attribution | author, publication, locator — all required |
| Purpose | the entry must engage with the quote, not display it |

The last row cannot be checked by a machine, which is why it belongs to a named
author who signs the entry.

**This is not a loophole. It is the one place quotation is genuinely defensible**,
because a signed entry arguing with a named critic is precisely the "work of
one's own with a critical purpose" the exception contemplates. Quotation earns
its place exactly where it is rare and disputed, and loses it exactly where it
is systematic and merely displayed.

## How to ask

Asking is always free. Asking for the wrong thing is not.

**Ask in this order:**

1. **Permission to cite ratings with a link back.** Small, obviously beneficial
   to the publication, very likely granted. Establishes a relationship and a
   named contact.
2. **Only then, a defined quotation licence** — a written scope, not a vague
   permission: how many, how long, where, with what attribution.

Do not open with the quotation request. It is the larger ask, more likely
refused, and **a documented refusal is materially worse than never having
asked** — it removes any argument that the use was made in good faith on a
reasonable reading of the exception.

## Consequences

The aggregate stays clean, mechanically enforceable and freely licensable. The
signed entries acquire the one thing that makes criticism feel alive — the sound
of someone disagreeing with a named opponent in their own words. And the
project's legal exposure concentrates in a handful of human-authored paragraphs
that a person has read, signed and can defend, rather than being distributed
across ten thousand machine-made records nobody has looked at.
