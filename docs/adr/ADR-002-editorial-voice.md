# ADR-002 — Two registers: the signed entry and the aggregate

**Status:** accepted · **Date:** 26 July 2026 · **Supersedes:** nothing · **Amends:** AGENTS.md §1

---

## The problem

Until now every judgement in this guide has been aggregated from external
sources. That made the algorithm defensible and the guide bloodless. A
catalogue with no voice of its own is a meta-aggregator: it can tell you what
the world thinks and never why you should care.

The *Dictionnaire des disques Diapason* worked the other way. Its entries were
written by named critics, in prose with a temperature, and that authorship was
the product. Nobody bought it for a weighted mean. They bought it because
someone who had listened harder than they had was willing to say so, in public,
with initials at the end.

But one person cannot write six hundred entries. Fifty-nine works at roughly
ten recordings each is a decade of evenings. So the guide cannot be *only*
authored, either, without being permanently incomplete.

## The decision

**Two registers, on the same page, never blended.**

| | Signed entry | Aggregate |
|---|---|---|
| Written by | A named person | The algorithm |
| Covers | Where someone has listened | Everything with a source |
| Carries | Its own stars, its own Référence | S, confidence, evidence spine |
| Changes when | The author revises it | New citations arrive |
| Weight in the other | **None** | **None** |

The critical clause is the last row. **The editor's judgement does not enter
the aggregate, and the aggregate does not constrain the editor.** They are
computed independently and displayed side by side.

This is not a compromise. It is the only arrangement in which both can be
trusted:

- If the editor's rating fed the aggregate, the aggregate would stop being a
  measurement of external consensus and become a measurement partly of its own
  author. The science would be decorative.
- If the aggregate constrained the editor, the guide would have no voice worth
  reading. Consensus is what the signed entry exists to argue with.

## The disagreement is the feature

When the editor gives two stars to a recording the consensus scores 2.9, that
divergence is the most interesting thing on the page, and the guide should
surface it rather than hide it:

> *The critical consensus places this near the top. Our editor does not, and
> says why below.*

No aggregator can produce that sentence. It requires a person willing to be
wrong in public. A **divergence index** — recordings ranked by the gap between
signed and aggregate verdicts — is a genuinely novel way into a catalogue, and
falls out of this architecture for free.

## What the algorithm does for the author

This is where the vastness stops being a problem and starts being useful. The
machine cannot write the entry, but it can decide **where the entry is worth
writing**, which is most of the editorial labour in a project this size.

The editorial queue ranks by need:

```
need = (no signed entry) × (low aggregate confidence)
     × (many competing recordings) × (work prominence)
```

A work where the sources disagree, where a dozen versions compete and where
nobody has yet said anything decisive is exactly where one paragraph from a
listener is worth more than fifty citations. The algorithm finds those. The
author writes them. Neither could do it alone.

The machine also prepares the ground: facts verified, editions identified,
credits cited, what other critics said and where. The author arrives at a brief,
not a blank page.

## What agents may and may not do here

`AGENTS.md` §1 says an agent never creates a critical judgement. This ADR does
not weaken that; it names the one place judgement legitimately lives and puts
it out of reach.

**Agents may:** compute the queue, assemble the brief, check facts inside a
signed entry, flag a claim that contradicts the catalogue, format and publish.

**Agents may not:** draft a sentence of the verdict, suggest a rating, complete
a half-written entry, or generate an entry "for the author to edit". A signed
entry that an agent started is not signed by the author, whatever the byline
says, and the byline is the entire point.

An entry is valid only with an author id, a date and a revision number. Unsigned
prose does not publish.

## Consequences

**Good.** The guide gets a voice without losing its evidence. Sparse authorship
becomes a mark of seriousness rather than a gap — twelve signed entries mean
twelve recordings someone actually sat with. The two layers grow at their own
natural rates: the aggregate broad and shallow, the signed layer narrow and
deep.

**Costs.** Two verdicts must be explained to readers who expect one; the
interface carries that burden through typography, not footnotes. Editorial
coverage will lag the catalogue permanently, and the design must present that
honestly. And the author's reputation is now attached to the guide in a way it
was not before — which is precisely what makes the entries worth reading, and
precisely why they cannot be machine-assisted.

**Anchors are settled by this too.** "What to listen for" describes the score,
not a performance, so it belongs to the work and may be maintained factually.
Anything evaluating how a given recording handles that passage is editorial and
requires a signature.

## Typography carries the distinction

A reader must never have to work out whether they are reading a person or a
computation. The signed entry is set on paper white, justified, at reading
measure, closed with initials and a date. The aggregate keeps the mono figures,
the influence bar and the source table. No shared furniture. The difference
should be legible at arm's length, before a word is read.
