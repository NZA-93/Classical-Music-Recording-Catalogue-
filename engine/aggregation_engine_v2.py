#!/usr/bin/env python3
"""
aggregation_engine_v2.py — Critical Discography, algorithm v2.0

What changed from v1.0
----------------------
1. Two axes, deliberately separated by *what they belong to*:
     interpretation  -> belongs to the recording   (Pinnock 1982, whenever you play it)
     sound           -> belongs to the edition     (which transfer of it you own)
   This is the hinge of the whole guide. Conflating them is why every other
   resource fails the second-hand buyer.

2. Provenance tiers. A statement's weight is multiplied by how well it is
   cited, not only by who said it. This is what lets the catalogue accept
   agent- and reader-supplied material without being poisoned by it:
   an uncited claim still enters, but it moves the score almost not at all
   until someone attaches a locator.

3. Editions carry catalogue numbers and barcodes, so a disc in the hand can
   be matched to a verdict.

4. Listening anchors and reception periods are first-class fields, because
   they are the part that builds a culture rather than settling a purchase.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import pathlib
from typing import Dict, Optional

ALGORITHM_VERSION = "2.0"

# Composer rollup is shown only when enough ratified interpretation signal exists.
# Below these floors the honest value is null — not a low score.
COMPOSER_MIN_STRONG = 3
COMPOSER_MIN_RECORDINGS = 2


# ---------------------------------------------------------------- weighting

class Cls(Enum):
    CRITIC = "independent critic"
    SURVEY = "specialist survey"
    AWARD = "major award"
    ENGINEER = "engineering / mastering literature"
    SECONDARY = "secondary literature"
    PROMO = "label promo"
    RETAIL = "retailer editorial"
    READER = "reader contribution"


BASE_WEIGHT = {
    Cls.CRITIC: 0.90,
    Cls.SURVEY: 0.85,
    Cls.AWARD: 0.90,
    Cls.ENGINEER: 0.88,     # technical writing on transfers, when it is real
    Cls.SECONDARY: 0.75,
    Cls.PROMO: 0.25,
    Cls.RETAIL: 0.30,
    Cls.READER: 0.35,
}


class Prov(Enum):
    """How well the statement is pinned down."""
    CITED = "cited"            # source + locator (URL, issue, page)
    ATTRIBUTED = "attributed"  # source named, no locator
    DRAFT = "draft"            # no citation yet — machine or reader draft


PROV_FACTOR = {Prov.CITED: 1.00, Prov.ATTRIBUTED: 0.70, Prov.DRAFT: 0.35}


@dataclass
class Statement:
    source: str
    cls: Cls
    axis: str                       # "interpretation" | "sound"
    score: float                    # 0–3
    text: str
    prov: Prov = Prov.ATTRIBUTED
    year: Optional[int] = None
    conflict: bool = False
    edition: Optional[str] = None   # sound statements attach to one edition
    # ADR-001: album awards name every work they cover. Shared across rows so
    # a three-symphony Grammy cannot mint three independent Référence signals.
    covers_works: Optional[tuple] = None
    locator: Optional[str] = None   # URL, issue, or page — evidence, never a claim

    def weight(self) -> float:
        w = BASE_WEIGHT[self.cls] * PROV_FACTOR[self.prov]
        if self.conflict and self.cls not in (Cls.PROMO, Cls.RETAIL):
            w = max(0.10, w - 0.50)
        return round(w, 3)

    def is_strong(self) -> bool:
        """Independent and at least attributed. Provenance scales a statement's
        pull on the mean; it does not decide whether the source is a serious
        one. Confidence therefore counts sources, not their discounted weight."""
        return (BASE_WEIGHT[self.cls] >= 0.80
                and self.prov is not Prov.DRAFT
                and not self.conflict)

    def signal_key(self) -> tuple:
        """Identity of a benchmark signal. Album awards collapse on
        (source, frozenset(covers_works)) so duplicates count once (ADR-001)."""
        if self.covers_works and len(self.covers_works) > 1:
            return ("album_award", self.source, frozenset(self.covers_works))
        if self.covers_works:
            return ("award", self.source, frozenset(self.covers_works))
        return ("stmt", self.source, self.text[:80])


@dataclass
class Edition:
    id: str
    label: str
    catno: str
    year: str
    fmt: str
    transfer: str                   # what this edition actually did to the sound
    barcode: Optional[str] = None
    mbid: Optional[str] = None
    verified: bool = False          # has a human checked the catalogue data


@dataclass
class Anchor:
    where: str                      # movement, scene, aria
    listen_for: str
    timing: Optional[str] = None    # filled by contributors; absent is honest


@dataclass
class Period:
    decade: str
    note: str


@dataclass
class Recording:
    id: str
    work_id: str
    soloists: str
    director: str
    ensemble: str
    published: str
    venue: str
    sessions: str
    producer: Optional[str]
    engineer: Optional[str]
    credits_status: str             # "cited" | "attributed" | "unknown"
    anchors: list[Anchor]
    reception: list[Period]
    editions: list[Edition]
    statements: list[Statement]


# ---------------------------------------------------------------- aggregation

def aggregate(stmts: list[Statement]) -> tuple[float, float, list[dict]]:
    if not stmts:
        return 0.0, 0.0, []
    num = den = 0.0
    strong = 0
    for s in stmts:
        w = s.weight()
        num += w * s.score
        den += w
        if s.is_strong():
            strong += 1
    S = num / den if den else 0.0
    scores = [s.score for s in stmts]
    var = statistics.variance(scores) if len(scores) > 1 else 0.0
    conf = min(1.0, (strong / 4.0) * (1.0 - min(var / 2.0, 0.8)))
    contrib = [{
        "source": s.source, "class": s.cls.value, "provenance": s.prov.value,
        "score": round(s.score, 2), "weight": s.weight(), "conflict": s.conflict,
        "text": s.text,
        "locator": s.locator,
    } for s in stmts]
    return S, conf, contrib


def derive_prov(source: str, locator: Optional[str]) -> Prov:
    """Provenance is derived from evidence (AGENTS §8), never from a claim."""
    if locator:
        return Prov.CITED
    if source:
        return Prov.ATTRIBUTED
    return Prov.DRAFT


def stars(S: float) -> int:
    return 3 if S >= 2.60 else 2 if S >= 1.70 else 1 if S >= 0.80 else 0


BENCHMARK_WORDS = ("reference", "benchmark", "indispensable", "unsurpassed",
                   "definitive", "landmark", "greatest")


def is_reference(S: float, conf: float, stmts: list[Statement]) -> bool:
    """Interpretation only. Sound never buys a Référence.

    ADR-001: an album award covering n works is one shared benchmark signal,
    not one per work. Signals are deduped by Statement.signal_key() so a
    thrice-ingested three-symphony Grammy still counts as one.
    """
    if S < 2.70 or conf < 0.55:
        return False
    keys = set()
    for s in stmts:
        if s.axis != "interpretation" or not s.is_strong():
            continue
        # Major awards count as a benchmark signal without needing the word
        # "reference" in a one-line characterisation; other classes still need
        # explicit benchmark language.
        is_award = s.cls is Cls.AWARD
        has_words = any(w in s.text.lower() for w in BENCHMARK_WORDS)
        if not (is_award or has_words):
            continue
        keys.add(s.signal_key())
    return len(keys) >= 3


TRANSFER_VERDICT = (
    (2.45, "preferred transfer"),
    (2.00, "sound and serviceable"),
    (0.00, "pass if you can"),
)


def edition_verdict(S: float, n: int) -> str:
    if n == 0:
        return "not yet assessed"
    for floor, label in TRANSFER_VERDICT:
        if S >= floor:
            return label
    return "not yet assessed"


def aggregate_composer(
    recordings: list[Recording],
    *,
    composer: str,
    composer_id: str,
    dates: str = "",
) -> dict:
    """Roll up interpretation statements across a composer's assessed recordings.

    This is not a new judgement. It reuses Statement.weight() so review *origin*
    (source class × provenance × conflict) still governs the mean. Signed
    editorial entries are never inputs. Returns interpretation=None when the
    evidence floor is not met.
    """
    interp: list[Statement] = []
    assessed_ids: list[str] = []
    for rec in recordings:
        rec_interp = [s for s in rec.statements if s.axis == "interpretation"]
        if rec_interp:
            assessed_ids.append(rec.id)
            interp.extend(rec_interp)

    by_class: Dict[str, int] = {}
    by_prov: Dict[str, int] = {}
    for s in interp:
        by_class[s.cls.value] = by_class.get(s.cls.value, 0) + 1
        by_prov[s.prov.value] = by_prov.get(s.prov.value, 0) + 1

    strong = sum(1 for s in interp if s.is_strong())
    floor_ok = (
        strong >= COMPOSER_MIN_STRONG
        and len(assessed_ids) >= COMPOSER_MIN_RECORDINGS
    )

    if not interp or not floor_ok:
        return {
            "id": composer_id,
            "composer": composer,
            "dates": dates,
            "interpretation": None,
            "confidence": None,
            "n_statements": len(interp),
            "n_strong": strong,
            "n_recordings_assessed": len(assessed_ids),
            "sources_by_class": by_class,
            "sources_by_provenance": by_prov,
            "note": "rollup withheld until enough cited independent sources exist",
        }

    S, conf, contrib = aggregate(interp)
    return {
        "id": composer_id,
        "composer": composer,
        "dates": dates,
        "interpretation": round(S, 3),
        "confidence": round(conf, 3),
        "n_statements": len(interp),
        "n_strong": strong,
        "n_recordings_assessed": len(assessed_ids),
        "sources_by_class": by_class,
        "sources_by_provenance": by_prov,
        "sources": contrib,
        "note": "weighted rollup of ratified interpretation statements; origin = class × provenance",
    }


EDITORIAL: Dict[str, dict] = {}


def run(rec: Recording) -> dict:
    interp = [s for s in rec.statements if s.axis == "interpretation"]
    S_i, conf_i, contrib_i = aggregate(interp)

    editions = []
    for ed in rec.editions:
        snd = [s for s in rec.statements if s.axis == "sound" and s.edition == ed.id]
        S_s, conf_s, contrib_s = aggregate(snd)
        editions.append({
            "id": ed.id, "label": ed.label, "catno": ed.catno, "year": ed.year,
            "format": ed.fmt, "transfer": ed.transfer, "barcode": ed.barcode,
            "mbid": ed.mbid, "verified": ed.verified,
            "sound": round(S_s, 3) if snd else None,
            "sound_confidence": round(conf_s, 3) if snd else None,
            "verdict": edition_verdict(S_s, len(snd)),
            "sources": contrib_s,
        })

    scored = [e for e in editions if e["sound"] is not None]
    best = max(scored, key=lambda e: e["sound"], default=None)

    assessed = bool(interp)
    ed_entry = EDITORIAL.get(rec.id)
    agg_stars = stars(S_i) if assessed else None
    divergence = (ed_entry["stars"] - agg_stars
                  if ed_entry and agg_stars is not None else None)

    return {
        "id": rec.id, "work": rec.work_id,
        "status": "assessed" if assessed else "awaiting sources",
        "editorial": ed_entry,
        "divergence": divergence,
        "soloists": rec.soloists, "director": rec.director, "ensemble": rec.ensemble,
        "published": rec.published,
        "engineering": {
            "venue": rec.venue, "sessions": rec.sessions,
            "producer": rec.producer, "engineer": rec.engineer,
            "status": rec.credits_status,
        },
        "interpretation": round(S_i, 3) if assessed else None,
        "confidence": round(conf_i, 3) if assessed else None,
        "stars": stars(S_i) if assessed else None,
        "reference": is_reference(S_i, conf_i, interp) if assessed else False,
        "sound_best": best["sound"] if best else None,
        "sound_best_edition": best["id"] if best else None,
        "anchors": [a.__dict__ for a in rec.anchors],
        "reception": [p.__dict__ for p in rec.reception],
        "editions": editions,
        "sources": contrib_i,
        "algorithm_version": ALGORITHM_VERSION,
        "built": datetime.now(timezone.utc).date().isoformat(),
    }


# ---------------------------------------------------------------- catalogue
# Editorial truth. In the repository this lives in /data/*.yaml; it is inline
# here so the first integration runs from a single file.
#
# NOTE ON HONESTY: production credits marked "cited" were taken from release
# documentation surfaced during research. The sound-axis statements below are
# a DRAFT scaffold — they carry Prov.DRAFT, which cuts their weight to about a
# third, and every edition shows its sourcing state in the interface. Nothing
# here should be read as established critical opinion until it is cited.

def catalogue() -> list[Recording]:
    return [
        Recording(
            id="bach_brandenburg_pinnock",
            work_id="bach_brandenburg",
            soloists="Trevor Pinnock, harpsichord",
            director="Trevor Pinnock",
            ensemble="The English Concert",
            published="Archiv, 1982",
            venue="Henry Wood Hall, London",
            sessions="1982",
            producer="Andreas Holschneider",
            engineer=None,
            credits_status="attributed",
            anchors=[
                Anchor("No. 5, first movement", "The harpsichord cadenza — Pinnock plays it as an argument rather than a display, and the ensemble waits on him rather than the reverse."),
                Anchor("No. 6, second movement", "Two violas alone. Listen for how little vibrato is used to shape the line, and how the phrase still bends."),
                Anchor("No. 3, outer movements", "Concertino and ripieno stay separable throughout; a good test of whether your copy has been compressed."),
            ],
            reception=[
                Period("1980s", "Received as the accessible face of period practice: the set that persuaded listeners who found Harnoncourt astringent."),
                Period("1990s–2000s", "Settles into the standard library recommendation; the Penguin Guide keeps it in the front rank across editions."),
                Period("2010s–", "Still cited at the head of surveys, now as much for consistency as for novelty. Pinnock's 2007 remake divides opinion — broader, some say safer."),
            ],
            editions=[
                Edition("pinnock_archiv_lp", "Archiv Produktion", "2742 003", "1982", "2×LP",
                        "Original analogue issue.", verified=False),
                Edition("pinnock_archiv_cd", "Archiv Produktion", "410 500-2", "1983", "CD",
                        "First CD issue, Nos. 1–3. Early digital transfer of the 1982 tapes.",
                        barcode="028941050021", mbid="b0255dd1-324d-4608-92e5-1638831c77b8", verified=True),
                Edition("pinnock_archiv_2cd", "Archiv Produktion", "—", "1990s", "2×CD",
                        "Concertos coupled with the Orchestral Suites; the widely circulated second-hand set.",
                        mbid="fc2fcc01-a4ea-45fb-84ce-d88fd1e8196b", verified=True),
                Edition("pinnock_avie", "Avie", "AV2119", "2007", "2×CD",
                        "Different recording, not a transfer: European Brandenburg Ensemble, broader tempos.",
                        verified=False),
            ],
            statements=[
                Statement("Gramophone / classical-music.com survey", Cls.SURVEY, "interpretation", 2.95,
                          "Elegant simplicity, directness of expression and consistency of approach; a leading modern recommendation.",
                          Prov.ATTRIBUTED, 2024),
                Statement("Independent critical consensus", Cls.CRITIC, "interpretation", 2.90,
                          "Frequently placed at the head of recent surveys as an HIP benchmark; crisp articulation throughout.",
                          Prov.ATTRIBUTED, 2020),
                Statement("Penguin Guide, historical editions", Cls.SURVEY, "interpretation", 2.80,
                          "Long-standing recommendation; refined and stylish.", Prov.ATTRIBUTED, 2005),
                Statement("Archiv / Avie promotional text", Cls.PROMO, "interpretation", 3.00,
                          "The definitive period-instrument Brandenburgs of our time.", Prov.ATTRIBUTED, 2007, conflict=True),
                Statement("Secondary discographic literature", Cls.SECONDARY, "interpretation", 2.70,
                          "A reference point for clarity and rhythmic vitality among HIP cycles.", Prov.ATTRIBUTED, 2018),
                Statement("Draft technical note", Cls.ENGINEER, "sound", 2.60,
                          "Natural perspective, clear separation of concertino and ripieno, hall resonance well judged.",
                          Prov.DRAFT, edition="pinnock_archiv_cd"),
                Statement("Draft technical note", Cls.ENGINEER, "sound", 2.55,
                          "Same tapes, later mastering; slightly firmer bass, no obvious noise reduction.",
                          Prov.DRAFT, edition="pinnock_archiv_2cd"),
            ],
        ),
        Recording(
            id="bach_brandenburg_harnoncourt",
            work_id="bach_brandenburg",
            soloists="Alice Harnoncourt, Jürg Schaeftlein, Walter Holy and principals",
            director="Nikolaus Harnoncourt",
            ensemble="Concentus Musicus Wien",
            published="Teldec / Das Alte Werk, 1964",
            venue="Palais Schönburg, Vienna",
            sessions="April 1964",
            producer="Wolf Erichson (executive)",
            engineer=None,
            credits_status="cited",
            anchors=[
                Anchor("No. 1, first movement", "Hunting horns played as hunting horns — rough, forward, refusing to blend. The whole argument of the cycle is audible in thirty seconds."),
                Anchor("No. 4, first movement", "Solo violin phrasing shaped by rhetoric rather than line; note where Harnoncourt lifts before a strong beat."),
                Anchor("No. 2, slow movement", "Chamber scale. Four players, no conductor's blend, every entry exposed."),
            ],
            reception=[
                Period("1960s", "Received as provocation. Reviewers split between historical seriousness and complaints of thin, effortful playing."),
                Period("1970s–80s", "Becomes the reference point of the early-music argument; imitated widely enough that its roughness stops sounding strange."),
                Period("1990s–", "Reassessed as a founding document. Praise shifts from the playing itself to what the playing made possible."),
            ],
            editions=[
                Edition("harn_teldec_lp", "Telefunken Das Alte Werk", "SAWT 9459/60", "1964", "2×LP",
                        "Original analogue issue.", verified=False),
                Edition("harn_teldec_1992", "Teldec", "9031-77611-2", "1992", "2×CD",
                        "1992 digital remastering of the 1964 tapes; the common second-hand CD.",
                        barcode="090317761121", mbid="c11b8758-00d4-4868-bccf-2d830dc4ce0a", verified=True),
                Edition("harn_warner_box", "Warner Classics", "—", "2010s", "CD in box",
                        "Reissued inside Harnoncourt anthology boxes; transfer lineage not yet established.",
                        verified=False),
            ],
            statements=[
                Statement("Independent historical criticism", Cls.CRITIC, "interpretation", 2.85,
                          "Pioneering period-instrument cycle of enduring value; a foundational document.",
                          Prov.ATTRIBUTED, 2015),
                Statement("Specialist early-music survey", Cls.SURVEY, "interpretation", 2.75,
                          "Retains pioneering energy and chamber-scale intensity despite dry original sound.",
                          Prov.ATTRIBUTED, 2010),
                Statement("Teldec / Warner reissue notes", Cls.PROMO, "interpretation", 2.95,
                          "Historic landmark recording that changed Bach performance practice.",
                          Prov.ATTRIBUTED, 2021, conflict=True),
                Statement("Retrospective critical consensus", Cls.CRITIC, "interpretation", 2.80,
                          "Still regarded as a reference for its pioneering status and austere sonority.",
                          Prov.ATTRIBUTED, 2022),
                Statement("Draft technical note", Cls.ENGINEER, "sound", 2.10,
                          "Dry 1964 analogue; remarkable clarity of inner parts, little hall, limited bass extension.",
                          Prov.DRAFT, edition="harn_teldec_1992"),
            ],
        ),
        Recording(
            id="puccini_tosca_desabata",
            work_id="puccini_tosca",
            soloists="Maria Callas, Giuseppe Di Stefano, Tito Gobbi",
            director="Victor de Sabata",
            ensemble="Orchestra e Coro del Teatro alla Scala",
            published="EMI / Columbia, 1953",
            venue="Teatro alla Scala, Milan",
            sessions="10–21 August 1953",
            producer="Walter Legge",
            engineer=None,
            credits_status="cited",
            anchors=[
                Anchor("Act II, 'Vissi d'arte'", "Vulnerability and defiance in the same phrase. Listen to where Callas stops singing legato and starts speaking."),
                Anchor("Act II, Tosca and Scarpia", "Gobbi never raises the pressure by volume. The menace is in the timing of his answers."),
                Anchor("Act I, Te Deum", "De Sabata builds it without letting the chorus swamp Scarpia's line — a balance most stereo remakes lose."),
                Anchor("Act II, 'E avanti a lui tremava tutta Roma'", "Legge reportedly kept Callas on this one line for half an hour. Judge whether it was worth it."),
            ],
            reception=[
                Period("1950s", "An immediate commercial success and a critical event; praised for dramatic truth at a time when vocal beauty was the usual measure."),
                Period("1960s–70s", "Karajan's stereo Tosca arrives and the discussion becomes sound versus performance — a framing the guide still inherits."),
                Period("1980s–2000s", "Canonised. Appears at or near the top of nearly every opera survey; the mono limitation is treated as a price worth paying."),
                Period("2010s–", "Remastering becomes the live question. Which transfer you own now matters more than whether to own it."),
            ],
            editions=[
                Edition("tosca53_columbia_lp", "Columbia", "33CX 1094-95", "1953", "2×LP",
                        "Original mono issue.", verified=False),
                Edition("tosca53_emi_groc", "EMI", "—", "1997", "2×CD",
                        "Great Recordings of the Century series; earlier-generation digital transfer.",
                        mbid="90c4d760-736f-3dc3-8657-15dd4f0eb289", verified=False),
                Edition("tosca53_warner_2014", "Warner Classics", "—", "2014", "2×CD",
                        "Callas Remastered: new 24-bit transfers from original tapes.", verified=False),
                Edition("tosca53_pristine", "Pristine Audio", "—", "2010s", "download / CD-R",
                        "XR reprocessing; a different philosophy of restoration, and divisive on principle.",
                        verified=False),
            ],
            statements=[
                Statement("Gramophone / critical consensus", Cls.CRITIC, "interpretation", 3.00,
                          "Universally regarded as the dramatic benchmark; the Act II confrontation remains unmatched.",
                          Prov.ATTRIBUTED, 2020),
                Statement("Multiple independent opera surveys", Cls.SURVEY, "interpretation", 2.95,
                          "The greatest Tosca recording for many critics; a recording of permanent reference value.",
                          Prov.ATTRIBUTED, 2019),
                Statement("Warner / EMI reissue notes", Cls.PROMO, "interpretation", 3.00,
                          "The legendary 1953 recording — one of the greatest opera recordings ever made.",
                          Prov.ATTRIBUTED, 2023, conflict=True),
                Statement("Historical discographic literature", Cls.SECONDARY, "interpretation", 2.90,
                          "Landmark mono recording whose dramatic immediacy has never been surpassed.",
                          Prov.ATTRIBUTED, 2015),
                Statement("Independent critics, various", Cls.CRITIC, "interpretation", 2.95,
                          "Benchmark status confirmed across decades of critical writing.", Prov.ATTRIBUTED, 2021),
                Statement("Draft technical note", Cls.ENGINEER, "sound", 1.95,
                          "Mono. Legge's balance places the voices in a real theatre space; dynamic range limited by 1953 tape.",
                          Prov.DRAFT, edition="tosca53_emi_groc"),
                Statement("Draft technical note", Cls.ENGINEER, "sound", 2.50,
                          "Fresh transfer from original tapes; more air at the top and less congestion in ensembles.",
                          Prov.DRAFT, edition="tosca53_warner_2014"),
                Statement("Draft technical note", Cls.ENGINEER, "sound", 2.30,
                          "Ambient reprocessing adds space that was never recorded. Rewards or falsifies, depending on your view.",
                          Prov.DRAFT, edition="tosca53_pristine"),
            ],
        ),
        Recording(
            id="puccini_tosca_karajan",
            work_id="puccini_tosca",
            soloists="Leontyne Price, Giuseppe Di Stefano, Giuseppe Taddei",
            director="Herbert von Karajan",
            ensemble="Wiener Philharmoniker",
            published="Decca, 1962–63",
            venue="Sofiensaal, Vienna",
            sessions="24–30 September 1962",
            producer="John Culshaw",
            engineer="Gordon Parry",
            credits_status="cited",
            anchors=[
                Anchor("Act I, Te Deum", "Culshaw's staging: bells and chorus placed in depth, Scarpia forward. Stereo used dramatically, not decoratively."),
                Anchor("Act II, 'Vissi d'arte'", "Price shapes it in long breaths where Callas breaks it into speech. The clearest illustration of two whole traditions."),
                Anchor("Act III, prelude", "Vienna Philharmonic strings and Karajan's patience with orchestral sonority — the moment his critics and admirers both point at."),
            ],
            reception=[
                Period("1960s", "Welcomed as the modern Tosca the catalogue needed: stereo, and vocally distinguished enough to stand beside 1953."),
                Period("1970s–90s", "Holds its place as the stereo recommendation; Taddei's Scarpia gains admirers over time."),
                Period("2000s–", "Reassessed upward for engineering. Frequently cited as a demonstration of what Decca's team could do in 1962."),
            ],
            editions=[
                Edition("tosca62_decca_lp", "Decca", "5BB 123-4", "1963", "2×LP",
                        "Original stereo issue.", verified=True),
                Edition("tosca62_decca_2006", "Decca", "475 7522", "2006", "2×CD",
                        "96 kHz / 24-bit transfer; the standard modern CD.", verified=False),
                Edition("tosca62_pristine", "Pristine Audio", "PACO223", "2020s", "download / CD-R",
                        "Stereo XR remastering by Andrew Rose.", verified=True),
            ],
            statements=[
                Statement("Independent critical consensus", Cls.CRITIC, "interpretation", 2.90,
                          "Outstanding stereo alternative; Price sensuous and opulent, Karajan flexible and powerful.",
                          Prov.ATTRIBUTED, 2020),
                Statement("Specialist opera survey", Cls.SURVEY, "interpretation", 2.85,
                          "The finest stereo Tosca for many listeners; complementary to the de Sabata set.",
                          Prov.ATTRIBUTED, 2018),
                Statement("Decca promotional material", Cls.PROMO, "interpretation", 2.95,
                          "One of the greatest stereo opera recordings.", Prov.ATTRIBUTED, 2015, conflict=True),
                Statement("Secondary literature", Cls.SECONDARY, "interpretation", 2.75,
                          "Strongly recommended stereo account; Te Deum and Act III prelude especially imposing.",
                          Prov.ATTRIBUTED, 2016),
                Statement("Release documentation", Cls.ENGINEER, "sound", 2.75,
                          "Culshaw and Parry at the Sofiensaal: wide stage, natural perspective, firm orchestral definition.",
                          Prov.CITED, 1962, edition="tosca62_decca_lp"),
                Statement("Draft technical note", Cls.ENGINEER, "sound", 2.70,
                          "24-bit transfer preserves the stage; a small lift in level over earlier CD issues.",
                          Prov.DRAFT, edition="tosca62_decca_2006"),
                Statement("Draft technical note", Cls.ENGINEER, "sound", 2.60,
                          "XR remastering; tighter bass, brighter top, and the usual argument about whether that is the tape or the engineer.",
                          Prov.DRAFT, edition="tosca62_pristine"),
            ],
        ),
    ]


# ---------------------------------------------------------------- data loader
# Partial S2-01: recordings and statements may now live in data/ as JSON rather
# than in this file. Hardcoded entries remain until the full migration, and the
# four published scores must be unaffected by this path existing.

SCALE_TO_SCORE = {"award": 2.90, "editors_choice": 2.85, "rosette": 2.95}
CLS_BY_NAME = {c.value: c for c in Cls}
CLS_BY_NAME["major_award"] = Cls.AWARD


def _score_from(st: dict) -> Optional[float]:
    scale, v = st.get("scale"), st.get("value")
    if scale in SCALE_TO_SCORE:
        return SCALE_TO_SCORE[scale]
    if v is None:
        return None
    if scale == "stars_5":   return round(float(v) / 5 * 3, 2)
    if scale == "stars_3":   return round(float(v), 2)
    if scale == "ten_point": return round(float(v) / 10 * 3, 2)
    if scale == "percent":   return round(float(v) / 100 * 3, 2)
    return None


def load_editorial(root: str = "data") -> Dict[str, dict]:
    """Signed entries, keyed by recording id. ADR-002: these never enter the
    aggregate and the aggregate never constrains them. An entry without an
    author, a date and a revision does not publish."""
    import glob
    out: Dict[str, dict] = {}
    for path in sorted(glob.glob(f"{root}/editorial/*.json")):
        if pathlib.Path(path).name.startswith("_"):
            continue
        doc = json.load(open(path, encoding="utf-8"))
        for ent in doc.get("entries", []):
            if not (ent.get("author") and ent.get("date") and ent.get("revision")):
                continue                      # unsigned prose does not publish
            out[ent["recording"]] = ent
    return out


def load_from_data(root: str = "data") -> List[Recording]:
    """Read data/recordings/**/*.json plus their statements. Facts only; the
    assessment layer is whatever data/statements holds, and nothing else."""
    import glob
    out: List[Recording] = []
    for path in sorted(glob.glob(f"{root}/recordings/*/*.json")):
        doc = json.load(open(path, encoding="utf-8"))
        sp = path.replace("/recordings/", "/statements/")
        raw = json.load(open(sp, encoding="utf-8")) if pathlib.Path(sp).exists() else []

        for rec in doc["recordings"]:
            stmts = []
            for st in raw:
                if st["recording"] != rec["id"]:
                    continue
                score = _score_from(st)
                if score is None:
                    continue          # prose awaits a human; it does not guess
                covers = st.get("covers_works")
                locator = st.get("locator") or None
                stmts.append(Statement(
                    source=st["source"],
                    cls=CLS_BY_NAME.get(st.get("class", "independent_critic"), Cls.CRITIC),
                    axis=st["axis"],
                    score=score,
                    text=st.get("characterisation", ""),
                    prov=derive_prov(st["source"], locator),
                    conflict=bool(st.get("conflict", False)),
                    edition=st.get("edition"),
                    covers_works=tuple(covers) if covers else None,
                    locator=locator,
                ))
            out.append(Recording(
                id=rec["id"], work_id=doc["work_id"],
                soloists=rec["soloists"], director=rec["director"], ensemble=rec["ensemble"],
                published=rec["published"], venue=rec["venue"], sessions=rec["sessions"],
                producer=rec.get("producer"), engineer=rec.get("engineer"),
                credits_status=rec.get("credits_status", "unknown"),
                anchors=[Anchor(**a) for a in rec.get("anchors", [])],
                reception=[Period(**p) for p in rec.get("reception", [])],
                editions=[Edition(**ed) for ed in rec.get("editions", [])],
                statements=stmts,
            ))
    return out


WORKS = {
    "bach_brandenburg": {
        "composer": "Johann Sebastian Bach", "dates": "1685–1750",
        "title": "Brandenburg Concertos", "cat": "BWV 1046–1051 · 1721",
        "standfirst": "Six concertos sent to Christian Ludwig of Brandenburg, and the work on which every argument about baroque performance style eventually lands.",
    },
    "shostakovich/sym5": {
        "composer": "Dmitri Shostakovich", "dates": "1906–1975",
        "title": "Symphony No. 5", "cat": "Op. 47 · D minor · 1937",
        "standfirst": "Written after the Pravda attack and premiered to a half-hour ovation. Whether the finale is triumph or coercion is the argument, and every recording takes a side.",
    },
    "puccini_tosca": {
        "composer": "Giacomo Puccini", "dates": "1858–1924",
        "title": "Tosca", "cat": "Teatro Costanzi, Rome · 14 January 1900",
        "standfirst": "Three acts of political violence at close range, and the opera where a recording either has dramatic nerve or has nothing.",
    },
}


def _composer_id_from_work(work_id: str, composer_name: str) -> str:
    if "/" in work_id:
        return work_id.split("/", 1)[0]
    # legacy inline ids: bach_brandenburg, puccini_tosca
    slug = composer_name.lower()
    for token in ("johann sebastian ", "giacomo ", "dmitri ", "wolfgang amadeus ",
                  "ludwig van "):
        slug = slug.replace(token, "")
    slug = slug.replace(" ", "_")
    return {
        "Johann Sebastian Bach": "bach",
        "Giacomo Puccini": "puccini",
        "Dmitri Shostakovich": "shostakovich",
        "Ludwig van Beethoven": "beethoven",
        "Wolfgang Amadeus Mozart": "mozart",
    }.get(composer_name, slug)


if __name__ == "__main__":
    EDITORIAL.update(load_editorial())
    all_recs = catalogue() + load_from_data()
    results = [run(r) for r in all_recs]

    works = []
    for wid, meta in WORKS.items():
        works.append({**meta, "id": wid,
                      "recordings": [r for r in results if r["work"] == wid]})

    by_composer: Dict[str, list[Recording]] = {}
    composer_meta: Dict[str, tuple[str, str]] = {}
    for rec in all_recs:
        meta = WORKS.get(rec.work_id, {})
        name = meta.get("composer", "Unknown")
        dates = meta.get("dates", "")
        cid = _composer_id_from_work(rec.work_id, name)
        by_composer.setdefault(cid, []).append(rec)
        composer_meta[cid] = (name, dates)

    composers = [
        aggregate_composer(
            recs,
            composer=composer_meta[cid][0],
            composer_id=cid,
            dates=composer_meta[cid][1],
        )
        for cid, recs in sorted(by_composer.items())
    ]

    barcodes = {
        e["barcode"]: {"recording": r["id"], "edition": e["id"]}
        for r in results for e in r["editions"] if e.get("barcode")
    }

    out = {"algorithm_version": ALGORITHM_VERSION,
           "built": datetime.now(timezone.utc).date().isoformat(),
           "works": works,
           "composers": composers,
           "barcode_index": barcodes}

    with open("build/catalogue.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"algorithm v{ALGORITHM_VERSION}")
    for r in results:
        ed = len(r["editions"])
        assessed = sum(1 for e in r["editions"] if e["sound"] is not None)
        if r["interpretation"] is None:
            print(f"  {r['id']:<32} awaiting sources                     "
                  f"editions {assessed}/{ed} assessed")
        else:
            print(f"  {r['id']:<32} interp {r['interpretation']:.3f} "
                  f"({'★' * r['stars']}{' RÉFÉRENCE' if r['reference'] else ''})  "
                  f"best sound {r['sound_best'] if r['sound_best'] else '—'}  "
                  f"editions {assessed}/{ed} assessed")
    for c in composers:
        if c["interpretation"] is None:
            print(f"  composer:{c['id']:<24} rollup withheld "
                  f"({c['n_strong']} strong / {c['n_recordings_assessed']} recordings)")
        else:
            print(f"  composer:{c['id']:<24} rollup {c['interpretation']:.3f} "
                  f"conf {c['confidence']:.3f} · {c['n_statements']} stmts")
    print(f"\n{len(barcodes)} barcodes indexed · wrote catalogue.json")
