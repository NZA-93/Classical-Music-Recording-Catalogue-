#!/usr/bin/env python3
"""Tests for identity confidence gating and CAA cover proposal shape."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load(name: str, relpath: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


har = _load("harvest_under_test", "agents/harvest.py")


class FakeHttp:
    def __init__(self, responses: dict):
        self.responses = responses
        self.spent = 0
        self.urls: list[str] = []

    def get(self, url: str):
        self.urls.append(url)
        self.spent += 1
        for prefix, body in self.responses.items():
            if prefix in url:
                return body
        return None


REC = {
    "id": "bach/brandenburg/0",
    "director": "Trevor Pinnock",
    "ensemble": "The English Concert",
    "soloists": "Trevor Pinnock, harpsichord",
    "label": "Archiv",
    "year": "1982",
    "mbid": None,
}
WORK = {
    "composer": "Johann Sebastian Bach",
    "title": "Brandenburg Concertos",
}


class TestIdentityConfidence(unittest.TestCase):
    def _groups(self, *rows):
        return {"release-groups": [
            {"id": rid, "title": title, "first-release-date": date, "score": score}
            for rid, title, date, score in rows
        ]}

    def test_high_confidence_clean_match_is_eligible(self):
        http = FakeHttp({
            "release-group": self._groups(
                ("mb-1", "Brandenburg Concertos", "1982-01-01", 98),
            ),
        })
        props = har.adapter_identity(REC, WORK, http)
        self.assertEqual(len(props), 1)
        p = props[0].payload
        self.assertEqual(p["confidence"], 98)
        self.assertEqual(p["match_score"], 98)
        self.assertTrue(p["auto_accept_eligible"])
        self.assertFalse(p["uncertain"])
        self.assertEqual(p["review_flags"], [])
        self.assertTrue(p["needs_human_review"])
        self.assertIn("mb_url", p)
        self.assertEqual(p["seed"]["label"], "Archiv")

    def test_below_80_is_not_auto_accept_eligible(self):
        http = FakeHttp({
            "release-group": self._groups(
                ("mb-low", "Brandenburg Concertos", "1982", 55),
            ),
        })
        p = har.adapter_identity(REC, WORK, http)[0].payload
        self.assertEqual(p["confidence"], 55)
        self.assertFalse(p["auto_accept_eligible"])
        self.assertTrue(p["uncertain"])
        self.assertTrue(any("confidence 55" in f for f in p["review_flags"]))

    def test_compilation_title_flagged(self):
        http = FakeHttp({
            "release-group": self._groups(
                ("mb-comp", "Bach: Best of the Brandenburgs", "1982", 95),
            ),
        })
        p = har.adapter_identity(REC, WORK, http)[0].payload
        self.assertFalse(p["auto_accept_eligible"])
        self.assertTrue(any("compilation" in f for f in p["review_flags"]))

    def test_date_drift_flagged(self):
        http = FakeHttp({
            "release-group": self._groups(
                ("mb-late", "Brandenburg Concertos", "1999", 99),
            ),
        })
        p = har.adapter_identity(REC, WORK, http)[0].payload
        self.assertFalse(p["auto_accept_eligible"])
        self.assertTrue(any("date off" in f for f in p["review_flags"]))

    def test_alternatives_listed(self):
        http = FakeHttp({
            "release-group": self._groups(
                ("mb-1", "Brandenburg Concertos", "1982", 90),
                ("mb-2", "Brandenburg Concertos", "1983", 80),
            ),
        })
        p = har.adapter_identity(REC, WORK, http)[0].payload
        self.assertEqual(p["mbid"], "mb-1")
        self.assertEqual(len(p["alternatives"]), 1)
        self.assertEqual(p["alternatives"][0]["mbid"], "mb-2")


class TestCoverProposals(unittest.TestCase):
    def test_hit_uses_caa_json_not_binary_front(self):
        meta = {
            "images": [{
                "front": True,
                "image": "https://coverartarchive.org/release/r1/front.jpg",
                "thumbnails": {
                    "500": "https://coverartarchive.org/release/r1/front-500",
                },
            }],
        }
        http = FakeHttp({"release-group/rg-1": meta})
        rec = {**REC, "mbid": "rg-1"}
        props = har.adapter_cover(rec, WORK, http)
        self.assertEqual(len(props), 1)
        p = props[0].payload
        self.assertEqual(p["status"], "hit")
        self.assertEqual(p["resolution_step"], "caa-release-group")
        self.assertFalse(p["rehost"])
        self.assertIsNotNone(p["image"])
        self.assertTrue(p["image"].startswith("https://coverartarchive.org/"))
        # Must hit the JSON metadata endpoint, not download front-500 bytes.
        self.assertTrue(any(u.endswith("/release-group/rg-1") for u in http.urls))
        self.assertFalse(any("front-500" in u for u in http.urls))

    def test_miss_emits_contribution_prompt(self):
        http = FakeHttp({"release-group/rg-miss": {"images": []}})
        rec = {**REC, "mbid": "rg-miss"}
        p = har.adapter_cover(rec, WORK, http)[0].payload
        self.assertEqual(p["status"], "miss")
        self.assertIsNone(p["image"])
        self.assertIn("contribution_prompt", p)
        self.assertIn("musicbrainz", p["contribution_prompt"]["musicbrainz_rg"])

    def test_release_step_preferred_when_release_mbid_present(self):
        release_meta = {
            "images": [{
                "front": True,
                "thumbnails": {"500": "https://coverartarchive.org/release/rel/front-500"},
            }],
        }
        http = FakeHttp({
            "release/rel-1": release_meta,
            "release-group/": {"images": []},
        })
        rec = {**REC, "mbid": "rg-1", "release_mbid": "rel-1"}
        p = har.adapter_cover(rec, WORK, http)[0].payload
        self.assertEqual(p["status"], "hit")
        self.assertEqual(p["resolution_step"], "caa-release")


class TestPrBodyPlan(unittest.TestCase):
    def test_dry_run_plan_documents_budget(self):
        import tempfile
        seed = {
            "works": [{
                "composer": "Bach", "title": "X",
                "candidates": [{**REC}],
            }],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "PR_BODY.md"
            har.write_pr_body(
                path, stamp="20260809", version=har.VERSION,
                contact="harvest@example.invalid", budget=300, spent=72,
                planned={"identity": 72}, proposals=[], seed=seed, dry=True,
            )
            text = path.read_text("utf-8")
            self.assertIn("DRY RUN", text)
            self.assertIn("budget **300**", text)
            self.assertIn("**72**", text)
            self.assertIn("harvest@example.invalid", text)
            self.assertIn("confidence < 80", text)


if __name__ == "__main__":
    unittest.main()
