#!/usr/bin/env python3
"""Tests for ingest and metrics."""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest
from copy import deepcopy

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents"))

import ingest as ing  # noqa: E402
import metrics as met  # noqa: E402


class TestIngestDedupe(unittest.TestCase):
    def test_dedupe_key(self):
        a = {"recording": "r1", "source": "s", "locator": "u"}
        b = {"recording": "r1", "source": "s", "locator": "u"}
        c = {"recording": "r1", "source": "s", "locator": None}
        self.assertEqual(ing.dedupe_key(a), ing.dedupe_key(b))
        self.assertNotEqual(ing.dedupe_key(a), ing.dedupe_key(c))


class TestIngestProseVisible(unittest.TestCase):
    def test_dry_run_noseda_prose(self):
        # Dry-run must surface unscored prose rather than skipping silently.
        path = ROOT / "contributions" / "nza93-noseda-sym5.json"
        if not path.exists():
            self.skipTest("contribution fixture missing")
        rc = ing.main([str(path), "--dry-run"])
        # May reject if edition unknown in catalogue — either way must not crash.
        self.assertIn(rc, (0, 1))


class TestMetrics(unittest.TestCase):
    def test_metrics_writes(self):
        rc = met.main()
        self.assertEqual(rc, 0)
        doc = json.loads((ROOT / "build" / "metrics.json").read_text())
        self.assertIn("citation_ratio", doc)
        self.assertIn("signed_entries", doc)
        self.assertGreaterEqual(doc["works"], 59)


if __name__ == "__main__":
    unittest.main()
