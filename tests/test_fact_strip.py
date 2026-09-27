"""Fact-strip rendering lists only known facts.

An unknown engineer (null, blank, or a placeholder such as "not established")
is left out of the sentence. A known engineer still renders. The same rule
applies to the other fact-strip fields, so the line does not keep a dangling
role label, a code-styled placeholder, or a stray separator.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _renderer_js() -> str:
    tpl = (ROOT / "site/template.html").read_text(encoding="utf-8")
    esc_at = tpl.index("const esc=")
    esc = tpl[esc_at:tpl.index("\n", esc_at) + 1]
    helpers = tpl[tpl.index("function knownFact"):tpl.index("function anchors")]
    fact = tpl[tpl.index("function factStrip"):tpl.index("function identityLine")]
    return esc + helpers + fact


def render(fn: str, payload: dict) -> str:
    script = _renderer_js() + (
        "const payload = JSON.parse(process.argv[2]);\n"
        f"const html = {fn}(payload);\n"
        "process.stdout.write(html == null ? '' : String(html));\n"
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


def _recording(rid: str) -> dict:
    cat = json.loads((ROOT / "build/catalogue.json").read_text(encoding="utf-8"))
    for work in cat["works"]:
        for rec in work["recordings"]:
            if rec["id"] == rid:
                return rec
    raise AssertionError(rid)


class TestFactStripOmitsUnknown(unittest.TestCase):
    def test_unknown_engineer_produces_no_engineer_text(self):
        html = render("credits", _recording("puccini_tosca_desabata")["engineering"])
        self.assertNotIn("Engineer", html)
        self.assertNotIn("not established", html.lower())
        self.assertNotIn("not known", html.lower())
        self.assertNotIn('class="unknown"', html)
        self.assertIn("Walter Legge", html)
        self.assertIn("Teatro alla Scala, Milan", html)
        self.assertIn("10–21 August 1953", html)
        self.assertNotIn("..", html)
        self.assertEqual(
            html,
            "<p class=\"credits\"><b>Teatro alla Scala, Milan</b>, "
            "10–21 August 1953. Producer Walter Legge. "
            "<span class=\"prov\">credits cited</span></p>",
        )

    def test_known_engineer_still_renders(self):
        html = render("credits", _recording("puccini_tosca_karajan")["engineering"])
        self.assertIn("Engineer Gordon Parry", html)
        self.assertIn("Producer John Culshaw", html)
        self.assertIn("Sofiensaal, Vienna", html)
        self.assertNotIn("not established", html.lower())
        self.assertEqual(
            html,
            "<p class=\"credits\"><b>Sofiensaal, Vienna</b>, "
            "24–30 September 1962. Producer John Culshaw. Engineer Gordon Parry. "
            "<span class=\"prov\">credits cited</span></p>",
        )

    def test_null_and_placeholder_fields_drop_out_of_the_sentence(self):
        html = render("credits", {
            "venue": "not established",
            "sessions": "live, 2015",
            "producer": None,
            "engineer": "not established — contribute",
            "status": "unknown",
        })
        self.assertNotIn("Engineer", html)
        self.assertNotIn("Producer", html)
        self.assertNotIn("not established", html.lower())
        self.assertNotIn("<b>", html)
        self.assertNotIn(", .", html)
        self.assertNotIn("..", html)
        self.assertIn("live, 2015.", html)
        self.assertIn("credits unknown", html)

        strip = render("factStrip", {
            "soloists": "Maria Callas",
            "director": "Victor de Sabata",
            "ensemble": "Orchestra e Coro del Teatro alla Scala",
            "fact_strip": {
                "label": "EMI",
                "venue": "—",
                "sessions": "10–21 August 1953",
                "producer": "n/a",
                "engineer": "not known",
                "contents_note": "HMC 901498.99 — Dec 1993 sessions.",
            },
        })
        self.assertNotIn("Engineer", strip)
        self.assertNotIn("Producer", strip)
        self.assertNotIn("not known", strip.lower())
        self.assertNotIn("<b>", strip)
        self.assertIn("10–21 August 1953.", strip)
        self.assertNotIn(", 10–21", strip)
        self.assertIn("HMC 901498.99 — Dec 1993 sessions.", strip)
        self.assertIn("EMI", strip)

        known = render("factStrip", {
            "soloists": "",
            "director": "",
            "ensemble": "",
            "fact_strip": {
                "venue": "Sofiensaal, Vienna",
                "sessions": "24–30 September 1962",
                "producer": "John Culshaw",
                "engineer": "Gordon Parry",
            },
        })
        self.assertIn(
            "Producer John Culshaw. Engineer Gordon Parry.",
            known,
        )
        self.assertIn("<b>Sofiensaal, Vienna</b>, 24–30 September 1962.", known)
