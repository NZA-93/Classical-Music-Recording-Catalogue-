#!/usr/bin/env python3
"""
build_divergence.py — rank recordings by signed-vs-aggregate gap.

Renders docs/divergence.html from catalogue.json `divergence` fields.
Reads as an invitation, not an erratum.
"""

from __future__ import annotations

import json
import pathlib
from html import escape

CAT = pathlib.Path("build/catalogue.json")
OUT = pathlib.Path("docs/divergence.html")


def main() -> int:
    cat = json.loads(CAT.read_text(encoding="utf-8")) if CAT.exists() else {"works": []}
    rows = []
    for w in cat.get("works", []):
        for r in w.get("recordings", []):
            d = r.get("divergence")
            if d is None:
                continue
            rows.append({
                "work": f'{w["composer"]} — {w["title"]}',
                "work_id": w["id"],
                "recording": r["id"],
                "director": r.get("director") or r.get("soloists"),
                "agg_stars": r.get("stars"),
                "ed_stars": (r.get("editorial") or {}).get("stars"),
                "divergence": d,
                "author": ((r.get("editorial") or {}).get("author") or {}).get("id"),
            })
    rows.sort(key=lambda x: -abs(x["divergence"]))

    body_rows = []
    if not rows:
        body_rows.append(
            "<tr><td colspan='5'>No signed entries yet — divergence appears "
            "when a named listener and the aggregate disagree.</td></tr>"
        )
    else:
        for row in rows:
            sign = "+" if row["divergence"] > 0 else ""
            body_rows.append(
                f"<tr>"
                f"<td><a href='entries.html#{escape(row['work_id'])}'>"
                f"{escape(row['work'])}</a><br>"
                f"<span class='who'>{escape(str(row['director']))}</span></td>"
                f"<td>{row['agg_stars']}</td>"
                f"<td>{row['ed_stars']} <span class='who'>({escape(str(row['author']))})</span></td>"
                f"<td class='gap'>{sign}{row['divergence']}</td>"
                f"<td><a href='entries.html#{escape(row['recording'])}'>entry</a></td>"
                f"</tr>"
            )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Divergence — Critical Discography</title>
<style>
  :root {{ --ink:#1a1510; --paper:#f7f1e6; --rule:#c9b8a0; --accent:#6b2d1a; }}
  body {{ margin:0; font:18px/1.5 "Iowan Old Style", "Palatino Linotype", Palatino, serif;
         color:var(--ink); background:linear-gradient(165deg,#efe6d6 0%,#f7f1e6 40%,#e8dfd0 100%); }}
  .wrap {{ max-width:52rem; margin:0 auto; padding:2.5rem 1.25rem 4rem; }}
  h1 {{ font-size:2.4rem; font-weight:600; margin:0 0 .4rem; letter-spacing:-.02em; }}
  .lead {{ max-width:36rem; color:#4a3f34; margin:0 0 2rem; }}
  nav a {{ color:var(--accent); margin-right:1rem; text-decoration:none; border-bottom:1px solid transparent; }}
  nav a:hover {{ border-bottom-color:var(--accent); }}
  table {{ width:100%; border-collapse:collapse; }}
  th, td {{ text-align:left; padding:.7rem .4rem; border-bottom:1px solid var(--rule); vertical-align:top; }}
  th {{ font-size:.75rem; text-transform:uppercase; letter-spacing:.06em; color:#6a5c4e; }}
  .who {{ font-size:.85rem; color:#6a5c4e; }}
  .gap {{ font-variant-numeric:tabular-nums; font-weight:600; color:var(--accent); }}
  footer {{ margin-top:2.5rem; font-size:.9rem; color:#6a5c4e; }}
</style>
</head>
<body>
<div class="wrap">
  <nav>
    <a href="index.html">Catalogue</a>
    <a href="entries.html">Entries</a>
    <a href="gallery.html">Gallery</a>
  </nav>
  <h1>Divergence</h1>
  <p class="lead">Where a named listener and the aggregate part company.
  The disagreement is stated, not resolved. An invitation to listen again.</p>
  <table>
    <thead><tr><th>Recording</th><th>Aggregate</th><th>Signed</th><th>Gap</th><th></th></tr></thead>
    <tbody>
      {''.join(body_rows)}
    </tbody>
  </table>
  <footer>{len(rows)} divergences on file · built from catalogue.json</footer>
</div>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT} · {len(rows)} divergences")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
