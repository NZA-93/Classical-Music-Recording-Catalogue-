"""ADR-004 scout candidate pool: ordinal ranks, never crowns.

Scout is a ranked shortlist for a Critic cut. It must not publish stars,
Référence, matrix or Dictionnaire text, must not feed the aggregate, and
must not auto-promote into seed.assessed. Pilot: Bach Brandenburg only.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
PILOT = ROOT / "data" / "scout" / "bach_brandenburg.json"


def _load(name: str, relpath: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


val = _load("validator_scout", "agents/validate.py")
ident = _load("identity_scout", "site/identity.py")
scout = _load("scout_pool", "site/scout.py")
rnd = _load("render_scout", "site/render.py")
disc = _load("disc_scout", "site/disc.py")


def _seed() -> dict:
    return json.loads((ROOT / "data/seed.json").read_text(encoding="utf-8"))


def _tpl() -> str:
    return (ROOT / "site/template.html").read_text(encoding="utf-8")


def _pilot() -> dict:
    return json.loads(PILOT.read_text(encoding="utf-8"))


def _recs() -> set[str]:
    recs = set()
    for work in _seed().get("works") or []:
        for cand in work.get("candidates") or []:
            if cand.get("id"):
                recs.add(cand["id"])
    return recs


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


PILOT_IDS = (
    "bach/brandenburg/0",
    "bach/brandenburg/1",
    "bach/brandenburg/4",
    "bach/brandenburg/3",
    "bach/brandenburg/2",
    "bach/brandenburg/5",
)


class TestScoutPilotFile(unittest.TestCase):
    def test_pilot_is_the_six_critic_rows(self):
        doc = _pilot()
        self.assertEqual(doc["work_id"], "bach/brandenburg")
        rows = doc["candidates"]
        self.assertEqual([c["recording"] for c in rows], list(PILOT_IDS))
        self.assertEqual([c["rank"] for c in rows], [1, 2, 3, 4, 5, 6])
        self.assertEqual(
            [c["status"] for c in rows],
            ["promoted-to-cut", "promoted-to-cut", "promoted-to-cut",
             "held", "held", "held"],
        )
        self.assertEqual(
            rows[0]["why_in"],
            "Widely cited digital period-instrument classic; clear neighbour to pioneering OI and modern Munich.",
        )
        self.assertIsNone(rows[0]["why_out"])
        self.assertIsNone(rows[3]["why_in"])
        self.assertEqual(
            rows[5]["why_out"],
            "Thin/wrong seed metadata; ranking a false Archiv ID would crown a ghost. Fix identity first.",
        )
        blob = json.dumps(doc)
        self.assertNotIn('"stars"', blob)
        self.assertNotIn('"reference"', blob)
        self.assertNotIn('"matrix"', blob)
        self.assertNotIn('"text"', blob)

    def test_pilot_passes_validate(self):
        errs = val.validate_scout_doc(_pilot(), PILOT, _recs(), _seed())
        self.assertEqual(errs, [])


class TestScoutCannotPublishCrowns(unittest.TestCase):
    def _check(self, mutate) -> list[str]:
        doc = mutate(copy.deepcopy(_pilot()))
        return val.validate_scout_doc(doc, PILOT, _recs(), _seed())

    def test_rejects_stars_on_a_row(self):
        def add(doc):
            doc["candidates"][0]["stars"] = 3
            return doc
        errs = self._check(add)
        self.assertTrue(any("stars" in e for e in errs), errs)

    def test_rejects_reference_matrix_and_text(self):
        for key, value in (
            ("reference", True),
            ("matrix", {"interpretation": 5, "sound": 4}),
            ("text", "Unsigned Dictionnaire prose."),
        ):
            def add(doc, k=key, v=value):
                doc["candidates"][1][k] = v
                return doc
            errs = self._check(add)
            self.assertTrue(any(key in e for e in errs), (key, errs))

    def test_rejects_forbidden_key_on_the_document(self):
        def add(doc):
            doc["stars"] = 3
            return doc
        errs = self._check(add)
        self.assertTrue(any("stars" in e for e in errs), errs)

    def test_rejects_auto_promote_of_a_held_id(self):
        def promo(doc):
            doc["candidates"][4]["status"] = "promoted-to-cut"
            return doc
        errs = self._check(promo)
        self.assertTrue(any("auto-promote" in e for e in errs), errs)

    def test_rejects_demoting_an_assessed_row(self):
        def hold(doc):
            doc["candidates"][0]["status"] = "held"
            return doc
        errs = self._check(hold)
        self.assertTrue(any("promoted-to-cut" in e for e in errs), errs)

    def test_rejects_a_fake_aggregate_rank(self):
        def frac(doc):
            doc["candidates"][0]["rank"] = 2.5
            return doc
        errs = self._check(frac)
        self.assertTrue(any("ordinal" in e for e in errs), errs)

    def test_loader_strips_stars_even_if_present(self):
        row = scout.public_scout_row({
            "recording": "bach/brandenburg/0",
            "rank": 1,
            "stance": "HIP studio digital",
            "status": "promoted-to-cut",
            "identity": "Pinnock",
            "why_in": "in",
            "why_out": None,
            "stars": 3,
            "reference": True,
            "matrix": {"interpretation": 5, "sound": 4},
            "text": "nope",
        })
        self.assertEqual(set(row), set(scout.SCOUT_ROW_KEYS))
        self.assertNotIn("stars", row)
        self.assertNotIn("reference", row)
        self.assertNotIn("matrix", row)
        self.assertNotIn("text", row)


class TestScoutNotInEditorialOrEngine(unittest.TestCase):
    def test_signed_editorial_is_untouched(self):
        signed = ident.load_signed_editorial()
        pinnock = signed["bach/brandenburg/0"]
        self.assertEqual(pinnock["stars"], 3)
        self.assertTrue(pinnock["reference"])
        self.assertEqual(pinnock["matrix"]["interpretation"], 5)
        self.assertNotIn("rank", pinnock)
        self.assertNotIn("stance", pinnock)
        self.assertNotIn("why_in", pinnock)
        ids = [
            ent["recording"]
            for ent in json.loads(
                (ROOT / "data/editorial/bach_brandenburg.json").read_text(encoding="utf-8")
            )["entries"]
        ]
        self.assertEqual(ids, [
            "bach/brandenburg/0",
            "bach/brandenburg/1",
            "bach/brandenburg/4",
        ])

    def test_public_cards_do_not_absorb_scout(self):
        works = ident.public_identity_works(_seed())
        brand = next(w for w in works if w["id"] == "bach/brandenburg")
        self.assertNotIn("scout", brand)
        self.assertEqual(
            [r["id"] for r in brand["recordings"]],
            ["bach/brandenburg/0", "bach/brandenburg/1", "bach/brandenburg/4"],
        )
        blob = json.dumps(brand)
        self.assertNotIn("bach/brandenburg/2", blob)
        self.assertNotIn("Abbado", blob)

    def test_engine_source_does_not_read_scout(self):
        src = (ROOT / "engine/aggregation_engine_v2.py").read_text(encoding="utf-8")
        self.assertNotIn("data/scout", src)
        self.assertNotIn("/scout/", src)

    def test_engine_catalogue_has_no_scout_key(self):
        cat = json.loads((ROOT / "build/catalogue.json").read_text(encoding="utf-8"))
        self.assertNotIn('"scout"', json.dumps(cat))

    def test_assessed_ids_unchanged(self):
        brand = next(w for w in _seed()["works"] if w["id"] == "bach/brandenburg")
        self.assertEqual(
            brand["assessed"],
            ["bach/brandenburg/0", "bach/brandenburg/1", "bach/brandenburg/4"],
        )


class TestScoutWorkPageRender(unittest.TestCase):
    def test_brandenburg_expand_carries_the_six_rows(self):
        merged = ident.merge_identity_works(
            json.loads((ROOT / "build/catalogue.json").read_text(encoding="utf-8")),
            _seed(),
        )
        brand = next(w for w in merged["works"] if w["id"] == "bach/brandenburg")
        html = _html_for(brand, merged)
        cat = _embedded_catalogue(html)
        work = cat["works"][0]
        self.assertEqual([r["id"] for r in work["recordings"]], [
            "bach/brandenburg/0", "bach/brandenburg/1", "bach/brandenburg/4",
        ])
        rows = work["scout"]
        self.assertEqual([c["recording"] for c in rows], list(PILOT_IDS))
        self.assertEqual([c["rank"] for c in rows], [1, 2, 3, 4, 5, 6])
        self.assertEqual(rows[0]["identity"], (
            "Pinnock / English Concert / Archiv 1982 Henry Wood Hall — not Avie 2007"
        ))
        self.assertEqual(rows[4]["identity"], (
            "Abbado / Orchestra Mozart / DG 2007 Reggio Emilia live"
        ))
        for row in rows:
            self.assertNotIn("stars", row)
            self.assertNotIn("reference", row)
            self.assertNotIn("matrix", row)
            self.assertNotIn("text", row)
            self.assertTrue(row.get("why_in") or row.get("why_out"))
        fn = _fn(html, "candidatesConsidered(w)", "workSection(w)")
        self.assertIn("Candidates considered", fn)
        self.assertIn("Why in", fn)
        self.assertIn("Why out", fn)
        self.assertNotIn("stylebox", fn)
        self.assertNotIn("stars", fn)
        self.assertNotIn("★", fn)
        self.assertNotIn("badge", fn)
        self.assertNotIn("Référence", fn)
        self.assertNotIn("matrixStrip", fn)
        work_fn = html[html.index("function workSection(w)"):html.index("function renderWorkDirectory")]
        self.assertIn("candidatesConsidered(w)", work_fn)
        signed = _fn(html, "signed(r)", "factStrip(r)")
        self.assertIn("Référence", signed)
        self.assertIn("★", signed)
        identity = html[html.index("function identityLine(r)"):html.index("function entry(r)")]
        self.assertNotIn("candidatesConsidered", identity)
        self.assertIn("Pinnock’s 1982 English Concert Brandenburgs", html)

    def test_goldberg_has_no_scout_payload(self):
        merged = ident.merge_identity_works(
            json.loads((ROOT / "build/catalogue.json").read_text(encoding="utf-8")),
            _seed(),
        )
        gold = next(w for w in merged["works"] if w["id"] == "bach/goldberg")
        html = _html_for(gold, merged)
        cat = _embedded_catalogue(html)
        self.assertNotIn("scout", cat["works"][0])
        self.assertNotIn("Abbado", html)
        self.assertNotIn("Orchestra Mozart", html)


if __name__ == "__main__":
    unittest.main()
