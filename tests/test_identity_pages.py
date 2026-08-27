"""Identity-only public pages from seed.works[].assessed (first slice: Goldberg).

Public cards are the critic-signed assessed IDs, not the harvest queue and
not engine scores. goldberg/3 stays a candidate and must not appear.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

OTHER_ASSESSED_OFF_THIS_SLICE = (
    "bach/cello_suites",
    "bach/violin_concertos",
    "bach/sonatas_partitas",
    "bach/matthew",
    "bach/john",
    "bach/mass_b_minor",
    "bach/art_of_fugue",
)

QUEUE_NAMES = ("Perahia", "Landowska", "Schiff")


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


def _goldberg_work(seed: dict) -> dict:
    for work in seed["works"]:
        if work["id"] == "bach/goldberg":
            return work
    raise AssertionError("bach/goldberg missing from seed")


def _goldberg_row(html: str) -> str:
    match = re.search(r'<tr id="bach_goldberg">.*?</tr>', html, re.S)
    if not match:
        raise AssertionError("Goldberg row missing from hub")
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


class TestSeedAssessedUnchanged(unittest.TestCase):
    def test_goldberg_assessed_is_exactly_zero_and_one(self):
        work = _goldberg_work(_seed())
        self.assertEqual(work["assessed"], ["bach/goldberg/0", "bach/goldberg/1"])
        ids = [c["id"] for c in work["candidates"]]
        self.assertIn("bach/goldberg/3", ids)

    def test_brandenburg_stays_empty_assessed(self):
        seed = _seed()
        brand = next(w for w in seed["works"] if w["id"] == "bach/brandenburg")
        self.assertEqual(brand["assessed"], [])


class TestIdentityFromAssessed(unittest.TestCase):
    def test_public_page_is_goldberg_zero_and_one_only(self):
        works = ident.public_identity_works(_seed())
        self.assertEqual([w["id"] for w in works], ["bach/goldberg"])
        recs = works[0]["recordings"]
        self.assertEqual([r["id"] for r in recs], ["bach/goldberg/0", "bach/goldberg/1"])
        self.assertEqual(recs[0]["soloists"], "Glenn Gould")
        self.assertEqual(recs[0]["published"], "Columbia, 1955")
        self.assertEqual(recs[1]["soloists"], "Glenn Gould")
        self.assertEqual(recs[1]["published"], "CBS, 1981")
        blob = json.dumps(works)
        self.assertNotIn("bach/goldberg/3", blob)
        self.assertNotIn("Perahia", blob)
        for rec in recs:
            self.assertEqual(rec["card"], "identity")
            self.assertNotIn("stars", rec)
            self.assertNotIn("interpretation", rec)
            self.assertNotIn("reference", rec)
            self.assertNotIn("confidence", rec)
            self.assertEqual(rec["sources"], [])
            self.assertIsNone(rec["editorial"])

    def test_other_assessed_works_are_not_in_this_slice(self):
        ids = {w["id"] for w in ident.public_identity_works(_seed())}
        for wid in OTHER_ASSESSED_OFF_THIS_SLICE:
            self.assertNotIn(wid, ids, wid)

    def test_merge_does_not_replace_engine_scored_pages(self):
        merged = ident.merge_identity_works(_engine_cat(), _seed())
        ids = [w["id"] for w in merged["works"]]
        self.assertIn("bach_brandenburg", ids)
        self.assertIn("puccini_tosca", ids)
        self.assertIn("shostakovich/sym5", ids)
        self.assertIn("bach/goldberg", ids)
        self.assertEqual(ids.count("bach/goldberg"), 1)
        for wid in OTHER_ASSESSED_OFF_THIS_SLICE:
            self.assertNotIn(wid, ids)
        brand = next(w for w in merged["works"] if "brandenburg" in w["id"])
        rec_ids = [r["id"] for r in brand["recordings"]]
        self.assertIn("bach_brandenburg_pinnock", rec_ids)
        self.assertAlmostEqual(
            next(r["interpretation"] for r in brand["recordings"] if r["id"].endswith("pinnock")),
            2.853,
            places=3,
        )

    def test_anchor_is_bach_goldberg(self):
        self.assertEqual(href.work_anchor("bach/goldberg"), "bach_goldberg")
        self.assertEqual(
            href.work_page_href("bach/goldberg"),
            "works/bach_goldberg.html",
        )


class TestGoldbergPublicHtml(unittest.TestCase):
    def _page(self) -> str:
        merged = ident.merge_identity_works(_engine_cat(), _seed())
        gold = next(w for w in merged["works"] if w["id"] == "bach/goldberg")
        return _html_for(gold, merged)

    def test_page_is_built_from_assessed_not_the_queue(self):
        html = self._page()
        self.assertIn("Goldberg Variations", html)
        self.assertIn("Glenn Gould", html)
        self.assertIn("Columbia, 1955", html)
        self.assertIn("CBS, 1981", html)
        self.assertIn("bach/goldberg/0", html)
        self.assertIn("bach/goldberg/1", html)
        self.assertNotIn("bach/goldberg/3", html)
        self.assertNotIn("bach/goldberg/2", html)
        self.assertNotIn("bach/goldberg/4", html)
        for name in QUEUE_NAMES:
            self.assertNotIn(name, html, name)
        cat = _embedded_catalogue(html)
        self.assertEqual([w["id"] for w in cat["works"]], ["bach/goldberg"])
        rec_ids = [r["id"] for r in cat["works"][0]["recordings"]]
        self.assertEqual(rec_ids, ["bach/goldberg/0", "bach/goldberg/1"])

    def test_candidate_queue_is_not_dumped(self):
        html = self._page()
        cat = _embedded_catalogue(html)
        recs = cat["works"][0]["recordings"]
        self.assertEqual(len(recs), 2)
        blob = json.dumps(cat)
        self.assertNotIn('"candidates"', blob)
        self.assertNotIn("queued", html.lower())
        self.assertNotIn("Sony SK 89243", html)

    def test_identity_cards_have_no_stars_reference_or_statements(self):
        html = self._page()
        cat = _embedded_catalogue(html)
        for rec in cat["works"][0]["recordings"]:
            self.assertEqual(rec.get("card"), "identity")
            self.assertNotIn("stars", rec)
            self.assertNotIn("interpretation", rec)
            self.assertNotIn("reference", rec)
            self.assertEqual(rec.get("sources"), [])
            self.assertIsNone(rec.get("editorial"))
        # Rendered identity path does not call the scored card.
        start = html.index("function identityLine(r)")
        scored = html.index("function entry(r)")
        identity_fn = html[start:scored]
        self.assertNotIn("scorebox", identity_fn)
        self.assertNotIn("Référence", identity_fn)
        self.assertNotIn("★", identity_fn)
        work_fn = html[html.index("function workSection(w)"):html.index("function renderWorkDirectory")]
        self.assertIn("identityLine", work_fn)
        sealed = rnd.seal_catalogue(
            ident.merge_identity_works(_engine_cat(), _seed()),
            next(w for w in ident.merge_identity_works(_engine_cat(), _seed())["works"]
                 if w["id"] == "bach/goldberg"),
        )
        payload = json.dumps(sealed)
        self.assertNotIn('"stars"', payload)
        self.assertNotIn('"interpretation"', payload)
        self.assertNotIn('"reference"', payload)

    def test_sealed_no_global_related_feed(self):
        html = self._page()
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


class TestHubChipFromAssessed(unittest.TestCase):
    def test_goldberg_chip_is_two_assessed_not_five_queued(self):
        cid, name, dates, works = site.composer_by_id("bach")
        html = site.composer_hub(cid, name, dates, works)
        row = _goldberg_row(html)
        self.assertIn("2 assessed", row)
        self.assertNotIn("queued", row)
        self.assertIn("../works/bach_goldberg.html", row)
        self.assertIn("open work", row)
        self.assertNotIn("Perahia", html)
        self.assertNotIn("bach/goldberg/3", html)
        self.assertIn("Glenn Gould", html)
        self.assertIn("Columbia, 1955", html)
        self.assertIn("CBS, 1981", html)

    def test_other_assessed_works_do_not_gain_pages_this_slice(self):
        cid, name, dates, works = site.composer_by_id("bach")
        html = site.composer_hub(cid, name, dates, works)
        self.assertNotIn("bach_cello_suites.html", html)
        self.assertNotIn("bach_violin_concertos.html", html)
        self.assertNotIn("bach_sonatas_partitas.html", html)
        self.assertNotIn("bach_matthew.html", html)
        self.assertNotIn("bach_john.html", html)
        self.assertNotIn("bach_mass_b_minor.html", html)
        self.assertNotIn("bach_art_of_fugue.html", html)
        cello = re.search(r'<tr id="bach_cello_suites">.*?</tr>', html, re.S)
        self.assertIsNotNone(cello)
        self.assertIn("queued", cello.group(0))
        self.assertNotIn("assessed", cello.group(0))

    def test_search_index_uses_assessed_count(self):
        idx = site.build_index(depth=1, composer_id="bach")
        gold = next(item for item in idx if item["label"] == "Goldberg Variations")
        self.assertIn("2 assessed", gold["sub"])
        self.assertNotIn("queued", gold["sub"])
        self.assertIn("bach_goldberg.html", gold["href"])
        rec_labels = [item["label"] for item in idx if item["kind"] == "recording"]
        joined = " ".join(rec_labels)
        self.assertIn("Glenn Gould", joined)
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
