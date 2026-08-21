#!/usr/bin/env python3
"""Tests for agents/review.py."""

from __future__ import annotations

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents"))

import review as rv  # noqa: E402


SEED = {
    "works": [{
        "id": "bach/brandenburg",
        "composer": "Bach",
        "title": "Brandenburgs",
        "candidates": [{
            "id": "bach/brandenburg/0",
            "director": "Trevor Pinnock",
            "ensemble": "The English Concert",
            "label": "Archiv",
            "year": "1982",
        }],
    }]
}


class TestReviewFlags(unittest.TestCase):
    def test_low_confidence_flagged(self):
        props = [{
            "target": "bach/brandenburg/0", "kind": "identity",
            "payload": {"mbid": "x", "mb_title": "Brandenburg Concertos",
                        "mb_first_release": "1982", "match_score": 40},
        }]
        items = rv.rows(props, SEED)
        self.assertTrue(any("confidence" in f for f in items[0]["flags"]))
        self.assertFalse(items[0]["mb"]["auto_accept_eligible"])

    def test_date_off_flagged(self):
        props = [{
            "target": "bach/brandenburg/0", "kind": "identity",
            "payload": {"mbid": "x", "mb_title": "Brandenburg Concertos",
                        "mb_first_release": "1999", "match_score": 95},
        }]
        items = rv.rows(props, SEED)
        self.assertTrue(any("date off" in f for f in items[0]["flags"]))

    def test_compilation_title_flagged(self):
        props = [{
            "target": "bach/brandenburg/0", "kind": "identity",
            "payload": {"mbid": "x", "mb_title": "Bach: Best of the Brandenburgs",
                        "mb_first_release": "1982", "match_score": 90},
        }]
        items = rv.rows(props, SEED)
        self.assertTrue(any("compilation" in f for f in items[0]["flags"]))

    def test_clean_match_unflagged(self):
        props = [{
            "target": "bach/brandenburg/0", "kind": "identity",
            "payload": {"mbid": "x", "mb_title": "Brandenburg Concertos",
                        "mb_first_release": "1982", "match_score": 98},
        }]
        items = rv.rows(props, SEED)
        self.assertEqual(items[0]["flags"], [])

    def test_wrong_work_not_eligible_even_if_harvest_said_so(self):
        """Stale auto_accept_eligible must not keep St John → St Matthew eligible."""
        props = [{
            "target": "bach/brandenburg/0", "kind": "identity",
            "payload": {
                "mbid": "x", "mb_title": "St. Matthew Passion",
                "mb_first_release": "1962", "match_score": 100,
                "auto_accept_eligible": True, "review_flags": [],
            },
        }]
        seed = {
            "works": [{
                "id": "bach/john", "composer": "Johann Sebastian Bach",
                "title": "St John Passion", "catalogue": "BWV 245",
                "candidates": [{
                    "id": "bach/brandenburg/0", "director": "Otto Klemperer",
                    "label": "EMI", "year": "1961",
                }],
            }]
        }
        items = rv.rows(props, seed)
        self.assertTrue(any(f.startswith("wrong work:") for f in items[0]["flags"]))
        self.assertFalse(items[0]["mb"]["auto_accept_eligible"])

    def test_markdown_says_match_not_score(self):
        props = [{
            "target": "bach/brandenburg/0", "kind": "identity",
            "payload": {"mbid": "x", "mb_title": "Brandenburg Concertos",
                        "mb_first_release": "1982", "match_score": 98,
                        "auto_accept_eligible": True},
        }]
        md = rv.render_markdown(rv.rows(props, SEED))
        self.assertIn("| Target |", md)
        self.assertIn("| Match |", md)
        self.assertNotIn("| Score |", md)
        self.assertIn("bach/brandenburg/0", md)


if __name__ == "__main__":
    unittest.main()
