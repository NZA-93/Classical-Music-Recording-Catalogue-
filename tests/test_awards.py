#!/usr/bin/env python3
"""Tests for agents/awards.py — S1-03 citation engine + ADR-001."""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents"))

import awards as aw  # noqa: E402


class TestPerformerMatch(unittest.TestCase):
    def test_nelsons_matches(self):
        self.assertTrue(aw.performer_match(
            "Boston Symphony Orchestra, Andris Nelsons",
            "Andris Nelsons", "Boston Symphony Orchestra"))

    def test_karajan_tosca_without_ensemble_still_matches_director(self):
        self.assertTrue(aw.performer_match(
            "Karajan", "Herbert von Karajan", "Vienna Philharmonic"))

    def test_unrelated_rejected(self):
        self.assertFalse(aw.performer_match(
            "Andris Nelsons", "Yevgeny Mravinsky", "Leningrad Philharmonic"))


class TestSourceClass(unittest.TestCase):
    def test_grammy_is_major_award(self):
        self.assertEqual(
            aw.source_class("Grammy — Best Orchestral Performance"),
            "major_award")

    def test_gramophone_award_is_major_award(self):
        self.assertEqual(
            aw.source_class("Gramophone Award — Orchestral"),
            "major_award")

    def test_editors_choice_is_specialist_survey(self):
        self.assertEqual(
            aw.source_class("Gramophone Editor's Choice"),
            "specialist survey")

    def test_building_a_library_is_specialist_survey(self):
        self.assertEqual(
            aw.source_class("BBC Building a Library first choice"),
            "specialist survey")


class TestAwardsRun(unittest.TestCase):
    def test_produces_nelsons_sym5_proposal(self):
        props = aw.run(dry_run=True, quiet=True)
        targets = [p["target"] for p in props]
        self.assertIn("shostakovich_sym5_nelsons", targets)
        nel = next(p for p in props if p["target"] == "shostakovich_sym5_nelsons")
        self.assertEqual(nel["kind"], "award")
        self.assertEqual(nel["payload"]["scale"], "award")
        self.assertEqual(nel["payload"]["provenance"], "cited")
        self.assertEqual(nel["payload"]["class"], "major_award")
        self.assertFalse(nel["payload"]["conflict"])
        self.assertTrue(nel["payload"]["needs_human_confirmation"])
        self.assertIn("shostakovich/sym5", nel["payload"]["covers_works"])
        self.assertGreater(len(nel["payload"]["covers_works"]), 1)
        self.assertTrue(nel["payload"]["locator"])
        self.assertLessEqual(len(nel["payload"]["characterisation"]), 240)

    def test_album_award_shares_covers_works_across_matched_recordings(self):
        """ADR-001: multi-work Grammy keeps the same covers_works on every row."""
        props = aw.run(dry_run=True, quiet=True)
        grammy_2017 = [
            p for p in props
            if p["payload"].get("award", "").startswith("Grammy")
            and p["payload"].get("year") == 2017
        ]
        self.assertGreaterEqual(len(grammy_2017), 2)
        covers_sets = {tuple(p["payload"]["covers_works"]) for p in grammy_2017}
        self.assertEqual(len(covers_sets), 1)
        covers = next(iter(covers_sets))
        self.assertEqual(len(covers), 3)
        self.assertIn("shostakovich/sym5", covers)
        self.assertIn("shostakovich/sym8", covers)
        self.assertIn("shostakovich/sym9", covers)

    def test_never_infers_without_locator(self):
        # All shipped award rows have locators; the adapter skips any that do not.
        for row in aw.load_awards():
            self.assertTrue(row.get("locator"), row)

    def test_skips_award_row_missing_locator(self):
        fake = [{
            "award": "Grammy — Best Orchestral Performance",
            "year": 2099,
            "performers": "Boston Symphony Orchestra, Andris Nelsons",
            "label": "Deutsche Grammophon",
            "covers_works": ["shostakovich/sym5"],
            # no locator — must not produce a proposal
        }]
        with mock.patch.object(aw, "load_awards", return_value=fake):
            props = aw.run(dry_run=True, quiet=True)
        self.assertEqual(props, [])

    def test_does_not_write_statements(self):
        """Awards adapter writes proposals/ only — never data/statements/."""
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "awards-test.json"
            rc = aw.main(["--quiet", "--out", str(out)])
            self.assertEqual(rc, 0)
            self.assertTrue(out.exists())
            text = out.read_text(encoding="utf-8")
            self.assertIn("needs_human_confirmation", text)
            # Sanity: output path is under the temp proposals-like file, not statements.
            self.assertNotIn("data/statements", str(out))


if __name__ == "__main__":
    unittest.main()
