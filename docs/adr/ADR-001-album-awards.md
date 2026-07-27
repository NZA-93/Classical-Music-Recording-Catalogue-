# ADR-001 — An album award is weaker evidence than a single-work award

**Status:** accepted · **Date:** 26 July 2026

## Problem

The 2017 Grammy for Best Orchestral Performance went to *Under Stalin's Shadow:
Symphonies Nos. 5, 8 and 9*. Recording an award signal of full strength against
Symphony No. 5 claims something the jury did not say: that the Fifth in
particular was the reason.

## Decision

An award covering *n* works is recorded once against each, at the award score,
but carries `covers_works` and counts as **one** benchmark signal shared across
them rather than one each. Référence requires three *independent* benchmark
signals; an album award that touches three symphonies must not appear to be
three.

The data model keeps `covers_works` on every award record so this stays
checkable rather than remembered.

## Consequence

Cycle-award-heavy composers — Shostakovich above all, where box sets and
multi-symphony albums dominate — will accumulate Référence more slowly than
opera, where awards attach to single works. That asymmetry is real, not an
artefact, and the guide should not correct for it.
