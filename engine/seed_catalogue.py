#!/usr/bin/env python3
"""
seed_catalogue.py — the editorial seed for round 1.

WHAT IS AND IS NOT IN HERE
--------------------------
In here: works, and candidate recordings. Both are matters of record — a
catalogue number, a set of performers, a label, a year. Wrong entries here are
correctable errors of fact, and step 1 of the harvest verifies every one of
them against MusicBrainz before anything else happens.

NOT in here: a single critical score, star, or assessment. Those must come
from a source with a locator. A seeded opinion is indistinguishable from a
fabricated one three months later, and the guide's only asset is that the
distinction is always visible. Works arrive `awaiting sources` and stay there
until the harvest brings back something citable.

Every candidate below carries verified=False. Round 1 promotes it or drops it.
"""

import json

# (id, title, catalogue, year, note)
BACH = [
    ("brandenburg", "Brandenburg Concertos", "BWV 1046–1051", "1721", "Concerto grosso and solo forms; the central HIP battleground."),
    ("suites", "Orchestral Suites", "BWV 1066–1069", "c. 1725–39", "French overture style; the Air of No. 3 and the B minor flute suite."),
    ("violin_concertos", "Violin Concertos", "BWV 1041–1043", "c. 1730", "Including the Double Concerto, a repertory staple in every style."),
    ("cello_suites", "Cello Suites", "BWV 1007–1012", "c. 1720", "Solo cello as complete polyphony; the most re-recorded solo cycle."),
    ("sonatas_partitas", "Sonatas and Partitas for Solo Violin", "BWV 1001–1006", "1720", "The Chaconne of the D minor Partita."),
    ("goldberg", "Goldberg Variations", "BWV 988", "1741", "Thirty variations over a bass; the piano-versus-harpsichord argument."),
    ("wtc", "The Well-Tempered Clavier, Books I & II", "BWV 846–893", "1722 / 1742", "Forty-eight preludes and fugues."),
    ("mass_b_minor", "Mass in B minor", "BWV 232", "1749", "Assembled late from a lifetime's work; the choral-forces question."),
    ("matthew", "St Matthew Passion", "BWV 244", "1727", "Double choir and orchestra; the largest question of scale in Bach."),
    ("john", "St John Passion", "BWV 245", "1724", "Sharper and more dramatic than the Matthew; several authorial versions."),
    ("art_of_fugue", "The Art of Fugue", "BWV 1080", "c. 1740–50", "Instrumentation unspecified, which makes every recording an argument."),
    ("harpsichord_concertos", "Harpsichord Concertos", "BWV 1052–1058", "c. 1738", "Mostly arrangements; the founding documents of the keyboard concerto."),
]

BEETHOVEN = [
    ("sym3", "Symphony No. 3, Eroica", "Op. 55", "1804", "The break; tempo and weight decide everything."),
    ("sym5", "Symphony No. 5", "Op. 67", "1808", "The most recorded symphony; interpretation history in miniature."),
    ("sym6", "Symphony No. 6, Pastoral", "Op. 68", "1808", "Where a conductor's idea of nature becomes audible."),
    ("sym7", "Symphony No. 7", "Op. 92", "1812", "Rhythm as subject; the Allegretto's tempo is a critical fault line."),
    ("sym9", "Symphony No. 9", "Op. 125", "1824", "Chorus, soloists, and a century of political readings."),
    ("pc4", "Piano Concerto No. 4", "Op. 58", "1806", "The slow movement's dialogue between piano and strings."),
    ("pc5", "Piano Concerto No. 5, Emperor", "Op. 73", "1809", "Scale and grandeur against clarity."),
    ("violin_concerto", "Violin Concerto", "Op. 61", "1806", "Lyrical rather than virtuosic; cadenza choice is an interpretation."),
    ("late_quartets", "Late String Quartets", "Opp. 127–135", "1825–26", "Including the Grosse Fuge; the summit of the chamber literature."),
    ("hammerklavier", "Piano Sonata No. 29, Hammerklavier", "Op. 106", "1818", "The fugue's tempo marking is still argued over."),
    ("missa_solemnis", "Missa Solemnis", "Op. 123", "1823", "Brutal on choirs; few recordings survive the Credo intact."),
    ("fidelio", "Fidelio", "Op. 72", "1805/1814", "Which overture, which version, which political moment."),
]

MOZART = [
    ("late_symphonies", "Symphonies Nos. 39, 40, 41", "K. 543, 550, 551", "1788", "Written in a single summer; the Jupiter fugue-finale."),
    ("pc20", "Piano Concerto No. 20", "K. 466", "1785", "D minor; Beethoven wrote cadenzas for it."),
    ("pc23", "Piano Concerto No. 23", "K. 488", "1786", "The F sharp minor Adagio."),
    ("pc27", "Piano Concerto No. 27", "K. 595", "1791", "Late, spare, and often played too gently."),
    ("clarinet_concerto", "Clarinet Concerto", "K. 622", "1791", "Basset clarinet versus modern instrument."),
    ("requiem", "Requiem", "K. 626", "1791", "Completion choice — Süssmayr, Beyer, Levin — is the first decision."),
    ("figaro", "Le nozze di Figaro", "K. 492", "1786", "Ensemble comedy that depends entirely on pacing."),
    ("don_giovanni", "Don Giovanni", "K. 527", "1787", "Prague or Vienna version; the supper scene."),
    ("cosi", "Così fan tutte", "K. 588", "1790", "Tone is the whole problem: cruelty, farce, or grief."),
    ("zauberflote", "Die Zauberflöte", "K. 620", "1791", "Singspiel; dialogue handling divides recordings sharply."),
    ("mass_c_minor", "Great Mass in C minor", "K. 427", "1783", "Unfinished; several performing completions."),
    ("string_quintets", "String Quintets", "K. 515, 516", "1787", "Two violas; the G minor is the darkest chamber music he wrote."),
]

PUCCINI = [
    ("manon_lescaut", "Manon Lescaut", "—", "1893", "The first success; orchestrally the most Wagnerian."),
    ("boheme", "La Bohème", "—", "1896", "The most recorded of all; conducting decides sentiment or truth."),
    ("tosca", "Tosca", "—", "1900", "Verismo at close range."),
    ("butterfly", "Madama Butterfly", "—", "1904", "Which of five versions is being performed matters."),
    ("fanciulla", "La fanciulla del West", "—", "1910", "Harmonically the most advanced; still under-recorded."),
    ("rondine", "La rondine", "—", "1917", "Operetta inheritance; the least settled discography."),
    ("trittico", "Il trittico", "—", "1918", "Three one-act operas, rarely recorded as the whole Puccini intended."),
    ("turandot", "Turandot", "—", "1926", "Unfinished; Alfano or Berio ending is a critical decision."),
    ("villi", "Le Villi", "—", "1884", "First opera; documentary interest."),
    ("edgar", "Edgar", "—", "1889", "The failure, revised repeatedly."),
    ("messa_gloria", "Messa di Gloria", "—", "1880", "Student work already recognisably him."),
]

# Candidate recordings: identity only. (work, soloists, director, ensemble, label, year)
CANDIDATES = {
    "bach/brandenburg": [
        ("Trevor Pinnock, harpsichord", "Trevor Pinnock", "The English Concert", "Archiv", "1982"),
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1964"),
        ("", "Claudio Abbado", "Orchestra Mozart", "Deutsche Grammophon", "2007"),
        ("", "Benjamin Britten", "English Chamber Orchestra", "Decca", "1968"),
    ],
    "bach/cello_suites": [
        ("Pablo Casals", "", "", "EMI", "1936–39"),
        ("Pierre Fournier", "", "", "Archiv", "1961"),
        ("Anner Bylsma", "", "", "Sony Vivarte", "1992"),
    ],
    "bach/goldberg": [
        ("Glenn Gould", "", "", "Columbia", "1955"),
        ("Glenn Gould", "", "", "CBS", "1981"),
        ("Wanda Landowska", "", "", "RCA", "1945"),
    ],
    "bach/sonatas_partitas": [
        ("Nathan Milstein", "", "", "Deutsche Grammophon", "1973"),
        ("Rachel Podger", "", "", "Channel Classics", "1999"),
    ],
    "bach/matthew": [
        ("", "Otto Klemperer", "Philharmonia", "EMI", "1961"),
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Archiv", "1988"),
    ],
    "bach/mass_b_minor": [
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Archiv", "1985"),
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1968"),
    ],
    "beethoven/sym3": [
        ("", "Otto Klemperer", "Philharmonia", "EMI", "1959"),
        ("", "John Eliot Gardiner", "Orchestre Révolutionnaire et Romantique", "Archiv", "1993"),
    ],
    "beethoven/sym5": [
        ("", "Carlos Kleiber", "Wiener Philharmoniker", "Deutsche Grammophon", "1974"),
        ("", "Wilhelm Furtwängler", "Berliner Philharmoniker", "EMI", "1954"),
    ],
    "beethoven/sym7": [
        ("", "Carlos Kleiber", "Wiener Philharmoniker", "Deutsche Grammophon", "1976"),
    ],
    "beethoven/sym9": [
        ("", "Wilhelm Furtwängler", "Bayreuth Festival", "EMI", "1951"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1962"),
        ("", "John Eliot Gardiner", "Orchestre Révolutionnaire et Romantique", "Archiv", "1992"),
    ],
    "beethoven/violin_concerto": [
        ("Jascha Heifetz", "Charles Munch", "Boston Symphony", "RCA", "1955"),
        ("Itzhak Perlman", "Carlo Maria Giulini", "Philharmonia", "EMI", "1980"),
    ],
    "beethoven/pc5": [
        ("Wilhelm Backhaus", "Hans Schmidt-Isserstedt", "Wiener Philharmoniker", "Decca", "1959"),
        ("Maurizio Pollini", "Karl Böhm", "Wiener Philharmoniker", "Deutsche Grammophon", "1978"),
    ],
    "beethoven/late_quartets": [
        ("Busch Quartet", "", "", "EMI", "1930s"),
        ("Quartetto Italiano", "", "", "Philips", "1967–75"),
    ],
    "beethoven/fidelio": [
        ("Christa Ludwig, Jon Vickers", "Otto Klemperer", "Philharmonia", "EMI", "1962"),
    ],
    "beethoven/missa_solemnis": [
        ("", "Otto Klemperer", "New Philharmonia", "EMI", "1965"),
    ],
    "mozart/late_symphonies": [
        ("", "Karl Böhm", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
        ("", "Nikolaus Harnoncourt", "Concentgebouw", "Teldec", "1980s"),
    ],
    "mozart/pc20": [
        ("Clara Haskil", "Igor Markevitch", "Orchestre des Concerts Lamoureux", "Philips", "1960"),
        ("Alfred Brendel", "Neville Marriner", "Academy of St Martin in the Fields", "Philips", "1970s"),
    ],
    "mozart/clarinet_concerto": [
        ("Jack Brymer", "Thomas Beecham", "Royal Philharmonic", "EMI", "1959"),
        ("Antony Pay", "Christopher Hogwood", "Academy of Ancient Music", "L'Oiseau-Lyre", "1980s"),
    ],
    "mozart/requiem": [
        ("", "Karl Böhm", "Wiener Philharmoniker", "Deutsche Grammophon", "1971"),
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Philips", "1986"),
    ],
    "mozart/figaro": [
        ("", "Erich Kleiber", "Wiener Philharmoniker", "Decca", "1955"),
        ("", "Carlo Maria Giulini", "Philharmonia", "EMI", "1959"),
    ],
    "mozart/don_giovanni": [
        ("", "Carlo Maria Giulini", "Philharmonia", "EMI", "1959"),
        ("", "Wilhelm Furtwängler", "Wiener Philharmoniker", "EMI", "1954"),
    ],
    "mozart/cosi": [
        ("", "Karl Böhm", "Philharmonia", "EMI", "1962"),
    ],
    "mozart/zauberflote": [
        ("", "Otto Klemperer", "Philharmonia", "EMI", "1964"),
        ("", "Karl Böhm", "Berliner Philharmoniker", "Deutsche Grammophon", "1964"),
    ],
    "puccini/tosca": [
        ("Maria Callas, Giuseppe Di Stefano, Tito Gobbi", "Victor de Sabata", "Teatro alla Scala", "EMI", "1953"),
        ("Leontyne Price, Giuseppe Di Stefano, Giuseppe Taddei", "Herbert von Karajan", "Wiener Philharmoniker", "Decca", "1962"),
        ("Maria Callas, Carlo Bergonzi, Tito Gobbi", "Georges Prêtre", "Paris Conservatoire", "EMI", "1964"),
    ],
    "puccini/boheme": [
        ("Victoria de los Ángeles, Jussi Björling", "Thomas Beecham", "RCA Victor Orchestra", "EMI", "1956"),
        ("Mirella Freni, Luciano Pavarotti", "Herbert von Karajan", "Berliner Philharmoniker", "Decca", "1972"),
    ],
    "puccini/butterfly": [
        ("Renata Scotto, Carlo Bergonzi", "John Barbirolli", "Rome Opera", "EMI", "1966"),
        ("Mirella Freni, Luciano Pavarotti", "Herbert von Karajan", "Wiener Philharmoniker", "Decca", "1974"),
    ],
    "puccini/turandot": [
        ("Birgit Nilsson, Franco Corelli", "Francesco Molinari-Pradelli", "Rome Opera", "EMI", "1965"),
        ("Joan Sutherland, Luciano Pavarotti", "Zubin Mehta", "London Philharmonic", "Decca", "1972"),
    ],
    "puccini/manon_lescaut": [
        ("Maria Callas, Giuseppe Di Stefano", "Tullio Serafin", "Teatro alla Scala", "EMI", "1957"),
    ],
    "shostakovich/sym5": [
        ("", "Yevgeny Mravinsky", "Leningrad Philharmonic Orchestra", "various", "1954"),
        ("", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1959"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Decca", "1981"),
        ("", "André Previn", "London Symphony Orchestra", "EMI", "1965"),
        ("", "Mstislav Rostropovich", "National Symphony Orchestra", "Teldec", "1993"),
        ("", "Vasily Petrenko", "Royal Liverpool Philharmonic", "Naxos", "2009"),
        ("", "Andris Nelsons", "Boston Symphony Orchestra", "Deutsche Grammophon", "2016"),
    ],
    "shostakovich/sym10": [
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1966"),
        ("", "Vasily Petrenko", "Royal Liverpool Philharmonic", "Naxos", "2010"),
        ("", "Andris Nelsons", "Boston Symphony Orchestra", "Deutsche Grammophon", "2015"),
    ],
    "shostakovich/sym7": [
        ("", "Leonard Bernstein", "Chicago Symphony Orchestra", "Deutsche Grammophon", "1988"),
    ],
    "shostakovich/sym8": [
        ("", "Yevgeny Mravinsky", "Leningrad Philharmonic Orchestra", "Praga", "1982"),
        ("", "Andris Nelsons", "Boston Symphony Orchestra", "Deutsche Grammophon", "2016"),
    ],
    "shostakovich/sym13": [
        ("", "Kirill Kondrashin", "Moscow Philharmonic", "Melodiya", "1967"),
    ],
    "puccini/fanciulla": [
        ("Renata Tebaldi, Mario Del Monaco", "Franco Capuana", "Accademia di Santa Cecilia", "Decca", "1958"),
    ],
}

SHOSTAKOVICH = [
    ("sym1", "Symphony No. 1", "Op. 10", "1925", "A conservatory graduation piece that went round the world within three years."),
    ("sym4", "Symphony No. 4", "Op. 43", "1936", "Withdrawn in rehearsal after the Pravda attack; unheard until 1961."),
    ("sym5", "Symphony No. 5", "Op. 47", "1937", "The rehabilitation, and the most argued-over finale in the repertory."),
    ("sym6", "Symphony No. 6", "Op. 54", "1939", "A vast Largo followed by two fast movements; the proportions unsettle conductors."),
    ("sym7", "Symphony No. 7, Leningrad", "Op. 60", "1941", "Written under siege and flown out on microfilm; the invasion theme divides opinion still."),
    ("sym8", "Symphony No. 8", "Op. 65", "1943", "The war symphony without consolation. Officially disliked for exactly that."),
    ("sym9", "Symphony No. 9", "Op. 70", "1945", "The victory symphony that refused to be one."),
    ("sym10", "Symphony No. 10", "Op. 93", "1953", "Written around Stalin's death; the DSCH monogram at its centre."),
    ("sym11", "Symphony No. 11, The Year 1905", "Op. 103", "1957", "Cinematic and continuous; read after 1956 as being about Hungary."),
    ("sym13", "Symphony No. 13, Babi Yar", "Op. 113", "1962", "Yevtushenko settings for bass and male chorus; censored before its premiere."),
    ("sym14", "Symphony No. 14", "Op. 135", "1969", "Eleven poems on death for two voices and chamber orchestra."),
    ("sym15", "Symphony No. 15", "Op. 141", "1971", "The last, quoting Rossini and Wagner and explaining neither."),
]

COMPOSERS = [
    ("bach", "Johann Sebastian Bach", "1685–1750", BACH),
    ("beethoven", "Ludwig van Beethoven", "1770–1827", BEETHOVEN),
    ("mozart", "Wolfgang Amadeus Mozart", "1756–1791", MOZART),
    ("puccini", "Giacomo Puccini", "1858–1924", PUCCINI),
    ("shostakovich", "Dmitri Shostakovich", "1906–1975", SHOSTAKOVICH),
]


def build() -> dict:
    works, candidates = [], 0
    for cid, name, dates, items in COMPOSERS:
        for wid, title, cat, year, note in items:
            key = f"{cid}/{wid}"
            cands = [{
                "id": f"{key}/{i}",
                "soloists": s, "director": d, "ensemble": e,
                "label": lab, "year": yr,
                "verified": False, "mbid": None,
                "status": "candidate",
            } for i, (s, d, e, lab, yr) in enumerate(CANDIDATES.get(key, []))]
            candidates += len(cands)
            works.append({
                "id": key, "composer_id": cid, "composer": name, "composer_dates": dates,
                "title": title, "catalogue": cat, "year": year, "note": note,
                "status": "awaiting sources",
                "candidates": cands,
                "assessed": [],
            })
    return {
        "schema": "seed/1",
        "composers": [{"id": c, "name": n, "dates": d, "works": len(i)} for c, n, d, i in COMPOSERS],
        "works": works,
        "totals": {"works": len(works), "candidates": candidates},
    }


if __name__ == "__main__":
    seed = build()
    with open("data/seed.json", "w", encoding="utf-8") as f:
        json.dump(seed, f, indent=2, ensure_ascii=False)
    t = seed["totals"]
    print(f"{len(seed['composers'])} composers · {t['works']} works · {t['candidates']} candidate recordings")
    for c in seed["composers"]:
        print(f"  {c['name']:<28} {c['works']:>2} works")
    print("\nNo scores seeded. Every work starts `awaiting sources`.")
