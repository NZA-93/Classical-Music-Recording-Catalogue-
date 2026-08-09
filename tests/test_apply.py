#!/usr/bin/env python3
"""Tests for agents/apply.py — proposals into seed/recordings."""

from __future__ import annotations

import json
import pathlib
import shutil
import sys
import tempfile
import unittest
from copy import deepcopy

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents"))

import apply as ap  # noqa: E402


SEED_MIN = {
    "schema": "seed/1",
    "works": [
        {
            "id": "bach/brandenburg",
            "title": "Brandenburg Concertos",
            "candidates": [
                {
                    "id": "bach/brandenburg/0",
                    "director": "Trevor Pinnock",
                    "ensemble": "The English Concert",
                    "label": "Archiv",
                    "year": "1982",
                    "verified": False,
                    "mbid": None,
                },
                {
                    "id": "bach/brandenburg/1",
                    "director": "Nikolaus Harnoncourt",
                    "year": "1964",
                    "verified": True,
                    "mbid": "already-verified-mbid",
                },
            ],
        }
    ],
}


class ApplyIdentity(unittest.TestCase):
    def test_sets_mbid_and_leaves_verified_false(self):
        seed = deepcopy(SEED_MIN)
        props = [{
            "target": "bach/brandenburg/0",
            "kind": "identity",
            "payload": {"mbid": "abc-123", "mb_title": "Brandenburg",
                        "mb_first_release": "1982", "match_score": 98},
            "source": "MusicBrainz",
            "provenance": "cited",
        }]
        new, _, log = ap.apply_proposals(props, seed)
        cand = ap.find_candidate(new, "bach/brandenburg/0")
        self.assertEqual(cand["mbid"], "abc-123")
        self.assertIs(cand["verified"], False)
        self.assertEqual(cand["match_score"], 98)
        self.assertTrue(any(e["action"] == "identity" for e in log))

    def test_idempotent(self):
        seed = deepcopy(SEED_MIN)
        props = [{
            "target": "bach/brandenburg/0",
            "kind": "identity",
            "payload": {"mbid": "abc-123", "match_score": 98},
            "source": "MusicBrainz", "provenance": "cited",
        }]
        once, _, _ = ap.apply_proposals(props, seed)
        twice, _, log = ap.apply_proposals(props, once)
        self.assertEqual(once, twice)
        self.assertTrue(any(e["action"] == "noop" for e in log))

    def test_verified_protected_without_force(self):
        seed = deepcopy(SEED_MIN)
        props = [{
            "target": "bach/brandenburg/1",
            "kind": "identity",
            "payload": {"mbid": "other-mbid"},
            "source": "MusicBrainz", "provenance": "cited",
        }]
        new, _, log = ap.apply_proposals(props, seed)
        cand = ap.find_candidate(new, "bach/brandenburg/1")
        self.assertEqual(cand["mbid"], "already-verified-mbid")
        self.assertTrue(any(e["action"] == "skipped_verified" for e in log))

    def test_force_overwrites_verified(self):
        seed = deepcopy(SEED_MIN)
        props = [{
            "target": "bach/brandenburg/1",
            "kind": "identity",
            "payload": {"mbid": "other-mbid"},
            "source": "MusicBrainz", "provenance": "cited",
        }]
        new, _, log = ap.apply_proposals(
            props, seed, force=True, reason="human confirmed rematch")
        cand = ap.find_candidate(new, "bach/brandenburg/1")
        self.assertEqual(cand["mbid"], "other-mbid")
        self.assertIs(cand["verified"], False)
        self.assertTrue(any(e["action"] == "force_overwrite" for e in log))


class ApplyEditions(unittest.TestCase):
    def test_drops_bad_barcode(self):
        seed = deepcopy(SEED_MIN)
        props = [{
            "target": "bach/brandenburg/0",
            "kind": "editions",
            "payload": {"editions": [
                {"mbid": "rel-1", "barcode": "090317761122",  # bad check digit
                 "catno": "X", "year": "1992", "label": "Teldec", "format": "CD"},
                {"mbid": "rel-2", "barcode": "090317761121",  # good
                 "catno": "Y", "year": "1992", "label": "Teldec", "format": "CD"},
            ]},
            "source": "MusicBrainz", "provenance": "cited",
        }]
        new, _, log = ap.apply_proposals(props, seed)
        cand = ap.find_candidate(new, "bach/brandenburg/0")
        barcodes = [e.get("barcode") for e in cand["editions"]]
        self.assertIn("090317761121", barcodes)
        self.assertNotIn("090317761122", barcodes)
        self.assertTrue(any(e["action"] == "dropped_barcode" for e in log))
        # Bad edition still stored, but barcode cleared.
        bad = next(e for e in cand["editions"] if e["mbid"] == "rel-1")
        self.assertIsNone(bad["barcode"])

    def test_idempotent_editions(self):
        seed = deepcopy(SEED_MIN)
        props = [{
            "target": "bach/brandenburg/0",
            "kind": "editions",
            "payload": {"editions": [
                {"mbid": "rel-2", "barcode": "090317761121",
                 "catno": "Y", "year": "1992", "label": "Teldec", "format": "CD"},
            ]},
            "source": "MusicBrainz", "provenance": "cited",
        }]
        once, _, _ = ap.apply_proposals(props, seed)
        twice, _, log = ap.apply_proposals(props, once)
        self.assertEqual(len(ap.find_candidate(once, "bach/brandenburg/0")["editions"]),
                         len(ap.find_candidate(twice, "bach/brandenburg/0")["editions"]))
        self.assertTrue(any(e["action"] == "noop" for e in log))


class ApplyCover(unittest.TestCase):
    def test_records_hit_and_miss(self):
        seed = deepcopy(SEED_MIN)
        hit = [{
            "target": "bach/brandenburg/0", "kind": "cover",
            "payload": {"image": "https://coverartarchive.org/x"},
            "source": "Cover Art Archive", "provenance": "cited",
        }]
        new, _, _ = ap.apply_proposals(hit, seed)
        self.assertEqual(ap.find_candidate(new, "bach/brandenburg/0")["image"],
                         "https://coverartarchive.org/x")
        miss = [{
            "target": "bach/brandenburg/0", "kind": "cover",
            "payload": {"image": None},
            "source": "Cover Art Archive", "provenance": "cited",
        }]
        new2, _, _ = ap.apply_proposals(miss, new)
        self.assertIsNone(ap.find_candidate(new2, "bach/brandenburg/0")["image"])

    def test_refuses_data_uri_binary(self):
        seed = deepcopy(SEED_MIN)
        props = [{
            "target": "bach/brandenburg/0", "kind": "cover",
            "payload": {"image": "data:image/jpeg;base64,/9j/4AAQ"},
            "source": "Cover Art Archive", "provenance": "cited",
        }]
        new, _, log = ap.apply_proposals(props, seed)
        self.assertNotIn("image", ap.find_candidate(new, "bach/brandenburg/0"))
        self.assertTrue(any(e["action"] == "skip" and "binaries" in e.get("note", "")
                            for e in log))

    def test_stores_cover_mbid_for_hotlink(self):
        seed = deepcopy(SEED_MIN)
        mbid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        props = [{
            "target": "bach/brandenburg/0", "kind": "cover",
            "payload": {
                "image": f"https://coverartarchive.org/release-group/{mbid}/front-500",
                "mbid": mbid,
            },
            "source": "Cover Art Archive", "provenance": "cited",
        }]
        new, _, _ = ap.apply_proposals(props, seed)
        cand = ap.find_candidate(new, "bach/brandenburg/0")
        self.assertEqual(cand["cover_mbid"], mbid)


class ApplyOnlyFilter(unittest.TestCase):
    def test_only_identity_skips_cover(self):
        seed = deepcopy(SEED_MIN)
        props = [
            {"target": "bach/brandenburg/0", "kind": "identity",
             "payload": {"mbid": "abc"}, "source": "MB", "provenance": "cited"},
            {"target": "bach/brandenburg/0", "kind": "cover",
             "payload": {"image": "https://coverartarchive.org/x"},
             "source": "CAA", "provenance": "cited"},
        ]
        new, _, _ = ap.apply_proposals(props, seed, only={"identity"})
        cand = ap.find_candidate(new, "bach/brandenburg/0")
        self.assertEqual(cand["mbid"], "abc")
        self.assertNotIn("image", cand)


class ApplyNeverTouchesStatements(unittest.TestCase):
    def test_kinds_exclude_statements(self):
        self.assertNotIn("statement", ap.KINDS)
        self.assertNotIn("citation_task", ap.KINDS)
        self.assertNotIn("editorial", ap.KINDS)

    def test_dry_run_leaves_seed_and_statements_untouched(self):
        """CLI dry-run must not mutate seed, recordings, statements, or editorial."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            root = tmp_path / "repo"
            for sub in ("agents", "data/statements", "data/editorial",
                        "data/recordings", "proposals"):
                (root / sub).mkdir(parents=True)
            seed = deepcopy(SEED_MIN)
            seed_path = root / "data" / "seed.json"
            seed_path.write_text(json.dumps(seed), encoding="utf-8")
            stmt = root / "data" / "statements" / "marker.json"
            editorial = root / "data" / "editorial" / "marker.json"
            stmt.write_text('{"ok": true}\n', encoding="utf-8")
            editorial.write_text('{"ok": true}\n', encoding="utf-8")
            props_path = root / "proposals" / "p.json"
            props_path.write_text(json.dumps([{
                "target": "bach/brandenburg/0", "kind": "identity",
                "payload": {"mbid": "abc-123", "match_score": 99},
                "source": "MusicBrainz", "provenance": "cited",
            }]), encoding="utf-8")

            # Point the module at the temp tree for this process.
            old = (ap.ROOT, ap.SEED_PATH, ap.RECORDINGS, ap.PROPOSALS_DIR)
            try:
                ap.ROOT = root
                ap.SEED_PATH = seed_path
                ap.RECORDINGS = root / "data" / "recordings"
                ap.PROPOSALS_DIR = root / "proposals"
                rc = ap.main(["--proposals", str(props_path), "--dry-run"])
            finally:
                ap.ROOT, ap.SEED_PATH, ap.RECORDINGS, ap.PROPOSALS_DIR = old

            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(seed_path.read_text(encoding="utf-8")), seed)
            self.assertEqual(stmt.read_text(encoding="utf-8"), '{"ok": true}\n')
            self.assertEqual(editorial.read_text(encoding="utf-8"), '{"ok": true}\n')
            # Applied report is reviewable even on dry-run.
            applied = list((root / "proposals").glob("applied-*.json"))
            self.assertEqual(len(applied), 1)


if __name__ == "__main__":
    unittest.main()
