"""Fact-strip rendering lists only known facts.

An unknown engineer (null, blank, or a placeholder such as "not established")
is left out of the sentence. A known engineer still renders. The same rule
applies to the other fact-strip fields, so the line does not keep a dangling
role label, a code-styled placeholder, or a stray separator.
"""

from __future__ import annotations

import json
import pathlib
import re
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
        self.assertNotIn("credits unknown", html)
        self.assertNotIn("credits ", html)
        self.assertEqual(html, '<p class="credits">live, 2015.</p>')

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

    def test_no_known_credit_prints_nothing(self):
        html = render("credits", {
            "venue": "not established",
            "sessions": None,
            "producer": "unknown",
            "engineer": "not known",
            "status": "unknown",
        })
        self.assertEqual(html, "")
        self.assertNotIn("credits unknown", html)
        self.assertNotIn("not established", html.lower())
        self.assertNotIn("not known", html.lower())


def _gallery_made_by_js() -> str:
    src = (ROOT / "site/build_gallery.py").read_text(encoding="utf-8")
    esc_at = src.index("const esc =")
    esc = src[esc_at:src.index("\n", esc_at) + 1]
    helpers = src[src.index("function knownFact"):src.index("function render(i)")]
    return esc + helpers


def render_made_by(payload: dict) -> str:
    script = _gallery_made_by_js() + (
        "const payload = JSON.parse(process.argv[2]);\n"
        "process.stdout.write(madeBy(payload));\n"
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


class TestGalleryMadeBy(unittest.TestCase):
    def test_unknown_rows_drop_and_known_credits_stay(self):
        html = render_made_by(_recording("bach_brandenburg_pinnock")["engineering"])
        self.assertIn("<h3>Made by</h3>", html)
        self.assertIn("Henry Wood Hall, London", html)
        self.assertIn("Andreas Holschneider", html)
        self.assertIn(">1982<", html)
        self.assertIn("attributed", html)
        self.assertIn("Producer", html)
        self.assertNotIn("Engineer", html)
        self.assertNotIn("not established", html.lower())
        self.assertNotIn("not known", html.lower())
        self.assertNotIn("credits unknown", html.lower())

    def test_known_engineer_still_renders(self):
        html = render_made_by(_recording("shostakovich_sym5_noseda")["engineering"])
        self.assertIn("<h3>Made by</h3>", html)
        self.assertIn("Engineer", html)
        self.assertIn("Classic Sound Ltd", html)
        self.assertIn("Nicholas Parker", html)
        self.assertIn("Barbican Hall, London", html)

    def test_every_unknown_row_omits_the_panel(self):
        html = render_made_by({
            "venue": "not established",
            "sessions": "—",
            "producer": None,
            "engineer": "not known",
            "status": "unknown",
        })
        self.assertEqual(html, "")
        self.assertNotIn("Made by", html)


_VISIBLE_FORBIDDEN = ("not established", "credits unknown", "not known")

_DOM_STUB = r"""
const __visible = [];
function __note(v){ if(v!=null) __visible.push(String(v)); }
function __el(id){
  const node = {
    id, style: {}, hidden: false, value: "", dataset: {},
    classList: { add(){}, remove(){}, toggle(){}, contains(){ return false; } },
    addEventListener(){}, setAttribute(){}, getAttribute(){ return ""; },
    removeAttribute(){}, closest(){ return null; }, scrollIntoView(){},
    focus(){}, blur(){}, click(){}, remove(){},
    play(){ return Promise.resolve(); },
    querySelector(){ return __el(String(id)+"-q"); },
    querySelectorAll(){ return []; },
  };
  let html = "", text = "";
  Object.defineProperty(node, "innerHTML", {
    get(){ return html; },
    set(v){ html = String(v ?? ""); __note(html); },
  });
  Object.defineProperty(node, "textContent", {
    get(){ return text; },
    set(v){ text = String(v ?? ""); __note(text); },
  });
  return node;
}
const __els = {};
const document = {
  getElementById(id){ return __els[id] || (__els[id] = __el(id)); },
  querySelector(){ return null; },
  querySelectorAll(){ return []; },
  addEventListener(){},
  createElement(){ return __el("dyn"); },
};
const location = { hash: "", href: "", replace(){}, assign(){} };
const window = {};
const navigator = { mediaDevices: {} };
"""


def _page_paths() -> list[pathlib.Path]:
    paths: list[pathlib.Path] = []
    for rel in ("docs", "works", "composers"):
        base = ROOT / rel
        if base.is_dir():
            paths.extend(p for p in base.rglob("*.html") if p.is_file())
    for name in ("gallery.html", "entries.html", "index.html"):
        path = ROOT / name
        if path.is_file():
            paths.append(path)
    return paths


def _tags_to_text(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).lower()


def _static_visible(html: str) -> str:
    stripped = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    stripped = re.sub(r"<style\b[^>]*>.*?</style>", " ", stripped, flags=re.I | re.S)
    stripped = re.sub(r"<!--.*?-->", " ", stripped, flags=re.S)
    return _tags_to_text(stripped)


def _rendered_visible(html: str) -> str:
    scripts = re.findall(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, flags=re.I | re.S)
    body = "\n".join(s for s in scripts if s.strip())
    if "function workSection" not in body and "const FLAT" not in body:
        return ""
    extra = ""
    if "const FLAT" in body:
        extra = (
            "if (typeof FLAT !== 'undefined' && typeof render === 'function') {\n"
            "  for (let i = 0; i < FLAT.length; i++) render(i);\n"
            "}\n"
        )
    script = _DOM_STUB + body + extra + "process.stdout.write(__visible.join('\\n'));\n"
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(script)
        path = fh.name
    try:
        proc = subprocess.run(
            ["node", path],
            check=False,
            capture_output=True,
            text=True,
        )
    finally:
        pathlib.Path(path).unlink(missing_ok=True)
    if proc.returncode != 0:
        raise AssertionError(proc.stderr or proc.stdout)
    return _tags_to_text(proc.stdout)


class TestRenderedPagesOmitUnknownPlaceholders(unittest.TestCase):
    def test_no_page_shows_unknown_credit_placeholders(self):
        hits = []
        for path in _page_paths():
            html = path.read_text(encoding="utf-8")
            visible = _static_visible(html) + " " + _rendered_visible(html)
            found = [phrase for phrase in _VISIBLE_FORBIDDEN if phrase in visible]
            if found:
                hits.append(f"{path.relative_to(ROOT)}: {', '.join(found)}")
        self.assertEqual(hits, [])
