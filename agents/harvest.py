#!/usr/bin/env python3
"""
harvest.py — the agent pipeline for the Critical Discography.

Round 1 does four things, in this order, and stops:

    1. IDENTITY    resolve every candidate recording to a MusicBrainz
                   release-group. Unresolvable candidates are dropped, not kept.
    2. EDITIONS    pull the releases under each group — catalogue number,
                   barcode, year, format. This is the second-hand layer.
    3. COVERS      ask the Cover Art Archive whether a front image exists.
    4. CITATIONS   for every recording, emit a task naming what a human or a
                   reading agent must find. It does not invent the answer.

WHAT THE AGENTS ARE ALLOWED TO DO
---------------------------------
Harvest open, licensed data (MusicBrainz CC0, Wikidata CC0, Wikipedia CC BY-SA),
and record *pointers* to everything else. Critical writing in Gramophone,
Diapason, ClassicsToday, Fanfare and the rest is copyrighted: the guide stores
a normalised score, a short characterisation in the guide's own words, and a
locator. It does not store or republish review text, and it does not scrape
sites whose terms forbid it. A citation a reader can follow is worth more than
a paragraph the guide cannot legally show.

Nothing here writes to the catalogue. It writes proposals, which become a pull
request, which a human merges.

    python harvest.py seed.json --contact you@example.org --budget 300
    python harvest.py seed.json --contact you@example.org --dry-run
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable, Optional

VERSION = "harvest/1.7"
CACHE = pathlib.Path(".cache")
OUT = pathlib.Path("proposals")

# MusicBrainz search score 0–100. Below this, never treat a match as eligible
# for auto-accept; leave it for human identity review (SPRINTS S1-06).
IDENTITY_MIN_CONFIDENCE = 80

COMPILATION_RE = re.compile(
    r"\b(best of|collection|anthology|sampler|highlights)\b",
    re.IGNORECASE,
)

# Tokens that name a *genre/form*, not a specific work. Sharing only these
# ("Concertos", "Symphony") must never count as an identity match — that is
# how a Piano Concerto release-group lands on a Brandenburg candidate.
WORK_STOPWORDS = {
    "the", "a", "an", "and", "of", "for", "in", "on", "nos", "no", "nr", "n",
    "op", "opp", "bwv", "hob", "woo", "kv", "k", "d", "wwv", "sz", "bb",
    # Common articles in MB titles — not work-identity signal.
    "die", "der", "das", "dem", "den", "des", "ein", "eine",
    "la", "le", "les", "el", "il", "lo", "gli", "une", "un",
}

# Multilingual title stems that name the same work (folded, no diacritics).
# Used only when both sides hit the same group — never alone as a form word.
TITLE_EQUIV_GROUPS = (
    frozenset({"creation", "schopfung", "schöpfung"}),
    frozenset({"seasons", "jahreszeiten"}),
    frozenset({"magic", "zauberflote", "zauberflöte"}),
    frozenset({"figaro", "nozze"}),
    frozenset({"matthew", "matthaus", "matthäus", "matthieu"}),
    frozenset({"john", "johannes", "jean"}),
)
WORK_GENERIC = {
    "concerto", "concertos", "konzert", "konzerte", "concerti", "concert",
    "sonata", "sonatas", "sonate", "sonaten",
    "symphony", "symphonies", "sinfonie", "sinfonien", "sinfonia",
    "quartet", "quartets", "quartett", "quintet", "quintets",
    "trio", "trios", "suite", "suites", "prelude", "preludes", "preludien",
    "mass", "messe", "requiem", "opera", "operas",
    "variation", "variations", "partita", "partitas",
    "fugue", "fugues", "cantata", "cantatas",
    "overture", "overtures", "ouverture",
    "fantasy", "fantasia", "fantaisie", "impromptu", "impromptus",
    "etude", "etudes", "étude", "études",
    "nocturne", "nocturnes", "ballade", "ballades",
    "waltz", "waltzes", "walzer", "valse", "valses",
    "passion", "passions",  # St Matthew / St John — evangelist token decides
    "complete", "works", "album", "selection", "volume", "vol",
    # Too common to identify a work ("Music for the Royal Fireworks" ≠ Rosamunde).
    "music", "incidental", "orchestral", "royal",
}

STALE = {"identity": timedelta(days=365), "editions": timedelta(days=90),
         "cover": timedelta(days=90), "cover_miss": timedelta(days=14),
         "citation": timedelta(days=180)}


# ------------------------------------------------------------------ transport

class Http:
    """One polite client. Per-host rate limiting, on-disk cache, robots gate."""

    LIMITS = {"musicbrainz.org": 1.05, "coverartarchive.org": 0.6,
              "www.wikidata.org": 0.3, "en.wikipedia.org": 0.3}

    # Documented APIs, used as their operators intend. robots.txt governs
    # crawling; MusicBrainz disallows /ws/ there precisely to keep crawlers out
    # of an endpoint meant for identified clients under a published rate limit.
    # Honouring the rate limit is the obligation that matters. Everything not on
    # this list is treated as HTML and goes through the robots gate.
    APIS = ("https://musicbrainz.org/ws/",
            "https://coverartarchive.org/",
            "https://www.wikidata.org/w/api.php",
            "https://en.wikipedia.org/api/")

    def __init__(self, contact: str, budget: int, dry: bool = False):
        self.ua = f"CriticalDiscography/2.0 ({contact})"
        self.budget = budget
        self.spent = 0
        self.dry = dry
        self.last: dict[str, float] = {}
        self.robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        # ok | empty | error | robots | dry — so the queue does not apply a
        # multi-day backoff after a 503/timeout.
        self.last_status: str = "ok"
        CACHE.mkdir(exist_ok=True)

    def allowed(self, url: str) -> bool:
        if url.startswith(self.APIS):
            return True
        host = urllib.parse.urlparse(url).netloc
        if host not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"https://{host}/robots.txt")
            try:
                rp.read()
            except Exception:
                rp = None
            self.robots[host] = rp
        rp = self.robots[host]
        if rp is None:
            print(f"    robots.txt unreachable for {host} — skipping (not an API)")
            return False          # cannot verify permission: do not scrape
        return rp.can_fetch(self.ua, url)

    def get(self, url: str) -> Optional[dict | bytes]:
        if self.spent >= self.budget:
            raise BudgetExhausted()
        if not self.allowed(url):
            print(f"    robots.txt disallows {url}")
            self.last_status = "robots"
            return None
        if self.dry:
            self.spent += 1
            self.last_status = "dry"
            return None

        host = urllib.parse.urlparse(url).netloc
        gap = self.LIMITS.get(host, 1.0) - (time.monotonic() - self.last.get(host, 0))
        if gap > 0:
            time.sleep(gap)
        self.last[host] = time.monotonic()

        req = urllib.request.Request(url, headers={"User-Agent": self.ua, "Accept": "application/json"})
        self.spent += 1
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                body = r.read()
                if "json" in r.headers.get("Content-Type", ""):
                    self.last_status = "ok"
                    return json.loads(body)
                self.last_status = "ok"
                return body
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.last_status = "empty"
                return None
            print(f"    HTTP {e.code} {url}")
            self.last_status = "error"
            return None
        except Exception as e:
            print(f"    {type(e).__name__} {url}")
            self.last_status = "error"
            return None


class BudgetExhausted(Exception):
    """Stop cleanly and resume next run. The queue keeps its cursor."""


# ------------------------------------------------------------------ proposals

@dataclass
class Proposal:
    target: str                  # "work/candidate" path this concerns
    kind: str                    # identity | editions | cover | citation_task
    payload: dict
    source: str
    provenance: str              # cited | attributed | draft
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ------------------------------------------------------------------ score maps

def normalise(scale: str, value) -> Optional[float]:
    """Map a publication's own scale onto 0–3. Prose-only sources return None,
    which routes them to a human rather than to a guess."""
    try:
        if scale == "stars_5":       return round(float(value) / 5 * 3, 2)
        if scale == "stars_3":       return round(float(value), 2)
        if scale == "ten_point":     return round(float(value) / 10 * 3, 2)
        if scale == "percent":       return round(float(value) / 100 * 3, 2)
        if scale == "award":         return 2.90     # Diapason d'Or, Gramophone Award
        if scale == "editors_choice":return 2.85
        if scale == "rosette":       return 2.95     # Penguin Guide rosette
    except (TypeError, ValueError):
        return None
    return None


# ------------------------------------------------------------------ adapters

def _title_tokens(title: str) -> set[str]:
    cleaned = re.sub(r"[^\w\s]", " ", (title or "").lower(), flags=re.UNICODE)
    tokens = {w for w in cleaned.split() if w and w not in WORK_STOPWORDS}
    # Split German compounds so Klavierkonzert → klavier + konzert.
    extras: set[str] = set()
    for t in list(tokens):
        for stem in ("klavier", "violin", "cello", "viola", "flote", "flute",
                     "oboe", "horn", "trumpet", "organ"):
            if t.startswith(stem) and t != stem and len(t) > len(stem) + 3:
                extras.add(stem)
                rest = t[len(stem):]
                if rest:
                    extras.add(rest)
    return tokens | extras


# Short / honorific tokens that must not alone identify a work ("don" would
# otherwise equate Don Giovanni with Don Carlo).
WEAK_DISTINCTIVE = frozenset({
    "don", "st", "saint", "ste", "lord", "sir", "von", "van", "de", "di", "du",
})

# Key-quality words are not work names ("flat" must not equate D. 960 with Op. 106).
KEY_WORDS = frozenset({
    "major", "minor", "dur", "moll", "flat", "sharp", "diesis", "bemol",
    "bemolle", "sostenido",
})

# Instruments are forces, not work identity ("piano" must not equate Brahms with
# Prokofiev, or Schubert D. 960 with the Hammerklavier).
INSTRUMENT_WORDS = frozenset({
    "piano", "klavier", "pianoforte", "violin", "violino", "geige",
    "cello", "violoncello", "violoncelle", "viola", "flute", "flote",
    "oboe", "horn", "trumpet", "organ", "clarinet", "klarinette",
    "soprano", "tenor", "bass", "choir", "chorus", "orchestra",
})


def distinctive_work_tokens(title: str) -> set[str]:
    """Name-bearing tokens (e.g. brandenburg), not bare form words (concertos).

    Length floor is 3 so short stems like "art" (Art of Fugue) count; bare
    form words, key words and instrument names stay excluded.
    """
    return {
        w for w in _title_tokens(title)
        if w not in WORK_GENERIC
        and w not in WEAK_DISTINCTIVE
        and w not in KEY_WORDS
        and w not in INSTRUMENT_WORDS
        and len(w) >= 3
    }


def _fold_token(tok: str) -> str:
    """ASCII-ish fold for alias lookup (schöpfung → schopfung)."""
    decomp = unicodedata.normalize("NFKD", tok or "")
    return "".join(c for c in decomp if not unicodedata.combining(c)).lower()


def _equiv_group(tok: str) -> Optional[frozenset]:
    folded = _fold_token(tok)
    for group in TITLE_EQUIV_GROUPS:
        folded_group = {_fold_token(g) for g in group}
        if folded in folded_group or tok in group:
            return group
    return None


def _extract_keys(title: str) -> set[str]:
    """Normalised tonal keys mentioned in a title (b-minor, c-minor, …)."""
    t = _fold_token(title or "").replace("♭", "b").replace("sharp", "#")
    keys: set[str] = set()
    for note, mode in re.findall(
        r"\b([a-gh])\s*[-\s]?(major|minor|dur|moll)\b", t
    ):
        n = "b" if note == "h" else note
        m = "minor" if mode in ("minor", "moll") else "major"
        keys.add(f"{n}-{m}")
    # "Piano Sonata in B-flat" names a key even without major/minor.
    for note, acc in re.findall(r"\b([a-gh])\s*[-\s]?(flat|sharp|#|b)\b", t):
        if acc in ("flat", "b"):
            keys.add(f"{'b' if note == 'h' else note}-flat")
        else:
            keys.add(f"{'b' if note == 'h' else note}-sharp")
    return keys


def _keys_conflict(seed_title: str, mb_title: str) -> bool:
    sk, mk = _extract_keys(seed_title), _extract_keys(mb_title)
    return bool(sk and mk and sk.isdisjoint(mk))


def _token_overlap(seed_tok: str, mb_tok: str) -> bool:
    """Prefix/containment so Brandenburg ≈ Brandenburgische / Brandenburgs."""
    if seed_tok == mb_tok:
        return True
    if min(len(seed_tok), len(mb_tok)) < 4:
        return False
    return seed_tok in mb_tok or mb_tok in seed_tok


# Cross-language form / instrument families. Sharing a family + work number
# is enough; sharing only "concerto" across different works is not.
FORM_FAMILIES = (
    frozenset({"symphony", "symphonies", "symphonie", "symphonien",
               "sinfonie", "sinfonien", "sinfonia"}),
    frozenset({"concerto", "concertos", "konzert", "konzerte", "concerti",
               "klavierkonzert", "violinkonzert", "concert"}),
    frozenset({"sonata", "sonatas", "sonate", "sonaten"}),
    frozenset({"quartet", "quartets", "quartett", "quartette"}),
    frozenset({"quintet", "quintets", "quintett"}),
    frozenset({"trio", "trios"}),
    frozenset({"suite", "suites"}),
    frozenset({"mass", "messe"}),
    frozenset({"requiem"}),
    frozenset({"prelude", "preludes", "preludien"}),
    frozenset({"partita", "partitas"}),
    frozenset({"cantata", "cantatas"}),
    frozenset({"opera", "operas"}),
    frozenset({"etude", "etudes", "étude", "études"}),
    frozenset({"overture", "overtures", "ouverture", "ouvertures"}),
)
INSTRUMENT_FAMILIES = (
    frozenset({"piano", "klavier", "pianoforte"}),
    frozenset({"violin", "violino", "geige"}),
    frozenset({"cello", "violoncello", "violoncelle"}),
    frozenset({"clarinet", "klarinette"}),
    frozenset({"trumpet"}),
    frozenset({"organ"}),
    frozenset({"horn"}),
    frozenset({"flute", "flote"}),
    frozenset({"oboe"}),
    frozenset({"viola"}),
)


def _family(tokens: set[str], families: tuple[frozenset, ...]) -> Optional[frozenset]:
    for fam in families:
        if tokens & fam:
            return fam
    return None


def extract_work_numbers(title: str) -> set[str]:
    """Symphony No. 5 / Symphonie Nr. 5 / nos. 5 & 9 → {'5'} / {'5','9'}."""
    t = (title or "").lower().replace("–", "-").replace("—", "-")
    nums = set(re.findall(r"\b(?:nos?|nr|n)\.?\s*(\d{1,3})\b", t))
    # "Nos. 39, 40, 41" / "nos. 5 / 8 / 9"
    for chunk in re.findall(r"\b(?:nos?|nr|n)\.?\s*([\d\s,/&and\-]+)", t):
        nums |= set(re.findall(r"\d{1,3}", chunk))
    _form = (
        r"(?:symphony|symphonies|symphonie|symphonien|sinfonie|sinfonien|"
        r"sinfonia|concerto|concertos|"
        r"konzert|sonata|sonatas|sonate|quartet|quartett|quintet|suite|suites|"
        r"klavierkonzert|violinkonzert)"
    )
    nums |= set(re.findall(
        rf"\b{_form}\s+(?:nos?\.?\s*|nr\.?\s*|n\.?\s*)?(\d{{1,3}})\b",
        t,
    ))
    # "Piano Concertos 2 & 3" / "Sonatas nos. 2 & 3" — the rest of the list.
    for chunk in re.findall(
        rf"\b{_form}\s+(?:nos?\.?\s*|nr\.?\s*|n\.?\s*)?([\d\s,/&and\-]+)",
        t,
    ):
        nums |= set(re.findall(r"\d{1,3}", chunk))
    # Inclusive short ranges: nos. 4-6 → {4,5,6}. Cap so catalogue spans
    # (1046-1051) are not treated as work numbers.
    for a, b in re.findall(
        r"\b(?:nos?|nr|n)\.?\s*(\d{1,3})\s*-\s*(\d{1,3})\b", t
    ):
        lo, hi = int(a), int(b)
        if 0 < hi - lo <= 20:
            nums |= {str(n) for n in range(lo, hi + 1)}
    return nums


_TITLE_COMPOSER_PREFIX = re.compile(
    r"^([A-ZÀ-Ý][A-Za-zÀ-ÿ'’.\-]{2,})\s*[:–—-]\s+"
)
_CATALOGUE_ID_RE = re.compile(
    r"\b(bwv|op(?:p)?|woo|hob|kv|wwv|k|d)\s*\.?\s*(\d{1,4})\b",
    re.IGNORECASE,
)
_CATALOGUE_RANGE_RE = re.compile(
    r"\b(bwv|op(?:p)?|woo|hob|kv|wwv)\s*\.?\s*(\d{1,4})\s*[–\-]\s*(\d{1,4})\b",
    re.IGNORECASE,
)
_COLLECTION_PLURAL_RE = re.compile(
    r"\b(suites|suiten|sonatas|sonaten|partitas|concertos|concerti|"
    r"konzerte|quartets|quintets|"
    r"trios|etudes|études|preludes|préludes|waltzes|walzer)\b",
    re.IGNORECASE,
)

# Adjectives/fillers that appear in MB titles without naming a different work.
_MB_NAME_FILLER = frozenset({
    "unaccompanied", "favourite", "favorite", "other", "solo",
    "sechs", "six", "pour", "fur", "für", "great", "new", "original",
    "complete", "digital", "remastered", "highlights", "excerpts",
    "volume", "vol", "integral", "integrale", "suiten", "album",
    "selection", "works", "recorded", "edition", "version",
    "live", "studio", "collection", "anthology", "sampler",
    "best", "remaster", "digital",
})


def extract_catalogue_ids(*texts: str) -> set[str]:
    """BWV 245 / Op. 83 / D. 960 → {'bwv:245', 'op:83', 'd:960'}."""
    ids: set[str] = set()
    for text in texts:
        if not text:
            continue
        t = text.replace("–", "-").replace("—", "-")
        for m in _CATALOGUE_RANGE_RE.finditer(t):
            prefix = m.group(1).lower()
            if prefix.startswith("op"):
                prefix = "op"
            for num in (m.group(2), m.group(3)):
                ids.add(f"{prefix}:{num.lstrip('0') or '0'}")
        for m in _CATALOGUE_ID_RE.finditer(t):
            prefix = m.group(1).lower()
            if prefix.startswith("op"):
                prefix = "op"
            elif prefix == "kv":
                prefix = "k"
            ids.add(f"{prefix}:{m.group(2).lstrip('0') or '0'}")
    return ids


def _catalogue_conflict(seed_catalogue: str, mb_title: str) -> bool:
    """True when both sides name catalogue ids and they do not overlap."""
    seed_ids = extract_catalogue_ids(seed_catalogue)
    mb_ids = extract_catalogue_ids(mb_title)
    return bool(seed_ids and mb_ids and seed_ids.isdisjoint(mb_ids))


def _catalogue_range_span(catalogue: str) -> Optional[int]:
    """BWV 1046–1051 → 6. None when the catalogue is not a range."""
    t = (catalogue or "").replace("–", "-").replace("—", "-")
    m = _CATALOGUE_RANGE_RE.search(t)
    if not m:
        return None
    a, b = int(m.group(2)), int(m.group(3))
    if b > a:
        return b - a + 1
    return None


def collection_subset_incomplete(
    seed_title: str, mb_title: str, catalogue: str = "",
) -> Optional[str]:
    """Flag when MB names a numbered subset of an unnumbered seed collection.

    Brandenburg Concertos (BWV 1046–1051) vs nos. 4–6, Cello Suites vs
    no. 1 & no. 2. Same work, not complete — needs-review, not accept.
    """
    if not (seed_title or "").strip() or not (mb_title or "").strip():
        return None
    if not _COLLECTION_PLURAL_RE.search(seed_title or ""):
        return None
    seed_nums = extract_work_numbers(seed_title)
    if seed_nums:
        return None
    mb_nums = extract_work_numbers(mb_title)
    if not mb_nums:
        return None
    span = _catalogue_range_span(catalogue)
    if span is not None and len(mb_nums) >= span:
        return None
    shown = ", ".join(sorted(mb_nums, key=lambda x: int(x)))
    return f"incomplete: MB title names a subset ({shown}) of seed collection"


def _mb_names_other_work(seed_title: str, mb_title: str) -> bool:
    """True when MB carries a work name the seed does not share.

    Catches Emperor / Christmas / Vienna Woods on a generic Concerto/Waltzes
    seed. Numbered and catalogue matches return earlier and never reach this.
    """
    mb_named = distinctive_work_tokens(mb_title) - _MB_NAME_FILLER
    if not mb_named:
        return False
    seed_named = distinctive_work_tokens(seed_title) - _MB_NAME_FILLER
    seed_all = _title_tokens(seed_title)
    for m in mb_named:
        if any(_token_overlap(m, s) for s in seed_named):
            return False
        if any(_token_overlap(m, s) for s in seed_all):
            return False
    return True


def _foreign_composer_prefix(mb_title: str, composer: str = "",
                             personnel: str = "") -> bool:
    """'Prokofiev - Piano Concertos' is not Brahms. One-word title prefixes only.

    Multi-word prefixes (Glenn Gould, Herbert von Karajan) are treated as
    personnel, not composers. A prefix that matches the seed composer or the
    candidate's director/ensemble/soloists is allowed.
    """
    m = _TITLE_COMPOSER_PREFIX.match((mb_title or "").strip())
    if not m:
        return False
    prefix = _fold_token(m.group(1))
    if not prefix or prefix in WORK_GENERIC or prefix in WORK_STOPWORDS:
        return False
    if prefix in INSTRUMENT_WORDS or prefix in KEY_WORDS:
        return False
    if _family({prefix}, FORM_FAMILIES) is not None:
        return False
    seed_surnames = {_fold_token(p) for p in re.split(r"\s+", composer or "") if p}
    if prefix in seed_surnames:
        return False
    pers = {
        _fold_token(p) for p in re.split(r"[\s,;/]+", personnel or "")
        if len(p) >= 3
    }
    if prefix in pers:
        return False
    return True


def sibling_work_numbers(work: dict, works: Optional[list] = None) -> set[str]:
    """Work numbers of the same composer + form + instrument in the seed.

    Chopin piano concertos → {1, 2}. Used to reject MB titles that name a
    number past that cycle (Concertos 2 & 3) without touching real couplings
    (Mozart 19+23, Chopin sonatas 2+3, Chopin concertos 1+2).
    """
    if not work or not works:
        return set()
    title = work.get("title") or ""
    tokens = _title_tokens(title)
    form = _family(tokens, FORM_FAMILIES)
    inst = _family(tokens, INSTRUMENT_FAMILIES)
    if form is None:
        return set()
    composer = work.get("composer") or ""
    composer_id = work.get("composer_id") or ""
    nums: set[str] = set()
    for other in works:
        if composer_id and other.get("composer_id"):
            if other.get("composer_id") != composer_id:
                continue
        elif composer and other.get("composer") != composer:
            continue
        ot = other.get("title") or ""
        otok = _title_tokens(ot)
        if _family(otok, FORM_FAMILIES) is not form:
            continue
        oinst = _family(otok, INSTRUMENT_FAMILIES)
        if inst and oinst and inst is not oinst:
            continue
        nums |= extract_work_numbers(ot)
    return nums


def _mb_number_past_composer_cycle(
    mb_title: str, sibling_numbers: Optional[set[str]],
) -> bool:
    """True when MB names a work number above this composer's known cycle."""
    if not sibling_numbers:
        return False
    try:
        ceiling = max(int(n) for n in sibling_numbers)
    except ValueError:
        return False
    if ceiling <= 0:
        return False
    for n in extract_work_numbers(mb_title):
        try:
            if int(n) > ceiling:
                return True
        except ValueError:
            continue
    return False


def work_title_compatible(seed_title: str, mb_title: str,
                          catalogue: str = "",
                          composer: str = "",
                          personnel: str = "",
                          sibling_numbers: Optional[set[str]] = None) -> bool:
    """True only when the MusicBrainz release-group is the same *work*.

    Sharing a generic form word ("Concertos") alone is never enough — that is
    how a Piano Concerto group was proposed under Brandenburg. Multilingual
    equivalents (Symphony/Symphonie, Mass/Messe) and work numbers are allowed.
    Ensemble names such as "The English Concert" are personnel and are not
    consulted here.
    """
    if not (seed_title or "").strip() or not (mb_title or "").strip():
        return False
    if _foreign_composer_prefix(mb_title, composer, personnel):
        return False
    if _catalogue_conflict(catalogue, mb_title):
        return False

    seed_tokens = _title_tokens(seed_title)
    mb_tokens = _title_tokens(mb_title)

    # 0) Identical work title after stopword/digit stripping
    #    ("The Art of Fugue" ↔ "Art of Fugue" / "The Art of the Fugue").
    seed_key = {t for t in seed_tokens if not t.isdigit()}
    mb_key = {t for t in mb_tokens if not t.isdigit()}
    if seed_key and seed_key == mb_key:
        return True

    # 0b) Known multilingual equivalents (Creation ↔ Die Schöpfung).
    seed_groups = {_equiv_group(t) for t in seed_key}
    mb_groups = {_equiv_group(t) for t in mb_key}
    seed_groups.discard(None)
    mb_groups.discard(None)
    if seed_groups and seed_groups & mb_groups:
        return True

    # 1) Distinctive work name: Brandenburg, Tosca, Giovanni, Emperor…
    #    Instruments and key words are not distinctive, so Piano ↛ Hammerklavier
    #    and "music" ↛ Royal Fireworks.
    dist = distinctive_work_tokens(seed_title)
    dist_hit = bool(
        dist and any(_token_overlap(d, m) for d in dist for m in mb_tokens)
    )
    if dist_hit and not _keys_conflict(seed_title, mb_title):
        return True

    seed_form = _family(seed_tokens, FORM_FAMILIES)
    mb_form = _family(mb_tokens, FORM_FAMILIES)
    seed_nums = extract_work_numbers(seed_title)
    mb_nums = set(re.findall(r"\d{1,3}", mb_title or ""))

    seed_inst = _family(seed_tokens, INSTRUMENT_FAMILIES)
    mb_inst = _family(mb_tokens, INSTRUMENT_FAMILIES)
    if seed_inst and mb_inst and seed_inst is not mb_inst:
        return False

    def numbered_form_match() -> bool:
        if not (seed_form and mb_form and seed_form is mb_form and seed_nums):
            return False
        if not (seed_nums & mb_nums):
            return False
        if seed_inst and mb_inst and seed_inst is not mb_inst:
            return False
        if seed_inst and not mb_inst:
            return False
        if _keys_conflict(seed_title, mb_title):
            return False
        return True

    # 2) Numbered form works: same form family + shared work number.
    #    "Symphony No. 5" ↔ "Symphonie Nr. 5" / "Symphonies nos. 5 & 9"
    #    but not ↔ "The 5 Piano Concertos" (form family differs).
    if numbered_form_match():
        if _mb_number_past_composer_cycle(mb_title, sibling_numbers):
            return False
        return True

    # 3) Mass in B minor ↔ Messe in h-Moll (German note names).
    if seed_form and mb_form and seed_form is mb_form:
        if ({"b", "minor"} <= seed_tokens and {"h", "moll"} <= mb_tokens) or (
            {"h", "moll"} <= seed_tokens and {"b", "minor"} <= mb_tokens
        ):
            return True

    # 6) Numbered seed with nickname distinctive (Emperor) — allow if number +
    #    form + instrument agree even when the nickname is absent on MB.
    if (
        dist and seed_form and mb_form and seed_form is mb_form
        and seed_nums and (seed_nums & mb_nums)
    ):
        if _mb_number_past_composer_cycle(mb_title, sibling_numbers):
            return False
        if seed_inst and mb_inst and seed_inst is mb_inst:
            return True
        if not seed_inst and not mb_inst:
            return True

    # 7) Catalogue number fragment (e.g. 1046 from BWV 1046–1051) in MB title.
    for frag in re.findall(r"\d{3,4}", catalogue or ""):
        if frag in (mb_title or ""):
            return True

    # Seed named a specific work (Rosamunde, St John, Tosca, Liebeslieder)
    # that is absent from the MB title — do not fall through to generic form.
    if dist and not dist_hit:
        return False
    if _keys_conflict(seed_title, mb_title):
        return False
    # MB named a different work (Emperor, Christmas, Vienna Woods) while the
    # seed only offered a generic form/instrument.
    if _mb_names_other_work(seed_title, mb_title):
        return False

    # 4) Instrument + collection without a seed number.
    #    Cello Suites ↔ Suites pour violoncelle
    #    Trumpet Concerto ↔ Trumpet Concertos
    #    Singular keyed sonatas (D. 960 vs Hammerklavier) do not qualify
    #    unless the MB side is also a collection of the same instrument.
    if seed_form and mb_form and seed_form is mb_form and seed_inst and mb_inst:
        if seed_inst is mb_inst and not seed_nums:
            seed_plural = bool(_COLLECTION_PLURAL_RE.search(seed_title or ""))
            mb_plural = bool(_COLLECTION_PLURAL_RE.search(mb_title or ""))
            if seed_plural or mb_plural:
                return True

    # 5) Unnumbered unique forms with no leftover distinctive seed token
    #    and no instrument (Requiem ↔ Requiem in D minor). Bare "Concerto"
    #    / "Sonata" never reaches here when the seed names an instrument.
    if (
        seed_form and mb_form and seed_form is mb_form
        and not seed_nums and not dist and not seed_inst
    ):
        return True

    return False


def _folded_person(name: str) -> str:
    return " ".join(
        _fold_token(p) for p in re.split(r"[\s,]+", name or "") if p
    )


def _generic_across_composers(title: str) -> bool:
    """True when the title is only form / instrument / number — not a unique work.

    'Violin Concerto', 'Symphony No. 6', 'Piano Concerto No. 1'.
    Not 'Symphony No. 6, Pathétique' or 'Brandenburg Concertos'.
    """
    if distinctive_work_tokens(title):
        return False
    return _family(_title_tokens(title), FORM_FAMILIES) is not None


def _generic_instrument_form_only(title: str) -> bool:
    """True for 'Violin Concerto' — form+instrument, no work name, no number."""
    if extract_work_numbers(title):
        return False
    if not _generic_across_composers(title):
        return False
    return _family(_title_tokens(title), INSTRUMENT_FAMILIES) is not None


def _same_performance_artists(a: dict, b: dict) -> bool:
    """Director+soloists when named; otherwise director+ensemble (no soloists)."""
    da = _folded_person(a.get("director") or "")
    db = _folded_person(b.get("director") or "")
    sa = _folded_person(a.get("soloists") or "")
    sb = _folded_person(b.get("soloists") or "")
    ea = _folded_person(a.get("ensemble") or "")
    eb = _folded_person(b.get("ensemble") or "")
    if sa or sb:
        if not sa or not sb or sa != sb:
            return False
        if da and db and da != db:
            return False
        return True
    if da and db:
        return da == db and bool(ea) and ea == eb
    return bool(ea) and ea == eb


def _mb_names_seed_composer(mb_title: str, composer: str) -> bool:
    surnames = {
        _fold_token(p) for p in re.split(r"\s+", composer or "") if len(p) >= 4
    }
    mb_toks = {_fold_token(t) for t in _title_tokens(mb_title)}
    return bool(surnames & mb_toks)


def composer_seed_index(composer_id: str, works: Optional[list] = None) -> int:
    """First appearance of composer_id in the seed. Missing composers sort last."""
    if not composer_id:
        return 10 ** 9
    for i, other in enumerate(works or []):
        if (other.get("composer_id") or "") == composer_id:
            return i
    return 10 ** 9


def other_composer_same_generic_artists(
    rec: dict, work: dict, works: Optional[list] = None,
) -> Optional[str]:
    """Another composer in the seed lists the same artists on the same
    generic form work (Brahms VC vs Tchaikovsky Heifetz/Reiner; Shostakovich
    Symphony No. 6 vs Tchaikovsky Pathétique Mravinsky).

    Numbered forms (Symphony No. 9) are recorded by the same conductor for
    many composers; only treat those as a leak when the other listing carries
    a distinctive work name the seed lacks (Pathétique, Pastoral, Eroica).
    """
    if not rec or not work or not works:
        return None
    seed_title = work.get("title") or ""
    if not _generic_across_composers(seed_title):
        return None
    my_cid = work.get("composer_id") or ""
    my_composer = work.get("composer") or ""
    seed_tok = _title_tokens(seed_title)
    seed_form = _family(seed_tok, FORM_FAMILIES)
    seed_inst = _family(seed_tok, INSTRUMENT_FAMILIES)
    seed_nums = extract_work_numbers(seed_title)
    seed_dist = distinctive_work_tokens(seed_title)
    for other in works:
        oid = other.get("composer_id") or ""
        oname = other.get("composer") or ""
        if my_cid and oid:
            if oid == my_cid:
                continue
        elif oname == my_composer:
            continue
        ot = other.get("title") or ""
        otok = _title_tokens(ot)
        if _family(otok, FORM_FAMILIES) is not seed_form:
            continue
        oinst = _family(otok, INSTRUMENT_FAMILIES)
        if seed_inst and oinst and seed_inst is not oinst:
            continue
        if seed_inst and not oinst:
            continue
        if _keys_conflict(seed_title, ot):
            continue
        other_nums = extract_work_numbers(ot)
        if seed_nums:
            if not (seed_nums & other_nums):
                continue
            other_dist = distinctive_work_tokens(ot)
            extra = False
            for o in other_dist:
                if any(_token_overlap(o, s) for s in seed_dist):
                    continue
                if any(_token_overlap(o, s) for s in seed_tok):
                    continue
                extra = True
                break
            if not extra:
                continue
        elif other_nums:
            continue
        for cand in other.get("candidates") or []:
            if _same_performance_artists(rec, cand):
                return oname or oid
    return None


def is_cross_composer_generic_flag(flag: str) -> bool:
    """Wrong-work flags that mean a generic title hid another composer's work."""
    s = str(flag)
    if not s.startswith("wrong work:"):
        return False
    return (
        "already listed under" in s
        or "proposed for more than one composer" in s
        or "not distinctive across composers" in s
    )


def identity_review_flags(rec: dict, mb_title: str, mb_first_release: Optional[str],
                          confidence: Optional[int],
                          work: Optional[dict] = None,
                          sibling_numbers: Optional[set[str]] = None,
                          works: Optional[list] = None) -> list[str]:
    """Flags that block auto-accept. Humans still review clean matches too.

    A wrong-work flag is fatal for apply.py — it cannot be force-overridden.
    """
    flags: list[str] = []
    if confidence is None:
        flags.append("missing MusicBrainz confidence")
    elif confidence < IDENTITY_MIN_CONFIDENCE:
        flags.append(f"confidence {confidence} < {IDENTITY_MIN_CONFIDENCE}")
    want = str(rec.get("year") or "")[:4]
    got = str(mb_first_release or "")[:4]
    if want.isdigit() and got.isdigit():
        delta = abs(int(want) - int(got))
        if delta > 3:
            flags.append(f"date off by {delta} years ({want} vs {got})")
    if mb_title and COMPILATION_RE.search(mb_title):
        flags.append(f"compilation-like title: {mb_title!r}")
    if work and mb_title:
        seed_title = work.get("title") or ""
        catalogue = work.get("catalogue") or ""
        inc = collection_subset_incomplete(seed_title, mb_title, catalogue)
        if inc:
            flags.append(inc)
        composer = work.get("composer") or ""
        personnel = " ".join(
            x for x in (rec.get("director"), rec.get("ensemble"), rec.get("soloists"))
            if x
        )
        if not work_title_compatible(
            seed_title, mb_title, catalogue,
            composer=composer, personnel=personnel,
            sibling_numbers=sibling_numbers,
        ):
            flags.append(
                f"wrong work: MusicBrainz {mb_title!r} does not match seed "
                f"{seed_title!r}"
            )
        else:
            other = other_composer_same_generic_artists(rec, work, works)
            if other:
                flags.append(
                    f"wrong work: MusicBrainz {mb_title!r} matches artists "
                    f"already listed under {other} — {seed_title!r} is not "
                    f"distinctive across composers"
                )
            elif (
                _generic_instrument_form_only(seed_title)
                and _generic_instrument_form_only(mb_title)
                and not _COLLECTION_PLURAL_RE.search(mb_title or "")
                and not _mb_names_seed_composer(mb_title, composer)
                and not (
                    extract_catalogue_ids(catalogue)
                    & extract_catalogue_ids(mb_title)
                )
            ):
                flags.append(
                    f"unsigned composer: MB title {mb_title!r} does not name "
                    f"{composer} or catalogue"
                )
    return flags


def refresh_identity_eligibility(
    payload: dict, rec: Optional[dict] = None, work: Optional[dict] = None,
    sibling_numbers: Optional[set[str]] = None,
    works: Optional[list] = None,
) -> tuple[list[str], bool]:
    """Recompute flags against the current matcher.

    Stale harvest files may have empty review_flags and auto_accept_eligible
    true for matches that are now wrong-work. Queue/board must not trust that.
    """
    rec = rec or {}
    confidence = payload.get("confidence")
    if confidence is None and payload.get("match_score") is not None:
        try:
            confidence = int(payload["match_score"])
        except (TypeError, ValueError):
            confidence = None
    elif confidence is not None:
        try:
            confidence = int(confidence)
        except (TypeError, ValueError):
            confidence = None
    flags = identity_review_flags(
        rec,
        payload.get("mb_title") or "",
        payload.get("mb_first_release"),
        confidence,
        work=work,
        sibling_numbers=sibling_numbers,
        works=works,
    )
    eligible = (
        confidence is not None
        and confidence >= IDENTITY_MIN_CONFIDENCE
        and not flags
    )
    return flags, eligible


# ------------------------------------------------------------------ identity facts
# Copied from the WS/2 search hit when a token is actually present.
# first-release-date is NEVER session year. Nested release ids are NEVER
# the identity MBID (identity is a release-group).

FASSUNG_PATTERNS = (
    re.compile(r"\b(original\s+version|original\s+fassung|urfassung)\b", re.I),
    re.compile(
        r"\b((?:prague|prag|vienna|wiener|wien)\s+(?:version|fassung|edition))\b",
        re.I,
    ),
    re.compile(r"\b((?:nowak|haas)\s+(?:edition|fassung|version))\b", re.I),
    re.compile(r"\(\s*((?:nowak|haas)(?:\s+edition)?)\s*\)", re.I),
    re.compile(
        r"\b((?:s[uü]ssmayr|suessmayr)(?:\s*/\s*\w+)?(?:\s+\d{4})?\s+completion)\b",
        re.I,
    ),
    re.compile(r"\(\s*(s[uü]ssmayr|suessmayr)\s*\)", re.I),
    re.compile(
        r"\b((?:1887|1890)\s+(?:version|fassung|revision|edition))\b", re.I,
    ),
    re.compile(r"\(\s*(1887|1890)\s*\)"),
)
COMPLETENESS_HIGHLIGHTS_RE = re.compile(
    r"\b(highlights?|excerpts?|scenes\s+from)\b", re.I,
)
COMPLETENESS_COMPLETE_RE = re.compile(
    r"\b(complete|int[eé]grale|integral)\b", re.I,
)
LIVE_TOKEN_RE = re.compile(
    r"\b(live|in\s+concert|concert\s+recording|"
    r"public\s+(?:performance|recording))\b",
    re.I,
)
STUDIO_TOKEN_RE = re.compile(
    r"\b(studio(?:\s+(?:recording|cast))?)\b", re.I,
)
SESSION_YEAR_PATTERNS = (
    re.compile(r"\b(1[89]\d{2}|20\d{2})\s+recordings?\b", re.I),
    re.compile(r"\brecorded(?:\s+in)?\s+(1[89]\d{2}|20\d{2})\b", re.I),
    re.compile(r"\b(1[89]\d{2}|20\d{2})\s+sessions?\b", re.I),
)


def _unique_token_list(hits: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for h in hits:
        key = " ".join(h.split()).lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(" ".join(h.split()))
    return out


def identity_facts_from_mb(
    group: Optional[dict] = None, *,
    title: str = "",
    disambiguation: str = "",
    secondary_types: Optional[list] = None,
) -> dict:
    """Pull Fassung / completeness / session year / live-studio iff present.

    Reads only fields the harvest search already receives (title,
    disambiguation, secondary-types). Omits a key when the WS/2 hit lacks
    the token. Does not copy first-release-date into session_year. Does not
    mint a release MBID.
    """
    group = group or {}
    title = title or (group.get("title") or "")
    disamb = disambiguation if disambiguation else (group.get("disambiguation") or "")
    types = (
        list(secondary_types) if secondary_types is not None
        else list(group.get("secondary-types") or [])
    )
    blob = " ".join(x for x in (title, disamb) if x)
    out: dict = {}
    if disamb:
        out["mb_disambiguation"] = disamb
    if types:
        out["mb_secondary_types"] = types
    if group.get("primary-type"):
        out["mb_primary_type"] = group["primary-type"]

    fassung_hits: list[str] = []
    for pat in FASSUNG_PATTERNS:
        for m in pat.finditer(blob):
            tok = m.group(1) if m.lastindex else m.group(0)
            if tok:
                fassung_hits.append(tok)
    fassung_hits = _unique_token_list(fassung_hits)
    if fassung_hits:
        out["fassung"] = "; ".join(fassung_hits)

    completeness: list[str] = []
    if COMPLETENESS_HIGHLIGHTS_RE.search(blob):
        completeness.append("highlights")
    if COMPLETENESS_COMPLETE_RE.search(blob):
        completeness.append("complete")
    if completeness:
        out["completeness"] = "; ".join(completeness)

    live_bits: list[str] = []
    type_fold = {str(t).strip().lower() for t in types}
    if "live" in type_fold or LIVE_TOKEN_RE.search(blob):
        live_bits.append("live")
    if STUDIO_TOKEN_RE.search(blob):
        live_bits.append("studio")
    if live_bits:
        out["live_studio"] = "; ".join(live_bits)

    years: list[str] = []
    seen_years: set[str] = set()
    for pat in SESSION_YEAR_PATTERNS:
        for m in pat.finditer(blob):
            year = m.group(1)
            if year and year not in seen_years:
                seen_years.add(year)
                years.append(year)
    if len(years) == 1:
        out["session_year"] = years[0]
    # Multiple recording years in one title are ambiguous — omit.
    return out


def adapter_identity(rec: dict, work: dict, http: Http,
                     works: Optional[list] = None) -> list[Proposal]:
    """Resolve a candidate to a MusicBrainz release-group. CC0 data.

    Emits confidence and review flags. Matches below IDENTITY_MIN_CONFIDENCE
    are never auto_accept_eligible — a human must decide. Wrong-work titles
    (Piano Concertos under a Brandenburg candidate) are never eligible.
    """
    if rec.get("mbid"):
        return []
    artist = rec.get("director") or rec.get("ensemble") or rec.get("soloists") or ""
    terms = f'{work["title"]} AND artist:"{artist}"' if artist else work["title"]
    q = urllib.parse.urlencode({"query": terms, "fmt": "json", "limit": 5})
    data = http.get(f"https://musicbrainz.org/ws/2/release-group/?{q}")
    if not data:
        return []
    groups = data.get("release-groups", [])
    if not groups:
        return []

    want = str(rec.get("year", ""))[:4]

    def rank(g):
        d = (g.get("first-release-date") or "")[:4]
        near = abs(int(d) - int(want)) if d.isdigit() and want.isdigit() else 999
        title = g.get("title") or ""
        # Prefer release-groups that actually name the seeded work.
        wrong = 0 if work_title_compatible(
            work.get("title") or "", title, work.get("catalogue") or "",
            composer=work.get("composer") or "",
            personnel=" ".join(
                x for x in (rec.get("director"), rec.get("ensemble"), rec.get("soloists"))
                if x
            ),
        ) else 1
        return (wrong, near, -g.get("score", 0))

    ranked = sorted(groups, key=rank)
    best = ranked[0]
    confidence = best.get("score")
    if confidence is not None:
        confidence = int(confidence)
    mb_title = best.get("title") or ""
    mb_first = best.get("first-release-date")
    flags = identity_review_flags(
        rec, mb_title, mb_first, confidence, work=work, works=works,
    )
    eligible = confidence is not None and confidence >= IDENTITY_MIN_CONFIDENCE and not flags

    alternatives = []
    for g in ranked[1:]:
        alt = {
            "mbid": g["id"],
            "mb_title": g.get("title"),
            "mb_first_release": g.get("first-release-date"),
            "confidence": g.get("score"),
            "mb_url": f"https://musicbrainz.org/release-group/{g['id']}",
        }
        alt_facts = identity_facts_from_mb(g)
        for key in ("fassung", "completeness", "session_year", "live_studio"):
            if key in alt_facts:
                alt[key] = alt_facts[key]
        alternatives.append(alt)

    payload = {
        "mbid": best["id"],
        "mb_title": mb_title,
        "mb_first_release": mb_first,
        "match_score": confidence,          # MusicBrainz search confidence 0–100
        "confidence": confidence,           # preferred name; not a critical verdict
        "auto_accept_eligible": eligible,
        "needs_human_review": True,         # identity always merges via human PR
        "uncertain": not eligible,
        "review_flags": flags,
        "mb_url": f"https://musicbrainz.org/release-group/{best['id']}",
        "query": terms,
        "seed": {
            "work": f'{work.get("composer")} — {work.get("title")}',
            "director": rec.get("director"),
            "ensemble": rec.get("ensemble"),
            "soloists": rec.get("soloists"),
            "label": rec.get("label"),
            "year": rec.get("year"),
        },
        "alternatives": alternatives,
    }
    # Honest omit: only store Fassung / completeness / session / live-studio
    # when the WS/2 search hit actually contains the token.
    payload.update(identity_facts_from_mb(best))
    return [Proposal(rec["id"], "identity", payload, "MusicBrainz", "cited")]


def adapter_editions(rec: dict, work: dict, http: Http) -> list[Proposal]:
    """Every physical release under the group: catno, barcode, format, year."""
    if not rec.get("mbid"):
        return []
    q = urllib.parse.urlencode({"release-group": rec["mbid"], "fmt": "json",
                                "inc": "labels+media", "limit": 25})
    data = http.get(f"https://musicbrainz.org/ws/2/release?{q}")
    if not data:
        return []
    editions = []
    for r in data.get("releases", []):
        li = (r.get("label-info") or [{}])[0]
        editions.append({
            "mbid": r["id"], "year": (r.get("date") or "")[:4],
            "catno": li.get("catalog-number"),
            "label": (li.get("label") or {}).get("name"),
            "barcode": r.get("barcode") or None,
            "format": (r.get("media") or [{}])[0].get("format"),
            "country": r.get("country"),
            "verified": False,
        })
    return [Proposal(rec["id"], "editions", {"editions": editions}, "MusicBrainz", "cited")] if editions else []


def _caa_front_from_meta(meta: dict) -> Optional[str]:
    """Pick a front-image hotlink from CAA JSON. Never download binary bytes."""
    for img in meta.get("images") or []:
        if not img.get("front"):
            continue
        thumbs = img.get("thumbnails") or {}
        # Prefer the 500px thumb URL; fall back to declared image URL.
        return thumbs.get("500") or thumbs.get("large") or img.get("image")
    return None


def adapter_cover(rec: dict, work: dict, http: Http) -> list[Proposal]:
    """Cover Art Archive existence check via JSON metadata (hotlink only).

    Resolution ladder (HARVEST_STRATEGY Part 2), stopping at the first hit:
      1. CAA by release (when a release mbid is already known)
      2. CAA by release-group (identity mbid)
    Misses are proposals too — a contribution prompt, not a failure.
    Images are never downloaded or committed; Discogs is never fetched.
    """
    if not rec.get("mbid"):
        return []

    release_mbid = rec.get("release_mbid")
    rg_mbid = rec["mbid"]
    image = None
    step = None
    checked = []

    if release_mbid:
        url = f"https://coverartarchive.org/release/{release_mbid}"
        checked.append(url)
        meta = http.get(url)
        if isinstance(meta, dict):
            image = _caa_front_from_meta(meta)
            if image:
                step = "caa-release"

    if image is None:
        url = f"https://coverartarchive.org/release-group/{rg_mbid}"
        checked.append(url)
        meta = http.get(url)
        if isinstance(meta, dict):
            image = _caa_front_from_meta(meta)
            if image:
                step = "caa-release-group"

    hit = image is not None
    # Stable hotlink shape for the site/render path (release-group front-500).
    hotlink = (
        f"https://coverartarchive.org/release-group/{rg_mbid}/front-500"
        if hit and step == "caa-release-group"
        else image
    )
    payload = {
        "image": hotlink if hit else None,
        "image_url": image,
        "status": "hit" if hit else "miss",
        "resolution_step": step,
        "release_group_mbid": rg_mbid,
        "release_mbid": release_mbid,
        "checked_urls": checked,
        "source": "Cover Art Archive",
        "rehost": False,
        "note": (
            "Hotlink only — do not download or commit image binaries. "
            "Missing sleeves should be uploaded upstream to MusicBrainz / CAA."
        ),
    }
    if not hit:
        payload["contribution_prompt"] = {
            "action": "photograph_sleeve_and_upload_to_musicbrainz",
            "musicbrainz_rg": f"https://musicbrainz.org/release-group/{rg_mbid}",
            "why": "CAA has no front image yet; the archive grows — re-check fortnightly.",
        }
    return [Proposal(rec["id"], "cover", payload, "Cover Art Archive", "cited")]


CITATION_TARGETS = [
    ("Gramophone", "review or Collection survey", "interpretation"),
    ("Diapason", "review, d'Or award, or guide entry", "interpretation"),
    ("Penguin Guide", "entry, any edition", "interpretation"),
    ("ClassicsToday", "review with numeric artistic/sound pair", "both"),
    ("Fanfare / MusicWeb", "review", "interpretation"),
    ("Remastering documentation", "engineer's notes, label technical sheet", "sound"),
]


def adapter_citation(rec: dict, work: dict, http: Http) -> list[Proposal]:
    """No network. Emits the work that a reading agent or a human must do,
    with the exact question, so nobody is asked to 'find some reviews'."""
    label = " — ".join(x for x in (rec.get("soloists"), rec.get("director"),
                                   rec.get("ensemble")) if x)
    tasks = [{
        "publication": pub, "looking_for": what, "axis": axis,
        "must_return": ["locator (URL, issue, or page)", "normalised score 0–3",
                        "one-sentence characterisation in the guide's own words"],
        "must_not_return": ["copied review text"],
    } for pub, what, axis in CITATION_TARGETS]
    return [Proposal(rec["id"], "citation_task",
                     {"recording": f"{label} ({rec.get('label')}, {rec.get('year')})",
                      "work": f'{work["composer"]} — {work["title"]}',
                      "sound_axis_note": "Sound must be attached to a specific edition, not the recording.",
                      "tasks": tasks},
                     VERSION, "draft")]


ADAPTERS: dict[str, Callable] = {
    "identity": adapter_identity,
    "editions": adapter_editions,
    "cover": adapter_cover,
    "citation": adapter_citation,
}

# Order matters: editions and covers need an mbid that identity supplies.
STAGES = ["identity", "editions", "cover", "citation"]


# ------------------------------------------------------------------ queue

def prominence(work: dict, rec: dict) -> int:
    """Cheap priority. Works with no assessment at all come first, then
    recordings whose year suggests they are the historically central ones."""
    p = 0
    if not work.get("assessed"):
        p += 10
    if rec.get("year", "").isdigit() and int(rec["year"]) < 1975:
        p += 3
    return p


def queue(seed: dict, state: dict) -> Iterable[tuple[str, dict, dict]]:
    items = []
    for work in seed["works"]:
        for rec in work["candidates"]:
            done = state.get(rec["id"], {})
            for stage in STAGES:
                # Preconditions. editions and cover need an mbid, which only
                # arrives when an identity proposal has been reviewed and
                # merged. A run therefore resolves identity; the next run,
                # after the pull request lands, goes deeper. The pipeline is
                # deliberately not allowed to build on unreviewed guesses.
                if stage in ("editions", "cover") and not rec.get("mbid"):
                    continue
                last = done.get(stage)
                if last:
                    age = datetime.now(timezone.utc) - datetime.fromisoformat(last["at"])
                    if last.get("hit"):
                        wait = STALE["cover_miss" if stage == "cover" else stage]
                    else:
                        # A miss may be a genuine absence or a bad day on the
                        # network. Back off rather than hammering either way.
                        wait = timedelta(days=min(7 * last.get("attempts", 1), 60))
                    if age < wait:
                        continue
                items.append((prominence(work, rec), stage, work, rec))
                break                       # one stage per recording per run
    items.sort(key=lambda x: -x[0])
    for _, stage, work, rec in items:
        yield stage, work, rec


# ------------------------------------------------------------------ reporting

def _seed_counts(seed: dict) -> tuple[int, int, int]:
    n_works = len(seed.get("works", []))
    n_cands = sum(len(w.get("candidates") or []) for w in seed.get("works", []))
    n_mbid = sum(1 for w in seed.get("works", [])
                 for r in (w.get("candidates") or []) if r.get("mbid"))
    return n_works, n_cands, n_mbid


def write_pr_body(path: pathlib.Path, *, stamp: str, version: str, contact: str,
                  budget: int, spent: int, planned: dict[str, int],
                  proposals: list[Proposal], seed: dict, dry: bool) -> None:
    n_works, n_cands, n_mbid = _seed_counts(seed)
    identities = [p for p in proposals if p.kind == "identity"]
    covers = [p for p in proposals if p.kind == "cover"]
    eligible = sum(1 for p in identities if p.payload.get("auto_accept_eligible"))
    uncertain = sum(1 for p in identities if p.payload.get("uncertain"))
    cover_hits = sum(1 for p in covers if p.payload.get("status") == "hit")
    cover_miss = sum(1 for p in covers if p.payload.get("status") == "miss")
    have_ids = {p.target for p in identities}
    unresolved = [
        c["id"]
        for w in seed.get("works", [])
        for c in (w.get("candidates") or [])
        if c["id"] not in have_ids and not c.get("mbid")
    ]

    title = f"# Harvest {stamp}" + (" · DRY RUN (plan only)" if dry else "")
    body = [
        title, "",
        f"`{version}` · contact `{contact}` · budget **{budget}** · "
        f"{'planned ' if dry else ''}**{spent}** requests · "
        f"**{len(proposals)}** proposals",
        "",
        "## Expected cost",
        "",
        f"- Seed: **{n_works}** works · **{n_cands}** candidates · "
        f"**{n_mbid}** already have an mbid",
        f"- Budget cap: **{budget}** requests (MusicBrainz ~1 req/s; CAA ~0.6s gap)",
        f"- This run: **{spent}** network request{'s' if spent != 1 else ''}"
        + (" (not sent — dry-run)" if dry else ""),
        f"- Wall-clock if live: ~{max(spent, 1)}–{spent + 30}s under polite rate limits",
        "",
        "| Stage | Planned |",
        "|---|---|",
    ]
    body += [f"| {k} | {v} |" for k, v in sorted(planned.items())] or ["| — | 0 |"]

    if dry:
        body += [
            "",
            "## Dry-run notes",
            "",
            "- No MusicBrainz / CAA requests were made.",
            "- Editions and covers stay gated on a human-merged mbid "
            "(pipeline does not build on unreviewed identity guesses).",
            "- After this plan is accepted, re-run without `--dry-run` with the "
            "same budget.",
        ]
    else:
        body += [
            "",
            "## Identity confidence",
            "",
            f"- Identity proposals: **{len(identities)}** / {n_cands} candidates",
            f"- `auto_accept_eligible` (confidence ≥ {IDENTITY_MIN_CONFIDENCE}, "
            f"no compilation/date flags): **{eligible}**",
            f"- Uncertain / must stay for human review: **{uncertain}**",
            f"- Unresolved (no MusicBrainz hit this run): **{len(unresolved)}**",
            "- **Do not auto-accept below 80.** Reject compilations, samplers, "
            "wrong-decade matches.",
            "",
            "## Covers (Cover Art Archive only)",
            "",
            f"- Cover proposals: **{len(covers)}** · hits **{cover_hits}** · "
            f"misses **{cover_miss}**",
            "- Cover stage stays gated until identity mbids are human-merged "
            "(pipeline does not build on unreviewed guesses).",
            "- When covers run: CAA JSON hotlinks only — no image binaries, "
            "no Discogs. Misses include an upstream upload prompt.",
        ]
        if unresolved:
            body += ["", "### Unresolved candidates", ""]
            body += [f"- `{u}`" for u in unresolved]

        if identities:
            body += ["", "### Identity review table", "",
                     "| Target | Seed | MusicBrainz | Conf. | Eligible | Flags |",
                     "|---|---|---|---|---|---|"]
            for p in identities:
                s = p.payload.get("seed") or {}
                seed_s = f"{s.get('director') or s.get('soloists') or '—'}; " \
                         f"{s.get('label')}, {s.get('year')}"
                mb = f"{p.payload.get('mb_title')} ({p.payload.get('mb_first_release')})"
                flags = "; ".join(p.payload.get("review_flags") or []) or ""
                elig = "yes" if p.payload.get("auto_accept_eligible") else "**no**"
                body.append(
                    f"| `{p.target}` | {seed_s} | {mb} | "
                    f"{p.payload.get('confidence')} | {elig} | {flags} |"
                )

        if covers:
            body += ["", "### Cover proposals", "",
                     "| Target | Status | Step | Hotlink |",
                     "|---|---|---|---|"]
            for p in covers:
                body.append(
                    f"| `{p.target}` | {p.payload.get('status')} | "
                    f"{p.payload.get('resolution_step') or '—'} | "
                    f"{p.payload.get('image') or '—'} |"
                )

    body += [
        "",
        "## Review checklist",
        "",
        "- [ ] Identity matches are the right recording, not a compilation / sampler",
        f"- [ ] No identity with confidence < {IDENTITY_MIN_CONFIDENCE} is treated "
        "as auto-accept",
        "- [ ] Rows flagged `wrong work:` are rejected — never apply "
        "(Piano Concertos must not land on Brandenburg, etc.)",
        "- [ ] Ensemble names (e.g. The English Concert) are personnel, not "
        "work titles",
        "- [ ] Uncertain rows reviewed against MusicBrainz (`mb_url`) before merge",
        "- [ ] Cover payloads are CAA / MusicBrainz hotlinks only (no binaries, "
        "no Discogs)",
        "- [ ] Barcodes belong to the edition claimed (editions stage)",
        "- [ ] No review text has been copied into any payload",
        "- [ ] Every score carries a locator, or it stays `draft`",
        "",
        "## Stop",
        "",
        "Human identity review gate. Do not begin editions/covers apply until "
        "mbids are ratified.",
    ]
    path.write_text("\n".join(body) + "\n", "utf-8")


# ------------------------------------------------------------------ main

def merge_proposals(existing: list[dict], new: list[Proposal]) -> list[dict]:
    """Upsert by (target, kind) so a resume run does not erase earlier work."""
    by_key: dict[tuple[str, str], dict] = {}
    for raw in existing:
        by_key[(raw.get("target", ""), raw.get("kind", ""))] = raw
    for p in new:
        by_key[(p.target, p.kind)] = asdict(p)
    return list(by_key.values())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", type=pathlib.Path)
    ap.add_argument("--contact", default="maintainer@example.org")
    ap.add_argument("--budget", type=int, default=300)
    ap.add_argument("--dry-run", action="store_true",
                    help="plan the run and count requests without making them")
    ap.add_argument("--only", default="",
                    help="comma-separated stages to run (default: all). "
                         "Example: --only identity,cover")
    args = ap.parse_args()

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    if only and not only.issubset(set(STAGES)):
        ap.error(f"--only entries must be in {STAGES}")

    seed = json.loads(args.seed.read_text("utf-8"))
    state_path = CACHE / "harvest_state.json"
    state = json.loads(state_path.read_text("utf-8")) if state_path.exists() else {}

    http = Http(args.contact, args.budget, dry=args.dry_run)
    proposals: list[Proposal] = []
    planned: dict[str, int] = {}

    n_works, n_cands, _ = _seed_counts(seed)
    print(f"{VERSION} · {n_works} works · {n_cands} candidates · "
          f"budget {args.budget} requests"
          + (" · DRY RUN" if args.dry_run else "")
          + (f" · only {','.join(sorted(only))}" if only else ""))

    try:
        for stage, work, rec in queue(seed, state):
            if only and stage not in only:
                continue
            planned[stage] = planned.get(stage, 0) + 1
            if args.dry_run and stage != "citation":
                http.spent += 1
                if http.spent >= http.budget:
                    raise BudgetExhausted()
                continue
            print(f"  [{stage}] {rec['id']}")
            if stage == "identity":
                got = adapter_identity(
                    rec, work, http, works=seed.get("works") or [],
                )
            else:
                got = ADAPTERS[stage](rec, work, http)
            # Transient transport failures must not advance the cursor into a
            # week-long backoff — retry next run (or later in this budget).
            if not got and http.last_status == "error":
                print("    transient failure — cursor not advanced")
                continue
            proposals.extend(got)
            prev = state.setdefault(rec["id"], {}).get(stage, {})
            state[rec["id"]][stage] = {
                "at": datetime.now(timezone.utc).isoformat(),
                "hit": bool(got),
                "attempts": 0 if got else prev.get("attempts", 0) + 1,
            }
    except BudgetExhausted:
        print("  budget reached — stopping cleanly, cursor kept")

    OUT.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_path = OUT / f"proposals-{stamp}.json"

    if not args.dry_run:
        CACHE.mkdir(exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2), "utf-8")
        existing: list[dict] = []
        if out_path.exists():
            try:
                prev = json.loads(out_path.read_text("utf-8"))
                if isinstance(prev, list):
                    existing = prev
            except json.JSONDecodeError:
                existing = []
        merged = merge_proposals(existing, proposals)
        out_path.write_text(
            json.dumps(merged, indent=2, ensure_ascii=False), "utf-8")
        # Report on the merged set so PR_BODY reflects the full day file.
        report_props = [
            Proposal(
                target=m["target"], kind=m["kind"], payload=m["payload"],
                source=m["source"], provenance=m["provenance"],
                created=m.get("created") or datetime.now(timezone.utc).isoformat(),
            )
            for m in merged
        ]
    else:
        report_props = proposals

    write_pr_body(
        OUT / "PR_BODY.md",
        stamp=stamp, version=VERSION, contact=args.contact,
        budget=args.budget, spent=http.spent, planned=planned,
        proposals=report_props, seed=seed, dry=args.dry_run,
    )

    n_wrote = len(report_props) if not args.dry_run else len(proposals)
    print(f"\n{http.spent} requests · {len(proposals)} new / {n_wrote} in file")
    for k, v in sorted(planned.items()):
        print(f"  {k:<10} {v:>4} queued")
    if args.dry_run:
        print(f"wrote {OUT}/PR_BODY.md (plan only — no proposals file, state untouched)")
    else:
        print(f"wrote {out_path} and PR_BODY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
