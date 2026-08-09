# Launch prompts — paste into Cursor cloud agents

Base branch after the automation PR lands: `main` (or
`cursor/composer-automation-5458` until merged). Each agent uses a **new**
branch matching `cursor/<name>-5458`.

Before every commit: `python3 -m unittest discover -s tests -q`,
`python3 agents/validate.py`, `make site`.

---

## Agent A — Seed week batch

```
Read AGENTS.md and proposals/WEEK_BRIEF.md. You are Role A (Seed expander) from
docs/automation/AGENT_ROLES.md.

Add the five composers marked status "next" in proposals/composer-queue.json
(Brahms, Haydn, Schubert, Handel, Chopin) to engine/seed_catalogue.py with
~10–12 core works each and well-known candidate recordings (performers, label,
year — facts only). No scores, stars, statements, or review text.

Run make seed. Update TestSeedIntegrity counts. Update site nav/copy if needed.
Mark the five composers status "in_progress" with week "2026-08-09" in the queue.
Open a PR. Stop when the seed PR is ready for human review.
```

---

## Agent B — Identity & Cover Art Archive

```
Read AGENTS.md, HARVEST_STRATEGY.md Part 2, and docs/automation/AGENT_ROLES.md
Role B. After the week seed lands (or on current seed if seed PR not merged),
run make plan then harvest with budget 300 into proposals/ only.

Resolve covers via Cover Art Archive hotlinks only — never download or commit
images, never use Discogs images. Write proposals/PR_BODY.md. Stop for human
identity review; do not auto-accept matches below 80.
```

---

## Agent C — Citations toward ≥5 sources

```
Read AGENTS.md, HARVEST_STRATEGY.md Part 1, docs/legal/DIAPASON_INGESTION.md,
and docs/automation/AGENT_ROLES.md Role C.

Build or extend award/citation proposal generation (reuse agents/awards.py ideas
from origin/cursor/s1-03-awards-* if present). Prefer public award facts with
locators. Target ≥5 independent sources per assessed recording over time from
the Role C source list. Do not scrape publication sites. Do not write
data/statements/. Emit proposals only; human ratifies. Characterisations ≤240
chars, guide's own words, with locator.
```

---

## Agent D — Apply tooling

```
Read AGENTS.md and SPRINTS.md S1-02 / S3-04. Land agents/apply.py so reviewed
proposals update seed/recordings facts. Never write data/statements/ or
data/editorial/. Reuse origin/cursor/s1-02-apply-* or s1-06-review-* where
possible. Tests required. Stop after PR.
```
