"""Morningstar matrix — schema, validate, derived 3×3 style-box UI, Critic scores.

The fixture remains synthetic. Live matrix is Critic-signed on the assessed
Bach set: Goldberg (3), Fournier, Podger concertos, both sonatas & partitas,
both Matthew Passions, Gardiner St John, Gardiner B-minor Mass, both Art of
Fugue, and the three assessed Brandenburgs (Pinnock Référence, Harnoncourt,
Richter). Gardiner /5 is not assessed. Handel week-1 adds Messiah (Gardiner
Référence, Mackerras, Christie), Water Music (Pinnock Référence, Harnoncourt)
and Giulio Cesare (Jacobs Référence, Mackerras ENO). This file does not invent
scores; it maps existing integers onto the box.
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


def stylebox_cell_index(interpretation: int, sound: int) -> int:
    """0-based index when cells are emitted high band first, then sound band left→right."""
    ib = val.matrix_band_index(interpretation, val.INTERPRETATION_BANDS)
    sb = val.matrix_band_index(sound, val.SOUND_BANDS)
    row_from_top = 2 - ib
    return row_from_top * 3 + sb


BAND_LINE = (
    "Interpretation: 5 is Outstanding, 4 is Strong, 1 to 3 is With reservations. "
    "Sound: 4 or 5 is Excellent, 3 is Good, 1 or 2 is Limited."
)


class TestMatrixBandMapping(unittest.TestCase):
    def test_every_integer_lands_in_exactly_one_band(self):
        for bands in (val.INTERPRETATION_BANDS, val.SOUND_BANDS):
            covered = []
            for lo, hi, _name in bands:
                covered.extend(range(lo, hi + 1))
            self.assertEqual(covered, [1, 2, 3, 4, 5])
            for score in range(1, 6):
                self.assertEqual(len(val.matrix_band_hits(score, bands)), 1)
            for score in (0, 6, 4.5, True, "4", None):
                self.assertEqual(val.matrix_band_hits(score, bands), [])

    def test_named_bands(self):
        self.assertEqual(
            [val.matrix_band(n, val.INTERPRETATION_BANDS) for n in range(1, 6)],
            [
                "With reservations",
                "With reservations",
                "With reservations",
                "Strong",
                "Outstanding",
            ],
        )
        self.assertEqual(
            [val.matrix_band(n, val.SOUND_BANDS) for n in range(1, 6)],
            ["Limited", "Limited", "Good", "Excellent", "Excellent"],
        )
        self.assertEqual(val.MATRIX_BAND_LINE, BAND_LINE)
        self.assertNotIn("Référence", [name for _lo, _hi, name in val.INTERPRETATION_BANDS])
        self.assertNotIn("Référence", [name for _lo, _hi, name in val.SOUND_BANDS])
        self.assertNotIn("Reference", [name for _lo, _hi, name in val.SOUND_BANDS])
        self.assertNotIn("Reference", [name for _lo, _hi, name in val.INTERPRETATION_BANDS])

    def test_cell_ignores_the_ledger(self):
        """Same integers, different ledger rows: one cell. The ledger is not an argument."""
        self.assertEqual(val.stylebox_grid_pos(4, 2), val.stylebox_grid_pos(4, 2))
        self.assertEqual(
            val.matrix_band(4, val.INTERPRETATION_BANDS),
            "Strong",
        )
        strip = _fn(_tpl(), "matrixStrip(m)", "howScored(m)")
        self.assertNotIn("m.ledger", strip)
        self.assertNotIn("row.tier", strip)
        ready = _fn(_tpl(), "matrixReady(m)", "matrixOverall(m)")
        self.assertNotIn("m.ledger", ready)
        self.assertIn("m.interpretation", ready)
        self.assertIn("m.sound", ready)

    def test_js_uses_the_same_partition(self):
        interp = _fn(_tpl(), "interpretationBandIndex(score)", "soundBandIndex(score)")
        sound = _fn(_tpl(), "soundBandIndex(score)", "matrixReady(m)")
        self.assertIn("if(score<=3) return 0;", interp)
        self.assertIn("if(score===4) return 1;", interp)
        self.assertIn("return 2;", interp)
        self.assertIn("if(score<=2) return 0;", sound)
        self.assertIn("if(score===3) return 1;", sound)
        self.assertIn("return 2;", sound)
        self.assertIn('const MATRIX_SOUND_BANDS=["Limited","Good","Excellent"]', _tpl())
        self.assertIn(
            'const MATRIX_INTERP_BANDS=["With reservations","Strong","Outstanding"]',
            _tpl(),
        )
        self.assertEqual(_tpl().count(BAND_LINE), 1)
        self.assertNotIn('"Reference"', _tpl())
        self.assertNotIn("Of historical interest", _tpl())
        self.assertNotIn(">Landmark<", _tpl())

    def test_interpretation_5_sound_3_is_top_row_middle_column(self):
        """Sound 3 is the middle band; interpretation 5 is the top band."""
        self.assertEqual(val.stylebox_grid_pos(5, 3), (2, 1))
        self.assertEqual(stylebox_cell_index(5, 3), 1)

    def test_corners_and_which_neighbours_share_a_cell(self):
        self.assertEqual(val.stylebox_grid_pos(1, 1), (1, 3))
        self.assertEqual(val.stylebox_grid_pos(1, 5), (3, 3))
        self.assertEqual(val.stylebox_grid_pos(5, 1), (1, 1))
        self.assertEqual(val.stylebox_grid_pos(5, 5), (3, 1))
        # Interpretation 1, 2 and 3 share With reservations. Sound 1 and 2 share Limited.
        self.assertEqual(val.stylebox_grid_pos(1, 1), val.stylebox_grid_pos(3, 2))
        # Interpretation 4 is Strong, not Outstanding. Sound 4 and 5 share Excellent.
        self.assertEqual(val.stylebox_grid_pos(4, 4), (3, 2))
        self.assertNotEqual(val.stylebox_grid_pos(4, 4), val.stylebox_grid_pos(5, 5))
        self.assertEqual(val.stylebox_grid_pos(5, 4), val.stylebox_grid_pos(5, 5))
        self.assertEqual(val.stylebox_grid_pos(3, 3), (2, 3))


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

    def test_rejects_stored_band_or_cell(self):
        errs, _ = self._check(matrix={
            "interpretation": 4, "sound": 5, "interpretation_band": "Outstanding",
        })
        self.assertTrue(any("interpretation_band" in e and "not stored" in e for e in errs))
        errs, _ = self._check(matrix={
            "interpretation": 4, "sound": 5, "cell": "Outstanding / Excellent",
        })
        self.assertTrue(any("cell" in e and "not stored" in e for e in errs))

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
    "handel/messiah/2": {"interpretation": 5, "sound": 4, "ledger": 3, "revision": 1, "date": "2026-09-19"},
    "handel/messiah/1": {"interpretation": 4, "sound": 3, "ledger": 3, "revision": 1, "date": "2026-09-19"},
    "handel/messiah/3": {"interpretation": 4, "sound": 4, "ledger": 3, "revision": 1, "date": "2026-09-19"},
    "handel/water_music/0": {"interpretation": 5, "sound": 5, "ledger": 3, "revision": 1, "date": "2026-09-19"},
    "handel/water_music/2": {"interpretation": 4, "sound": 3, "ledger": 3, "revision": 1, "date": "2026-09-19"},
    "handel/giulio_cesare/1": {"interpretation": 5, "sound": 4, "ledger": 3, "revision": 1, "date": "2026-09-19"},
    "handel/giulio_cesare/0": {"interpretation": 5, "sound": 4, "ledger": 3, "revision": 1, "date": "2026-09-19"},
}


class TestLiveCriticMatrix(unittest.TestCase):
    def test_live_assessed_entries_carry_matrix(self):
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
                    self.assertEqual(set(mx), {"interpretation", "sound", "ledger"})
                    self.assertEqual(len(mx["ledger"]), expected["ledger"])
                    self.assertEqual(ent["date"], expected.get("date", "2026-09-08"))
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
            elif ed is None:
                # Handel week-1 identity cards: no signed entry, no matrix.
                self.assertTrue(str(rid).startswith("handel/"), rid)
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
        self.assertIn("grid-column:${col}", strip)
        self.assertIn("grid-row:${row}", strip)
        self.assertIn("repeat(3,1fr)", html)
        self.assertIn("The 1955 Goldberg is still the shock", html)
        self.assertIn(">References<", html)
        cello = next(w for w in merged["works"] if w["id"] == "bach/cello_suites")
        cello_html = _html_for(cello, merged)
        cello_cat = _embedded_catalogue(cello_html)
        fournier = cello_cat["works"][0]["recordings"][0]
        self.assertEqual(fournier["id"], "bach/cello_suites/1")
        self.assertEqual(fournier["editorial"]["matrix"]["interpretation"], 5)
        self.assertEqual(fournier["editorial"]["matrix"]["sound"], 3)
        self.assertEqual(val.stylebox_grid_pos(5, 3), (2, 1))
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
        self.assertEqual(val.stylebox_grid_pos(5, 4), (3, 1))

    def test_handel_week1_cards_show_interpretation_and_sound(self):
        merged = ident.merge_identity_works(
            {"algorithm_version": "2.0", "built": "2026-09-19",
             "works": [], "barcode_index": {}},
            _seed(),
        )
        messiah = next(w for w in merged["works"] if w["id"] == "handel/messiah")
        html = _html_for(messiah, merged)
        self.assertIn("Gardiner’s Philips Messiah remains the digital period-instrument classic", html)
        self.assertIn("Mackerras’s Ambrosian/ECO Messiah", html)
        self.assertNotIn("Three stars", html)
        cat = _embedded_catalogue(html)
        gardiner = next(
            r for r in cat["works"][0]["recordings"] if r["id"] == "handel/messiah/2"
        )
        self.assertEqual(gardiner["editorial"]["matrix"]["interpretation"], 5)
        self.assertEqual(gardiner["editorial"]["matrix"]["sound"], 4)
        self.assertTrue(gardiner["editorial"]["reference"])
        self.assertEqual(val.stylebox_grid_pos(5, 4), (3, 1))
        water = next(w for w in merged["works"] if w["id"] == "handel/water_music")
        water_html = _html_for(water, merged)
        water_cat = _embedded_catalogue(water_html)
        pinnock = next(
            r for r in water_cat["works"][0]["recordings"]
            if r["id"] == "handel/water_music/0"
        )
        self.assertEqual(pinnock["editorial"]["matrix"]["interpretation"], 5)
        self.assertEqual(pinnock["editorial"]["matrix"]["sound"], 5)
        self.assertTrue(pinnock["editorial"]["reference"])
        self.assertEqual(val.stylebox_grid_pos(5, 5), (3, 1))
        cesare = next(w for w in merged["works"] if w["id"] == "handel/giulio_cesare")
        cesare_html = _html_for(cesare, merged)
        cesare_cat = _embedded_catalogue(cesare_html)
        jacobs = next(
            r for r in cesare_cat["works"][0]["recordings"]
            if r["id"] == "handel/giulio_cesare/1"
        )
        self.assertEqual(jacobs["editorial"]["matrix"]["interpretation"], 5)
        self.assertEqual(jacobs["editorial"]["matrix"]["sound"], 4)
        self.assertTrue(jacobs["editorial"]["reference"])

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
        self.assertIn("Interpretation: ${esc(iName)} · Sound: ${esc(sName)}", strip)
        self.assertNotIn("Overall", strip)
        self.assertIn("Interpretation ${esc(m.interpretation)}", how)
        self.assertIn("Sound ${esc(m.sound)}", how)
        self.assertIn("${MATRIX_BAND_LINE}", how)
        scores_at = how.index("Interpretation ${esc(m.interpretation)}")
        line_at = how.index("${MATRIX_BAND_LINE}")
        self.assertLess(scores_at, line_at)
        self.assertNotIn("rubric", how[scores_at:line_at])

    def test_fixture_5_3_places_filled_cell_at_grid_position(self):
        """Interpretation 5, Sound 3 → middle column, CSS row 1 (top band)."""
        entry = _fixture_entry()
        entry["matrix"]["interpretation"] = 5
        entry["matrix"]["sound"] = 3
        html = self._page(entry)
        cat = _embedded_catalogue(html)
        matrix = cat["works"][0]["recordings"][0]["editorial"]["matrix"]
        self.assertEqual(matrix["interpretation"], 5)
        self.assertEqual(matrix["sound"], 3)
        self.assertNotIn("cell", matrix)
        col, row = val.stylebox_grid_pos(5, 3)
        self.assertEqual((col, row), (2, 1))
        self.assertEqual(stylebox_cell_index(5, 3), 1)
        strip = _fn(html, "matrixStrip(m)", "howScored(m)")
        self.assertIn("for(let y=2;y>=0;y--)", strip)
        self.assertIn("for(let x=0;x<=2;x++)", strip)
        self.assertIn("x===sb && y===ib", strip)
        self.assertIn("grid-column:${col}", strip)
        self.assertIn("grid-row:${row}", strip)
        self.assertIn('data-sound-band="${col}"', strip)
        self.assertIn('data-interpretation-band="${y+1}"', strip)
        self.assertIn('class="cell${filled?" filled":""}"', strip)
        self.assertIn("Interpretation: ${esc(iName)} · Sound: ${esc(sName)}", strip)
        self.assertIn("Filled cell:", strip)
        self.assertIn("repeat(3,1fr)", html)

    def test_caption_uses_band_names_integers_stay_in_the_expand(self):
        html = self._page(_fixture_entry())
        strip = _fn(html, "matrixStrip(m)", "howScored(m)")
        how = _fn(html, "howScored(m)", "signed(r)")
        self.assertIn("matrix-cap", strip)
        self.assertIn("Interpretation: ${esc(iName)} · Sound: ${esc(sName)}", strip)
        self.assertNotIn("Interpretation ${esc(i)} · Sound ${esc(s)}", strip)
        self.assertIn("Interpretation ${esc(m.interpretation)} · Sound ${esc(m.sound)}", how)
        self.assertIn("${MATRIX_BAND_LINE}", how)
        self.assertLess(
            how.index("Interpretation ${esc(m.interpretation)}"),
            how.index("${MATRIX_BAND_LINE}"),
        )
        cat = _embedded_catalogue(html)
        mx = cat["works"][0]["recordings"][0]["editorial"]["matrix"]
        self.assertEqual(mx["interpretation"], 4)
        self.assertEqual(mx["sound"], 3)
        self.assertEqual(set(mx), {"interpretation", "sound", "ledger"})
        self.assertEqual(val.matrix_band(4, val.INTERPRETATION_BANDS), "Strong")
        self.assertEqual(val.matrix_band(3, val.SOUND_BANDS), "Good")

    def test_band_names_are_not_the_reference_flag(self):
        tpl = _tpl()
        self.assertIn('const MATRIX_SOUND_BANDS=["Limited","Good","Excellent"]', tpl)
        self.assertIn(
            'const MATRIX_INTERP_BANDS=["With reservations","Strong","Outstanding"]',
            tpl,
        )
        self.assertNotIn("Hard listen", tpl)
        self.assertNotIn("Landmark", tpl)
        self.assertNotIn('"Reference"', tpl)
        self.assertEqual(tpl.count(BAND_LINE), 1)
        strip = _fn(tpl, "matrixStrip(m)", "howScored(m)")
        how = _fn(tpl, "howScored(m)", "signed(r)")
        self.assertNotIn("Référence", strip)
        self.assertNotIn("Référence", how)
        self.assertNotIn(BAND_LINE, strip)
        for index in (0, 1, 2):
            self.assertIn(f"MATRIX_SOUND_BANDS[{index}]", strip)
            self.assertIn(f"MATRIX_INTERP_BANDS[{index}]", strip)
        self.assertIn("m.interpretation", how)
        self.assertIn("m.sound", how)
        self.assertIn('<p class="band-key">${MATRIX_BAND_LINE}</p>', how)
        self.assertNotIn("<sup", how)
        self.assertNotIn("†", how)
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
        self.assertIn('if(!matrixReady(m)) return ""', strip)
        self.assertNotIn('class="grid"', _fn(html, "notYetScored()", "matrixStrip(m)"))
        unscored = _fn(html, "notYetScored()", "matrixStrip(m)")
        self.assertIn("Not yet scored", unscored)
        self.assertNotIn("not yet scored", unscored)
        self.assertNotIn("stylebox", unscored)
        how = _fn(html, "howScored(m)", "signed(r)")
        self.assertIn("if(!m) return \"\"", how)
        signed = _fn(html, "signed(r)", "factStrip(r)")
        self.assertIn("notYetScored()", signed)
        self.assertIn("matrixReady(e.matrix)?matrixStrip(e.matrix):notYetScored()", signed)
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

    def test_engine_assessed_without_critic_matrix_stays_unscored(self):
        """Puccini and Shostakovich are assessed by the aggregate. No cell is invented."""
        cat = json.loads((ROOT / "build" / "catalogue.json").read_text(encoding="utf-8"))
        tosca = next(w for w in cat["works"] if w["id"] == "puccini_tosca")
        shos = next(w for w in cat["works"] if w["id"] == "shostakovich/sym5")
        self.assertEqual(len(tosca["recordings"]), 2)
        self.assertEqual(len(shos["recordings"]), 3)
        for rec in tosca["recordings"] + shos["recordings"]:
            self.assertTrue(rec.get("editorial") in (None, {}))
            self.assertNotIn("matrix", rec.get("editorial") or {})
        empty = json.loads(
            (ROOT / "data" / "editorial" / "shostakovich_sym5.json").read_text(encoding="utf-8")
        )
        self.assertEqual(empty.get("entries"), [])


def _signed_editorial(rec: dict) -> dict | None:
    """Same gate as signedEntry() in the page: author, date, revision."""
    editorial = rec.get("editorial")
    if not isinstance(editorial, dict):
        return None
    if not (editorial.get("author") and editorial.get("date") and editorial.get("revision")):
        return None
    return editorial


def _star_marks(n: int) -> str:
    marks = "".join(
        f'<span class="{"on" if i < n else "off"}">★</span>' for i in range(3)
    )
    return f'<span class="stars" aria-label="{n} of 3 stars">{marks}</span>'


def _standing_html(editorial: dict | None) -> str:
    """Same rule as standingMarks(): signed stars, plus the mark when signed Référence."""
    if editorial is None:
        return '<span class="plain">No signed entry</span>'
    n = editorial.get("stars")
    stars = _star_marks(n) if isinstance(n, int) and not isinstance(n, bool) else ""
    mark = '<span class="badge">Référence</span>' if editorial.get("reference") else ""
    return f"{stars}{mark}"


def _rendered_card(rec: dict) -> str:
    """Card face the work page draws. Standing reads the signed entry, not the aggregate."""
    editorial = _signed_editorial(rec)
    parts: list[str] = [
        f'<div class="standing"><span class="k">Standing</span>{_standing_html(editorial)}</div>'
    ]
    if rec.get("card") != "identity" and editorial is None:
        parts.append(
            '<div class="unsigned">No signed entry yet.</div>'
            '<p class="matrix-unscored">Not yet scored</p>'
        )
    if editorial is not None:
        badge = '<span class="badge">Référence</span>' if editorial.get("reference") else ""
        parts.append(f'<div class="signed">{badge}</div>')
        matrix = editorial.get("matrix") if isinstance(editorial.get("matrix"), dict) else None
        ready = bool(
            matrix
            and isinstance(matrix.get("interpretation"), int)
            and isinstance(matrix.get("sound"), int)
            and 1 <= matrix["interpretation"] <= 5
            and 1 <= matrix["sound"] <= 5
        )
        if not ready:
            parts.append('<p class="matrix-unscored">Not yet scored</p>')
    return "".join(parts)


class TestReferenceBadgeIsSignedOnly(unittest.TestCase):
    def test_template_and_gallery_hide_the_aggregate_badge(self):
        tpl = _tpl()
        start = tpl.index("function signedEntry(r)")
        scorebox = tpl[start:tpl.index("function credits(c)", start)]
        self.assertIn("function signedEntry(r)", scorebox)
        self.assertIn("!signedEntry(r)", scorebox)
        self.assertIn('<span class="plain">No signed entry</span>', scorebox)
        self.assertLess(
            scorebox.index("!signedEntry(r)"),
            scorebox.index('<span class="badge">Référence</span>'),
        )
        signed = _fn(tpl, "signed(r)", "factStrip(r)")
        self.assertIn("if(!e)", signed)
        self.assertLess(signed.index("if(!e)"), signed.index("Référence"))
        gallery = (ROOT / "site/build_gallery.py").read_text(encoding="utf-8")
        self.assertIn("function signedEntry(r)", gallery)
        self.assertIn("r.reference && signedEntry(r)", gallery)
        self.assertIn("!signedEntry(r)", gallery)
        self.assertIn('<span class="plain">No signed entry</span>', gallery)
        self.assertNotIn("r.reference?'<span class=\"ref\">", gallery)
        self.assertNotIn("const stand = r.reference\n", gallery)
        hubs = (ROOT / "site/build_site.py").read_text(encoding="utf-8")
        self.assertNotIn("Référence", hubs)

    def test_unsigned_cards_hide_reference_and_signed_cards_keep_it(self):
        seed = _seed()
        raw = json.loads((ROOT / "build/catalogue.json").read_text(encoding="utf-8"))
        works = ident.merge_identity_works(raw, seed)["works"]
        recordings = [rec for work in works for rec in work.get("recordings") or []]
        self.assertEqual(len(recordings), 28)
        unsigned = []
        signed_reference = []
        for rec in recordings:
            card = _rendered_card(rec)
            editorial = _signed_editorial(rec)
            if editorial is None:
                unsigned.append(rec["id"])
                self.assertIn("No signed entry", card, rec["id"])
                self.assertNotIn("Référence", card, rec["id"])
                self.assertNotIn("not a référence", card, rec["id"])
                self.assertNotIn(">RÉF<", card, rec["id"])
            elif editorial.get("reference"):
                signed_reference.append(rec["id"])
                self.assertIn("Référence", card, rec["id"])
                self.assertIn(
                    f'aria-label="{editorial["stars"]} of 3 stars"',
                    card,
                    rec["id"],
                )
                self.assertNotIn("not a référence", card, rec["id"])
            else:
                self.assertNotIn("Référence", card, rec["id"])
                self.assertNotIn("No signed entry", card, rec["id"])
                self.assertNotIn("not a référence", card, rec["id"])
                self.assertIn(
                    f'aria-label="{editorial["stars"]} of 3 stars"',
                    card,
                    rec["id"],
                )
        self.assertIn("puccini_tosca_desabata", unsigned)
        self.assertGreaterEqual(len(signed_reference), 1)
        callas = next(r for r in recordings if r["id"] == "puccini_tosca_desabata")
        self.assertTrue(callas["reference"])
        self.assertIsNone(callas.get("editorial"))
        callas_card = _rendered_card(callas)
        self.assertIn("Not yet scored", callas_card)
        self.assertNotIn("Référence", callas_card)
        self.assertNotIn("not a référence", callas_card)
        pinnock = next(r for r in recordings if r["id"] == "bach/brandenburg/0")
        self.assertTrue(_signed_editorial(pinnock)["reference"])
        self.assertIn("Référence", _rendered_card(pinnock))
        for rid in (
            "puccini_tosca_desabata",
            "puccini_tosca_karajan",
            "shostakovich_sym5_mravinsky",
            "shostakovich_sym5_nelsons",
            "shostakovich_sym5_noseda",
        ):
            self.assertIn(rid, unsigned)

    def test_gallery_standing_says_no_signed_entry(self):
        """Gallery rows are the engine catalogue. None of them carry a signed entry."""
        raw = json.loads((ROOT / "build/catalogue.json").read_text(encoding="utf-8"))
        recordings = [rec for work in raw["works"] for rec in work.get("recordings") or []]
        self.assertGreaterEqual(len(recordings), 1)
        gallery = (ROOT / "site/build_gallery.py").read_text(encoding="utf-8")
        start = gallery.index("function standingMarks")
        stand = gallery[start:gallery.index("/* rail */", start)]
        self.assertIn("No signed entry", stand)
        self.assertIn("e.reference", stand)
        self.assertIn("e.stars", stand)
        self.assertNotIn("not a référence", stand)
        self.assertNotIn("not a référence", gallery)
        for rec in recordings:
            self.assertIsNone(_signed_editorial(rec), rec["id"])
            card = _rendered_card(rec)
            self.assertIn("No signed entry", card, rec["id"])
            self.assertNotIn("not a référence", card, rec["id"])
            self.assertNotIn("Référence", card, rec["id"])


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
