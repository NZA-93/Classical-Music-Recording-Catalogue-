"""Sealed work pages under a composer hub.

A: a work page is one work (composer + catalogue / work_id). Empty related
is correct. A Brandenburg page must not be fed Symphony No. 5, Tosca, or any
other composer's work via loose tokens or popularity.

B: the composer hub lists that composer's works and links into the sealed
pages. Navigation is catalogue → composer hub → sealed work page.

D (parent): no global related / recommended / trending feed. The review
board must not grow a cross-work suggestion rail.

C: On this disc couplings are attached to the recording from shared barcode
or release MBID, and render on the recording card only. Title tokens must
not couple Brandenburg to Symphony No. 5 or Tosca.
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
site = _load("build_site", "site/build_site.py")
disc = _load("disc_couplings", "site/disc.py")


FEED_PHRASES = (
    "you may also like",
    "recommended for you",
    "trending",
    "related works",
    "follow the thread",
    "popular now",
)

FOREIGN_ON_BRANDENBURG = (
    "symphony no. 5",
    "dmitri shostakovich",
    "tosca",
    "giacomo puccini",
    "shostakovich/sym5",
    "puccini_tosca",
)


def _catalogue() -> dict:
    return json.loads((ROOT / "build/catalogue.json").read_text(encoding="utf-8"))


def _work(cat: dict, fragment: str) -> dict:
    for work in cat["works"]:
        if fragment in work["id"] or fragment in (work.get("title") or ""):
            return work
    raise AssertionError(f"no work matching {fragment!r}")


def _html_for(work: dict, cat: dict) -> str:
    cat = disc.attach_on_this_disc(cat)
    work = next(w for w in cat["works"] if w["id"] == work["id"])
    tpl = (ROOT / "site/template.html").read_text(encoding="utf-8")
    title = f"{work['title']} — {work['composer']}"
    return rnd.apply_template(
        tpl,
        rnd.seal_catalogue(cat, work),
        [],
        base="../",
        title=title,
        crumb=rnd.work_crumb(work, base="../"),
    )


class TestWorkHrefs(unittest.TestCase):
    def test_anchors(self):
        self.assertEqual(href.work_anchor("bach_brandenburg"), "bach_brandenburg")
        self.assertEqual(href.work_anchor("shostakovich/sym5"), "shostakovich_sym5")
        self.assertEqual(href.work_anchor("puccini_tosca"), "puccini_tosca")

    def test_composer_id_from_work_id_not_from_title(self):
        self.assertEqual(href.composer_id_of("bach_brandenburg"), "bach")
        self.assertEqual(href.composer_id_of("bach/brandenburg"), "bach")
        self.assertEqual(href.composer_id_of("shostakovich/sym5"), "shostakovich")
        self.assertEqual(href.composer_id_of("puccini_tosca"), "puccini")

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
        self.assertEqual(
            href.composer_page_href("bach", depth=1),
            "../composers/bach.html",
        )


class TestSealCatalogue(unittest.TestCase):
    def test_one_work_only_and_barcodes_do_not_leak(self):
        cat = _catalogue()
        bach = _work(cat, "brandenburg")
        sealed = rnd.seal_catalogue(cat, bach)
        self.assertEqual([w["id"] for w in sealed["works"]], [bach["id"]])
        self.assertEqual(sealed["works"][0]["composer_id"], "bach")
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
        low = html.lower()
        for phrase in FOREIGN_ON_BRANDENBURG:
            self.assertNotIn(phrase, low, phrase)
        self.assertIn("const WORK_INDEX = []", html)
        self.assertIn("composers/bach.html", html)
        self.assertIn("Catalogue", html)

    def test_symphony_5_page_is_not_fed_brandenburg(self):
        cat = _catalogue()
        html = _html_for(_work(cat, "sym5"), cat)
        self.assertIn("Symphony No. 5", html)
        self.assertNotIn("Brandenburg Concertos", html)
        self.assertNotIn("Tosca", html)
        self.assertIn("composers/shostakovich.html", html)

    def test_work_page_has_no_global_related_feed(self):
        cat = _catalogue()
        html = _html_for(_work(cat, "brandenburg"), cat).lower()
        for phrase in FEED_PHRASES:
            self.assertNotIn(phrase, html, phrase)

    def test_work_page_find_hint_does_not_name_another_work(self):
        cat = _catalogue()
        html = _html_for(_work(cat, "brandenburg"), cat)
        self.assertIn("Find on this page", html)
        self.assertNotIn("try pinnock, tosca", html.lower())

    def test_entries_directory_does_not_dump_work_bodies(self):
        cat = _catalogue()
        tpl = (ROOT / "site/template.html").read_text(encoding="utf-8")
        index = [rnd.work_index_row(w) for w in cat["works"]]
        html = rnd.apply_template(
            tpl,
            rnd.directory_catalogue(cat),
            index,
            base="",
            title="Entries",
            find_placeholder="Composer, work or recording",
            entries_current=True,
        )
        self.assertIn('"works": []', html)
        self.assertNotIn("Trevor Pinnock, harpsichord", html)
        self.assertNotIn("Andris Nelsons", html)
        self.assertIn('"anchor": "bach_brandenburg"', html)
        self.assertIn('"anchor": "shostakovich_sym5"', html)
        self.assertIn("works/${esc(w.anchor)}.html", html)
        self.assertIn("composer_id", html)


class TestComposerHub(unittest.TestCase):
    def test_bach_hub_index_is_composer_strict(self):
        idx = site.build_index(depth=1, composer_id="bach")
        labels = {item["label"] for item in idx}
        self.assertIn("Johann Sebastian Bach", labels)
        self.assertIn("Brandenburg Concertos", labels)
        self.assertNotIn("Tosca", labels)
        self.assertNotIn("Symphony No. 5", labels)
        self.assertNotIn("Dmitri Shostakovich", labels)
        self.assertNotIn("Giacomo Puccini", labels)
        blob = json.dumps(idx).lower()
        self.assertNotIn("shostakovich", blob)
        self.assertNotIn("puccini", blob)
        self.assertNotIn("tosca", blob)
        hrefs = " ".join(item["href"] for item in idx)
        self.assertIn("bach_brandenburg.html", hrefs)
        self.assertNotIn("shostakovich_sym5", hrefs)

    def test_catalogue_index_still_lists_composers(self):
        idx = site.build_index(depth=0)
        kinds = {item["kind"] for item in idx}
        self.assertIn("composer", kinds)
        hrefs = {item["href"] for item in idx if item["kind"] == "composer"}
        self.assertIn("composers/bach.html", hrefs)
        self.assertIn("composers/shostakovich.html", hrefs)

    def test_bach_hub_html_lists_works_and_links_sealed_page(self):
        cid, name, dates, works = site.composer_by_id("bach")
        html = site.composer_hub(cid, name, dates, works)
        self.assertIn("Brandenburg Concertos", html)
        self.assertIn("../works/bach_brandenburg.html", html)
        self.assertIn("open work", html)
        self.assertIn('href="../index.html"', html)
        low = html.lower()
        self.assertNotIn("dmitri shostakovich", low)
        self.assertNotIn("tosca", low)
        self.assertNotIn("symphony no. 5", low)
        self.assertNotIn("giacomo puccini", low)
        # Hub find is this composer only — no global token dump.
        self.assertIn('const SCOPE = "composer"', html)

    def test_bach_hub_does_not_list_foreign_works_in_the_table(self):
        cid, name, dates, works = site.composer_by_id("bach")
        titles = {w["title"] for w in works}
        self.assertIn("Brandenburg Concertos", titles)
        self.assertNotIn("Symphony No. 5", titles)
        self.assertNotIn("Tosca", titles)


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
        # Remake siblings stay same-composer; they are not a related-work feed.
        self.assertIn("Remake siblings (same composer, same forces, different year)", src)

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


def _rec(rid: str, *, mbid=None, barcode=None, extra=None) -> dict:
    rec = {
        "id": rid,
        "soloists": "",
        "director": "D",
        "ensemble": "E",
        "published": "Label, 1980",
        "interpretation": None,
        "confidence": None,
        "stars": None,
        "reference": False,
        "sound_best": None,
        "editorial": None,
        "divergence": None,
        "engineering": {
            "venue": "x",
            "sessions": "1980",
            "producer": None,
            "engineer": None,
            "status": "unknown",
        },
        "anchors": [],
        "reception": [],
        "editions": [
            {
                "id": f"{rid}_ed",
                "label": "Label",
                "catno": "1",
                "year": "1980",
                "format": "CD",
                "transfer": "original",
                "barcode": barcode,
                "mbid": mbid,
                "verified": False,
                "sound": None,
                "verdict": "not yet assessed",
            }
        ],
        "sources": [],
    }
    if extra:
        rec.update(extra)
    return rec


def _work_row(wid: str, title: str, composer: str, rec: dict) -> dict:
    return {
        "id": wid,
        "composer": composer,
        "dates": "",
        "title": title,
        "cat": "",
        "standfirst": "",
        "recordings": [rec],
    }


def _fixture_catalogue() -> dict:
    """Shared MBID couples Bach Brandenburg + Suites. Sym5 / Tosca share none."""
    return {
        "algorithm_version": "2.0",
        "built": "2026-08-22",
        "barcode_index": {},
        "works": [
            _work_row(
                "bach_brandenburg",
                "Brandenburg Concertos",
                "Johann Sebastian Bach",
                _rec("bach_brandenburg_pinnock", mbid="shared-release-mbid"),
            ),
            _work_row(
                "bach/suites",
                "Orchestral Suites",
                "Johann Sebastian Bach",
                _rec("bach_suites_pinnock", mbid="shared-release-mbid"),
            ),
            _work_row(
                "shostakovich/sym5",
                "Symphony No. 5",
                "Dmitri Shostakovich",
                _rec("shostakovich_sym5_nelsons", mbid="other-mbid", barcode="028947952017"),
            ),
            _work_row(
                "puccini_tosca",
                "Tosca",
                "Giacomo Puccini",
                _rec("puccini_tosca_desabata", barcode="5099924322423"),
            ),
        ],
    }


class TestOnThisDiscCardOnly(unittest.TestCase):
    def test_shared_mbid_couples_same_disc_not_foreign_works(self):
        attached = disc.attach_on_this_disc(_fixture_catalogue())
        by_id = {w["id"]: w for w in attached["works"]}
        bach = by_id["bach_brandenburg"]["recordings"][0]["on_this_disc"]
        titles = {row["title"] for row in bach}
        self.assertEqual(titles, {"Orchestral Suites"})
        self.assertEqual(bach[0]["composer_id"], "bach")
        self.assertEqual(bach[0]["via"], "mbid")
        self.assertNotIn("Symphony No. 5", titles)
        self.assertNotIn("Tosca", titles)
        for foreign in ("shostakovich/sym5", "puccini_tosca"):
            self.assertEqual(by_id[foreign]["recordings"][0]["on_this_disc"], [])

    def test_title_tokens_do_not_couple_brandenburg_to_sym5(self):
        cat = {
            "works": [
                _work_row(
                    "bach_brandenburg",
                    "Brandenburg Concertos No. 5",
                    "Johann Sebastian Bach",
                    _rec("bach_brandenburg_pinnock"),
                ),
                _work_row(
                    "shostakovich/sym5",
                    "Symphony No. 5",
                    "Dmitri Shostakovich",
                    _rec("shostakovich_sym5_nelsons"),
                ),
                _work_row(
                    "puccini_tosca",
                    "Tosca",
                    "Giacomo Puccini",
                    _rec("puccini_tosca_desabata"),
                ),
            ]
        }
        attached = disc.attach_on_this_disc(cat)
        for work in attached["works"]:
            self.assertEqual(work["recordings"][0]["on_this_disc"], [], work["id"])

    def test_shared_barcode_is_enough_without_title_overlap(self):
        cat = {
            "works": [
                _work_row(
                    "shostakovich/sym5",
                    "Symphony No. 5",
                    "Dmitri Shostakovich",
                    _rec("sym5", barcode="0822231180227"),
                ),
                _work_row(
                    "shostakovich/sym1",
                    "Symphony No. 1",
                    "Dmitri Shostakovich",
                    _rec("sym1", barcode="0822231180227"),
                ),
            ]
        }
        attached = disc.attach_on_this_disc(cat)
        disc5 = attached["works"][0]["recordings"][0]["on_this_disc"]
        self.assertEqual([row["title"] for row in disc5], ["Symphony No. 1"])
        self.assertEqual(disc5[0]["via"], "barcode")

    def test_on_this_disc_survives_seal_without_importing_the_other_work(self):
        attached = disc.attach_on_this_disc(_fixture_catalogue())
        bach = next(w for w in attached["works"] if w["id"] == "bach_brandenburg")
        sealed = rnd.seal_catalogue(attached, bach)
        self.assertEqual([w["id"] for w in sealed["works"]], ["bach_brandenburg"])
        coupled = sealed["works"][0]["recordings"][0]["on_this_disc"]
        self.assertEqual([row["title"] for row in coupled], ["Orchestral Suites"])
        titles = {w["title"] for w in sealed["works"]}
        self.assertNotIn("Symphony No. 5", titles)
        self.assertNotIn("Tosca", titles)
        blob = json.dumps(sealed).lower()
        self.assertNotIn("dmitri shostakovich", blob)
        self.assertNotIn("giacomo puccini", blob)

    def test_template_renders_couplings_inside_entry_only(self):
        tpl = (ROOT / "site/template.html").read_text(encoding="utf-8")
        self.assertIn("function onThisDisc(r)", tpl)
        self.assertIn("${onThisDisc(r)}", tpl)
        start = tpl.index("function entry(r)")
        work = tpl.index("function workSection(w)")
        directory = tpl.index("function renderWorkDirectory")
        self.assertLess(start, work)
        self.assertIn("${onThisDisc(r)}", tpl[start:work])
        self.assertNotIn("onThisDisc", tpl[work:directory])
        low = tpl.lower()
        for phrase in FEED_PHRASES:
            self.assertNotIn(phrase, low, phrase)
        self.assertNotIn("you may also like", low)

    def test_brandenburg_card_html_keeps_foreign_works_off_the_page(self):
        attached = disc.attach_on_this_disc(_fixture_catalogue())
        bach = next(w for w in attached["works"] if w["id"] == "bach_brandenburg")
        html = _html_for(bach, attached).lower()
        self.assertIn("on this disc", html)
        self.assertIn("orchestral suites", html)
        self.assertIn('class="on-disc"', html)
        for phrase in FOREIGN_ON_BRANDENBURG:
            self.assertNotIn(phrase, html, phrase)
        self.assertNotIn("related works", html)
        self.assertNotIn("you may also like", html)

    def test_live_brandenburg_page_has_card_hook_and_no_foreign_feed(self):
        cat = disc.attach_on_this_disc(_catalogue())
        bach = _work(cat, "brandenburg")
        html = _html_for(bach, cat)
        low = html.lower()
        self.assertIn("function onthisdisc(r)", low)
        self.assertIn("${onthisdisc(r)}", low)
        for phrase in FOREIGN_ON_BRANDENBURG:
            self.assertNotIn(phrase, low, phrase)
        for phrase in FEED_PHRASES:
            self.assertNotIn(phrase, low, phrase)
        sealed = rnd.seal_catalogue(cat, bach)
        for rec in sealed["works"][0]["recordings"]:
            for row in rec.get("on_this_disc") or []:
                self.assertEqual(row.get("composer_id"), "bach")
                self.assertNotIn("symphony no. 5", (row.get("title") or "").lower())
                self.assertNotIn("tosca", (row.get("title") or "").lower())


if __name__ == "__main__":
    unittest.main()
