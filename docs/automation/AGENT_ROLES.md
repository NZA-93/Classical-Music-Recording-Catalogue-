# Cursor agent roles

Each role is a separate Cursor cloud agent on its own branch
`cursor/<role>-<week>-5458`. One task per branch. Harvest / identity /
citation roles stop at every `[H]` gate. **Critic editorial landings do not** —
see [`CRITIC.md`](CRITIC.md).

---

## Role A — Seed expander `[A]`

**Mission:** Add the next five composers from `proposals/composer-queue.json`
into `engine/seed_catalogue.py`, regenerate `data/seed.json`, update
`TestSeedIntegrity` counts, fix stale “four/five composers” copy in the site.

**May write:** `engine/seed_catalogue.py`, `data/seed.json`, tests that assert
counts, `site/build_site.py` nav/copy, `PROGRAM.md` tallies.

**Must not:** add scores, stars, statements, editorial prose, or scrape reviews.

**Done when:** `make seed && make test && make site` pass; PR checklist notes
sources for any factual performer/label claims.

**Prompt sketch:** follow `proposals/WEEK_BRIEF.md` section A.

---

## Role B — Identity & covers harvester `[A]`

**Mission:** Run / extend `agents/harvest.py` for new and existing candidates:
identity → editions → cover (CAA front existence). Write only to `proposals/`.

**May write:** `proposals/proposals-YYYYMMDD.json`, `proposals/PR_BODY.md`,
cache under `.cache/` (not committed).

**Must not:** download/commit cover binaries; fetch Discogs images; widen budget
beyond 300 without a human note in the PR.

**Done when:** dry-run plan posted; live harvest PR opened with identity
confidence visible; covers as CAA URLs only.

---

## Role C — Citation & awards `[A→H]`

**Mission:** Prefer award lists and structured ratings (HARVEST_STRATEGY rounds
1–3). Emit proposals / citation_tasks aiming for **≥5 independent sources** on
each assessed recording (stretch 10). Map each source to a `Cls` value.

**Target sources (canonical set):**

1. Gramophone Award / Editor’s Choice  
2. Diapason d’Or / Diapason rating (facts + locator; see legal note)  
3. Preis der deutschen Schallplattenkritik  
4. Choc de Classica  
5. BBC Building a Library first choice  
6. Penguin / Guide survey listing  
7. ClassicsToday artistic/sound pair (**ask permission first**)  
8. Fanfare or MusicWeb International (terms + robots first)  
9. Major award (Grammy classical / equivalent)  
10. Remastering / engineering literature for the sound axis  

**May write:** `proposals/`, `data/awards/*.json` (facts with locators only).

**Must not:** store review body text; write `data/statements/`; invent a score
without a locator; bypass paywalls.

**Human gate:** every match confirmed before apply into statements.

---

## Role D — Composer rollup & site `[A]`

**Mission:** Keep `aggregate_composer()` and the index display honest: show a
composer score only when enough ratified interpretation statements exist;
always show class/provenance breakdown so origin stays visible.

**May write:** `engine/aggregation_engine_v2.py`, `site/build_site.py`,
`site/template.html`, tests. Must not change the four regression recording scores.

---

## Role E — Apply & review tooling `[A]`

**Mission:** Land / maintain `agents/apply.py` and `agents/review.py` so
proposals become seed/recording facts without touching statements or editorial.

Reuse work on remote branches `cursor/s1-02-apply-*`, `cursor/s1-06-review-*`
where possible.

---

## Role Critic — Classical Music Recording Critic `[C]`

**Mission:** Author Dictionnaire-style signed entries in `data/editorial/` and
land them on `main` so live Pages updates. First cut: the Bach assessed set on
work pages.

**May write:** `data/editorial/` (text, stars, Référence, ADR-003 quotes), and
the site publish that follows a signed entry. May merge that PR or ask
Developer to ship it.

**Must not:** invent scores into `data/seed.json` or `data/statements/`;
weaken the four regression recording scores; scrape publications; skip
`docs/legal/DIAPASON_INGESTION.md`.

**Done when:** the signed block is on the work page on `main` / Pages.
Unsigned prose does not publish.

**Prompt sketch:** follow [`LAUNCH_PROMPTS.md`](LAUNCH_PROMPTS.md) Agent Critic.

---

## Developer — ship Critic content

**Mission:** Merge or push a ready Critic editorial PR to `main` so Pages
updates. Do not invent or rewrite verdict prose. Do not use this path to land
harvest guesses or statement scores.

---

## Orchestrator (this agent / human)

1. Run `make expand-brief`.  
2. Launch Roles A–E as separate Cursor agents with the brief sections.  
3. Do not start Role C harvest against a publication until terms/robots are clear.  
4. Stop the harvest loop when a PR needs human identity or statement ratification.  
5. Launch Critic for signed entries (Bach assessed set first). That work lands
   on `main` without a human merge gate.
