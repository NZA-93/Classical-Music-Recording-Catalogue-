#!/usr/bin/env python3
"""Tests for agents/identity_board.py — honest omit, derived why-missed only."""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents"))

import identity_board as ib  # noqa: E402


SEED_HARN = {
    "id": "bach/brandenburg/1",
    "work": "Johann Sebastian Bach — Brandenburg Concertos",
    "work_title": "Brandenburg Concertos",
    "catalogue": "BWV 1046–1051",
    "director": "Nikolaus Harnoncourt",
    "ensemble": "Concentus Musicus Wien",
    "soloists": "",
    "label": "Teldec",
    "year": "1964",
}

PROP_HARN = {
    "target": "bach/brandenburg/1",
    "kind": "identity",
    "payload": {
        "mbid": "bfa92d8f-6b21-3b68-b584-9e130b1405b3",
        "mb_title": "Brandenburgische Konzerte",
        "mb_first_release": "1967",
        "confidence": 56,
        "review_flags": ["confidence 56 < 80"],
    },
}


class TestWhyItMissed(unittest.TestCase):
    def test_parses_confidence_flag(self):
        reasons = ib.why_it_missed(SEED_HARN, PROP_HARN)
        codes = {r["code"] for r in reasons}
        self.assertIn("low_confidence", codes)
        self.assertTrue(any("56" in r["detail"] for r in reasons))

    def test_parses_date_off_flag(self):
        prop = {
            "payload": {
                "mb_title": "Brandenburg Concertos",
                "mb_first_release": "1985",
                "review_flags": ["date off by 21 years (1964 vs 1985)"],
            }
        }
        reasons = ib.why_it_missed(SEED_HARN, prop)
        self.assertEqual(reasons[0]["code"], "date_mismatch")
        self.assertIn("date off by 21", reasons[0]["detail"])

    def test_parses_compilation_flag(self):
        prop = {
            "payload": {
                "mb_title": "Messiah (Highlights)",
                "mb_first_release": "1990",
                "review_flags": ["compilation-like title: 'Messiah (Highlights)'"],
            }
        }
        seed = {**SEED_HARN, "work_title": "Messiah", "year": "1990"}
        reasons = ib.why_it_missed(seed, prop)
        self.assertIn("compilation_or_box", {r["code"] for r in reasons})

    def test_never_invents_when_no_mismatch(self):
        prop = {
            "payload": {
                "mb_title": "Brandenburg Concertos",
                "mb_first_release": "1964",
                "review_flags": [],
            }
        }
        reasons = ib.why_it_missed(SEED_HARN, prop)
        self.assertEqual(len(reasons), 1)
        self.assertEqual(reasons[0]["code"], "needs_human_review_bucket")


class TestFieldPresence(unittest.TestCase):
    def test_inventory_lists_critic_fields_as_payload_when_present(self):
        by_field = {r["field"]: r for r in ib.FIELD_INVENTORY}
        self.assertEqual(by_field["fassung"]["status"], "present")
        self.assertEqual(by_field["completeness"]["status"], "present")
        self.assertEqual(by_field["session_year"]["status"], "present")
        self.assertEqual(by_field["live_studio"]["status"], "present")
        self.assertEqual(by_field["why_it_missed"]["status"], "derived")
        self.assertIn("work_id", by_field["remake_siblings"]["source"])

    def test_enrichment_does_not_synthesize_absents(self):
        enrich = ib.enrichment_for_row(SEED_HARN, PROP_HARN, [SEED_HARN])
        fp = enrich["field_presence"]
        self.assertIsNone(fp["fassung"])
        self.assertIsNone(fp["completeness"])
        self.assertIsNone(fp["session_year"])
        self.assertIsNone(fp["live_studio"])
        self.assertIsNone(fp["release_mbid"])
        self.assertEqual(fp["seed_year"], "1964")
        self.assertEqual(fp["mb_first_release"], "1967")

    def test_criteria_omit_absent_fassung_boilerplate(self):
        checks = {c["criterion"]: c for c in ib.criterion_status(SEED_HARN, PROP_HARN)}
        self.assertNotIn("same_fassung", checks)
        self.assertNotIn("same_completeness", checks)
        self.assertNotIn("live_vs_studio", checks)
        self.assertNotIn("session_year_field", checks)

    def test_populated_fields_come_from_payload_tokens(self):
        seed = {**SEED_HARN, "work_title": "Don Giovanni"}
        prop = {
            "payload": {
                "mb_title": "Don Giovanni (Prague version)",
                "mb_disambiguation": "1955 recording",
                "mb_secondary_types": ["Live"],
                "mb_first_release": "1956",
            }
        }
        fp = ib.enrichment_for_row(seed, prop, [seed])["field_presence"]
        self.assertRegex(fp["fassung"] or "", r"Prague")
        self.assertEqual(fp["session_year"], "1955")
        self.assertIn("live", (fp["live_studio"] or "").lower())
        self.assertNotEqual(fp["session_year"], "1956")

    def test_highlights_completeness_from_title(self):
        prop = {"payload": {"mb_title": "Messiah (Highlights)", "mb_first_release": "1990"}}
        fp = ib.enrichment_for_row(SEED_HARN, prop, [SEED_HARN])["field_presence"]
        self.assertEqual(fp["completeness"], "highlights")

    def test_omitted_when_ws2_has_no_token(self):
        prop = {"payload": {"mb_title": "Brandenburg Concertos", "mb_first_release": "1982"}}
        fp = ib.enrichment_for_row(SEED_HARN, prop, [SEED_HARN])["field_presence"]
        self.assertIsNone(fp["fassung"])
        self.assertIsNone(fp["completeness"])
        self.assertIsNone(fp["session_year"])
        self.assertIsNone(fp["live_studio"])

    def test_language_variant_is_not_work_conflict(self):
        seed = {
            **SEED_HARN,
            "work_title": "Symphony No. 7",
            "composer": "Ludwig van Beethoven",
            "year": "1976",
        }
        prop = {
            "payload": {
                "mb_title": "Symphonie Nr. 7",
                "mb_first_release": "1976",
                "review_flags": [],
            }
        }
        codes = {r["code"] for r in ib.why_it_missed(seed, prop)}
        self.assertNotIn("title_string_differs", codes)
        checks = {c["criterion"]: c for c in ib.criterion_status(seed, prop)}
        self.assertEqual(checks["same_work"]["status"], "pass")


class TestRemakeSiblings(unittest.TestCase):
    def test_finds_same_forces_different_year(self):
        others = [
            {**SEED_HARN, "work_id": "bach/brandenburg"},
            {
                "id": "bach/brandenburg/9",
                "work_id": "bach/brandenburg",
                "work_title": "Brandenburg Concertos",
                "composer": "Johann Sebastian Bach",
                "director": "Nikolaus Harnoncourt",
                "ensemble": "Concentus Musicus Wien",
                "year": "1987",
                "label": "Teldec",
            },
            {
                "id": "bach/brandenburg/8",
                "work_id": "bach/brandenburg",
                "work_title": "Brandenburg Concertos",
                "director": "Trevor Pinnock",
                "ensemble": "The English Concert",
                "year": "1982",
                "label": "Archiv",
            },
        ]
        sibs = ib.remake_siblings(
            {**SEED_HARN, "work_id": "bach/brandenburg"},
            others, exclude_id="bach/brandenburg/1",
        )
        self.assertEqual(len(sibs), 1)
        self.assertEqual(sibs[0]["id"], "bach/brandenburg/9")

    def test_does_not_cross_composers_on_fifth(self):
        beethoven = {
            "id": "beethoven/sym5/0",
            "work_id": "beethoven/sym5",
            "work_title": "Symphony No. 5",
            "composer": "Ludwig van Beethoven",
            "catalogue": "Op. 67",
            "director": "Herbert von Karajan",
            "ensemble": "Berliner Philharmoniker",
            "year": "1962",
            "label": "DG",
        }
        tchaikovsky = {
            "id": "tchaikovsky/sym5/0",
            "work_id": "tchaikovsky/sym5",
            "work_title": "Symphony No. 5",
            "composer": "Pyotr Ilyich Tchaikovsky",
            "catalogue": "Op. 64",
            "director": "Herbert von Karajan",
            "ensemble": "Berliner Philharmoniker",
            "year": "1975",
            "label": "DG",
        }
        mahler = {
            "id": "mahler/sym5/0",
            "work_id": "mahler/sym5",
            "work_title": "Symphony No. 5",
            "composer": "Gustav Mahler",
            "director": "Herbert von Karajan",
            "ensemble": "Berliner Philharmoniker",
            "year": "1973",
            "label": "DG",
        }
        sibs = ib.remake_siblings(beethoven, [beethoven, tchaikovsky, mahler],
                                  exclude_id="beethoven/sym5/0")
        self.assertEqual(sibs, [])


class TestGapsMarkdown(unittest.TestCase):
    def test_writes_payload_gaps(self):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "PAYLOAD_GAPS.md"
            ib.write_payload_gaps_markdown(str(path))
            text = path.read_text(encoding="utf-8")
            self.assertIn("payload absent (blank)", text)
            self.assertIn("`fassung`", text)
            self.assertIn("`why_it_missed`", text)
            self.assertIn("Never fill a blank with a guess", text)


class TestBoardCopy(unittest.TestCase):
    def test_match_confidence_not_labelled_score(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_review_under_test", ROOT / "site" / "build_review.py",
        )
        br = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(br)
        html = br.render_simple_row(
            "bach/goldberg/0",
            {"work": "Goldberg Variations", "director": "Glenn Gould",
             "ensemble": "", "label": "Columbia", "year": "1955",
             "work_title": "Goldberg Variations",
             "composer": "Johann Sebastian Bach"},
            {"mb_title": "The Goldberg Variations", "mb_first_release": "1956",
             "match_score": 100, "mbid": "x"},
            {},
            [],
            "accept_eligible",
        )
        self.assertIn("match 100", html)
        self.assertNotIn("score 100", html)
        self.assertNotIn("★", html)
        self.assertIn("confidence, not a verdict", html)
        self.assertIn("Owner: decisions file", html)
        self.assertIn("Owner: Review apply", html)
        rich = br.render_identity_rich(
            "bach/brandenburg/1",
            SEED_HARN,
            PROP_HARN,
            {},
            [],
            "needs_review",
            ib.enrichment_for_row(SEED_HARN, PROP_HARN, [SEED_HARN]),
        )
        self.assertIn("match confidence (not a verdict)", rich)
        self.assertNotIn("Fassung not in seed or harvest payload", rich)
        self.assertNotIn('<span class="k">session year</span>', rich)
        self.assertNotIn('<span class="k">live/studio</span>', rich)
        self.assertIn(".find", br.CSS)

    def test_session_year_and_live_shown_when_payload_has_tokens(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_review_under_test", ROOT / "site" / "build_review.py",
        )
        br = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(br)
        prop = {
            "target": "puccini/tosca/9",
            "payload": {
                "mbid": "mb-live",
                "mb_title": "Tosca (Live)",
                "mb_first_release": "1965",
                "confidence": 90,
                "session_year": "1964",
                "live_studio": "live",
                "mb_disambiguation": "1964 recording",
                "mb_secondary_types": ["Live"],
            },
        }
        seed = {
            "id": "puccini/tosca/9",
            "work": "Giacomo Puccini — Tosca",
            "work_title": "Tosca",
            "director": "X",
            "ensemble": "Y",
            "soloists": "",
            "label": "EMI",
            "year": "1964",
        }
        rich = br.render_identity_rich(
            "puccini/tosca/9", seed, prop, {}, [], "needs_review",
            ib.enrichment_for_row(seed, prop, [seed]),
        )
        self.assertIn('<span class="k">session year</span>', rich)
        self.assertIn("1964", rich)
        self.assertIn('<span class="k">live/studio</span>', rich)
        self.assertIn("live", rich)
        # first-release stays labelled as a release proxy, not session year
        self.assertIn("release proxy, not session", rich)

    def test_accept_eligible_chip_never_shows_stale_reject(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_review_under_test", ROOT / "site" / "build_review.py",
        )
        br = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(br)
        html = br.render_simple_row(
            "haydn/creation/1",
            {"work": "The Creation", "director": "John Eliot Gardiner",
             "ensemble": "English Baroque Soloists", "label": "Archiv",
             "year": "1996", "work_title": "The Creation",
             "composer": "Joseph Haydn", "catalogue": "Hob. XXI:2"},
            {"mb_title": "Die Schöpfung", "mb_first_release": "1997-01-03",
             "match_score": 100, "mbid": "x", "auto_accept_eligible": True},
            {"decision": "reject", "note": "wrong work: pre-rejected by review_queue"},
            [],
            "accept_eligible",
        )
        self.assertIn('data-bucket="accept_eligible"', html)
        self.assertIn("chip pending", html)
        self.assertNotIn("chip reject", html)
        self.assertNotIn("chip wrong", html)

    def test_wrong_work_chip_on_reject_bucket(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_review_under_test", ROOT / "site" / "build_review.py",
        )
        br = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(br)
        html = br.render_simple_row(
            "haydn/trumpet_concerto/2",
            {"work": "Trumpet Concerto", "director": "Karl Richter",
             "ensemble": "Münchener Bach-Orchester", "label": "Archiv",
             "year": "1960s", "work_title": "Trumpet Concerto",
             "composer": "Joseph Haydn", "catalogue": "Hob. VIIe:1"},
            {"mb_title": "Organ Concertos, Vol. 3: Nos. 9, 10, 11, 12",
             "mb_first_release": "1960", "match_score": 100, "mbid": "x"},
            {"decision": "reject"},
            [],
            "reject_wrong_work",
        )
        self.assertIn('data-bucket="reject_wrong_work"', html)
        self.assertIn("chip wrong", html)
        self.assertIn("wrong work", html)

    def test_accept_eligible_ignores_stale_wrong_flag_from_sibling(self):
        """Chip follows the live bucket, not a leftover Brahms-collision flag."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_review_under_test", ROOT / "site" / "build_review.py",
        )
        br = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(br)
        self.assertIn(
            "chip pending",
            br.chip("reject", wrong=True, bucket="accept_eligible"),
        )
        self.assertNotIn(
            "chip wrong",
            br.chip("reject", wrong=True, bucket="accept_eligible"),
        )
        self.assertEqual(
            br.flags_for_bucket(
                ["wrong work: MusicBrainz 'Violin Concerto' matches artists "
                 "already listed under Johannes Brahms"],
                "accept_eligible",
            ),
            [],
        )
        self.assertTrue(
            br.flags_for_bucket(
                ["wrong work: MusicBrainz 'Violin Concerto' is proposed for "
                 "more than one composer"],
                "reject_wrong_work",
            )
        )


class TestSharedReleaseGroupBoard(unittest.TestCase):
    """Mutter/Karajan Beethoven VC owns the disc; Brahms /2 is the collision."""

    TARGET_BEETHOVEN = "beethoven/violin_concerto/3"
    TARGET_BRAHMS = "brahms/violin_concerto/2"

    @classmethod
    def setUpClass(cls):
        import importlib.util
        import json
        sys.path.insert(0, str(ROOT / "agents"))
        import review_queue as rq  # noqa: E402
        spec = importlib.util.spec_from_file_location(
            "build_review_shared_rg", ROOT / "site" / "build_review.py",
        )
        cls.br = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.br)
        cls.seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        cls.props = json.loads(
            (ROOT / "proposals" / "proposals-20260809.json").read_text(encoding="utf-8")
        )
        cls.live = rq.live_identity_buckets(cls.props, cls.seed)
        cls.by_seed, _, _ = cls.br.index_seed(cls.seed)
        cls.by_prop = cls.br.proposal_by_target(cls.props)

    def _row(self, target: str, bucket: str) -> str:
        return self.br.render_simple_row(
            target,
            self.by_seed[target],
            (self.by_prop[target].get("payload") or {}),
            {},
            [],
            bucket,
            works=self.seed.get("works") or [],
        )

    def test_beethoven_mutter_is_accept_eligible_without_wrong_work_chip(self):
        acc = {r["target"] for r in self.live["accept_eligible"]}
        wrong = {r["target"] for r in self.live["reject_wrong_work"]}
        self.assertIn(self.TARGET_BEETHOVEN, acc)
        self.assertNotIn(self.TARGET_BEETHOVEN, wrong)
        html = self._row(self.TARGET_BEETHOVEN, "accept_eligible")
        self.assertIn('data-bucket="accept_eligible"', html)
        self.assertIn("chip pending", html)
        self.assertNotIn("chip wrong", html)
        self.assertNotIn("chip reject", html)
        self.assertNotIn("wrong work", html.lower())
        self.assertNotIn("Johannes Brahms", html)

    def test_brahms_collision_stays_reject_wrong_work(self):
        acc = {r["target"] for r in self.live["accept_eligible"]}
        wrong = {r["target"] for r in self.live["reject_wrong_work"]}
        self.assertIn(self.TARGET_BRAHMS, wrong)
        self.assertNotIn(self.TARGET_BRAHMS, acc)
        html = self._row(self.TARGET_BRAHMS, "reject_wrong_work")
        self.assertIn('data-bucket="reject_wrong_work"', html)
        self.assertIn("chip wrong", html)
        self.assertIn("wrong work", html.lower())
        self.assertIn("Ludwig van Beethoven", html)


if __name__ == "__main__":
    unittest.main()
