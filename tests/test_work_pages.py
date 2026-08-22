"""Sealed work pages: no global related / recommended / trending feed.

D only. Empty related is correct. A Brandenburg page must not be fed
Symphony No. 5 (or any other composer's work) via loose tokens or
popularity. The review board must not grow a cross-work suggestion rail.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load(name: str, relpath: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


href = _load("work_href", "site/work_href.py")
rnd = _load("render_site", "site/render.py")


FEED_PHRASES = (
    "you may also like",
    "recommended for you",
    "trending",
    "related works",
    "follow the thread",
    "popular now",
)


def _catalogue() -> dict:
    return json.loads((ROOT / "build/catalogue.json").read_text(encoding="utf-8"))


def _work(cat: dict, fragment: str) -> dict:
    for work in cat["works"]:
        if fragment in work["id"] or fragment in (work.get("title") or ""):
            return work
    raise AssertionError(f"no work matching {fragment!r}")


def _html_for(work: dict, cat: dict) -> str:
    tpl = (ROOT / "site/template.html").read_text(encoding="utf-8")
    title = f"{work['title']} — {work['composer']}"
    return rnd.apply_template(
        tpl, rnd.seal_catalogue(cat, work), [], base="../", title=title
    )


class TestWorkHrefs(unittest.TestCase):
    def test_anchors(self):
        self.assertEqual(href.work_anchor("bach_brandenburg"), "bach_brandenburg")
        self.assertEqual(href.work_anchor("shostakovich/sym5"), "shostakovich_sym5")
        self.assertEqual(href.work_anchor("puccini_tosca"), "puccini_tosca")

    def test_page_href_is_sealed_work_file(self):
        self.assertEqual(
            href.work_page_href("bach_brandenburg"),
            "works/bach_brandenburg.html",
        )
        self.assertEqual(
            href.work_page_href(
                "shostakovich/sym5", depth=1, recording_id="shostakovich_sym5_nelsons"
            ),
            "../works/shostakovich_sym5.html#shostakovich_sym5_nelsons",
        )


class TestSealCatalogue(unittest.TestCase):
    def test_one_work_only_and_barcodes_do_not_leak(self):
        cat = _catalogue()
        bach = _work(cat, "brandenburg")
        sealed = rnd.seal_catalogue(cat, bach)
        self.assertEqual([w["id"] for w in sealed["works"]], [bach["id"]])
        titles = {w["title"] for w in sealed["works"]}
        self.assertNotIn("Symphony No. 5", titles)
        self.assertNotIn("Tosca", titles)
        rec_ids = {r["id"] for r in bach["recordings"]}
        for hit in sealed["barcode_index"].values():
            self.assertIn(hit.get("recording"), rec_ids)

    def test_entries_directory_carries_no_work_bodies(self):
        cat = _catalogue()
        directory = rnd.directory_catalogue(cat)
        self.assertEqual(directory["works"], [])
        self.assertEqual(directory["barcode_index"], {})


class TestSealedWorkPageHtml(unittest.TestCase):
    def test_brandenburg_page_is_not_fed_symphony_no_5(self):
        cat = _catalogue()
        html = _html_for(_work(cat, "brandenburg"), cat)
        self.assertIn("Brandenburg Concertos", html)
        self.assertIn("Trevor Pinnock", html)
        self.assertNotIn("Symphony No. 5", html)
        self.assertNotIn("Dmitri Shostakovich", html)
        self.assertNotIn("Tosca", html)
        self.assertNotIn("Giacomo Puccini", html)
        self.assertNotIn("shostakovich/sym5", html)
        self.assertNotIn("puccini_tosca", html)
        self.assertIn("const WORK_INDEX = []", html)

    def test_symphony_5_page_is_not_fed_brandenburg(self):
        cat = _catalogue()
        html = _html_for(_work(cat, "sym5"), cat)
        self.assertIn("Symphony No. 5", html)
        self.assertNotIn("Brandenburg Concertos", html)
        self.assertNotIn("Tosca", html)

    def test_work_page_has_no_global_related_feed(self):
        cat = _catalogue()
        html = _html_for(_work(cat, "brandenburg"), cat).lower()
        for phrase in FEED_PHRASES:
            self.assertNotIn(phrase, html, phrase)

    def test_entries_directory_does_not_dump_work_bodies(self):
        cat = _catalogue()
        tpl = (ROOT / "site/template.html").read_text(encoding="utf-8")
        index = [rnd.work_index_row(w) for w in cat["works"]]
        html = rnd.apply_template(
            tpl, rnd.directory_catalogue(cat), index, base="", title="Entries"
        )
        self.assertIn('"works": []', html)
        self.assertNotIn("Trevor Pinnock, harpsichord", html)
        self.assertNotIn("Andris Nelsons", html)
        self.assertIn('"anchor": "bach_brandenburg"', html)
        self.assertIn('"anchor": "shostakovich_sym5"', html)
        self.assertIn("works/${esc(w.anchor)}.html", html)


class TestGalleryAndReviewHaveNoGlobalRelated(unittest.TestCase):
    def test_gallery_builder_dropped_follow_the_thread(self):
        src = (ROOT / "site/build_gallery.py").read_text(encoding="utf-8")
        self.assertNotIn("Follow the thread", src)
        self.assertNotIn("o.engineering.producer===e.producer", src)
        low = src.lower()
        for phrase in ("you may also like", "trending", "related works"):
            self.assertNotIn(phrase, low)

    def test_review_board_has_no_cross_work_suggestion_rail(self):
        src = (ROOT / "site/build_review.py").read_text(encoding="utf-8")
        low = src.lower()
        for phrase in FEED_PHRASES:
            self.assertNotIn(phrase, low, phrase)
        # Remake siblings stay same-work; they are not a related-work feed.
        self.assertIn("Remake siblings (same forces, different year)", src)

    def test_live_seed_siblings_never_cross_composers(self):
        ib = _load("identity_board_under_test", "agents/identity_board.py")
        seed = json.loads((ROOT / "data/seed.json").read_text(encoding="utf-8"))
        by_id, all_cands, _ = _index_seed(seed)
        for cand in all_cands:
            composer = (cand.get("composer") or "").strip()
            if not composer:
                continue
            sibs = ib.remake_siblings(cand, all_cands, exclude_id=str(cand.get("id") or ""))
            for sib in sibs:
                other = by_id.get(sib["id"]) or {}
                other_composer = (other.get("composer") or "").strip()
                self.assertEqual(
                    other_composer, composer,
                    f"{cand.get('id')} sibling {sib['id']} crossed composers",
                )


def _index_seed(seed: dict) -> tuple[dict, list, None]:
    by_id: dict = {}
    all_cands: list = []
    for work in seed.get("works") or []:
        display = f"{work.get('composer')} — {work.get('title')}"
        for cand in work.get("candidates") or []:
            row = {
                "id": cand.get("id"),
                "work": display,
                "work_title": work.get("title") or "",
                "composer": work.get("composer") or "",
                "catalogue": work.get("catalogue") or "",
                "work_id": work.get("id") or "",
                "director": cand.get("director") or "",
                "ensemble": cand.get("ensemble") or "",
                "label": cand.get("label") or "",
                "year": cand.get("year"),
            }
            by_id[row["id"]] = row
            all_cands.append(row)
    return by_id, all_cands, None


if __name__ == "__main__":
    unittest.main()
