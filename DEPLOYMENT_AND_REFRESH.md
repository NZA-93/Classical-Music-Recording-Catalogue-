# Going Online, and Keeping It Cheap
### Strategy note for the Critical Discography — 25 July 2026

---

## 1. GitHub Pages as the first venue

**Verdict: right choice for phase 1, and probably for longer than expected.**

The guide is a read-mostly catalogue whose content changes when an editor changes it, not when a user acts. That is exactly the shape Pages serves well, and it buys three things the project already wants:

- **The repository *is* the audit trail.** Source statements, weights and aggregation results live in version control. An editorial change becomes a pull request with a visible diff: "Penguin Guide weight 0.85 → 0.80, three recordings re-scored." That is stronger provenance than any database admin screen.
- **Zero operational surface.** No server, no database to back up, no dependency that expires. Free TLS and a custom domain.
- **Reproducibility.** Same inputs plus same algorithm version produce the same site, from any checkout.

**What Pages cannot do, and the honest answer to each:**

| Limitation | Answer for phase 1 |
|---|---|
| No server-side search | Build the index at build time (Pagefind or a small JSON + client filter). A few hundred works stays well under a megabyte. |
| No user contributions | Contributions arrive as pull requests or issues at first. A moderated web form is Strategy B, later. |
| Soft limits: 1 GB site, ~100 GB/month bandwidth, 10 builds/hour | Not a constraint at this size. Images are the only thing that could approach it; see §4. |
| No private data | None here. |

**Suggested layout**

```
/data/          sources.yaml, recordings.yaml   ← the editorial truth, hand-edited
/engine/        aggregation_engine.py, build_covers.py, render.py
/build/         aggregation_results.json, covers.json   ← committed, machine-written
/site/          index.html, /works/*.html, /img/*        ← published to Pages
.github/workflows/
```

Two workflows, deliberately separate:

- **`render.yml`** — on every push. Reads `/build/*.json`, regenerates `/site`, deploys. No network beyond the checkout, runs in seconds.
- **`harvest.yml`** — on a schedule and on manual dispatch. Talks to the outside world, updates `/build/*.json`, opens a pull request rather than committing to main. Scores never change without a human seeing the diff.

That split is the single most valuable decision in this note: **publishing must never depend on anything being reachable.**

---

## 2. Refreshing the algorithm without wasting anything

Aggregation itself is free — a weighted mean over a few dozen numbers, microseconds per recording. Every real cost is network I/O and CI minutes. So the optimisation target is *avoided work*, not faster arithmetic.

**a. Hash the inputs, skip the unchanged.**
Give each recording an input fingerprint: `sha256` over its sorted list of `(source_id, statement, raw_score, weight_class)`. Store it beside the result. On a run, recompute only where the fingerprint moved. A typical week will touch three recordings out of four hundred.

**b. Version the algorithm, and let the version force a full pass.**
Store `algorithm_version` in every result. Changing a weight table or the Référence threshold bumps the version, which invalidates every fingerprint at once — a deliberate, reviewable, full recalculation. This is how you recalibrate without ever wondering whether some entries are stale.

**c. Tier the harvest by volatility.**
Not all entries decay at the same rate.

| Class | Re-check |
|---|---|
| Historic benchmark, criticism settled for decades (Tosca 1953) | every 12 months |
| Established modern recording | every 3 months |
| Recent release, still accumulating reviews | monthly |
| Award cycles (Diapason d'Or, Gramophone) | after each announcement |
| Cover art already found | 90 days |
| Cover art not found | 14 days — the archive grows |

**d. Budget every run.**
The harvest works a priority queue ordered by `staleness × prominence`, with a hard cap — say 300 requests — and it persists its cursor. CI time then becomes constant and predictable no matter how large the catalogue grows. A run that hits the cap simply resumes next week.

**e. Cache conditionally, and commit the cache.**
Send `If-None-Match` / `If-Modified-Since`; a 304 costs almost nothing. Keep the cache in the repository so every CI run starts warm instead of cold. This alone removes most of the traffic.

**f. Respect the sources' own limits.**
MusicBrainz asks for one request per second and a descriptive User-Agent with a contact address. `build_covers.py` enforces both. Past a few thousand lookups, stop using the API and load a MusicBrainz database dump locally — it is designed for exactly this and removes the rate limit from the equation entirely.

**Recommended cadence:** weekly harvest (budgeted, opens a PR), monthly cover-art sweep for misses, render on every push. Nothing runs nightly, because nothing changes nightly.

---

## 3. Page weight

The current prototype loads Plotly — roughly 3.5 MB of JavaScript to draw four bar charts. The new draft draws the same information in CSS with no library at all, which is both faster and more legible on a phone. Keep that rule: **no runtime dependency the build could have resolved.**

Everything else follows from it — cover images lazy-loaded, one small JSON per work rather than one large file for the site, fonts subset and self-hosted once the design settles.

---

## 4. Images, and the licensing question

The pipeline is: MusicBrainz release MBID → Cover Art Archive front image → page.

`build_covers.py` resolves the MBID once, caches it, and asks the archive whether a front cover exists. Two ways to serve the result:

- **Hotlink the archive** (what the draft does). Nothing to store, always current, and it is the use the archive is built for. Slower first paint, because the URL redirects.
- **Download and commit thumbnails.** Much faster, fully self-contained. About 40 KB per recording at 500 px WebP — four hundred recordings is under 20 MB, comfortably inside the Pages limit.

One caveat worth deciding deliberately rather than by default: MusicBrainz *data* is openly licensed and safe to embed, but cover images are label artwork, and the archive hosts them without granting redistribution rights. Hotlinking keeps the guide out of that question; rehosting puts it in. For a non-commercial reference site the practical risk is small, but the licences should be read before the second option is chosen, and every entry should credit the archive and offer a takedown path.

Where no cover exists — which is common for exactly the historic recordings this guide cares about most — the interface sets a plate from the label and year instead, and links back to MusicBrainz so a reader can contribute one. Missing art becomes an invitation rather than a hole.

---

## 5. What this leaves for Strategy B

Nothing in the above is thrown away when a service arrives. The engine, the data model, the fingerprints and the rendered HTML all survive; a backend only adds moderated submissions and on-demand recomputation. Pages first is not a detour.
