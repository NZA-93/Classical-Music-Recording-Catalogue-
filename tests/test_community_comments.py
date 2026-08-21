#!/usr/bin/env python3
"""Tests for the community comments layer (fenced from editorial)."""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents"))

import community_comments as cc  # noqa: E402
import ingest_community_issue as ing  # noqa: E402


class TestCommunityValidate(unittest.TestCase):
    def test_rejects_score_claim(self):
        known = {"bach/brandenburg/0"}
        errs = cc.validate_comment({
            "layer": "community", "kind": "identity_review",
            "id": "x", "target": "bach/brandenburg/0",
            "author": "github:alice", "body": "score: 3 stars easy",
        }, known)
        self.assertTrue(any("score" in e for e in errs))

    def test_requires_community_layer(self):
        errs = cc.validate_comment({
            "layer": "editorial", "kind": "general",
            "id": "x", "target": "bach/brandenburg/0",
            "author": "github:alice", "body": "nice pressing",
        }, {"bach/brandenburg/0"})
        self.assertTrue(any("community" in e for e in errs))

    def test_parse_issue_form(self):
        body = """### Target id\n\nbach/brandenburg/0\n\n### Kind\n\nidentity_review\n\n### Comment\n\nUse the 1982 Archiv RG.\n\n### Your GitHub login\n\nalice\n"""
        mapped = ing.map_fields(ing.parse_issue_body(body))
        self.assertEqual(mapped["target"], "bach/brandenburg/0")
        self.assertEqual(mapped["author"], "github:alice")
        self.assertIn("1982", mapped["body"])


if __name__ == "__main__":
    unittest.main()
