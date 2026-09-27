"""Standing lists the signed entry. It does not say what a disc lacks.

Unsigned cards keep the line "No signed entry". A signed card shows the stars
stored on that entry. A signed Référence card shows those stars and the mark.
A signed entry with no stars field draws nothing in their place.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORBIDDEN = "not a référence"


def _js_between(text: str, start: str, end: str) -> str:
    i = text.index(start)
    return text[i:text.index(end, i)]


def _render_standing(source: str, payload: dict) -> str:
    js = _js_between(source, "function signedEntry", "function scorebox" if "function scorebox" in source else "/* rail */")
    if "function standingMarks" not in js:
        js = _js_between(source, "function signedEntry", "/* rail */")
    script = js + (
        "const payload = JSON.parse(process.argv[2]);\n"
        "process.stdout.write(standingMarks(payload));\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(script)
        path = fh.name
    try:
        proc = subprocess.run(
            ["node", path, json.dumps(payload, ensure_ascii=False)],
            check=False,
            capture_output=True,
            text=True,
        )
    finally:
        pathlib.Path(path).unlink(missing_ok=True)
    if proc.returncode != 0:
        raise AssertionError(proc.stderr or proc.stdout)
    return proc.stdout


def _signed(stars, reference):
    entry = {
        "author": {"id": "cmrc", "name": "Critic"},
        "date": "2026-09-01",
        "revision": 1,
        "reference": reference,
    }
    if stars is not None:
        entry["stars"] = stars
    return {"editorial": entry, "reference": True, "stars": 1}


class TestStandingMarks(unittest.TestCase):
    def setUp(self):
        self.template = (ROOT / "site/template.html").read_text(encoding="utf-8")
        self.gallery = (ROOT / "site/build_gallery.py").read_text(encoding="utf-8")

    def test_unsigned_is_exactly_no_signed_entry(self):
        for source in (self.template, self.gallery):
            html = _render_standing(source, {"editorial": None, "reference": True, "stars": 3})
            self.assertEqual(html, '<span class="plain">No signed entry</span>')
            self.assertNotIn(FORBIDDEN, html)

    def test_signed_non_reference_shows_stored_stars_only(self):
        for source in (self.template, self.gallery):
            html = _render_standing(source, _signed(3, False))
            self.assertIn('aria-label="3 of 3 stars"', html)
            self.assertIn('<span class="on">★</span><span class="on">★</span><span class="on">★</span>', html)
            self.assertNotIn("Référence", html)
            self.assertNotIn(FORBIDDEN, html)
            self.assertNotIn("No signed entry", html)
            self.assertNotIn("—", html)

    def test_signed_reference_shows_stars_and_mark(self):
        for source in (self.template, self.gallery):
            html = _render_standing(source, _signed(2, True))
            self.assertIn('aria-label="2 of 3 stars"', html)
            self.assertIn('<span class="on">★</span><span class="on">★</span><span class="off">★</span>', html)
            self.assertIn('<span class="badge">Référence</span>', html)
            self.assertNotIn(FORBIDDEN, html)

    def test_signed_without_stars_draws_nothing_negative(self):
        for source in (self.template, self.gallery):
            html = _render_standing(source, _signed(None, False))
            self.assertEqual(html, "")
            self.assertNotIn(FORBIDDEN, html)
            self.assertNotIn("★", html)
            self.assertNotIn("—", html)


class TestNoPageStatesTheLack(unittest.TestCase):
    def test_sources_and_pages_omit_the_negative_label(self):
        paths = [
            ROOT / "site/template.html",
            ROOT / "site/build_gallery.py",
        ]
        paths += list((ROOT / "docs").rglob("*.html"))
        paths += list((ROOT / "works").glob("*.html"))
        paths += [ROOT / "gallery.html", ROOT / "entries.html"]
        hits = []
        for path in paths:
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if FORBIDDEN in text:
                hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])
