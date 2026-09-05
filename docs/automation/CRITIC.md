# Critic landing path

The **Classical Music Recording Critic** is the named editorial role for
signed entries (ADR-002). That includes the Critic agent acting in the role.
This is the path that puts Dictionnaire-style prose on work pages.

Harvest, identity, citation and seed work is a different path. It still
proposes; a human still merges.

## Who writes what

| Path | Who | Lands how |
|---|---|---|
| Signed entry (`data/editorial/`) | **Critic** | Critic merges, or **Developer** ships the Critic PR, to `main` → live Pages. No human merge babysit |
| Seed / identity / covers | Roles A–B, E | Pull request; human merges |
| Citation proposals → `data/statements/` | Role C, then a human | Human ratifies; agents never write statements |
| Composer rollup / site plumbing | Roles D–E, Developer | PR; human merges unless the change is only shipping already-signed Critic content |

## What Critic may do

- Author a signed entry: `text`, `stars`, `reference`, `compared_with`,
  ADR-003-bounded quotes
- Close it with author id, name, date and revision — unsigned prose does not
  publish
- Land it on `main` so GitHub Pages updates
- Ask Developer to merge or push that editorial PR if Critic cannot merge

## What Critic must not do

- Invent interpretation or sound scores into `data/seed.json` or
  `data/statements/`
- Invent an aggregate rating without a citation basis
- Weaken the four Brandenburg / Tosca regression anchors except through a
  deliberate, reviewed algorithm-version bump
- Scrape a publication or skip
  [`docs/legal/DIAPASON_INGESTION.md`](../legal/DIAPASON_INGESTION.md)
- Add a runtime dependency

## First cut

Nicolò’s mandate: signed entries on work pages, **Bach assessed set first**
(the critic-signed IDs already on public cards). The editorial queue still
ranks need; it does not override that first cut.

Do not start from a harvest agent “draft for the author to edit”. Critic
writes the entry. Other agents may run `make queue` and assemble a brief of
facts only.

## Commands

```bash
make queue                 # rank where a signed entry is worth the most
# write data/editorial/<work>.json from data/editorial/_SCHEMA.json
python3 agents/validate.py
make site                  # signed block renders on the work page
```

Then open the editorial PR and **land it**. Developer may merge or push.
Other roles stop at the human gate; this role does not.

## Developer

Developer may merge or push a Critic editorial PR so `main` and Pages stay
current. Developer may **not** invent or complete the verdict, or use this
exception to land harvest guesses or statement scores.
