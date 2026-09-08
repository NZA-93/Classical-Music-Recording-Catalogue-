# ADR-004 — Scout candidate pool: ranked, never canon

**Status:** accepted · **Date:** 8 September 2026 · **Depends on:** ADR-002 · **Amends:** AGENTS.md §1 (scout is not the signed register)

---

## The problem

Identity and harvest answer one question: *is this the right disc?* The signed
entry answers another: *what does this recording do, and is it Référence?*
Between those two sits a third question the guide was answering only by
omission:

> Which recordings on this work deserve a Critic cut at all?

Leaving that implicit makes the assessed cut look like a hidden ranking of
everything in the seed. It is not. Brandenburg’s public cards are three poles
(Pinnock 1982, Harnoncourt 1964, Richter 1967). Abbado, Britten and the broken
Gardiner seed row were considered and held. Without a visible shortlist, a
reader cannot tell *considered and declined* from *never looked at*.

The danger the other way is worse. A machine-ordered “best of” with stars,
Référence, a Morningstar box or Dictionnaire prose would be an unsigned canon.
That is exactly the fabrication AGENTS.md forbids.

## The decision

**A scout pool is a ranked shortlist of candidates for a Critic cut. It is
never canon.**

| | Identity / harvest | Scout pool | Assessed + signed entry |
|---|---|---|---|
| Question | Right disc? | Deserve a cut? | What does it do? |
| May set | MBID, label, year, credits | Ordinal rank, stance, why-in / why-out, status | Stars, Référence, matrix, Dictionnaire `text` |
| Feeds the aggregate | No | **No** | **No** |
| Auto-promotes | No | **No** | Promotion is the Critic cut + prose SIGN only |

Scout ranks are ordinal integers (`1`, `2`, `3`…), not a fake 0–3 aggregate
and not stars. Stance is a tag (HIP studio digital, pioneering OI, modern
Munich orchestra), not a verdict paragraph. `why_in` / `why_out` are short
visible reasons; the unused side is `null`. Status is one of `shortlist`,
`held`, `promoted-to-cut`, `rejected`.

`promoted-to-cut` records a fact already true in `seed.works[].assessed`. It
does not write assessed IDs, does not publish a crown, and does not mint a
signed entry. Held and rejected rows stay off the public cards.

The signed-entry schema in `data/editorial/` is unchanged. Scout lives in
`data/scout/`, is validated separately, and is not merged into the editorial
publish path. Engine, statements and seed scoring never read it.

## Visible why-in / why-out

A rank without a reason is a hidden score. Every scout row carries a short
`why_in` or `why_out` (the other is `null`). That copy is not Dictionnaire
prose: it does not set stars, Référence or matrix, and it does not publish
without the scout fence (no `text`, no `stars`, no `reference`, no `matrix`
keys — validate rejects the file if they appear).

## Comparative field still required for cuts

Scout does not relax ADR-002. A recording that is promoted to the assessed
cut still needs a signed entry that is comparative by reflex — what it does
that the alternatives do not — closed with author, date and revision. The
pool explains *why this one was in the room*. The entry is the listening
report.

## What agents may and may not do

**Critic (named editorial role) may:** author the pool: identity lock, ordinal
rank, stance, why-in / why-out, status.

**Other agents may:** load and render an existing pool; validate that it cannot
publish crowns; refuse to merge it into editorial, statements or the
aggregate.

**Other agents may not:** invent scout ranks, stance tags or why-in / why-out;
auto-Référence; auto-promote a row into `assessed`; draft Dictionnaire `text`
onto a scout file “for the author to edit”.

## Consequences

**Good.** The assessed cut stays small and signed. The reader can see who was
considered. Identity work stays identity work. The algorithm stays a
measurement of cited sources.

**Costs.** A third register on the work page, behind a one-click expand
(**Candidates considered**), with no crown, no stars and no style box on
scout rows. The card face of assessed discs does not change. Coverage of the
pool will lag the seed, as authorship should.

**Pilot.** Bach Brandenburg only, six rows, Critic-authored. Promoted rows
are exactly the assessed cut (`/0`, `/1`, `/4`).
