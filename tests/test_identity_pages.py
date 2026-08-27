"""Identity-only public pages from seed.works[].assessed (signed Bach).

Public cards are the critic-signed assessed IDs, not the harvest queue and
not engine scores. goldberg/3 (Perahia) stays a candidate and must not
appear. goldberg/4 (Schiff, Decca 1982) is assessed. Held Bach works stay
off this slice.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Public identity cards in seed-work order (Goldberg /0 /1 /4 plus the remaining ten).
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
    "bach/violin_concertos",
    "bach/cello_suites",
    "bach/sonatas_partitas",
    "bach/goldberg",
    "bach/mass_b_minor",
    "bach/matthew",
    "bach/john",
    "bach/art_of_fugue",
)

HELD_EMPTY = (
    "bach/suites",
    "bach/wtc",
    "bach/harpsichord_concertos",
)

QUEUE_NAMES_GOLDBERG = ("Perahia", "Landowska")

# Performer/label strings that live only on unassessed candidates of enabled
# works. Must not leak onto sealed identity pages or the hub assessed list.
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
    "Karl Richter",
    "Nikolaus Harnoncourt",
    "Tatiana Nikolayeva",
    "Davitt Moroney",
    "Gustav Leonhardt",
    "Philippe Herreweghe",
    "Angela Hewitt",
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
        for work in seed["works"]:
            if not str(work["id"]).startswith("bach/"):
                continue
            if work["id"] == "bach/goldberg":
                continue
            got.extend(work.get("assessed") or [])
        self.assertEqual(set(got), set(REMAINING_TEN))
        self.assertEqual(len(got), len(REMAINING_TEN))

    def test_brandenburg_and_held_stay_empty_assessed(self):
        seed = _seed()
        brand = next(w for w in seed["works"] if w["id"] == "bach/brandenburg")
        self.assertEqual(brand["assessed"], [])
        for wid in HELD_EMPTY:
            self.assertEqual(_work(seed, wid)["assessed"], [], wid)


class TestIdentityFromAssessed(unittest.TestCase):
    def test_public_cards_are_signed_ids_only(self):
        works = ident.public_identity_works(_seed())
        self.assertEqual([w["id"] for w in works], list(IDENTITY_WORKS))
        recs = [r for w in works for r in w["recordings"]]
        self.assertEqual([r["id"] for r in recs], list(SIGNED_IDENTITY_IDS))
        blob = json.dumps(works)
        self.assertNotIn("bach/goldberg/3", blob)
        self.assertNotIn("Perahia", blob)
        self.assertIn("bach/goldberg/4", blob)
        self.assertIn("Schiff", blob)
        for rec in recs:
            self.assertEqual(rec["card"], "identity")
            self.assertNotIn("stars", rec)
            self.assertNotIn("interpretation", rec)
            self.assertNotIn("reference", rec)
            self.assertNotIn("confidence", rec)
            self.assertEqual(rec["sources"], [])
            self.assertIsNone(rec["editorial"])

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
        self.assertNotIn("bach/brandenburg", ids)

    def test_merge_does_not_replace_engine_scored_pages(self):
        merged = _merged()
        ids = [w["id"] for w in merged["works"]]
        self.assertIn("bach_brandenburg", ids)
        self.assertIn("puccini_tosca", ids)
        self.assertIn("shostakovich/sym5", ids)
        for wid in IDENTITY_WORKS:
            self.assertIn(wid, ids, wid)
            self.assertEqual(ids.count(wid), 1, wid)
        for wid in HELD_EMPTY:
            self.assertNotIn(wid, ids, wid)
        brand = next(w for w in merged["works"] if "brandenburg" in w["id"])
        rec_ids = [r["id"] for r in brand["recordings"]]
        self.assertIn("bach_brandenburg_pinnock", rec_ids)
        self.assertAlmostEqual(
            next(r["interpretation"] for r in brand["recordings"] if r["id"].endswith("pinnock")),
            2.853,
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
            self.assertEqual(rec.get("card"), "identity")
            self.assertNotIn("stars", rec)
            self.assertNotIn("interpretation", rec)
            self.assertNotIn("reference", rec)
            self.assertEqual(rec.get("sources"), [])
            self.assertIsNone(rec.get("editorial"))
        start = html.index("function identityLine(r)")
        scored = html.index("function entry(r)")
        identity_fn = html[start:scored]
        self.assertNotIn("scorebox", identity_fn)
        self.assertNotIn("Référence", identity_fn)
        self.assertNotIn("★", identity_fn)
        work_fn = html[html.index("function workSection(w)"):html.index("function renderWorkDirectory")]
        self.assertIn("identityLine", work_fn)
        sealed = rnd.seal_catalogue(
            _merged(),
            next(w for w in _merged()["works"] if w["id"] == "bach/goldberg"),
        )
        payload = json.dumps(sealed)
        self.assertNotIn('"stars"', payload)
        self.assertNotIn('"interpretation"', payload)
        self.assertNotIn('"reference"', payload)

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
            self.assertEqual(rec.get("card"), "identity", rid)
            self.assertNotIn("stars", rec)
            self.assertNotIn("interpretation", rec)
            self.assertNotIn("reference", rec)
            self.assertEqual(rec.get("sources"), [])
            self.assertIsNone(rec.get("editorial"))
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
                self.assertEqual(rec.get("card"), "identity")
                self.assertNotIn("stars", rec)
                self.assertNotIn("reference", rec)

    def test_queues_are_not_dumped_on_enabled_pages(self):
        for wid in IDENTITY_WORKS:
            html = _page(wid)
            for name in QUEUE_ONLY:
                self.assertNotIn(name, html, f"{wid} leaked {name}")
            self.assertNotIn('"candidates"', json.dumps(_embedded_catalogue(html)))

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
        for token in ("scorebox", "signed(", "sources(", "Référence", "★"):
            self.assertNotIn(token, identity, token)
        self.assertIn('if(r.card==="identity") return identityLine(r)', tpl[entry:work])
        self.assertIn("recs.every(r=>r.card===\"identity\")", tpl[work:])
        self.assertIn("${recs.map(identityLine).join(\"\")}", tpl[work:])


if __name__ == "__main__":
    unittest.main()
