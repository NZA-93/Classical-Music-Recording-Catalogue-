# S1-04 Award harvest — human confirmation required

Agent gathered award **candidates with locators** into `data/awards/` and
emitted proposals via `agents/awards.py`. **Nothing enters `data/statements/`
until a human confirms each match.** AGENTS.md §3.

## How to confirm

1. Open `proposals/awards-*.json` (latest).
2. For each proposal where `needs_human_confirmation` is true:
   - Verify the award happened (follow `locator`).
   - Verify the recording identity (conductor, ensemble, label, year).
   - Reject if more than one recording fits and year/label are missing.
3. Accepted rows: copy the corresponding draft from
   `proposals/pending-statements/` into the right
   `data/statements/<composer>/<work>.json` file (create if needed),
   keeping `covers_works` for ADR-001.
4. Re-run `python3 agents/awards.py` after adding seed candidates for
   unmatched winners (Nelsons Sym 4/11, Haitink Sym 4, Gardiner Missa).

## Done when

- At least 30 `cited` statements exist
- Citation ratio (cited / all interpretation statements) > 50%

Today (before human confirm): citation remains ~5%. Pipeline is ready;
the constraint is editorial confirmation, not tooling.

## Do not

- Ingest nominees as awards
- Paste promotional prose from label pages (see Petrenko `locator_caveat`)
- Let an agent write the statement files
