# Classical Music Recording Catalogue

## Cursor Cloud specific instructions

### What is actually in this repo (important, non-obvious)
This repository currently contains only the **rendered static site** plus Markdown docs:
- `index.html` — catalogue landing page (composer tables, tally).
- `entries.html` — per-recording assessment entries (linked from `index.html`).

The Python pipeline described in `README.md` and referenced by the `Makefile`
(`engine/`, `agents/`, `site/`, `data/seed.json`, `build/catalogue.json`, `docs/`) is
**NOT present** in the repo. As a result `make` (and `make seed/score/render/plan/harvest/validate`)
will fail with `No such file or directory`. Do not treat that as a broken environment — the
source for those stages simply isn't committed here.

### Running the application
It is a self-contained GitHub Pages static site (only external dependency is Google Fonts over the network). Serve from the repo root:

```bash
python3 -m http.server 8000   # then open http://localhost:8000/index.html
```

Navigation: `index.html` anchors (`#bach`, `#beethoven`, `#mozart`, `#puccini`) and the
`Entries` link / `read` links go to `entries.html#<anchor>`.

### Tooling
- Python 3.11+ standard library only. No packages to install, no virtualenv needed.
- There is no test suite, no linter, and no build step for the committed files (the HTML is
  pre-rendered). If pipeline source is later added, `make` becomes the build entry point.
