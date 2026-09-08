"""Identity-only public pages from seed.works[].assessed (signed Bach).

Public cards are the critic-signed assessed IDs, not the harvest queue and
not engine scores. goldberg/3 (Perahia) stays a candidate and must not
appear. goldberg/4 (Schiff, Decca 1982) is assessed. Brandenburg assessed
cut is /0 Pinnock 1982, /1 Harnoncourt 1964, /4 Richter 1967, now with
Critic-signed Dictionnaire prose and Morningstar matrix. Gardiner /5 stays
off the public cards. Held Bach works stay off this slice.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Public identity cards in seed-work order (Brandenburg cut, then Goldberg
# /0 /1 /4, then the remaining ten).
SIGNED_IDENTITY_IDS = (
    "bach/violin_concertos/4",
    "bach/cello_suites/1",
    "bach/sonatas_partitas/0",
    "bach/sonatas_partitas/1",
    "bach/goldberg/0",
    "bach/goldberg/1",
    "bach/goldberg/4",
    "bach/mass_b_minor/0",
    "bach/matthew/0",
    "bach/matthew/1",
    "bach/john/1",
    "bach/art_of_fugue/0",
    "bach/art_of_fugue/3",
)

BRANDENBURG_ASSESSED = (
    "bach/brandenburg/0",
    "bach/brandenburg/1",
    "bach/brandenburg/4",
)

PUBLIC_IDENTITY_IDS = BRANDENBURG_ASSESSED + SIGNED_IDENTITY_IDS

REMAINING_TEN = (
    "bach/cello_suites/1",
    "bach/violin_concertos/4",
    "bach/sonatas_partitas/0",
    "bach/sonatas_partitas/1",
    "bach/matthew/0",
    "bach/matthew/1",
    "bach/john/1",
    "bach/mass_b_minor/0",
    "bach/art_of_fugue/0",
    "bach/art_of_fugue/3",
)

IDENTITY_WORKS = (
    "bach/brandenburg",
    "bach/violin_concertos",
    "bach/cello_suites",
    "bach/sonatas_partitas",
    "bach/goldberg",
    "bach/mass_b_minor",
    "bach/matthew",
    "bach/john",
    "bach/art_of_fugue",
)

SIGNED_GOLDBERG = (
    "bach/goldberg/0",
    "bach/goldberg/1",
    "bach/goldberg/4",
)


def _assert_no_aggregate(test, rec, rid=""):
    """Identity cards may carry a Critic entry; they may not carry engine scores."""
    test.assertEqual(rec.get("card"), "identity", rid)
    test.assertNotIn("stars", rec, rid)
    test.assertNotIn("interpretation", rec, rid)
    test.assertNotIn("reference", rec, rid)
    test.assertNotIn("confidence", rec, rid)
    test.assertEqual(rec.get("sources"), [], rid)

HELD_EMPTY = (
    "bach/suites",
    "bach/wtc",
    "bach/harpsichord_concertos",
)

QUEUE_NAMES_GOLDBERG = ("Perahia", "Landowska")

# Performer/label strings that live only on unassessed candidates of enabled
# works. Must not leak onto sealed identity pages or the hub assessed list.
# Harnoncourt and Richter belong on the Brandenburg assessed cut; they are
# still forbidden on every other first-slice page.
QUEUE_ONLY = (
    "Perahia",
    "Landowska",
    "Pablo Casals",
    "Anner Bylsma",
    "Yo-Yo Ma",
    "Mstislav Rostropovich",
    "Itzhak Perlman",
    "Gidon Kremer",
    "Yehudi Menuhin",
    "Henryk Szeryng",
    "Arthur Grumiaux",
    "Wilhelm Furtwängler",
    "Tatiana Nikolayeva",
    "Davitt Moroney",
    "Gustav Leonhardt",
    "Philippe Herreweghe",
    "Angela Hewitt",
)

BRANDENBURG_HOLD = (
    "Claudio Abbado",
    "Benjamin Britten",
    "John Eliot Gardiner",
    "Orchestra Mozart",
    "English Chamber Orchestra",
    "English Baroque Soloists",
    "Avie",
)

BRANDENBURG_ONLY = (
    "Karl Richter",
    "Nikolaus Harnoncourt",
)


def _load(name: str, relpath: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


href = _load("work_href_identity", "site/work_href.py")
ident = _load("identity_pages", "site/identity.py")
rnd = _load("render_identity", "site/render.py")
site = _load("build_site_identity", "site/build_site.py")
disc = _load("disc_identity", "site/disc.py")
scout = _load("scout_identity", "site/scout.py")


def _seed() -> dict:
    return json.loads((ROOT / "data/seed.json").read_text(encoding="utf-8"))


def _engine_cat() -> dict:
    return json.loads((ROOT / "build/catalogue.json").read_text(encoding="utf-8"))


def _work(seed: dict, wid: str) -> dict:
    for work in seed["works"]:
        if work["id"] == wid:
            return work
    raise AssertionError(f"{wid} missing from seed")


def _hub_row(html: str, anchor: str) -> str:
    match = re.search(rf'<tr id="{re.escape(anchor)}">.*?</tr>', html, re.S)
    if not match:
        raise AssertionError(f"{anchor} row missing from hub")
    return match.group(0)


def _html_for(work: dict, cat: dict) -> str:
    cat = scout.attach_scout_pools(disc.attach_on_this_disc(cat))
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


def _embedded_catalogue(html: str) -> dict:
    start = html.index("const CATALOGUE = ") + len("const CATALOGUE = ")
    end = html.index(";\nconst WORK_INDEX", start)
    return json.loads(html[start:end])


def _merged() -> dict:
    return ident.merge_identity_works(_engine_cat(), _seed())


def _page(wid: str) -> str:
    merged = _merged()
    work = next(w for w in merged["works"] if w["id"] == wid)
    return _html_for(work, merged)


class TestSeedAssessedUnchanged(unittest.TestCase):
    def test_goldberg_assessed_is_exactly_zero_one_and_four(self):
        work = _work(_seed(), "bach/goldberg")
        self.assertEqual(
            work["assessed"],
            ["bach/goldberg/0", "bach/goldberg/1", "bach/goldberg/4"],
        )
        ids = [c["id"] for c in work["candidates"]]
        self.assertIn("bach/goldberg/3", ids)
        self.assertIn("bach/goldberg/4", ids)
        self.assertNotIn("bach/goldberg/3", work["assessed"])
        four = next(c for c in work["candidates"] if c["id"] == "bach/goldberg/4")
        self.assertEqual(four["soloists"], "András Schiff")
        self.assertEqual(four["label"], "Decca")
        self.assertEqual(four["year"], "1982")
        three = next(c for c in work["candidates"] if c["id"] == "bach/goldberg/3")
        self.assertEqual(three["soloists"], "Murray Perahia")

    def test_remaining_ten_are_already_the_seed_assessed_set(self):
        seed = _seed()
        got = []
        skip = {"bach/goldberg", "bach/brandenburg"}
        for work in seed["works"]:
            if not str(work["id"]).startswith("bach/"):
                continue
            if work["id"] in skip:
                continue
            got.extend(work.get("assessed") or [])
        self.assertEqual(set(got), set(REMAINING_TEN))
        self.assertEqual(len(got), len(REMAINING_TEN))

    def test_brandenburg_assessed_is_exactly_zero_one_and_four(self):
        brand = _work(_seed(), "bach/brandenburg")
        self.assertEqual(list(brand["assessed"]), list(BRANDENBURG_ASSESSED))
        by_id = {c["id"]: c for c in brand["candidates"]}
        self.assertEqual(by_id["bach/brandenburg/0"]["year"], "1982")
        self.assertEqual(by_id["bach/brandenburg/0"]["director"], "Trevor Pinnock")
        self.assertEqual(by_id["bach/brandenburg/1"]["year"], "1964")
        self.assertEqual(by_id["bach/brandenburg/1"]["director"], "Nikolaus Harnoncourt")
        self.assertEqual(by_id["bach/brandenburg/4"]["year"], "1967")
        self.assertEqual(by_id["bach/brandenburg/4"]["director"], "Karl Richter")
        self.assertEqual(by_id["bach/brandenburg/5"]["year"], "1990s")
        self.assertNotIn("bach/brandenburg/2", brand["assessed"])
        self.assertNotIn("bach/brandenburg/3", brand["assessed"])
        self.assertNotIn("bach/brandenburg/5", brand["assessed"])

    def test_held_stay_empty_assessed(self):
        seed = _seed()
        for wid in HELD_EMPTY:
            self.assertEqual(_work(seed, wid)["assessed"], [], wid)


class TestIdentityFromAssessed(unittest.TestCase):
    def test_public_cards_are_signed_ids_only(self):
        works = ident.public_identity_works(_seed())
        self.assertEqual([w["id"] for w in works], list(IDENTITY_WORKS))
        recs = [r for w in works for r in w["recordings"]]
        self.assertEqual([r["id"] for r in recs], list(PUBLIC_IDENTITY_IDS))
        blob = json.dumps(works)
        self.assertNotIn("bach/goldberg/3", blob)
        self.assertNotIn("Perahia", blob)
        self.assertIn("bach/goldberg/4", blob)
        self.assertIn("Schiff", blob)
        self.assertNotIn("bach/brandenburg/2", blob)
        self.assertNotIn("bach/brandenburg/3", blob)
        self.assertNotIn("bach/brandenburg/5", blob)
        self.assertNotIn("Abbado", blob)
        self.assertNotIn("Britten", blob)
        for rec in recs:
            _assert_no_aggregate(self, rec, rec["id"])
            self.assertIsNotNone(rec["editorial"], rec["id"])
            self.assertEqual(rec["editorial"]["author"]["id"], "cmrc")

    def test_goldberg_facts_stay_goulds_and_schiff_1982(self):
        gold = next(
            w for w in ident.public_identity_works(_seed()) if w["id"] == "bach/goldberg"
        )
        recs = gold["recordings"]
        self.assertEqual(
            [r["id"] for r in recs],
            ["bach/goldberg/0", "bach/goldberg/1", "bach/goldberg/4"],
        )
        self.assertEqual(recs[0]["soloists"], "Glenn Gould")
        self.assertEqual(recs[0]["published"], "Columbia, 1955")
        self.assertEqual(recs[1]["soloists"], "Glenn Gould")
        self.assertEqual(recs[1]["published"], "CBS, 1981")
        self.assertEqual(recs[2]["soloists"], "András Schiff")
        self.assertEqual(recs[2]["published"], "Decca, 1982")

    def test_remaining_ten_carry_seed_identity_facts(self):
        recs = {
            r["id"]: r
            for w in ident.public_identity_works(_seed())
            for r in w["recordings"]
        }
        self.assertEqual(recs["bach/cello_suites/1"]["soloists"], "Pierre Fournier")
        self.assertEqual(recs["bach/cello_suites/1"]["published"], "Archiv, 1961")
        self.assertEqual(recs["bach/violin_concertos/4"]["soloists"], "Rachel Podger")
        self.assertEqual(recs["bach/violin_concertos/4"]["published"], "Channel Classics, 2009")
        self.assertEqual(recs["bach/sonatas_partitas/0"]["soloists"], "Nathan Milstein")
        self.assertEqual(recs["bach/sonatas_partitas/0"]["published"], "Deutsche Grammophon, 1973")
        self.assertEqual(recs["bach/sonatas_partitas/1"]["soloists"], "Rachel Podger")
        self.assertEqual(recs["bach/sonatas_partitas/1"]["published"], "Channel Classics, 1999")
        self.assertEqual(recs["bach/matthew/0"]["director"], "Otto Klemperer")
        self.assertEqual(recs["bach/matthew/0"]["published"], "EMI, 1961")
        self.assertEqual(recs["bach/matthew/1"]["director"], "John Eliot Gardiner")
        self.assertEqual(recs["bach/matthew/1"]["published"], "Archiv, 1988")
        self.assertEqual(recs["bach/john/1"]["director"], "John Eliot Gardiner")
        self.assertEqual(recs["bach/john/1"]["published"], "Archiv, 1986")
        self.assertEqual(recs["bach/mass_b_minor/0"]["director"], "John Eliot Gardiner")
        self.assertEqual(recs["bach/mass_b_minor/0"]["published"], "Archiv, 1985")
        self.assertEqual(recs["bach/art_of_fugue/0"]["soloists"], "Glenn Gould")
        self.assertEqual(recs["bach/art_of_fugue/0"]["published"], "CBS, 1962")
        self.assertEqual(recs["bach/art_of_fugue/3"]["soloists"], "Emerson String Quartet")
        self.assertEqual(recs["bach/art_of_fugue/3"]["published"], "Deutsche Grammophon, 2003")

    def test_held_works_are_not_in_this_slice(self):
        ids = {w["id"] for w in ident.public_identity_works(_seed())}
        for wid in HELD_EMPTY:
            self.assertNotIn(wid, ids, wid)
        self.assertIn("bach/brandenburg", ids)

    def test_merge_replaces_engine_brandenburg_keeps_tosca(self):
        merged = _merged()
        ids = [w["id"] for w in merged["works"]]
        self.assertIn("bach/brandenburg", ids)
        self.assertNotIn("bach_brandenburg", ids)
        self.assertIn("puccini_tosca", ids)
        self.assertIn("shostakovich/sym5", ids)
        for wid in IDENTITY_WORKS:
            self.assertIn(wid, ids, wid)
            self.assertEqual(ids.count(wid), 1, wid)
        for wid in HELD_EMPTY:
            self.assertNotIn(wid, ids, wid)
        brand = next(w for w in merged["works"] if "brandenburg" in w["id"])
        rec_ids = [r["id"] for r in brand["recordings"]]
        self.assertEqual(rec_ids, list(BRANDENBURG_ASSESSED))
        for rec in brand["recordings"]:
            _assert_no_aggregate(self, rec, rec["id"])
            self.assertIsNotNone(rec.get("editorial"), rec["id"])
            self.assertEqual(rec["editorial"]["author"]["id"], "cmrc")
        engine = _engine_cat()
        eng_brand = next(w for w in engine["works"] if w["id"] == "bach_brandenburg")
        self.assertAlmostEqual(
            next(r["interpretation"] for r in eng_brand["recordings"] if r["id"].endswith("pinnock")),
            2.853,
            places=3,
        )
        self.assertAlmostEqual(
            next(r["interpretation"] for r in eng_brand["recordings"] if r["id"].endswith("harnoncourt")),
            2.814,
            places=3,
        )

    def test_anchors_use_underscore_work_files(self):
        self.assertEqual(href.work_anchor("bach/goldberg"), "bach_goldberg")
        self.assertEqual(
            href.work_page_href("bach/cello_suites"),
            "works/bach_cello_suites.html",
        )
        self.assertEqual(
            href.work_page_href("bach/art_of_fugue"),
            "works/bach_art_of_fugue.html",
        )


class TestGoldbergPublicHtml(unittest.TestCase):
    def test_page_is_built_from_assessed_not_the_queue(self):
        html = _page("bach/goldberg")
        self.assertIn("Goldberg Variations", html)
        self.assertIn("Glenn Gould", html)
        self.assertIn("Columbia, 1955", html)
        self.assertIn("CBS, 1981", html)
        self.assertIn("András Schiff", html)
        self.assertIn("Decca, 1982", html)
        self.assertIn("bach/goldberg/0", html)
        self.assertIn("bach/goldberg/1", html)
        self.assertIn("bach/goldberg/4", html)
        self.assertNotIn("bach/goldberg/3", html)
        self.assertNotIn("bach/goldberg/2", html)
        for name in QUEUE_NAMES_GOLDBERG:
            self.assertNotIn(name, html, name)
        cat = _embedded_catalogue(html)
        self.assertEqual([w["id"] for w in cat["works"]], ["bach/goldberg"])
        rec_ids = [r["id"] for r in cat["works"][0]["recordings"]]
        self.assertEqual(rec_ids, ["bach/goldberg/0", "bach/goldberg/1", "bach/goldberg/4"])

    def test_candidate_queue_is_not_dumped(self):
        html = _page("bach/goldberg")
        cat = _embedded_catalogue(html)
        recs = cat["works"][0]["recordings"]
        self.assertEqual(len(recs), 3)
        blob = json.dumps(cat)
        self.assertNotIn('"candidates"', blob)
        self.assertNotIn("queued", html.lower())
        self.assertNotIn("Sony SK 89243", html)

    def test_identity_cards_have_no_stars_reference_or_statements(self):
        html = _page("bach/goldberg")
        cat = _embedded_catalogue(html)
        for rec in cat["works"][0]["recordings"]:
            _assert_no_aggregate(self, rec, rec["id"])
            self.assertIsNotNone(rec.get("editorial"), rec["id"])
        start = html.index("function identityLine(r)")
        scored = html.index("function entry(r)")
        identity_fn = html[start:scored]
        self.assertNotIn("scorebox", identity_fn)
        self.assertIn("signed(", identity_fn)
        self.assertNotIn("Référence", identity_fn)
        self.assertNotIn("★", identity_fn)
        work_fn = html[html.index("function workSection(w)"):html.index("function renderWorkDirectory")]
        self.assertIn("identityLine", work_fn)
        sealed = rnd.seal_catalogue(
            _merged(),
            next(w for w in _merged()["works"] if w["id"] == "bach/goldberg"),
        )
        for rec in sealed["works"][0]["recordings"]:
            _assert_no_aggregate(self, rec, rec["id"])
            self.assertIsNotNone(rec.get("editorial"), rec["id"])

    def test_goldberg_signed_entries_are_on_the_cards(self):
        html = _page("bach/goldberg")
        cat = _embedded_catalogue(html)
        recs = {r["id"]: r for r in cat["works"][0]["recordings"]}
        zero = recs["bach/goldberg/0"]["editorial"]
        one = recs["bach/goldberg/1"]["editorial"]
        four = recs["bach/goldberg/4"]["editorial"]
        self.assertEqual(zero["stars"], 3)
        self.assertTrue(zero["reference"])
        self.assertIn("The 1955 Goldberg is still the shock", zero["text"])
        self.assertEqual(zero["quotes"], [])
        self.assertEqual(one["stars"], 3)
        self.assertFalse(one["reference"])
        self.assertIn("Gould’s 1981 remake is a late architecture", one["text"])
        self.assertEqual(four["stars"], 2)
        self.assertFalse(four["reference"])
        self.assertIn("Schiff’s first studio Goldberg", four["text"])
        self.assertNotIn("bach/goldberg/3", html)
        self.assertNotIn("Perahia", html)
        self.assertIn("function signed(r)", html)
        self.assertIn("Number.isFinite(r.divergence)", html)
        for rec in recs.values():
            self.assertIsNone(rec.get("divergence"), rec["id"])

    def test_sealed_no_global_related_feed(self):
        html = _page("bach/goldberg")
        self.assertIn("const WORK_INDEX = []", html)
        self.assertIn("composers/bach.html", html)
        low = html.lower()
        for phrase in (
            "you may also like",
            "recommended for you",
            "trending",
            "related works",
        ):
            self.assertNotIn(phrase, low, phrase)


class TestRemainingSignedPages(unittest.TestCase):
    def test_each_of_the_ten_ids_is_an_identity_card(self):
        for rid in REMAINING_TEN:
            wid = "/".join(rid.split("/")[:2])
            html = _page(wid)
            cat = _embedded_catalogue(html)
            self.assertEqual([w["id"] for w in cat["works"]], [wid], rid)
            recs = cat["works"][0]["recordings"]
            ids = [r["id"] for r in recs]
            self.assertIn(rid, ids, rid)
            rec = next(r for r in recs if r["id"] == rid)
            _assert_no_aggregate(self, rec, rid)
            self.assertIsNotNone(rec.get("editorial"), rid)
            self.assertEqual(rec["editorial"]["author"]["id"], "cmrc")
            self.assertEqual(rec["editorial"]["quotes"], [])
            self.assertIn(rid, html)
            blob = json.dumps(cat)
            self.assertNotIn("bach/goldberg/3", blob)
            self.assertNotIn('"candidates"', blob)
            self.assertNotIn("queued", html.lower())
            if wid != "bach/goldberg":
                self.assertNotIn("bach/goldberg/4", blob)

    def test_goldberg_three_absent_four_only_on_goldberg_page(self):
        for wid in IDENTITY_WORKS:
            html = _page(wid)
            self.assertNotIn("bach/goldberg/3", html, wid)
            self.assertNotIn("Perahia", html, wid)
            cat = _embedded_catalogue(html)
            rec_ids = [r["id"] for w in cat["works"] for r in w["recordings"]]
            if wid == "bach/goldberg":
                self.assertIn("bach/goldberg/4", rec_ids)
                self.assertIn("Schiff", html)
            else:
                self.assertNotIn("bach/goldberg/4", html, wid)
                self.assertNotIn("Schiff", html, wid)
            for rec_id in rec_ids:
                rec = next(
                    r for w in cat["works"] for r in w["recordings"] if r["id"] == rec_id
                )
                _assert_no_aggregate(self, rec, rec_id)

    def test_queues_are_not_dumped_on_enabled_pages(self):
        for wid in IDENTITY_WORKS:
            html = _page(wid)
            for name in QUEUE_ONLY:
                self.assertNotIn(name, html, f"{wid} leaked {name}")
            self.assertNotIn('"candidates"', json.dumps(_embedded_catalogue(html)))
            if wid == "bach/brandenburg":
                cat = _embedded_catalogue(html)
                rec_blob = json.dumps(cat["works"][0]["recordings"])
                for name in BRANDENBURG_HOLD:
                    if name == "Avie":
                        continue
                    self.assertNotIn(
                        name, rec_blob, f"{wid} card leaked hold {name}",
                    )
                for rec in cat["works"][0]["recordings"]:
                    self.assertNotIn("Avie", rec.get("published") or "", rec["id"])
                self.assertNotIn("scout", rec_blob)
            else:
                for name in BRANDENBURG_ONLY:
                    self.assertNotIn(name, html, f"{wid} leaked {name}")

    def test_pages_are_one_work_sealed(self):
        html = _page("bach/cello_suites")
        cat = _embedded_catalogue(html)
        self.assertEqual([w["id"] for w in cat["works"]], ["bach/cello_suites"])
        self.assertEqual(
            [r["id"] for r in cat["works"][0]["recordings"]],
            ["bach/cello_suites/1"],
        )
        self.assertIn("Pierre Fournier", html)
        self.assertIn("Archiv, 1961", html)
        self.assertIn("const WORK_INDEX = []", html)

    def test_remaining_signed_entries_are_on_the_cards(self):
        expected = {
            "bach/cello_suites/1": (3, True, "Fournier’s Archiv studio cycle"),
            "bach/violin_concertos/4": (3, True, "Podger and Brecon Baroque"),
            "bach/sonatas_partitas/0": (3, False, "Milstein’s stereo remake"),
            "bach/sonatas_partitas/1": (3, True, "Podger’s complete gut-strung cycle"),
            "bach/matthew/0": (3, False, "Klemperer’s Philharmonia Matthew Passion"),
            "bach/matthew/1": (3, True, "Gardiner’s 1988 Archiv Matthew Passion"),
            "bach/john/1": (3, True, "Gardiner’s first St John Passion"),
            "bach/mass_b_minor/0": (3, True, "Gardiner’s first B-minor Mass"),
            "bach/art_of_fugue/0": (2, False, "Gould’s only commercial organ recording"),
            "bach/art_of_fugue/3": (3, True, "The Emersons play the Art of Fugue"),
        }
        for rid, (stars, reference, snippet) in expected.items():
            wid = "/".join(rid.split("/")[:2])
            html = _page(wid)
            cat = _embedded_catalogue(html)
            rec = next(r for r in cat["works"][0]["recordings"] if r["id"] == rid)
            ed = rec["editorial"]
            self.assertEqual(ed["stars"], stars, rid)
            self.assertEqual(ed["reference"], reference, rid)
            self.assertIn(snippet, ed["text"], rid)
            self.assertEqual(ed["quotes"], [], rid)
            self.assertEqual(ed["author"]["id"], "cmrc", rid)
            self.assertIsNone(rec.get("divergence"), rid)
            self.assertIn("function signed(r)", html)


class TestHubChipFromAssessed(unittest.TestCase):
    def test_goldberg_chip_is_three_assessed_not_five_queued(self):
        cid, name, dates, works = site.composer_by_id("bach")
        html = site.composer_hub(cid, name, dates, works)
        row = _hub_row(html, "bach_goldberg")
        self.assertIn("3 assessed", row)
        self.assertNotIn("queued", row)
        self.assertIn("../works/bach_goldberg.html", row)
        self.assertIn("open work", row)
        self.assertNotIn("Perahia", html)
        self.assertNotIn("bach/goldberg/3", html)
        self.assertIn("Glenn Gould", html)
        self.assertIn("Columbia, 1955", html)
        self.assertIn("CBS, 1981", html)
        self.assertIn("András Schiff", html)
        self.assertIn("Decca, 1982", html)

    def test_hub_assessed_list_names_soloist_not_only_ensemble(self):
        cid, name, dates, works = site.composer_by_id("bach")
        html = site.composer_hub(cid, name, dates, works)
        start = html.index('class="rec-list"')
        rec_list = html[start:html.index("</ul>", start)]
        self.assertIn("Rachel Podger", rec_list)
        self.assertIn("Rachel Podger — Brecon Baroque", rec_list)
        self.assertNotRegex(
            rec_list,
            r'bach_violin_concertos\.html#[^"]+">Brecon Baroque<',
        )
        self.assertIn("Pierre Fournier", rec_list)
        self.assertIn("Nathan Milstein", rec_list)
        self.assertIn("András Schiff", rec_list)
        self.assertNotIn("Perahia", rec_list)
        self.assertIn("Trevor Pinnock — The English Concert", rec_list)

    def test_enabled_works_chip_from_assessed_ids_not_queue(self):
        cid, name, dates, works = site.composer_by_id("bach")
        html = site.composer_hub(cid, name, dates, works)
        expected = {
            "bach_brandenburg": ("3 assessed", "bach_brandenburg.html"),
            "bach_cello_suites": ("1 assessed", "bach_cello_suites.html"),
            "bach_violin_concertos": ("1 assessed", "bach_violin_concertos.html"),
            "bach_sonatas_partitas": ("2 assessed", "bach_sonatas_partitas.html"),
            "bach_matthew": ("2 assessed", "bach_matthew.html"),
            "bach_john": ("1 assessed", "bach_john.html"),
            "bach_mass_b_minor": ("1 assessed", "bach_mass_b_minor.html"),
            "bach_art_of_fugue": ("2 assessed", "bach_art_of_fugue.html"),
        }
        for anchor, (chip, page) in expected.items():
            row = _hub_row(html, anchor)
            self.assertIn(chip, row, anchor)
            self.assertNotIn("queued", row, anchor)
            self.assertIn(f"../works/{page}", row, anchor)
            self.assertIn("open work", row, anchor)

    def test_held_works_stay_queued_without_pages(self):
        cid, name, dates, works = site.composer_by_id("bach")
        html = site.composer_hub(cid, name, dates, works)
        for wid in HELD_EMPTY:
            anchor = wid.replace("/", "_")
            row = _hub_row(html, anchor)
            self.assertIn("queued", row, wid)
            self.assertNotIn("assessed", row, wid)
            self.assertNotIn(f"{anchor}.html", html, wid)

    def test_search_index_uses_assessed_count(self):
        idx = site.build_index(depth=1, composer_id="bach")
        gold = next(item for item in idx if item["label"] == "Goldberg Variations")
        self.assertIn("3 assessed", gold["sub"])
        self.assertNotIn("queued", gold["sub"])
        self.assertIn("bach_goldberg.html", gold["href"])
        cello = next(item for item in idx if item["label"] == "Cello Suites")
        self.assertIn("1 assessed", cello["sub"])
        self.assertIn("bach_cello_suites.html", cello["href"])
        rec_labels = [item["label"] for item in idx if item["kind"] == "recording"]
        joined = " ".join(rec_labels)
        self.assertIn("Glenn Gould", joined)
        self.assertIn("Pierre Fournier", joined)
        self.assertIn("Rachel Podger", joined)
        self.assertIn("Schiff", joined)
        self.assertNotIn("Perahia", joined)

    def test_hub_stays_bach_only(self):
        cid, name, dates, works = site.composer_by_id("bach")
        html = site.composer_hub(cid, name, dates, works).lower()
        self.assertNotIn("tosca", html)
        self.assertNotIn("dmitri shostakovich", html)
        self.assertNotIn("symphony no. 5", html)


class TestTemplateIdentityPath(unittest.TestCase):
    def test_identity_entry_does_not_render_scored_furniture(self):
        tpl = (ROOT / "site/template.html").read_text(encoding="utf-8")
        start = tpl.index("function identityLine(r)")
        entry = tpl.index("function entry(r)")
        work = tpl.index("function workSection(w)")
        identity = tpl[start:entry]
        for token in ("scorebox", "sources(", "Référence", "★"):
            self.assertNotIn(token, identity, token)
        self.assertIn("signed(", identity)
        self.assertIn("factStrip(", identity)
        self.assertNotIn("editions(", identity)
        self.assertNotIn("Editions and transfers", identity)
        self.assertIn('if(r.card==="identity") return identityLine(r)', tpl[entry:work])
        self.assertIn("recs.every(r=>r.card===\"identity\")", tpl[work:])
        self.assertIn("${recs.map(identityLine).join(\"\")}", tpl[work:])
        signed = tpl[tpl.index("function signed(r)"):tpl.index("function factStrip(r)")]
        refs_fn = tpl[tpl.index("function consultedRefs(e)"):tpl.index("function matrixOverall")]
        self.assertIn("consultedRefs(", signed)
        self.assertIn(">References<", refs_fn)
        self.assertIn("function consultedRefs(e)", tpl)
        self.assertIn("function matrixStrip(m)", tpl)
        self.assertIn("function howScored(m)", tpl)
        body_start = signed.index('class="body"')
        matrix_at = signed.index("matrixStrip(")
        how_at = signed.index("howScored(")
        refs_at = signed.index("consultedRefs(")
        self.assertGreater(matrix_at, body_start)
        self.assertGreater(how_at, matrix_at)
        self.assertGreater(refs_at, how_at)


class TestAssessedEditionsRefsFactStrip(unittest.TestCase):
    """Payload editions, consulted refs, and Brandenburg-lite facts on identity cards."""

    EMERSON_MBID = "1d748095-0c33-4fd7-b925-9e50849f101d"
    OTHER_MBID = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
    CONSULTED_KINDS = {
        "discography", "review", "label", "reference", "award",
    }
    GOULD_1955 = "2a7844fb-13b9-437a-8f68-c018c53f5f72"
    PINNOCK_MBID = "b0255dd1-324d-4608-92e5-1638831c77b8"
    HARNONCOURT_MBID = "c5286a10-3d04-402c-8f3e-65435a039e7c"
    RICHTER_MBID = "ed4c4834-026d-4a09-a7e9-f2efc9e44f77"

    def test_all_public_cards_carry_a_cover_mbid_and_fact_strip(self):
        recs = {
            r["id"]: r
            for w in ident.public_identity_works(_seed())
            for r in w["recordings"]
        }
        self.assertEqual(set(recs), set(PUBLIC_IDENTITY_IDS))
        for rid, rec in recs.items():
            eds = rec.get("editions") or []
            self.assertTrue(eds, rid)
            self.assertTrue(any(e.get("mbid") for e in eds), rid)
            for ed in eds:
                self.assertNotIn("sound", ed, rid)
                self.assertNotIn("verdict", ed, rid)
                self.assertNotIn("transfer", ed, rid)
            strip = rec.get("fact_strip") or {}
            self.assertTrue(strip.get("label") or strip.get("venue") or strip.get("sessions"), rid)
            self.assertNotIn("seed_year_note", strip, rid)
            self.assertNotIn("cover_face", strip, rid)
            ed = rec["editorial"]
            self.assertIsNotNone(ed, rid)
            consulted = ed.get("consulted") or []
            if rid in BRANDENBURG_ASSESSED:
                self.assertEqual(consulted, [], rid)
                continue
            self.assertGreaterEqual(len(consulted), 1, rid)
            self.assertLessEqual(len(consulted), 8, rid)
            for item in consulted:
                self.assertTrue(item.get("title"), rid)
                self.assertRegex(item.get("url") or "", r"^https?://")
                self.assertIn(item.get("kind"), self.CONSULTED_KINDS, rid)

    def test_brandenburg_preferred_covers_and_fact_strip(self):
        recs = {
            r["id"]: r
            for w in ident.public_identity_works(_seed())
            for r in w["recordings"]
        }
        pinnock = recs["bach/brandenburg/0"]
        harn = recs["bach/brandenburg/1"]
        richter = recs["bach/brandenburg/4"]
        self.assertEqual(pinnock["editions"][0]["mbid"], self.PINNOCK_MBID)
        self.assertEqual(harn["editions"][0]["mbid"], self.HARNONCOURT_MBID)
        self.assertEqual(richter["editions"][0]["mbid"], self.RICHTER_MBID)
        self.assertNotEqual(harn["editions"][0]["mbid"], "c11b8758-00d4-4868-bccf-2d830dc4ce0a")
        self.assertEqual(pinnock["published"], "Archiv, 1982")
        self.assertEqual(harn["published"], "Teldec, 1964")
        self.assertEqual(richter["published"], "Archiv, 1967")
        self.assertEqual(pinnock["fact_strip"]["venue"], "Henry Wood Hall, London")
        self.assertEqual(harn["fact_strip"]["venue"], "Palais Schönburg, Vienna")
        self.assertEqual(harn["fact_strip"]["sessions"], "April 1964")
        self.assertEqual(richter["fact_strip"]["sessions"], "January 1967")
        self.assertEqual(pinnock["editorial"]["author"]["id"], "cmrc")
        self.assertTrue(pinnock["editorial"]["reference"])
        self.assertFalse(harn["editorial"]["reference"])
        self.assertFalse(richter["editorial"]["reference"])

    def test_emerson_lock_uses_only_the_caa_200_release(self):
        recs = {
            r["id"]: r
            for w in ident.public_identity_works(_seed())
            for r in w["recordings"]
        }
        emerson = recs["bach/art_of_fugue/3"]
        mbids = [e["mbid"] for e in emerson["editions"]]
        self.assertEqual(mbids, [self.EMERSON_MBID])
        mb_release = [
            item["url"] for item in emerson["editorial"]["consulted"]
            if "musicbrainz.org/release/" in item["url"]
        ]
        self.assertEqual(len(mb_release), 1)
        self.assertEqual(
            mb_release[0],
            f"https://musicbrainz.org/release/{self.EMERSON_MBID}",
        )

    def test_pages_render_caa_covers_refs_and_fact_strip(self):
        gold = _page("bach/goldberg")
        cat = _embedded_catalogue(gold)
        g0 = next(r for r in cat["works"][0]["recordings"] if r["id"] == "bach/goldberg/0")
        self.assertEqual(g0["editions"][0]["mbid"], self.GOULD_1955)
        self.assertIn("coverartarchive.org/release/${ed.mbid}/front-500", gold)
        self.assertIn(">References<", gold)
        self.assertIn("Columbia Masterworks", gold)
        self.assertIn("Columbia 30th Street Studio", gold)
        self.assertIn("June 1955", gold)
        identity_fn = gold[gold.index("function identityLine(r)"):gold.index("function entry(r)")]
        self.assertNotIn("editions(", identity_fn)
        self.assertNotIn("Editions and transfers", identity_fn)

        aof = _page("bach/art_of_fugue")
        aof_cat = _embedded_catalogue(aof)
        emerson = next(
            r for r in aof_cat["works"][0]["recordings"] if r["id"] == "bach/art_of_fugue/3"
        )
        self.assertEqual(emerson["editions"][0]["mbid"], self.EMERSON_MBID)
        self.assertIn(
            f"https://musicbrainz.org/release/{self.EMERSON_MBID}",
            aof,
        )
        self.assertIn("American Academy of Arts and Letters", aof)
        self.assertIn("January–February 2003", aof)
        identity_fn = aof[aof.index("function identityLine(r)"):aof.index("function entry(r)")]
        self.assertNotIn("editions(", identity_fn)
        # Verdict text is unchanged; refs sit outside the prose paragraph.
        self.assertIn("The Emersons play the Art of Fugue as a modern string quartet", aof)
        start = aof.index('class="body"')
        end = aof.index('class="sig"', start)
        self.assertNotIn(">References<", aof[start:end])

    def test_signed_fields_other_than_consulted_are_untouched(self):
        matrix_ids = {
            "bach/goldberg/0",
            "bach/goldberg/1",
            "bach/goldberg/4",
            "bach/cello_suites/1",
            "bach/violin_concertos/4",
            "bach/sonatas_partitas/0",
            "bach/sonatas_partitas/1",
            "bach/matthew/0",
            "bach/matthew/1",
            "bach/john/1",
            "bach/mass_b_minor/0",
            "bach/art_of_fugue/0",
            "bach/art_of_fugue/3",
            "bach/brandenburg/0",
            "bach/brandenburg/1",
            "bach/brandenburg/4",
        }
        expected = {
            "bach/goldberg/0": (3, True, 4, "The 1955 Goldberg is still the shock"),
            "bach/goldberg/1": (3, False, 4, "Gould’s 1981 remake is a late architecture"),
            "bach/goldberg/4": (2, False, 4, "Schiff’s first studio Goldberg"),
            "bach/cello_suites/1": (3, True, 4, "Fournier’s Archiv studio cycle"),
            "bach/violin_concertos/4": (3, True, 4, "Podger and Brecon Baroque"),
            "bach/sonatas_partitas/0": (3, False, 4, "Milstein’s stereo remake"),
            "bach/sonatas_partitas/1": (3, True, 4, "Podger’s complete gut-strung cycle"),
            "bach/matthew/0": (3, False, 4, "Klemperer’s Philharmonia Matthew Passion"),
            "bach/matthew/1": (3, True, 4, "Gardiner’s 1988 Archiv Matthew Passion"),
            "bach/john/1": (3, True, 4, "Gardiner’s first St John Passion"),
            "bach/mass_b_minor/0": (3, True, 4, "Gardiner’s first B-minor Mass"),
            "bach/art_of_fugue/0": (2, False, 4, "Gould’s only commercial organ recording"),
            "bach/art_of_fugue/3": (3, True, 4, "The Emersons play the Art of Fugue"),
            "bach/brandenburg/0": (3, True, 1, "Pinnock’s 1982 English Concert Brandenburgs"),
            "bach/brandenburg/1": (3, False, 1, "Harnoncourt’s first Concentus Musicus cycle"),
            "bach/brandenburg/4": (3, False, 1, "The modern Munich pole of this argument."),
        }
        recs = {
            r["id"]: r
            for w in ident.public_identity_works(_seed())
            for r in w["recordings"]
        }
        for rid, (stars, reference, revision, snippet) in expected.items():
            ed = recs[rid]["editorial"]
            self.assertEqual(ed["stars"], stars, rid)
            self.assertEqual(ed["reference"], reference, rid)
            self.assertEqual(ed["revision"], revision, rid)
            self.assertEqual(
                ed["date"],
                "2026-09-08" if rid in matrix_ids else "2026-09-07",
                rid,
            )
            self.assertIn(snippet, ed["text"], rid)

    def test_identity_editions_rejects_any_other_emerson_mbid(self):
        with self.assertRaises(ValueError):
            ident.identity_editions({
                "id": "bach/art_of_fugue/3",
                "editions": [{"id": "bad", "mbid": self.OTHER_MBID}],
            })


class TestBrandenburgPublicHtml(unittest.TestCase):
    def test_page_is_the_assessed_cut_without_engine_furniture(self):
        html = _page("bach/brandenburg")
        self.assertIn("Brandenburg Concertos", html)
        self.assertIn("Trevor Pinnock", html)
        self.assertIn("Archiv, 1982", html)
        self.assertIn("Henry Wood Hall", html)
        self.assertIn("Nikolaus Harnoncourt", html)
        self.assertIn("Teldec, 1964", html)
        self.assertIn("Palais Schönburg", html)
        self.assertIn("Karl Richter", html)
        self.assertIn("Archiv, 1967", html)
        self.assertIn("January 1967", html)
        self.assertIn("bach/brandenburg/0", html)
        self.assertIn("bach/brandenburg/1", html)
        self.assertIn("bach/brandenburg/4", html)
        self.assertNotIn("bach_brandenburg_pinnock", html)
        cat = _embedded_catalogue(html)
        self.assertEqual([w["id"] for w in cat["works"]], ["bach/brandenburg"])
        recs = cat["works"][0]["recordings"]
        self.assertEqual([r["id"] for r in recs], list(BRANDENBURG_ASSESSED))
        rec_ids = {r["id"] for r in recs}
        self.assertNotIn("bach/brandenburg/2", rec_ids)
        self.assertNotIn("bach/brandenburg/3", rec_ids)
        self.assertNotIn("bach/brandenburg/5", rec_ids)
        for rec in recs:
            _assert_no_aggregate(self, rec, rec["id"])
            self.assertIsNotNone(rec.get("editorial"), rec["id"])
            self.assertEqual(rec["editorial"]["author"]["id"], "cmrc")
        by_id = {r["id"]: r for r in recs}
        self.assertTrue(by_id["bach/brandenburg/0"]["editorial"]["reference"])
        self.assertFalse(by_id["bach/brandenburg/1"]["editorial"]["reference"])
        self.assertFalse(by_id["bach/brandenburg/4"]["editorial"]["reference"])
        self.assertIn("Pinnock’s 1982 English Concert Brandenburgs", html)
        self.assertIn("Harnoncourt’s first Concentus Musicus cycle", html)
        richter = by_id["bach/brandenburg/4"]["editorial"]["text"]
        self.assertTrue(
            richter.endswith("The modern Munich pole of this argument."),
            richter[-80:],
        )
        self.assertNotIn("Three stars", html)
        self.assertNotIn("Gardiner", html)
        identity_fn = html[html.index("function identityLine(r)"):html.index("function entry(r)")]
        self.assertNotIn("scorebox", identity_fn)
        self.assertNotIn("Référence", identity_fn)
        self.assertNotIn("★", identity_fn)
        self.assertNotIn("editions(", identity_fn)
        work_fn = html[html.index("function workSection(w)"):html.index("function renderWorkDirectory")]
        self.assertIn("identityLine", work_fn)
        blob = json.dumps(cat)
        self.assertNotIn("2.853", blob)
        self.assertNotIn("2.814", blob)
        self.assertNotIn('"candidates"', blob)
        self.assertIn("Avie remake", html)
        self.assertNotIn("Avie, 2007", html)
        mbids = [r["editions"][0]["mbid"] for r in recs]
        self.assertEqual(
            mbids,
            [
                TestAssessedEditionsRefsFactStrip.PINNOCK_MBID,
                TestAssessedEditionsRefsFactStrip.HARNONCOURT_MBID,
                TestAssessedEditionsRefsFactStrip.RICHTER_MBID,
            ],
        )
        self.assertIn("coverartarchive.org/release/${ed.mbid}/front-500", html)


if __name__ == "__main__":
    unittest.main()
