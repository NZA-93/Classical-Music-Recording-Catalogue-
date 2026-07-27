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
from typing import Optional

ALGORITHM_VERSION = "2.0"


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
    } for s in stmts]
    return S, conf, contrib


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


# ---------------------------------------------------------------- data loader

SCALE_TO_SCORE = {"award": 2.90, "editors_choice": 2.85, "rosette": 2.95}
CLS_BY_NAME = {c.value: c for c in Cls}
CLS_BY_NAME["major_award"] = Cls.AWARD
# Accept underscored aliases used in some contribution drafts.
CLS_BY_NAME["independent_critic"] = Cls.CRITIC
CLS_BY_NAME["specialist_survey"] = Cls.SURVEY


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
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
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
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        sp = path.replace("/recordings/", "/statements/")
        if pathlib.Path(sp).exists():
            with open(sp, encoding="utf-8") as fh:
                raw = json.load(fh)
        else:
            raw = []

        for rec in doc["recordings"]:
            stmts = []
            for st in raw:
                if st["recording"] != rec["id"]:
                    continue
                score = _score_from(st)
                if score is None:
                    continue          # prose awaits a human; it does not guess
                covers = st.get("covers_works")
                cls_key = st.get("class", "independent critic")
                stmts.append(Statement(
                    source=st["source"],
                    cls=CLS_BY_NAME.get(cls_key, Cls.CRITIC),
                    axis=st["axis"],
                    score=score,
                    text=st.get("characterisation", ""),
                    prov=Prov(st.get("provenance", "draft")),
                    year=st.get("year"),
                    conflict=bool(st.get("conflict", False)),
                    edition=st.get("edition"),
                    covers_works=tuple(covers) if covers else None,
                ))
            out.append(Recording(
                id=rec["id"], work_id=doc["work_id"],
                soloists=rec["soloists"], director=rec["director"], ensemble=rec["ensemble"],
                published=rec["published"], venue=rec["venue"], sessions=rec["sessions"],
                producer=rec.get("producer"), engineer=rec.get("engineer"),
                credits_status=rec.get("credits_status", "unknown"),
                anchors=[Anchor(where=a["where"], listen_for=a["listen_for"],
                                timing=a.get("timing"))
                         for a in rec.get("anchors", [])],
                reception=[Period(**p) for p in rec.get("reception", [])],
                editions=[Edition(
                    id=ed["id"], label=ed["label"], catno=ed["catno"],
                    year=ed["year"], fmt=ed["fmt"], transfer=ed["transfer"],
                    barcode=ed.get("barcode"), mbid=ed.get("mbid"),
                    verified=bool(ed.get("verified", False)),
                ) for ed in rec.get("editions", [])],
                statements=stmts,
            ))
    return out


WORKS = {
    "bach/brandenburg": {
        "composer": "Johann Sebastian Bach", "dates": "1685–1750",
        "title": "Brandenburg Concertos", "cat": "BWV 1046–1051 · 1721",
        "standfirst": "Six concertos sent to Christian Ludwig of Brandenburg, and the work on which every argument about baroque performance style eventually lands.",
    },
    "shostakovich/sym5": {
        "composer": "Dmitri Shostakovich", "dates": "1906–1975",
        "title": "Symphony No. 5", "cat": "Op. 47 · D minor · 1937",
        "standfirst": "Written after the Pravda attack and premiered to a half-hour ovation. Whether the finale is triumph or coercion is the argument, and every recording takes a side.",
    },
    "puccini/tosca": {
        "composer": "Giacomo Puccini", "dates": "1858–1924",
        "title": "Tosca", "cat": "Teatro Costanzi, Rome · 14 January 1900",
        "standfirst": "Three acts of political violence at close range, and the opera where a recording either has dramatic nerve or has nothing.",
    },
}


if __name__ == "__main__":
    EDITORIAL.update(load_editorial())
    results = [run(r) for r in load_from_data()]

    works = []
    for wid, meta in WORKS.items():
        works.append({**meta, "id": wid,
                      "recordings": [r for r in results if r["work"] == wid]})

    barcodes = {
        e["barcode"]: {"recording": r["id"], "edition": e["id"]}
        for r in results for e in r["editions"] if e.get("barcode")
    }

    out = {"algorithm_version": ALGORITHM_VERSION,
           "built": datetime.now(timezone.utc).date().isoformat(),
           "works": works, "barcode_index": barcodes}

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
    print(f"\n{len(barcodes)} barcodes indexed · wrote catalogue.json")
