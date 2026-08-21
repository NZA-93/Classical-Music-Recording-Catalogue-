#!/usr/bin/env python3
"""Tests for agents/review_queue.py and decisions-gated apply."""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest
from copy import deepcopy

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents"))

import apply as ap  # noqa: E402
import review_queue as rq  # noqa: E402


SEED = {
    "works": [{
        "id": "bach/brandenburg",
        "composer": "Bach",
        "title": "Brandenburg Concertos",
        "catalogue": "BWV 1046–1051",
        "candidates": [
            {"id": "bach/brandenburg/0", "director": "Pinnock",
             "ensemble": "TEC", "label": "Archiv", "year": "1982",
             "verified": False, "mbid": None},
            {"id": "bach/brandenburg/1", "director": "Other",
             "label": "X", "year": "1990", "verified": False, "mbid": None},
        ],
    }]
}


class TestBuckets(unittest.TestCase):
    def test_wrong_work_bucket(self):
        items = [{
            "target": "bach/brandenburg/1",
            "flags": ["wrong work: Piano Concertos"],
            "mb": {"auto_accept_eligible": False, "match_score": 90},
            "seed": {},
        }]
        b = rq.bucket_identity(items)
        self.assertEqual(b["reject_wrong_work"][0]["target"], "bach/brandenburg/1")
        self.assertEqual(b["accept_eligible"], [])

    def test_eligible_clean(self):
        items = [{
            "target": "bach/brandenburg/0",
            "flags": [],
            "mb": {"auto_accept_eligible": True, "match_score": 95},
            "seed": {},
        }]
        b = rq.bucket_identity(items)
        self.assertEqual(len(b["accept_eligible"]), 1)


class TestDecisionsApply(unittest.TestCase):
    def test_only_accepted_rows_apply(self):
        seed = deepcopy(SEED)
        props = [{
            "target": "bach/brandenburg/0", "kind": "identity",
            "payload": {"mbid": "aaa", "mb_title": "Brandenburg Concertos",
                        "match_score": 95, "auto_accept_eligible": True},
        }, {
            "target": "bach/brandenburg/1", "kind": "identity",
            "payload": {"mbid": "bbb", "mb_title": "Brandenburg Concertos",
                        "match_score": 95, "auto_accept_eligible": True},
        }]
        decisions = {
            ("bach/brandenburg/0", "identity"): {
                "target": "bach/brandenburg/0", "kind": "identity",
                "decision": "accept", "by": "NZ",
            },
            ("bach/brandenburg/1", "identity"): {
                "target": "bach/brandenburg/1", "kind": "identity",
                "decision": "pending",
            },
        }
        new, _, log = ap.apply_proposals(
            props, seed, decisions=decisions, require_decisions=True,
        )
        self.assertEqual(ap.find_candidate(new, "bach/brandenburg/0")["mbid"], "aaa")
        self.assertIsNone(ap.find_candidate(new, "bach/brandenburg/1")["mbid"])
        self.assertTrue(any(e["action"] == "skipped_decision" for e in log))

    def test_human_accept_ratifies_ineligible(self):
        seed = deepcopy(SEED)
        props = [{
            "target": "bach/brandenburg/0", "kind": "identity",
            "payload": {
                "mbid": "aaa", "mb_title": "Brandenburg Concertos",
                "match_score": 70, "auto_accept_eligible": False,
                "review_flags": ["confidence 70 < 80"],
            },
        }]
        decisions = {
            ("bach/brandenburg/0", "identity"): {
                "decision": "accept", "by": "NZ", "kind": "identity",
                "target": "bach/brandenburg/0",
            },
        }
        new, _, log = ap.apply_proposals(
            props, seed, decisions=decisions, require_decisions=True,
        )
        self.assertEqual(ap.find_candidate(new, "bach/brandenburg/0")["mbid"], "aaa")
        self.assertFalse(any(e["action"] == "refused_ineligible" for e in log))

    def test_wrong_work_still_blocked_after_accept(self):
        seed = deepcopy(SEED)
        props = [{
            "target": "bach/brandenburg/0", "kind": "identity",
            "payload": {
                "mbid": "aaa", "mb_title": "Piano Concertos",
                "match_score": 99, "auto_accept_eligible": False,
                "review_flags": [
                    "wrong work: MusicBrainz 'Piano Concertos' does not match "
                    "seed 'Brandenburg Concertos'"
                ],
            },
        }]
        decisions = {
            ("bach/brandenburg/0", "identity"): {"decision": "accept", "by": "NZ"},
        }
        new, _, log = ap.apply_proposals(
            props, seed, decisions=decisions, require_decisions=True,
        )
        self.assertIsNone(ap.find_candidate(new, "bach/brandenburg/0")["mbid"])
        self.assertTrue(any(e["action"] == "refused_wrong_work" for e in log))


class TestDecisionsTemplate(unittest.TestCase):
    def test_preserves_prior_accept(self):
        buckets = {
            "reject_wrong_work": [],
            "accept_eligible": [{"target": "bach/brandenburg/0"}],
            "needs_review": [],
        }
        existing = {
            "decisions": [{
                "target": "bach/brandenburg/0", "kind": "identity",
                "decision": "accept", "by": "NZ", "date": "2026-08-09",
            }],
        }
        out = rq.build_decisions_template("proposals/x.json", buckets, existing)
        self.assertEqual(out["decisions"][0]["decision"], "accept")
        self.assertEqual(out["decisions"][0]["by"], "NZ")


if __name__ == "__main__":
    unittest.main()
