#!/usr/bin/env python3
"""Tests for identity confidence gating and CAA cover proposal shape."""

from __future__ import annotations

import importlib.util
import json
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
    "catalogue": "BWV 1046–1051",
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

    def test_piano_concertos_never_match_brandenburg(self):
        """The failure mode that would put the wrong work on a Brandenburg page."""
        http = FakeHttp({
            "release-group": self._groups(
                ("mb-piano", "Piano Concertos", "2007", 100),
            ),
        })
        p = har.adapter_identity(
            {**REC, "id": "bach/brandenburg/2", "director": "Claudio Abbado",
             "ensemble": "Orchestra Mozart", "year": "2007"},
            WORK, http,
        )[0].payload
        self.assertFalse(p["auto_accept_eligible"])
        self.assertTrue(any(f.startswith("wrong work:") for f in p["review_flags"]))

    def test_german_brandenburgische_still_matches(self):
        self.assertTrue(har.work_title_compatible(
            "Brandenburg Concertos", "Brandenburgische Konzerte", "BWV 1046–1051"))

    def test_english_concert_ensemble_is_not_a_work_title(self):
        """Personnel label 'The English Concert' must not be confused with a concerto work."""
        # Compatibility is work-to-work; ensemble names are out of scope.
        self.assertTrue(har.work_title_compatible(
            "Brandenburg Concertos", "Brandenburg Concertos nos. 4-6"))
        self.assertFalse(har.work_title_compatible(
            "Brandenburg Concertos", "The English Concert Plays Bach"))

    def test_art_of_fugue_matches_itself(self):
        """Identical titles must not false-positive as wrong-work."""
        self.assertTrue(har.work_title_compatible(
            "The Art of Fugue", "The Art of Fugue"))
        self.assertTrue(har.work_title_compatible(
            "The Art of Fugue", "The Art of the Fugue"))

    def test_don_giovanni_is_not_don_carlo(self):
        self.assertFalse(har.work_title_compatible(
            "Don Giovanni", "Don Carlo"))
        self.assertTrue(har.work_title_compatible(
            "Don Giovanni", "Don Giovanni"))

    def test_matthew_passion_matches_matthaus(self):
        self.assertTrue(har.work_title_compatible(
            "St Matthew Passion", "Matthäus-Passion"))
        self.assertFalse(har.work_title_compatible(
            "St John Passion", "Matthäus-Passion"))
        self.assertFalse(har.work_title_compatible(
            "St John Passion", "St. Matthew Passion"))

    def test_mass_key_conflict(self):
        self.assertFalse(har.work_title_compatible(
            "Mass in C minor", "Mass in B minor"))

    def test_creation_matches_die_schopfung(self):
        self.assertTrue(har.work_title_compatible(
            "The Creation", "Die Schöpfung"))
        self.assertTrue(har.work_title_compatible(
            "The Seasons", "Die Jahreszeiten"))

    def test_etudes_match_op_numbered_album(self):
        self.assertTrue(har.work_title_compatible(
            "Études", "Études op. 10 & op. 25"))

    def test_symphonien_matches_symphonies_with_shared_numbers(self):
        self.assertTrue(har.work_title_compatible(
            "Symphonies Nos. 39, 40, 41",
            'Symphonien Nos. 40 & 41 "Jupiter"'))

    def test_symphony_no_vs_symphonie_nr_is_compatible(self):
        self.assertTrue(har.work_title_compatible(
            "Symphony No. 7", "Symphonie Nr. 7"))
        self.assertTrue(har.work_title_compatible(
            "Symphony No. 7", "Sinfonie Nr. 7"))
        self.assertTrue(har.work_title_compatible(
            "Symphony No. 5", "Symphonie Nr. 5"))

    def test_st_john_is_not_st_matthew(self):
        self.assertFalse(har.work_title_compatible(
            "St John Passion", "St. Matthew Passion",
            "BWV 245", composer="Johann Sebastian Bach"))

    def test_brahms_pc2_is_not_prokofiev(self):
        self.assertFalse(har.work_title_compatible(
            "Piano Concerto No. 2",
            "Prokofiev - Piano Concertos No. 1 & 2",
            "Op. 83", composer="Johannes Brahms"))

    def test_schubert_d960_is_not_hammerklavier(self):
        self.assertFalse(har.work_title_compatible(
            "Piano Sonata in B-flat",
            'Piano Sonatas No. 28 in A major, Op. 101 & No. 29 in B flat major, Op. 106 "Hammerklavier"',
            "D. 960", composer="Franz Schubert"))

    def test_rosamunde_is_not_fireworks(self):
        self.assertFalse(har.work_title_compatible(
            "Rosamunde (incidental music)",
            "Music for the Royal Fireworks / Orchestral Works",
            "D. 797", composer="Franz Schubert"))

    def test_liebeslieder_is_not_vienna_woods_waltzes(self):
        self.assertFalse(har.work_title_compatible(
            "Liebeslieder Waltzes",
            '"Tales from the Vienna Woods" and Other Favourite Waltzes',
            "Op. 52", composer="Johannes Brahms"))

    def test_haydn_trumpet_is_not_organ_concertos(self):
        self.assertFalse(har.work_title_compatible(
            "Trumpet Concerto",
            "Organ Concertos, Vol. 3: Nos. 9, 10, 11, 12",
            "Hob. VIIe:1", composer="Joseph Haydn"))

    def test_haydn_trumpet_is_not_emperor_concerto(self):
        self.assertFalse(har.work_title_compatible(
            "Trumpet Concerto",
            '"Emperor" Concerto',
            "Hob. VIIe:1", composer="Joseph Haydn"))

    def test_handel_organ_concertos_are_not_christmas_concertos(self):
        self.assertFalse(har.work_title_compatible(
            "Organ Concertos",
            "Christmas Concertos",
            "Opp. 4 & 7", composer="George Frideric Handel"))

    def test_trumpet_concerto_still_matches_trumpet_concertos(self):
        self.assertTrue(har.work_title_compatible(
            "Trumpet Concerto", "Trumpet Concertos",
            "Hob. VIIe:1", composer="Joseph Haydn"))

    def test_organ_concertos_still_match_organ_concertos(self):
        self.assertTrue(har.work_title_compatible(
            "Organ Concertos", "5 Organ Concertos",
            "Opp. 4 & 7", composer="George Frideric Handel"))

    def test_emperor_nickname_still_matches_beethoven_pc5(self):
        self.assertTrue(har.work_title_compatible(
            "Piano Concerto No. 5, Emperor",
            '"Emperor" Concerto',
            "Op. 73", composer="Ludwig van Beethoven"))

    def test_brandenburg_subset_is_compatible_but_incomplete(self):
        self.assertTrue(har.work_title_compatible(
            "Brandenburg Concertos",
            "Brandenburg Concertos nos. 4-6",
            "BWV 1046–1051"))
        flag = har.collection_subset_incomplete(
            "Brandenburg Concertos",
            "Brandenburg Concertos nos. 4-6",
            "BWV 1046–1051",
        )
        self.assertIsNotNone(flag)
        self.assertTrue(flag.startswith("incomplete:"))

    def test_cello_suites_subset_is_incomplete_not_wrong_work(self):
        self.assertTrue(har.work_title_compatible(
            "Cello Suites",
            "The Unaccompanied Cello Suites no. 1 & no. 2",
            "BWV 1007–1012"))
        flag = har.collection_subset_incomplete(
            "Cello Suites",
            "The Unaccompanied Cello Suites no. 1 & no. 2",
            "BWV 1007–1012",
        )
        self.assertIsNotNone(flag)
        self.assertTrue(flag.startswith("incomplete:"))

    def test_chopin_pc2_is_not_concertos_2_and_3(self):
        self.assertEqual(
            har.extract_work_numbers("Piano Concertos 2 & 3"), {"2", "3"})
        self.assertFalse(har.work_title_compatible(
            "Piano Concerto No. 2",
            "Piano Concertos 2 & 3",
            "Op. 21", composer="Frédéric Chopin",
            sibling_numbers={"1", "2"}))

    def test_chopin_pc_coupling_1_and_2_stays(self):
        self.assertTrue(har.work_title_compatible(
            "Piano Concerto No. 1",
            "Piano Concertos nos. 1 & 2",
            "Op. 11", composer="Frédéric Chopin",
            sibling_numbers={"1", "2"}))
        self.assertTrue(har.work_title_compatible(
            "Piano Concerto No. 2",
            "Piano Concertos No. 1 & 2",
            "Op. 21", composer="Frédéric Chopin",
            sibling_numbers={"1", "2"}))

    def test_chopin_sonatas_2_and_3_stay(self):
        self.assertTrue(har.work_title_compatible(
            "Piano Sonata No. 2",
            "Piano Sonatas nos. 2 & 3",
            "Op. 35", composer="Frédéric Chopin",
            sibling_numbers={"2", "3"}))

    def test_mozart_pc_coupling_stays(self):
        self.assertTrue(har.work_title_compatible(
            "Piano Concerto No. 23",
            "Piano Concertos no. 19, K. 459 and no. 23, K. 488",
            "K. 488", composer="Wolfgang Amadeus Mozart",
            sibling_numbers={"20", "23", "27"}))
        self.assertTrue(har.work_title_compatible(
            "Piano Concerto No. 27",
            "Great Piano Concertos nos. 20, 21, 25 & 27",
            "K. 595", composer="Wolfgang Amadeus Mozart",
            sibling_numbers={"20", "23", "27"}))

    def test_shostakovich_sym1_is_not_tchaikovsky_1_2_and_5(self):
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        work = next(w for w in seed["works"] if w["id"] == "shostakovich/sym1")
        sibs = har.sibling_work_numbers(work, seed["works"])
        self.assertIn("1", sibs)
        self.assertNotIn("2", sibs)
        self.assertFalse(har.work_title_compatible(
            "Symphony No. 1",
            "Symphonies 1, 2 and 5",
            "Op. 10", composer="Dmitri Shostakovich",
            sibling_numbers=sibs))
        rec = next(c for c in work["candidates"] if c["id"] == "shostakovich/sym1/4")
        flags = har.identity_review_flags(
            rec, "Symphonies 1, 2 and 5", "2006-06", 98,
            work=work, sibling_numbers=sibs, works=seed["works"],
        )
        self.assertTrue(any(f.startswith("wrong work:") for f in flags))

    def test_shostakovich_petrenko_5_and_9_stays(self):
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        work = next(w for w in seed["works"] if w["id"] == "shostakovich/sym5")
        sibs = har.sibling_work_numbers(work, seed["works"])
        self.assertTrue(har.work_title_compatible(
            "Symphony No. 5",
            "Symphonies nos. 5 & 9",
            "Op. 47", composer="Dmitri Shostakovich",
            sibling_numbers=sibs))

    def test_shostakovich_cello_concerto_coupling_does_not_fill_sym_gap(self):
        """Rostropovich: Cello Concerto no. 2 / Symphony no. 5 is Shostakovich."""
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        work = next(w for w in seed["works"] if w["id"] == "shostakovich/sym5")
        sibs = har.sibling_work_numbers(work, seed["works"])
        form = har._family(har._title_tokens("Symphony No. 5"), har.FORM_FAMILIES)
        self.assertEqual(
            har.extract_work_numbers_for_form(
                "Cello Concerto no. 2 / Symphony no. 5", form),
            {"5"},
        )
        self.assertTrue(har.work_title_compatible(
            "Symphony No. 5",
            "Cello Concerto no. 2 / Symphony no. 5",
            "Op. 47", composer="Dmitri Shostakovich",
            sibling_numbers=sibs))

    def test_shostakovich_cycle_box_with_seed_gap_stays(self):
        """Kondrashin Melodiya box names Symphony 3, which the seed omits."""
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        work = next(w for w in seed["works"] if w["id"] == "shostakovich/sym4")
        sibs = har.sibling_work_numbers(work, seed["works"])
        self.assertTrue(har.work_title_compatible(
            "Symphony No. 4",
            "Symphonies 1, 3, 4, 5, 6, 7, 9",
            "Op. 43", composer="Dmitri Shostakovich",
            sibling_numbers=sibs))

    def test_shostakovich_sym6_is_not_tchaikovsky_3_4_and_6(self):
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        work = next(w for w in seed["works"] if w["id"] == "shostakovich/sym6")
        sibs = har.sibling_work_numbers(work, seed["works"])
        self.assertFalse(har.work_title_compatible(
            "Symphony No. 6",
            "Symphonies 3, 4 and 6",
            "Op. 54", composer="Dmitri Shostakovich",
            sibling_numbers=sibs))

    def test_shostakovich_adjacent_pair_with_seed_gap_stays(self):
        """Rostropovich LSO Live 3 & 4 is Shostakovich; seed simply omits 3."""
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        work = next(w for w in seed["works"] if w["id"] == "shostakovich/sym4")
        sibs = har.sibling_work_numbers(work, seed["works"])
        self.assertTrue(har.work_title_compatible(
            "Symphony No. 4",
            "Symphonies Nos. 3 & 4",
            "Op. 43", composer="Dmitri Shostakovich",
            sibling_numbers=sibs))

    def test_beethoven_7_and_8_stays(self):
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        work = next(w for w in seed["works"] if w["id"] == "beethoven/sym7")
        sibs = har.sibling_work_numbers(work, seed["works"])
        self.assertTrue(har.work_title_compatible(
            work["title"],
            "Symphonies 7 and 8",
            work.get("catalogue") or "",
            composer=work.get("composer") or "",
            sibling_numbers=sibs))

    def test_haydn_london_coupling_stays_despite_missing_103(self):
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        work = next(w for w in seed["works"] if w["id"] == "haydn/sym104")
        sibs = har.sibling_work_numbers(work, seed["works"])
        self.assertTrue(har.work_title_compatible(
            work["title"],
            "Symphony No. 103 “Drum Roll” / Symphony no. 104 “London”",
            work.get("catalogue") or "",
            composer=work.get("composer") or "",
            sibling_numbers=sibs))

    def test_heifetz_reiner_listed_under_tchaikovsky_not_brahms(self):
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        brahms = next(w for w in seed["works"] if w["id"] == "brahms/violin_concerto")
        rec = next(c for c in brahms["candidates"] if c["id"] == "brahms/violin_concerto/1")
        other = har.other_composer_same_generic_artists(rec, brahms, seed["works"])
        self.assertIsNotNone(other)
        self.assertIn("Tchaikovsky", other)
        flags = har.identity_review_flags(
            rec, "Violin Concerto", "1958", 100,
            work=brahms, works=seed["works"],
        )
        self.assertTrue(any(f.startswith("wrong work:") for f in flags))

    def test_mutter_karajan_listed_under_beethoven_not_brahms(self):
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        brahms = next(w for w in seed["works"] if w["id"] == "brahms/violin_concerto")
        rec = next(c for c in brahms["candidates"] if c["id"] == "brahms/violin_concerto/2")
        other = har.other_composer_same_generic_artists(rec, brahms, seed["works"])
        self.assertIsNotNone(other)
        self.assertIn("Beethoven", other)
        flags = har.identity_review_flags(
            rec, "Violin Concerto", "1980", 98,
            work=brahms, works=seed["works"],
        )
        self.assertTrue(any(f.startswith("wrong work:") for f in flags))

    def test_generic_violin_concerto_is_not_distinctive(self):
        self.assertTrue(har._generic_instrument_form_only("Violin Concerto"))
        self.assertTrue(har.work_title_compatible(
            "Violin Concerto", "Violin Concerto", "Op. 77",
            composer="Johannes Brahms"))
        self.assertFalse(har._generic_instrument_form_only("Piano Concerto No. 1"))
        self.assertTrue(har._COLLECTION_PLURAL_RE.search("Trumpet Concertos"))

    def test_generic_symphony_number_is_not_distinctive(self):
        self.assertTrue(har._generic_across_composers("Symphony No. 6"))
        self.assertTrue(har._generic_across_composers("Symphony no. 6"))
        self.assertFalse(har._generic_across_composers(
            "Symphony No. 6, Pathétique"))
        self.assertFalse(har._generic_across_composers(
            "Symphony No. 6, Pastoral"))
        self.assertFalse(har._generic_instrument_form_only("Symphony No. 6"))

    def test_mravinsky_listed_under_tchaikovsky_not_shostakovich_6(self):
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        shost = next(w for w in seed["works"] if w["id"] == "shostakovich/sym6")
        rec = next(c for c in shost["candidates"] if c["id"] == "shostakovich/sym6/0")
        other = har.other_composer_same_generic_artists(rec, shost, seed["works"])
        self.assertIsNotNone(other)
        self.assertIn("Tchaikovsky", other)
        flags = har.identity_review_flags(
            rec, "Symphony no. 6", "1961", 100,
            work=shost, works=seed["works"],
        )
        self.assertTrue(any(f.startswith("wrong work:") for f in flags))

    def test_same_conductor_symphony_9_is_not_automatically_wrong_work(self):
        """Abbado recorded Beethoven 9 and Mahler 9; both titles are generic."""
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        bee = next(w for w in seed["works"] if w["id"] == "beethoven/sym9")
        rec = next(c for c in bee["candidates"] if c["id"] == "beethoven/sym9/4")
        self.assertIsNone(
            har.other_composer_same_generic_artists(rec, bee, seed["works"]))

    def test_chopin_pc1_coupling_is_not_tchaikovsky_collision(self):
        seed = json.loads((ROOT / "data" / "seed.json").read_text(encoding="utf-8"))
        chopin = next(w for w in seed["works"] if w["id"] == "chopin/pc1")
        rec = next(c for c in chopin["candidates"] if c["id"] == "chopin/pc1/2")
        self.assertIsNone(
            har.other_composer_same_generic_artists(rec, chopin, seed["works"]))

    def test_english_concert_in_title_is_not_live(self):
        facts = har.identity_facts_from_mb(title="Brandenburg Concertos")
        self.assertNotIn("live_studio", facts)
        self.assertNotIn("fassung", facts)
        self.assertNotIn("session_year", facts)

    def test_identity_facts_from_tokens_only(self):
        live = har.identity_facts_from_mb(
            title="Puccini: La Bohème live (Live)",
            secondary_types=["Live"],
        )
        self.assertEqual(live["live_studio"], "live")
        self.assertEqual(live["mb_secondary_types"], ["Live"])
        highlights = har.identity_facts_from_mb(title="The Magic Flute: Highlights")
        self.assertEqual(highlights["completeness"], "highlights")
        fassung = har.identity_facts_from_mb(title="Don Giovanni (Prague version)")
        self.assertRegex(fassung["fassung"], r"Prague")
        session = har.identity_facts_from_mb(
            title="The Goldberg Variations",
            disambiguation="1955 recording",
        )
        self.assertEqual(session["session_year"], "1955")
        # first-release-date is not a session year and is not read here
        none = har.identity_facts_from_mb(
            {"title": "Tosca", "first-release-date": "1953"},
        )
        self.assertNotIn("session_year", none)

    def test_identity_payload_omits_absent_facts(self):
        http = FakeHttp({
            "release-group": self._groups(
                ("mb-1", "Brandenburg Concertos", "1982-01-01", 98),
            ),
        })
        p = har.adapter_identity(REC, WORK, http)[0].payload
        self.assertNotIn("fassung", p)
        self.assertNotIn("completeness", p)
        self.assertNotIn("session_year", p)
        self.assertNotIn("live_studio", p)
        self.assertNotIn("release_mbid", p)

    def test_identity_payload_stores_tokens_from_search_hit(self):
        http = FakeHttp({
            "release-group": {"release-groups": [{
                "id": "mb-live",
                "title": "Tosca (Live)",
                "first-release-date": "1965",
                "score": 90,
                "disambiguation": "1964 recording",
                "secondary-types": ["Live"],
            }]},
        })
        rec = {**REC, "id": "puccini/tosca/9", "director": "X", "year": "1964"}
        work = {"composer": "Giacomo Puccini", "title": "Tosca", "catalogue": ""}
        p = har.adapter_identity(rec, work, http)[0].payload
        self.assertEqual(p["live_studio"], "live")
        self.assertEqual(p["session_year"], "1964")
        self.assertEqual(p["mb_disambiguation"], "1964 recording")
        self.assertEqual(p["mb_first_release"], "1965")
        self.assertEqual(p["session_year"], "1964")
        self.assertNotEqual(p["session_year"], p["mb_first_release"][:4])


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


class TestMergeProposals(unittest.TestCase):
    def test_upsert_by_target_and_kind(self):
        existing = [{
            "target": "a/0", "kind": "identity",
            "payload": {"confidence": 10}, "source": "MusicBrainz",
            "provenance": "cited", "created": "old",
        }]
        newer = har.Proposal(
            "a/0", "identity", {"confidence": 90}, "MusicBrainz", "cited",
        )
        extra = har.Proposal(
            "b/0", "identity", {"confidence": 80}, "MusicBrainz", "cited",
        )
        merged = har.merge_proposals(existing, [newer, extra])
        by = {(m["target"], m["kind"]): m for m in merged}
        self.assertEqual(by[("a/0", "identity")]["payload"]["confidence"], 90)
        self.assertIn(("b/0", "identity"), by)


if __name__ == "__main__":
    unittest.main()
