"""Morningstar matrix — schema, validate, 5×5 style-box UI, Critic scores.

The fixture remains synthetic. Live matrix is Critic-signed on the assessed
Bach set: Goldberg (3), Fournier, Podger concertos, both sonatas & partitas,
both Matthew Passions, Gardiner St John, Gardiner B-minor Mass, both Art of
Fugue, and the three assessed Brandenburgs (Pinnock Référence, Harnoncourt,
Richter). Gardiner /5 is not assessed. This file does not invent scores; it
maps existing integers onto the box.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "editorial_matrix.json"


def _load(name: str, relpath: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


val = _load("validator_matrix", "agents/validate.py")
ident = _load("identity_matrix", "site/identity.py")
rnd = _load("render_matrix", "site/render.py")
disc = _load("disc_matrix", "site/disc.py")
scout = _load("scout_matrix", "site/scout.py")


def _seed() -> dict:
    return json.loads((ROOT / "data/seed.json").read_text(encoding="utf-8"))


def _tpl() -> str:
    return (ROOT / "site/template.html").read_text(encoding="utf-8")


def _fixture_entry() -> dict:
    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return doc["entries"][0]


def _html_for(work: dict, cat: dict) -> str:
    cat = scout.attach_scout_pools(disc.attach_on_this_disc(cat))
    work = next(w for w in cat["works"] if w["id"] == work["id"])
    title = f"{work['title']} — {work['composer']}"
    return rnd.apply_template(
        _tpl(),
        rnd.seal_catalogue(cat, work),
        [],
        base="../",
        title=title,
        crumb=rnd.work_crumb(work, base="../"),
    )


def _embedded_catalogue(html: str) -> dict:
    start = html.index("const CATALOGUE = ") + len("const CATALOGUE = ")
    end = html.index(";\nconst WORK_INDEX", start)
    return json.loads(html[start:end])


def _fn(tpl: str, name: str, until: str) -> str:
    start = tpl.index(f"function {name}")
    end = tpl.index(f"function {until}", start + 1)
    return tpl[start:end]


class TestMatrixOverallFormula(unittest.TestCase):
    def test_one_decimal_weighted_mean(self):
        self.assertEqual(val.matrix_overall(4, 3), "3.6")
        self.assertEqual(val.matrix_overall(5, 1), "3.4")
        self.assertEqual(val.matrix_overall(1, 1), "1.0")

    def test_js_uses_the_same_weights(self):
        tpl = _tpl()
        overall = _fn(tpl, "matrixOverall(m)", "matrixStrip(m)")
        self.assertIn("0.6*m.interpretation + 0.4*m.sound", overall)
        self.assertIn(".toFixed(1)", overall)
        strip = _fn(tpl, "matrixStrip(m)", "howScored(m)")
        self.assertNotIn("Overall", strip)
        self.assertNotIn("matrixOverall", strip)
        self.assertNotIn('class="badge"', strip)


def stylebox_grid_pos(interpretation: int, sound: int) -> tuple[int, int]:
    """CSS grid (column, row) for the 5×5 box.

    X = sound, left→right 1–5. Y = interpretation, bottom→top 1–5.
    CSS row 1 is the top of the grid.
    """
    return sound, 6 - interpretation


def stylebox_cell_index(interpretation: int, sound: int) -> int:
    """0-based index when cells are emitted high-Y first, then sound 1→5."""
    row_from_top = 5 - interpretation
    return row_from_top * 5 + (sound - 1)


class TestStyleBoxMapping(unittest.TestCase):
    def test_interpretation_5_sound_3_is_top_row_column_three(self):
        self.assertEqual(stylebox_grid_pos(5, 3), (3, 1))
        self.assertEqual(stylebox_cell_index(5, 3), 2)

    def test_corners(self):
        self.assertEqual(stylebox_grid_pos(1, 1), (1, 5))
        self.assertEqual(stylebox_grid_pos(1, 5), (5, 5))
        self.assertEqual(stylebox_grid_pos(5, 1), (1, 1))
        self.assertEqual(stylebox_grid_pos(5, 5), (5, 1))


class TestValidateMatrix(unittest.TestCase):

    RECS = {"fixture/matrix/0"}

    def _check(self, **kw):
        entry = {
            "recording": "fixture/matrix/0",
            "author": {"id": "cmrc", "name": "Classical Music Recording Critic"},
            "date": "2026-09-08",
            "revision": 1,
            "text": "An entry.",
        }
        entry.update(kw)
        return val.validate_editorial(entry, pathlib.Path("e.json"), self.RECS)

    def test_absent_matrix_is_fine(self):
        errs, _ = self._check()
        self.assertEqual(errs, [])

    def test_fixture_matrix_is_accepted(self):
        errs, _ = val.validate_editorial(
            _fixture_entry(), pathlib.Path("editorial_matrix.json"), self.RECS
        )
        self.assertEqual(errs, [])

    def test_valid_matrix_without_ledger(self):
        errs, _ = self._check(matrix={"interpretation": 1, "sound": 5})
        self.assertEqual(errs, [])

    def test_rejects_out_of_range(self):
        for bad in (0, 6, 4.5, True, "4", None):
            errs, _ = self._check(matrix={"interpretation": bad, "sound": 3})
            self.assertTrue(any("interpretation" in e for e in errs), bad)
        errs, _ = self._check(matrix={"interpretation": 3, "sound": 0})
        self.assertTrue(any("sound" in e for e in errs))

    def test_rejects_missing_axes(self):
        errs, _ = self._check(matrix={"sound": 3})
        self.assertTrue(any("interpretation" in e for e in errs))

    def test_rejects_stored_overall(self):
        errs, _ = self._check(matrix={
            "interpretation": 4, "sound": 3, "overall": 3.6,
        })
        self.assertTrue(any("overall" in e for e in errs))

    def test_rejects_bad_ledger_row(self):
        base = {"interpretation": 4, "sound": 3}
        errs, _ = self._check(matrix={**base, "ledger": "nope"})
        self.assertTrue(any("ledger" in e for e in errs))
        errs, _ = self._check(matrix={**base, "ledger": [{
            "axis": "tempo", "tier": "A", "title": "x",
            "url": "https://example.org", "note": "n",
        }]})
        self.assertTrue(any("axis" in e for e in errs))
        errs, _ = self._check(matrix={**base, "ledger": [{
            "axis": "sound", "tier": "D", "title": "x",
            "url": "https://example.org", "note": "n",
        }]})
        self.assertTrue(any("tier" in e for e in errs))
        errs, _ = self._check(matrix={**base, "ledger": [{
            "axis": "sound", "tier": "A", "title": "x",
            "url": "ftp://example.org", "note": "n",
        }]})
        self.assertTrue(any("url" in e for e in errs))
        errs, _ = self._check(matrix={**base, "ledger": [{
            "axis": "sound", "tier": "A", "title": "x",
            "url": "https://example.org", "note": "n" * 201,
        }]})
        self.assertTrue(any("200" in e for e in errs))

    def test_does_not_derive_scores_from_ledger(self):
        """C-tier rows do not invent or alter axis integers."""
        errs, _ = self._check(matrix={
            "interpretation": 2,
            "sound": 2,
            "ledger": [{
                "axis": "interpretation",
                "tier": "C",
                "title": "thin",
                "url": "https://example.org/thin",
                "note": "Secondary only; Critic still sets the integer.",
            }],
        })
        self.assertEqual(errs, [])
        self.assertEqual(val.matrix_overall(2, 2), "2.0")


# Critic-signed Morningstar axes. Integers are judgements, not ledger-derived.
LIVE_MATRIX = {
    "bach/goldberg/0": {"interpretation": 5, "sound": 3, "ledger": 3},
    "bach/goldberg/1": {"interpretation": 5, "sound": 4, "ledger": 2},
    "bach/goldberg/4": {"interpretation": 3, "sound": 4, "ledger": 2},
    "bach/cello_suites/1": {"interpretation": 5, "sound": 3, "ledger": 2},
    "bach/violin_concertos/4": {"interpretation": 5, "sound": 4, "ledger": 2},
    "bach/sonatas_partitas/0": {"interpretation": 4, "sound": 4, "ledger": 2},
    "bach/sonatas_partitas/1": {"interpretation": 5, "sound": 4, "ledger": 2},
    "bach/matthew/0": {"interpretation": 4, "sound": 3, "ledger": 2},
    "bach/matthew/1": {"interpretation": 5, "sound": 4, "ledger": 2},
    "bach/john/1": {"interpretation": 5, "sound": 4, "ledger": 2},
    "bach/mass_b_minor/0": {"interpretation": 5, "sound": 4, "ledger": 2},
    "bach/art_of_fugue/0": {"interpretation": 2, "sound": 2, "ledger": 2},
    "bach/art_of_fugue/3": {"interpretation": 4, "sound": 4, "ledger": 2},
    "bach/brandenburg/0": {"interpretation": 5, "sound": 4, "ledger": 2, "revision": 1},
    "bach/brandenburg/1": {"interpretation": 4, "sound": 2, "ledger": 2, "revision": 1},
    "bach/brandenburg/4": {"interpretation": 4, "sound": 3, "ledger": 2, "revision": 1},
}


class TestLiveCriticMatrix(unittest.TestCase):
    def test_live_assessed_bach_entries_carry_matrix(self):
        ed_dir = ROOT / "data" / "editorial"
        found = []
        for path in sorted(ed_dir.glob("*.json")):
            if path.name.startswith("_"):
                continue
            doc = json.loads(path.read_text(encoding="utf-8"))
            for ent in doc.get("entries") or []:
                if "matrix" in ent:
                    found.append(ent.get("recording"))
                    expected = LIVE_MATRIX[ent["recording"]]
                    mx = ent["matrix"]
                    self.assertEqual(mx["interpretation"], expected["interpretation"])
                    self.assertEqual(mx["sound"], expected["sound"])
                    self.assertNotIn("overall", mx)
                    self.assertEqual(len(mx["ledger"]), expected["ledger"])
                    self.assertEqual(ent["date"], "2026-09-08")
                    self.assertEqual(ent["revision"], expected.get("revision", 4))
        self.assertEqual(sorted(found), sorted(LIVE_MATRIX))

    def test_goldberg_and_fournier_cards_show_interpretation_and_sound(self):
        recs = {
            r["id"]: r
            for w in ident.public_identity_works(_seed())
            for r in w["recordings"]
        }
        self.assertGreater(len(recs), 0)
        for rid, rec in recs.items():
            ed = rec["editorial"]
            if rid in LIVE_MATRIX:
                mx = ed["matrix"]
                self.assertEqual(mx["interpretation"], LIVE_MATRIX[rid]["interpretation"], rid)
                self.assertEqual(mx["sound"], LIVE_MATRIX[rid]["sound"], rid)
                self.assertNotIn("overall", mx)
            else:
                self.assertNotIn("matrix", ed, rid)
        merged = ident.merge_identity_works(
            {"algorithm_version": "2.0", "built": "2026-09-08",
             "works": [], "barcode_index": {}},
            _seed(),
        )
        gold = next(w for w in merged["works"] if w["id"] == "bach/goldberg")
        html = _html_for(gold, merged)
        cat = _embedded_catalogue(html)
        for rec in cat["works"][0]["recordings"]:
            mx = rec["editorial"]["matrix"]
            self.assertEqual(mx["interpretation"], LIVE_MATRIX[rec["id"]]["interpretation"])
            self.assertEqual(mx["sound"], LIVE_MATRIX[rec["id"]]["sound"])
        signed = html[html.index("function signed(r)"):html.index("function factStrip")]
        self.assertIn("matrixStrip(e.matrix)", signed)
        strip = _fn(html, "matrixStrip(m)", "howScored(m)")
        self.assertIn("Interpretation", strip)
        self.assertIn("Sound", strip)
        self.assertIn("class=\"stylebox\"", strip)
        self.assertIn("grid-column:${x}", strip)
        self.assertIn("grid-row:${6-y}", strip)
        self.assertIn("The 1955 Goldberg is still the shock", html)
        self.assertIn(">References<", html)
        cello = next(w for w in merged["works"] if w["id"] == "bach/cello_suites")
        cello_html = _html_for(cello, merged)
        cello_cat = _embedded_catalogue(cello_html)
        fournier = cello_cat["works"][0]["recordings"][0]
        self.assertEqual(fournier["id"], "bach/cello_suites/1")
        self.assertEqual(fournier["editorial"]["matrix"]["interpretation"], 5)
        self.assertEqual(fournier["editorial"]["matrix"]["sound"], 3)
        self.assertEqual(stylebox_grid_pos(5, 3), (3, 1))
        vc = next(w for w in merged["works"] if w["id"] == "bach/violin_concertos")
        vc_html = _html_for(vc, merged)
        vc_cat = _embedded_catalogue(vc_html)
        podger = vc_cat["works"][0]["recordings"][0]
        self.assertEqual(podger["id"], "bach/violin_concertos/4")
        self.assertEqual(podger["editorial"]["matrix"]["interpretation"], 5)
        self.assertEqual(podger["editorial"]["matrix"]["sound"], 4)
        aof = next(w for w in merged["works"] if w["id"] == "bach/art_of_fugue")
        aof_html = _html_for(aof, merged)
        aof_cat = _embedded_catalogue(aof_html)
        gould = next(r for r in aof_cat["works"][0]["recordings"] if r["id"] == "bach/art_of_fugue/0")
        emerson = next(r for r in aof_cat["works"][0]["recordings"] if r["id"] == "bach/art_of_fugue/3")
        self.assertEqual(gould["editorial"]["matrix"]["interpretation"], 2)
        self.assertEqual(gould["editorial"]["matrix"]["sound"], 2)
        self.assertEqual(emerson["editorial"]["matrix"]["interpretation"], 4)
        self.assertEqual(emerson["editorial"]["matrix"]["sound"], 4)
        brand = next(w for w in merged["works"] if w["id"] == "bach/brandenburg")
        brand_html = _html_for(brand, merged)
        self.assertIn("Pinnock’s 1982 English Concert Brandenburgs", brand_html)
        self.assertIn("The modern Munich pole of this argument.", brand_html)
        self.assertNotIn("Three stars", brand_html)
        brand_cat = _embedded_catalogue(brand_html)
        pinnock = next(
            r for r in brand_cat["works"][0]["recordings"]
            if r["id"] == "bach/brandenburg/0"
        )
        self.assertEqual(pinnock["editorial"]["matrix"]["interpretation"], 5)
        self.assertEqual(pinnock["editorial"]["matrix"]["sound"], 4)
        self.assertTrue(pinnock["editorial"]["reference"])
        self.assertEqual(stylebox_grid_pos(5, 4), (4, 1))

    def test_brandenburg_matrix_is_the_three_assessed(self):
        path = ROOT / "data" / "editorial" / "bach_brandenburg.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        ids = [ent["recording"] for ent in doc["entries"]]
        self.assertEqual(ids, [
            "bach/brandenburg/0",
            "bach/brandenburg/1",
            "bach/brandenburg/4",
        ])
        self.assertNotIn("bach/brandenburg/5", ids)
        by_id = {ent["recording"]: ent for ent in doc["entries"]}
        self.assertTrue(by_id["bach/brandenburg/0"]["reference"])
        self.assertFalse(by_id["bach/brandenburg/1"]["reference"])
        self.assertFalse(by_id["bach/brandenburg/4"]["reference"])
        richter = by_id["bach/brandenburg/4"]["text"]
        self.assertTrue(
            richter.endswith("The modern Munich pole of this argument."),
            richter[-80:],
        )
        self.assertNotIn("Three stars", richter)
        for ent in doc["entries"]:
            self.assertNotIn("Three stars", ent["text"])
            self.assertNotEqual(ent["recording"], "bach/brandenburg/5")
            self.assertNotIn("Gardiner", ent["text"])


class TestMatrixCardRender(unittest.TestCase):
    def _page(self, editorial: dict | None, *, card="identity") -> str:
        rec = {
            "id": "fixture/matrix/0",
            "work": "fixture/matrix",
            "card": card,
            "soloists": "Fixture Pianist",
            "director": "",
            "ensemble": "",
            "published": "Test, 2026",
            "editions": [],
            "fact_strip": {"label": "Test"},
            "anchors": [],
            "reception": [],
            "sources": [],
            "editorial": editorial,
            "divergence": None,
        }
        if card != "identity":
            rec.update({
                "interpretation": None,
                "confidence": None,
                "stars": None,
                "reference": False,
                "sound_best": None,
                "engineering": {
                    "venue": "x", "sessions": "2026",
                    "producer": None, "engineer": None, "status": "unknown",
                },
            })
        work = {
            "id": "fixture/matrix",
            "composer": "Fixture Composer",
            "dates": "",
            "title": "Fixture Work",
            "cat": "",
            "standfirst": "",
            "recordings": [rec],
        }
        cat = {
            "algorithm_version": "2.0",
            "built": "2026-09-08",
            "barcode_index": {},
            "works": [work],
        }
        return _html_for(work, cat)

    def test_fixture_with_matrix_embeds_two_integers_and_expand(self):
        entry = _fixture_entry()
        html = self._page(entry)
        cat = _embedded_catalogue(html)
        rec = cat["works"][0]["recordings"][0]
        matrix = rec["editorial"]["matrix"]
        self.assertEqual(matrix["interpretation"], 4)
        self.assertEqual(matrix["sound"], 3)
        self.assertNotIn("overall", matrix)
        self.assertEqual(len(matrix["ledger"]), 2)
        tpl = html
        strip = _fn(tpl, "matrixStrip(m)", "howScored(m)")
        self.assertIn("Interpretation", strip)
        self.assertIn("Sound", strip)
        self.assertIn("m.interpretation", strip)
        self.assertIn("m.sound", strip)
        how = _fn(tpl, "howScored(m)", "signed(r)")
        self.assertIn("How scored", how)
        self.assertIn("Evidence ledger", how)
        self.assertIn("Tier C evidence cannot raise an axis", how)
        self.assertIn("Overall", how)
        self.assertIn("matrixOverall(m)", how)
        self.assertIn("row.axis", how)
        self.assertIn("row.tier", how)
        self.assertIn("row.title", how)
        self.assertIn("row.url", how)
        self.assertIn("row.note", how)
        signed = _fn(tpl, "signed(r)", "factStrip(r)")
        body_at = signed.index('class="body"')
        self.assertGreater(signed.index("matrixStrip("), body_at)
        self.assertGreater(signed.index("howScored("), signed.index("matrixStrip("))
        self.assertGreater(signed.index("consultedRefs("), signed.index("howScored("))
        self.assertIn(">References<", html)
        self.assertIn("class=\"matrix\"", strip)
        self.assertIn("class=\"stylebox\"", strip)
        self.assertIn("Interpretation ${esc(i)} · Sound ${esc(s)}", strip)
        self.assertNotIn("Overall", strip)

    def test_fixture_5_3_places_filled_cell_at_grid_position(self):
        """Interpretation 5, Sound 3 → column 3, CSS row 1 (top)."""
        entry = _fixture_entry()
        entry["matrix"]["interpretation"] = 5
        entry["matrix"]["sound"] = 3
        html = self._page(entry)
        cat = _embedded_catalogue(html)
        matrix = cat["works"][0]["recordings"][0]["editorial"]["matrix"]
        self.assertEqual(matrix["interpretation"], 5)
        self.assertEqual(matrix["sound"], 3)
        col, row = stylebox_grid_pos(5, 3)
        self.assertEqual((col, row), (3, 1))
        self.assertEqual(stylebox_cell_index(5, 3), 2)
        strip = _fn(html, "matrixStrip(m)", "howScored(m)")
        self.assertIn("for(let y=5;y>=1;y--)", strip)
        self.assertIn("for(let x=1;x<=5;x++)", strip)
        self.assertIn("x===s && y===i", strip)
        self.assertIn("grid-column:${x}", strip)
        self.assertIn("grid-row:${6-y}", strip)
        self.assertIn('data-sound="${x}"', strip)
        self.assertIn('data-interpretation="${y}"', strip)
        self.assertIn('class="cell${filled?" filled":""}"', strip)
        self.assertIn("Interpretation ${esc(i)} · Sound ${esc(s)}", strip)
        self.assertIn("Filled cell:", strip)

    def test_caption_keeps_integer_pair(self):
        html = self._page(_fixture_entry())
        strip = _fn(html, "matrixStrip(m)", "howScored(m)")
        self.assertIn("matrix-cap", strip)
        self.assertIn("Interpretation ${esc(i)} · Sound ${esc(s)}", strip)
        cat = _embedded_catalogue(html)
        mx = cat["works"][0]["recordings"][0]["editorial"]["matrix"]
        self.assertEqual(mx["interpretation"], 4)
        self.assertEqual(mx["sound"], 3)

    def test_sound_axis_uses_reference_not_reference_flag(self):
        tpl = _tpl()
        self.assertIn('const MATRIX_SOUND=["Hard listen","Serviceable","Clean","Excellent","Reference"]', tpl)
        self.assertIn('const MATRIX_INTERP=["Documentary","Competent","Solid","Outstanding","Landmark"]', tpl)
        strip = _fn(tpl, "matrixStrip(m)", "howScored(m)")
        how = _fn(tpl, "howScored(m)", "signed(r)")
        self.assertNotIn("Référence", strip)
        self.assertNotIn("Référence", how)
        self.assertIn("MATRIX_SOUND[0]", strip)
        self.assertIn("MATRIX_SOUND[4]", strip)
        self.assertIn("MATRIX_INTERP[0]", strip)
        self.assertIn("MATRIX_INTERP[4]", strip)
        self.assertNotIn("MATRIX_SOUND[1]", strip)
        self.assertNotIn("MATRIX_SOUND[2]", strip)
        self.assertNotIn("MATRIX_SOUND[3]", strip)
        self.assertNotIn("MATRIX_INTERP[1]", strip)
        self.assertNotIn("MATRIX_INTERP[2]", strip)
        self.assertNotIn("MATRIX_INTERP[3]", strip)
        self.assertIn("MATRIX_SOUND.map", how)
        self.assertIn("MATRIX_INTERP.map", how)
        signed = _fn(tpl, "signed(r)", "factStrip(r)")
        self.assertIn("Référence", signed)

    def test_entry_without_matrix_keeps_signed_block_and_skips_strip(self):
        editorial = {
            "recording": "fixture/matrix/0",
            "author": {"id": "cmrc", "name": "Classical Music Recording Critic"},
            "date": "2026-09-08",
            "revision": 1,
            "stars": 2,
            "reference": False,
            "text": "Fixture signed prose without a matrix.",
            "quotes": [],
            "consulted": [{
                "title": "Example",
                "url": "https://example.org/disc",
                "kind": "discography",
            }],
        }
        html = self._page(editorial)
        cat = _embedded_catalogue(html)
        rec = cat["works"][0]["recordings"][0]
        self.assertNotIn("matrix", rec["editorial"])
        strip = _fn(html, "matrixStrip(m)", "howScored(m)")
        self.assertIn("if(!m) return \"\"", strip)
        how = _fn(html, "howScored(m)", "signed(r)")
        self.assertIn("if(!m) return \"\"", how)
        self.assertIn("Fixture signed prose without a matrix.", html)
        self.assertIn(">References<", html)
        identity = html[html.index("function identityLine(r)"):html.index("function entry(r)")]
        self.assertNotIn("scorebox", identity)
        self.assertIn("signed(", identity)

    def test_scored_entry_path_also_calls_signed_matrix(self):
        html = self._page(_fixture_entry(), card="scored")
        entry_fn = html[html.index("function entry(r)"):html.index("const workDomId")]
        self.assertIn("signed(r)", entry_fn)
        cat = _embedded_catalogue(html)
        self.assertEqual(
            cat["works"][0]["recordings"][0]["editorial"]["matrix"]["interpretation"],
            4,
        )


class TestRegressionAnchorsUntouched(unittest.TestCase):
    def test_engine_anchors_still_match_agents_table(self):
        eng = _load("engine_v2_matrix", "engine/aggregation_engine_v2.py")
        by_id = {r["id"]: r for r in (eng.run(rec) for rec in eng.catalogue())}
        self.assertAlmostEqual(by_id["bach_brandenburg_pinnock"]["interpretation"], 2.853, places=3)
        self.assertFalse(by_id["bach_brandenburg_pinnock"]["reference"])
        self.assertAlmostEqual(by_id["bach_brandenburg_harnoncourt"]["interpretation"], 2.814, places=3)
        self.assertFalse(by_id["bach_brandenburg_harnoncourt"]["reference"])
        self.assertAlmostEqual(by_id["puccini_tosca_desabata"]["interpretation"], 2.955, places=3)
        self.assertTrue(by_id["puccini_tosca_desabata"]["reference"])
        self.assertAlmostEqual(by_id["puccini_tosca_karajan"]["interpretation"], 2.848, places=3)
        self.assertFalse(by_id["puccini_tosca_karajan"]["reference"])
        self.assertEqual(eng.ALGORITHM_VERSION, "2.0")


if __name__ == "__main__":
    unittest.main()
