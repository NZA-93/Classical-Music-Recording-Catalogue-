"""Tests for the aggregation engine and the contribution validator.

The regression cases in TestRegression are the project's memory. They fix the
four published scores against accidental drift. If a refactor changes them, the
refactor is wrong — do not update the expected values to match new output.
"""

import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load(name: str, relpath: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


eng = _load("engine_v2", "engine/aggregation_engine_v2.py")
val = _load("validator", "agents/validate.py")
har = _load("harvest", "agents/harvest.py")


class TestWeighting(unittest.TestCase):
    def stmt(self, **kw):
        base = dict(source="x", cls=eng.Cls.CRITIC, axis="interpretation",
                    score=2.5, text="t")
        base.update(kw)
        return eng.Statement(**base)

    def test_provenance_scales_weight(self):
        self.assertAlmostEqual(self.stmt(prov=eng.Prov.CITED).weight(), 0.90, places=3)
        self.assertAlmostEqual(self.stmt(prov=eng.Prov.ATTRIBUTED).weight(), 0.63, places=3)
        self.assertAlmostEqual(self.stmt(prov=eng.Prov.DRAFT).weight(), 0.315, places=3)

    def test_conflict_penalises_independent_looking_sources(self):
        clean = self.stmt(prov=eng.Prov.CITED).weight()
        dirty = self.stmt(prov=eng.Prov.CITED, conflict=True).weight()
        self.assertLess(dirty, clean)
        self.assertGreaterEqual(dirty, 0.10)

    def test_promo_is_already_discounted_not_double_penalised(self):
        promo = self.stmt(cls=eng.Cls.PROMO, prov=eng.Prov.ATTRIBUTED, conflict=True)
        self.assertAlmostEqual(promo.weight(), 0.25 * 0.70, places=3)

    def test_draft_is_never_strong(self):
        self.assertFalse(self.stmt(prov=eng.Prov.DRAFT).is_strong())
        self.assertTrue(self.stmt(prov=eng.Prov.ATTRIBUTED).is_strong())
        self.assertFalse(self.stmt(prov=eng.Prov.CITED, conflict=True).is_strong())


class TestScoring(unittest.TestCase):
    def test_star_thresholds(self):
        self.assertEqual(eng.stars(2.60), 3)
        self.assertEqual(eng.stars(2.59), 2)
        self.assertEqual(eng.stars(1.70), 2)
        self.assertEqual(eng.stars(1.69), 1)
        self.assertEqual(eng.stars(0.79), 0)

    def test_edition_verdicts(self):
        self.assertEqual(eng.edition_verdict(2.50, 1), "preferred transfer")
        self.assertEqual(eng.edition_verdict(2.10, 1), "sound and serviceable")
        self.assertEqual(eng.edition_verdict(1.20, 1), "pass if you can")
        self.assertEqual(eng.edition_verdict(2.90, 0), "not yet assessed")

    def test_reference_needs_three_strong_benchmark_signals(self):
        def s(text, prov=eng.Prov.ATTRIBUTED):
            return eng.Statement("src", eng.Cls.CRITIC, "interpretation", 2.95, text, prov)
        two = [s("a benchmark"), s("the reference"), s("very fine indeed")]
        self.assertFalse(eng.is_reference(2.95, 0.75, two))
        three = two + [s("a landmark")]
        self.assertTrue(eng.is_reference(2.95, 0.75, three))

    def test_sound_axis_cannot_buy_a_reference(self):
        sound = [eng.Statement("s", eng.Cls.ENGINEER, "sound", 3.0,
                               "a benchmark transfer, definitive and unsurpassed",
                               eng.Prov.CITED) for _ in range(4)]
        self.assertFalse(eng.is_reference(3.0, 1.0, sound))

    def test_low_confidence_blocks_reference(self):
        strong = [eng.Statement("s", eng.Cls.CRITIC, "interpretation", 2.9,
                                "the benchmark", eng.Prov.CITED) for _ in range(3)]
        self.assertFalse(eng.is_reference(2.9, 0.30, strong))


class TestRegression(unittest.TestCase):
    """The four published scores. See AGENTS.md §7."""

    EXPECTED = {
        "bach_brandenburg_pinnock":     (2.853, 0.745, 3, False),
        "bach_brandenburg_harnoncourt": (2.814, 0.747, 3, False),
        "puccini_tosca_desabata":       (2.955, 0.749, 3, True),
        "puccini_tosca_karajan":        (2.848, 0.498, 3, False),
    }

    def test_published_scores_are_stable(self):
        got = {r["id"]: r for r in (eng.run(rec) for rec in eng.catalogue())}
        self.assertEqual(set(got), set(self.EXPECTED))

        for rid, (S, conf, stars, ref) in self.EXPECTED.items():
            with self.subTest(rid):
                self.assertAlmostEqual(got[rid]["interpretation"], S, places=3)
                self.assertAlmostEqual(got[rid]["confidence"], conf, places=3)
                self.assertEqual(got[rid]["stars"], stars)
                self.assertEqual(got[rid]["reference"], ref)

    def test_data_loader_does_not_disturb_hardcoded_scores(self):
        """S2-01 guard: the JSON path existing must not move a published score."""
        hard = {r["id"]: r["interpretation"] for r in (eng.run(x) for x in eng.catalogue())}
        for rid, (S, *_ ) in self.EXPECTED.items():
            self.assertAlmostEqual(hard[rid], S, places=3)

    def test_unassessed_recordings_are_null_not_zero(self):
        loaded = {r["id"]: r for r in (eng.run(x) for x in eng.load_from_data())}
        mrav = loaded["shostakovich_sym5_mravinsky"]
        self.assertIsNone(mrav["interpretation"])
        self.assertIsNone(mrav["stars"])
        self.assertEqual(mrav["status"], "awaiting sources")
        self.assertFalse(mrav["reference"])

    def test_a_single_award_cannot_earn_reference(self):
        nel = {r["id"]: r for r in (eng.run(x) for x in eng.load_from_data())}["shostakovich_sym5_nelsons"]
        self.assertAlmostEqual(nel["interpretation"], 2.90, places=2)
        self.assertFalse(nel["reference"], "one award is not three independent benchmark signals")

    def test_album_award_is_one_shared_benchmark_signal(self):
        """ADR-001: three copies of a three-work Grammy still count as one signal."""
        covers = ("shostakovich/sym5", "shostakovich/sym8", "shostakovich/sym9")
        stmts = [
            eng.Statement(
                source="Grammy — Best Orchestral Performance, 59th",
                cls=eng.Cls.AWARD, axis="interpretation", score=2.90,
                text="Album award for Symphonies 5, 8 and 9.",
                prov=eng.Prov.CITED, covers_works=covers,
            )
            for _ in range(3)
        ]
        # High S and conf so only the signal count decides.
        self.assertFalse(eng.is_reference(2.90, 0.80, stmts))
        # Three independent single-work awards would clear the bar.
        independent = [
            eng.Statement(
                source=f"Award {i}", cls=eng.Cls.AWARD, axis="interpretation",
                score=2.90, text="single-work award", prov=eng.Prov.CITED,
                covers_works=(f"work/{i}",),
            )
            for i in range(3)
        ]
        self.assertTrue(eng.is_reference(2.90, 0.80, independent))

    def test_every_sound_statement_is_attached_to_an_edition(self):
        for rec in eng.catalogue():
            for s in rec.statements:
                if s.axis == "sound":
                    with self.subTest(rec.id):
                        self.assertIsNotNone(s.edition,
                            "sound belongs to an edition, not a recording")


class TestNormalisation(unittest.TestCase):
    def test_scales(self):
        self.assertEqual(har.normalise("stars_5", 5), 3.0)
        self.assertEqual(har.normalise("stars_5", 4), 2.4)
        self.assertEqual(har.normalise("ten_point", 10), 3.0)
        self.assertEqual(har.normalise("percent", 50), 1.5)
        self.assertEqual(har.normalise("award", None), 2.90)

    def test_unknown_and_unparseable_return_none(self):
        self.assertIsNone(har.normalise("vibes", 3))
        self.assertIsNone(har.normalise("stars_5", "excellent"))


class TestValidator(unittest.TestCase):
    def test_real_barcodes_pass(self):
        self.assertTrue(val.check_digit_ok("090317761121"))   # Teldec 1992
        self.assertTrue(val.check_digit_ok("028941050021"))   # Archiv CD

    def test_transcription_errors_fail(self):
        self.assertFalse(val.check_digit_ok("090317761122"))
        self.assertFalse(val.check_digit_ok("09031776112"))
        self.assertFalse(val.check_digit_ok("09031776112X"))

    def test_tier_is_earned_not_declared(self):
        self.assertEqual(val.earned_tier({"locator": "u", "source": "s"}), "cited")
        self.assertEqual(val.earned_tier({"source": "s"}), "attributed")
        self.assertEqual(val.earned_tier({}), "draft")

    def _check(self, contrib):
        return val.validate(contrib, pathlib.Path("t.json"),
                            {"puccini/tosca/0"}, {"tosca53_warner_2014"})

    def test_sound_without_edition_is_rejected(self):
        errs, _ = self._check({"recording": "puccini/tosca/0", "axis": "sound",
                               "source": "s", "characterisation": "x", "scale": "stars_5",
                               "value": 4, "conflict": False})
        self.assertTrue(any("edition" in e for e in errs))

    def test_overclaimed_provenance_is_rejected(self):
        errs, _ = self._check({"recording": "puccini/tosca/0", "axis": "interpretation",
                               "source": "s", "provenance": "cited", "scale": "stars_5",
                               "value": 4, "characterisation": "x", "conflict": False})
        self.assertTrue(any("locator" in e for e in errs))

    def test_quoted_review_text_is_rejected(self):
        errs, _ = self._check({"recording": "puccini/tosca/0", "axis": "interpretation",
                               "source": "s", "scale": "stars_5", "value": 4,
                               "conflict": False,
                               "characterisation": 'He called it "the finest of all the many '
                                                   'recordings that this opera has ever received".'})
        self.assertTrue(any("quoted" in e for e in errs))

    def test_prose_scale_carries_no_number(self):
        errs, _ = self._check({"recording": "puccini/tosca/0", "axis": "interpretation",
                               "source": "s", "scale": "prose", "value": 2.5,
                               "characterisation": "x", "conflict": False})
        self.assertTrue(any("prose" in e for e in errs))

    def test_a_good_contribution_passes(self):
        errs, _ = self._check({"recording": "puccini/tosca/0", "axis": "interpretation",
                               "source": "Gramophone", "locator": "issue 1247, p. 84",
                               "provenance": "cited", "scale": "stars_5", "value": 5,
                               "characterisation": "Treated as the benchmark account.",
                               "conflict": False})
        self.assertEqual(errs, [])


class TestEditorialQuotation(unittest.TestCase):
    """ADR-003. Quotation is bounded where it is allowed at all."""

    RECS = {"r1"}

    def entry(self, **kw):
        base = {"recording": "r1", "author": {"id": "NZA"}, "date": "2026-07-26",
                "revision": 1, "text": "An entry."}
        base.update(kw)
        return val.validate_editorial(base, pathlib.Path("e.json"), self.RECS)

    def test_unsigned_entry_does_not_publish(self):
        errs, _ = val.validate_editorial(
            {"recording": "r1", "author": {"id": "NZA"}, "text": "x"},
            pathlib.Path("e.json"), self.RECS)
        self.assertTrue(any("date" in e for e in errs))
        self.assertTrue(any("revision" in e for e in errs))

    def test_word_limit(self):
        long_quote = " ".join(["word"] * 26)
        errs, _ = self.entry(quotes=[{"text": long_quote, "quoted_author": "A",
                                      "publication": "Diapason", "locator": "p. 1"}])
        self.assertTrue(any("26 words" in e for e in errs))

    def test_brevity_is_relative_to_the_source(self):
        """25 words of a 5000-word feature is a fragment. Of a 100-word notice
        it is a quarter of the work."""
        q = {"text": " ".join(["word"] * 25), "quoted_author": "A",
             "publication": "Diapason", "locator": "p. 1"}
        ok, _ = self.entry(quotes=[dict(q, source_length_words=5000)])
        self.assertEqual(ok, [])
        bad, _ = self.entry(quotes=[dict(q, source_length_words=100)])
        self.assertTrue(any("of a 100-word notice" in e for e in bad))

    def test_attribution_is_mandatory(self):
        errs, _ = self.entry(quotes=[{"text": "fine", "publication": "Diapason"}])
        self.assertTrue(any("quoted_author" in e for e in errs))
        self.assertTrue(any("locator" in e for e in errs))

    def test_quote_count_capped(self):
        q = {"text": "fine", "quoted_author": "A", "publication": "D",
             "locator": "p", "source_length_words": 200}
        errs, _ = self.entry(quotes=[q, q, q])
        self.assertTrue(any("limit is 2" in e for e in errs))

    def test_a_proper_quotation_passes(self):
        errs, _ = self.entry(quotes=[{
            "text": "sweeps aside every rival in the modern catalogue",
            "quoted_author": "A. Critic", "publication": "Diapason no. 700",
            "locator": "p. 84", "source_length_words": 140}])
        self.assertEqual(errs, [])


class TestComposerRollup(unittest.TestCase):
    """Composer scores are origin-weighted rollups, never a new judgement layer."""

    def stmt(self, **kw):
        base = dict(source="Gramophone", cls=eng.Cls.CRITIC, axis="interpretation",
                    score=2.8, text="benchmark reading", prov=eng.Prov.CITED)
        base.update(kw)
        return eng.Statement(**base)

    def rec(self, rid, stmts):
        return eng.Recording(
            id=rid, work_id="bach/brandenburg",
            soloists="", director="D", ensemble="E", published="1980",
            venue="", sessions="",
            producer=None, engineer=None, credits_status="unknown",
            anchors=[], reception=[], editions=[],
            statements=stmts,
        )

    def test_withholds_until_evidence_floor(self):
        out = eng.aggregate_composer(
            [self.rec("a", [self.stmt()])],
            composer="Bach", composer_id="bach",
        )
        self.assertIsNone(out["interpretation"])
        self.assertEqual(out["n_strong"], 1)

    def test_origin_weights_prefer_cited_critic_over_draft_promo(self):
        critic = self.stmt(source="Diapason", cls=eng.Cls.CRITIC, score=3.0,
                           prov=eng.Prov.CITED)
        promo = self.stmt(source="Label", cls=eng.Cls.PROMO, score=1.0,
                          prov=eng.Prov.DRAFT, conflict=True)
        survey = self.stmt(source="Penguin", cls=eng.Cls.SURVEY, score=2.7,
                           prov=eng.Prov.CITED)
        out = eng.aggregate_composer(
            [
                self.rec("r1", [critic, promo]),
                self.rec("r2", [survey, self.stmt(source="Award", cls=eng.Cls.AWARD,
                                                   score=2.9)]),
            ],
            composer="Bach", composer_id="bach",
        )
        self.assertIsNotNone(out["interpretation"])
        # Promo must not drag a cited-critic/award consensus down to the floor.
        self.assertGreater(out["interpretation"], 2.5)
        self.assertIn("independent critic", out["sources_by_class"])
        self.assertIn("cited", out["sources_by_provenance"])

    def test_regression_recordings_unchanged_when_rollup_added(self):
        """Adding composers[] must not move the four published recording scores."""
        results = {r["id"]: r for r in (eng.run(x) for x in eng.catalogue())}
        self.assertAlmostEqual(results["bach_brandenburg_pinnock"]["interpretation"], 2.853, places=3)
        self.assertAlmostEqual(results["bach_brandenburg_harnoncourt"]["interpretation"], 2.814, places=3)
        self.assertAlmostEqual(results["puccini_tosca_desabata"]["interpretation"], 2.955, places=3)
        self.assertAlmostEqual(results["puccini_tosca_karajan"]["interpretation"], 2.848, places=3)


class TestSeedIntegrity(unittest.TestCase):
    def setUp(self):
        self.seed = json.loads((ROOT / "data/seed.json").read_text("utf-8"))

    def test_shape(self):
        self.assertEqual(len(self.seed["composers"]), 10)
        self.assertEqual(self.seed["totals"]["works"], 119)
        for c in self.seed["composers"]:
            self.assertGreaterEqual(c["works"], 10)
            self.assertLessEqual(c["works"], 12)

    def test_no_assessment_leaked_into_the_seed(self):
        """The seed holds facts. A score here would be a fabrication by default."""
        banned = ("score", "stars", "rating", "reference", "verdict", "assessment")
        blob = json.dumps(self.seed).lower()
        for word in banned:
            with self.subTest(word):
                self.assertNotIn(f'"{word}"', blob)

    def test_candidates_start_unverified(self):
        for w in self.seed["works"]:
            for c in w["candidates"]:
                self.assertFalse(c["verified"])
                self.assertIsNone(c["mbid"])


class TestDataSourceTextGuard(unittest.TestCase):
    """S1-05: planting pasted prose in data/ must fail validation."""

    def test_clean_tree_passes(self):
        self.assertEqual(val.scan_data_tree(ROOT / "data"), [])

    def test_long_characterisation_fails(self):
        import tempfile
        paste = "word " * 80  # well over 240 characters
        doc = [{"recording": "x", "characterisation": paste, "axis": "interpretation"}]
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "planted.json"
            p.write_text(json.dumps(doc), encoding="utf-8")
            # scan_data_file on the planted file
            errs = val.scan_data_file(p)
        self.assertTrue(any("characterisation" in e and "characters" in e for e in errs))

    def test_quoted_run_in_characterisation_fails(self):
        text = 'He wrote "the finest of all the many recordings made in that decade ever"'
        doc = [{"characterisation": text}]
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "quoted.json"
            p.write_text(json.dumps(doc), encoding="utf-8")
            errs = val.scan_data_file(p)
        self.assertTrue(any("quoted" in e.lower() for e in errs))


if __name__ == "__main__":
    unittest.main(verbosity=2)
