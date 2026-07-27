#!/usr/bin/env python3
"""render.py — build the site from committed JSON. No network, no dependencies."""
import json, pathlib, sys

tpl = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site/template.html").read_text("utf-8")
cat = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "build/catalogue.json").read_text("utf-8")
out = pathlib.Path(sys.argv[3] if len(sys.argv) > 3 else "docs/entries.html")

marker = "/*__CATALOGUE__*/{}"
if marker not in tpl:
    raise SystemExit("template is missing the catalogue marker")
out.write_text(tpl.replace(marker, cat), "utf-8")
print(f"wrote {out} ({out.stat().st_size/1024:.0f} KB)")
