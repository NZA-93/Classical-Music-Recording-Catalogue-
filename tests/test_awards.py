#!/usr/bin/env python3
"""Tests for agents/awards.py."""

from __future__ import annotations

import pathlib
import sys
import unittest

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

    def test_never_infers_without_locator(self):
        # All shipped award rows have locators; the adapter skips any that do not.
        for row in aw.load_awards():
            self.assertTrue(row.get("locator"), row)


if __name__ == "__main__":
    unittest.main()
