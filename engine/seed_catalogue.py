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
    # Brahms
    "brahms/sym1": [
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1963"),
        ("", "Otto Klemperer", "Philharmonia", "EMI", "1957"),
        ("", "Carlo Maria Giulini", "Los Angeles Philharmonic", "Deutsche Grammophon", "1981"),
    ],
    "brahms/sym4": [
        ("", "Carlos Kleiber", "Wiener Philharmoniker", "Deutsche Grammophon", "1980"),
        ("", "Otto Klemperer", "Philharmonia", "EMI", "1957"),
    ],
    "brahms/pc1": [
        ("Emil Gilels", "Eugen Jochum", "Berliner Philharmoniker", "Deutsche Grammophon", "1972"),
        ("Clifford Curzon", "George Szell", "London Symphony Orchestra", "Decca", "1962"),
    ],
    "brahms/pc2": [
        ("Emil Gilels", "Eugen Jochum", "Berliner Philharmoniker", "Deutsche Grammophon", "1972"),
        ("Sviatoslav Richter", "Erich Leinsdorf", "Chicago Symphony Orchestra", "RCA", "1960"),
    ],
    "brahms/violin_concerto": [
        ("David Oistrakh", "Otto Klemperer", "Orchestre National de la Radiodiffusion Française", "EMI", "1960"),
        ("Jascha Heifetz", "Fritz Reiner", "Chicago Symphony Orchestra", "RCA", "1955"),
    ],
    "brahms/german_requiem": [
        ("", "Otto Klemperer", "Philharmonia", "EMI", "1961"),
        ("", "John Eliot Gardiner", "Orchestre Révolutionnaire et Romantique", "Philips", "1990"),
    ],
    "brahms/clarinet_quintet": [
        ("Reginald Kell; Busch Quartet", "", "", "EMI", "1937"),
        ("Karl Leister; Amadeus Quartet", "", "", "Deutsche Grammophon", "1967"),
    ],
    "brahms/piano_quintet": [
        ("Artur Rubinstein; Guarneri Quartet", "", "", "RCA", "1967"),
        ("Sviatoslav Richter; Borodin Quartet", "", "", "EMI", "1983"),
    ],
    "brahms/haydn_variations": [
        ("", "Arturo Toscanini", "NBC Symphony Orchestra", "RCA", "1952"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Philips", "1970s"),
    ],
    "brahms/liebeslieder": [
        ("Mathis, Fassbaender, Schreier, Fischer-Dieskau; Karl Engel, Wolfgang Sawallisch, piano", "", "", "Deutsche Grammophon", "1974"),
    ],
    "brahms/academic_festival": [
        ("", "George Szell", "Cleveland Orchestra", "CBS", "1960s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Philips", "1970s"),
    ],
    "brahms/tragic_overture": [
        ("", "Carlos Kleiber", "Wiener Philharmoniker", "Deutsche Grammophon", "1980"),
    ],
    # Haydn
    "haydn/sym104": [
        ("", "Colin Davis", "Concertgebouw Orchestra", "Philips", "1975"),
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1990s"),
    ],
    "haydn/sym94": [
        ("", "Thomas Beecham", "Royal Philharmonic", "EMI", "1950s"),
        ("", "Christopher Hogwood", "Academy of Ancient Music", "L'Oiseau-Lyre", "1980s"),
    ],
    "haydn/creation": [
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1969"),
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Archiv", "1996"),
    ],
    "haydn/op76": [
        ("Quatuor Mosaïques", "", "", "Astree", "1990s"),
        ("Amadeus Quartet", "", "", "Deutsche Grammophon", "1960s"),
    ],
    "haydn/trumpet_concerto": [
        ("Maurice André", "Riccardo Muti", "Philharmonia", "EMI", "1980s"),
        ("Wynton Marsalis", "Raymond Leppard", "National Philharmonic Orchestra", "CBS", "1982"),
    ],
    "haydn/cello_concerto1": [
        ("Jacqueline du Pré", "Daniel Barenboim", "English Chamber Orchestra", "EMI", "1967"),
        ("Anner Bylsma", "Frans Brüggen", "Orchestra of the 18th Century", "Philips", "1980s"),
    ],
    "haydn/seasons": [
        ("", "Karl Böhm", "Wiener Philharmoniker", "Deutsche Grammophon", "1967"),
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Archiv", "1992"),
    ],
    "haydn/nelson_mass": [
        ("", "David Willcocks", "King's College Choir, Cambridge", "EMI", "1962"),
        ("", "Trevor Pinnock", "The English Concert", "Archiv", "1980s"),
    ],
    "haydn/piano_sonatas": [
        ("Alfred Brendel", "", "", "Philips", "1970s–80s"),
        ("András Schiff", "", "", "Teldec", "1990s"),
    ],
    "haydn/sym44": [
        ("", "Antal Doráti", "Philharmonia Hungarica", "Decca", "1970s"),
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1980s"),
    ],
    "haydn/sym45": [
        ("", "Antal Doráti", "Philharmonia Hungarica", "Decca", "1970s"),
        ("", "Christopher Hogwood", "Academy of Ancient Music", "L'Oiseau-Lyre", "1980s"),
    ],
    "haydn/seven_last_words": [
        ("", "Juilliard Quartet", "", "Sony", "1980s"),
        ("", "Henschel Quartet", "", "Hänssler", "2000s"),
    ],
    # Schubert
    "schubert/sym8": [
        ("", "Carlos Kleiber", "Wiener Philharmoniker", "Deutsche Grammophon", "1978"),
        ("", "Günter Wand", "Berliner Philharmoniker", "RCA", "1990s"),
    ],
    "schubert/sym9": [
        ("", "Josef Krips", "London Symphony Orchestra", "Decca", "1958"),
        ("", "Carlo Maria Giulini", "Chicago Symphony Orchestra", "Deutsche Grammophon", "1976"),
    ],
    "schubert/winterreise": [
        ("Dietrich Fischer-Dieskau; Gerald Moore, piano", "", "", "EMI", "1962"),
        ("Peter Pears; Benjamin Britten, piano", "", "", "Decca", "1965"),
    ],
    "schubert/schone_mullerin": [
        ("Dietrich Fischer-Dieskau; Gerald Moore, piano", "", "", "EMI", "1961"),
        ("Fritz Wunderlich; Hubert Giesen, piano", "", "", "Deutsche Grammophon", "1960s"),
    ],
    "schubert/string_quintet": [
        ("Amadeus Quartet; William Pleeth, cello", "", "", "Deutsche Grammophon", "1965"),
        ("Alban Berg Quartet; Heinrich Schiff, cello", "", "", "EMI", "1982"),
    ],
    "schubert/death_maiden": [
        ("Amadeus Quartet", "", "", "Deutsche Grammophon", "1960s"),
        ("Quartetto Italiano", "", "", "Philips", "1965"),
    ],
    "schubert/sonata_d960": [
        ("Arturo Benedetti Michelangeli", "", "", "Deutsche Grammophon", "1981"),
        ("Alfred Brendel", "", "", "Philips", "1970s"),
        ("Maurizio Pollini", "", "", "Deutsche Grammophon", "1987"),
    ],
    "schubert/trout": [
        ("Clifford Curzon; members of the Vienna Octet", "", "", "Decca", "1957"),
        ("Emil Gilels; Amadeus Quartet", "", "", "Deutsche Grammophon", "1970s"),
    ],
    "schubert/mass_e_flat": [
        ("", "Wolfgang Sawallisch", "Bavarian Radio Symphony Orchestra", "EMI", "1970s"),
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Philips", "1990s"),
    ],
    "schubert/impromptus": [
        ("Alfred Brendel", "", "", "Philips", "1970s"),
        ("Murray Perahia", "", "", "Sony", "1980s"),
    ],
    "schubert/schwanengesang": [
        ("Dietrich Fischer-Dieskau; Gerald Moore, piano", "", "", "EMI", "1962"),
        ("Hans Hotter; Gerald Moore, piano", "", "", "EMI", "1954"),
    ],
    "schubert/rosamunde": [
        ("", "Willi Boskovsky", "Wiener Philharmoniker", "Decca", "1960s"),
        ("", "Claudio Abbado", "Chamber Orchestra of Europe", "Deutsche Grammophon", "1980s"),
    ],
    # Handel
    "handel/messiah": [
        ("", "Colin Davis", "London Symphony Orchestra", "Philips", "1966"),
        ("", "Charles Mackerras", "English Chamber Orchestra", "EMI", "1967"),
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Philips", "1982"),
    ],
    "handel/water_music": [
        ("", "Trevor Pinnock", "The English Concert", "Archiv", "1983"),
        ("", "Neville Marriner", "Academy of St Martin in the Fields", "Decca", "1970s"),
    ],
    "handel/fireworks": [
        ("", "Trevor Pinnock", "The English Concert", "Archiv", "1984"),
        ("", "Charles Mackerras", "Pro Arte Orchestra", "Pye", "1959"),
    ],
    "handel/giulio_cesare": [
        ("Janet Baker", "Charles Mackerras", "English National Opera", "EMI", "1984"),
        ("", "René Jacobs", "Concerto Köln", "Harmonia Mundi", "1991"),
    ],
    "handel/alcina": [
        ("Joan Sutherland", "Richard Bonynge", "London Symphony Orchestra", "Decca", "1962"),
        ("", "Alan Curtis", "Il Complesso Barocco", "Deutsche Harmonia Mundi", "2000s"),
    ],
    "handel/op6": [
        ("", "Trevor Pinnock", "The English Concert", "Archiv", "1982"),
        ("", "Christopher Hogwood", "Academy of Ancient Music", "L'Oiseau-Lyre", "1980s"),
    ],
    "handel/organ_concertos": [
        ("Simon Preston", "Trevor Pinnock", "The English Concert", "Archiv", "1980s"),
        ("Peter Hurford", "Christopher Hogwood", "Academy of Ancient Music", "Decca", "1980s"),
    ],
    "handel/israel_in_egypt": [
        ("", "John Eliot Gardiner", "Monteverdi Choir", "Philips", "1980"),
        ("", "Andrew Parrott", "Taverner Choir and Players", "EMI", "1990"),
    ],
    "handel/solomon": [
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Philips", "1984"),
        ("", "Daniel Barenboim", "English Chamber Orchestra", "Deutsche Grammophon", "1970s"),
    ],
    "handel/agrippina": [
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Philips", "1990s"),
        ("", "René Jacobs", "Akademie für Alte Musik Berlin", "Harmonia Mundi", "2000s"),
    ],
    "handel/rodelinda": [
        ("Joan Sutherland", "Richard Bonynge", "Welsh National Opera", "Decca", "1985"),
        ("", "Alan Curtis", "Il Complesso Barocco", "Deutsche Harmonia Mundi", "2000s"),
    ],
    "handel/dixit_dominus": [
        ("", "John Eliot Gardiner", "Monteverdi Choir", "Archiv", "1978"),
        ("", "Marc Minkowski", "Les Musiciens du Louvre", "Archiv", "1990s"),
    ],
    # Chopin
    "chopin/ballades": [
        ("Arthur Rubinstein", "", "", "RCA", "1959–61"),
        ("Krystian Zimerman", "", "", "Deutsche Grammophon", "1987"),
    ],
    "chopin/etudes": [
        ("Maurizio Pollini", "", "", "Deutsche Grammophon", "1972"),
        ("Murray Perahia", "", "", "Sony", "2002"),
    ],
    "chopin/preludes": [
        ("Martha Argerich", "", "", "Deutsche Grammophon", "1977"),
        ("Alfred Cortot", "", "", "EMI", "1933–34"),
    ],
    "chopin/sonata2": [
        ("Arthur Rubinstein", "", "", "RCA", "1961"),
        ("Maurizio Pollini", "", "", "Deutsche Grammophon", "1984"),
    ],
    "chopin/sonata3": [
        ("Martha Argerich", "", "", "Deutsche Grammophon", "1960s"),
        ("Arthur Rubinstein", "", "", "RCA", "1961"),
    ],
    "chopin/pc1": [
        ("Krystian Zimerman", "Carlo Maria Giulini", "Los Angeles Philharmonic", "Deutsche Grammophon", "1979"),
        ("Arthur Rubinstein", "Stanisław Skrowaczewski", "New Symphony Orchestra of London", "RCA", "1961"),
    ],
    "chopin/pc2": [
        ("Arthur Rubinstein", "Stanisław Skrowaczewski", "New Symphony Orchestra of London", "RCA", "1958"),
        ("Martha Argerich", "Charles Dutoit", "Orchestre Symphonique de Montréal", "EMI", "1999"),
    ],
    "chopin/nocturnes": [
        ("Arthur Rubinstein", "", "", "RCA", "1965–67"),
        ("Claudio Arrau", "", "", "Philips", "1978"),
    ],
    "chopin/polonaises": [
        ("Arthur Rubinstein", "", "", "RCA", "1950s–60s"),
        ("Maurizio Pollini", "", "", "Deutsche Grammophon", "1976"),
    ],
    "chopin/mazurkas": [
        ("Arthur Rubinstein", "", "", "RCA", "1965–66"),
        ("Ignaz Friedman", "", "", "Columbia", "1920s–30s"),
    ],
    "chopin/scherzi": [
        ("Arthur Rubinstein", "", "", "RCA", "1959–61"),
        ("Sviatoslav Richter", "", "", "various", "1960s"),
    ],
    "chopin/impromptus": [
        ("Arthur Rubinstein", "", "", "RCA", "1960s"),
        ("Murray Perahia", "", "", "Sony", "1980s"),
    ],
    # Tchaikovsky / Wagner / Verdi / Mahler / Debussy (week 2026-08-09 batch 2)
    "tchaikovsky/sym6": [
        ("", "Yevgeny Mravinsky", "Leningrad Philharmonic Orchestra", "Deutsche Grammophon", "1960"),
        ("", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1960s"),
    ],
    "tchaikovsky/sym4": [
        ("", "Yevgeny Mravinsky", "Leningrad Philharmonic Orchestra", "Deutsche Grammophon", "1960"),
        ("", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1950s"),
    ],
    "tchaikovsky/sym5": [
        ("", "Yevgeny Mravinsky", "Leningrad Philharmonic Orchestra", "Deutsche Grammophon", "1960"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
    ],
    "tchaikovsky/pc1": [
        ("Van Cliburn", "Kirill Kondrashin", "RCA Symphony Orchestra", "RCA", "1958"),
        ("Martha Argerich", "Charles Dutoit", "Orchestre de la Suisse Romande", "Deutsche Grammophon", "1975"),
    ],
    "tchaikovsky/violin_concerto": [
        ("Jascha Heifetz", "Fritz Reiner", "Chicago Symphony Orchestra", "RCA", "1957"),
        ("David Oistrakh", "Eugene Ormandy", "Philadelphia Orchestra", "Columbia", "1960s"),
    ],
    "tchaikovsky/swan_lake": [
        ("", "André Previn", "London Symphony Orchestra", "EMI", "1976"),
        ("", "Ernest Ansermet", "Orchestre de la Suisse Romande", "Decca", "1950s"),
    ],
    "tchaikovsky/nutcracker": [
        ("", "Antal Doráti", "London Symphony Orchestra", "Mercury", "1962"),
        ("", "André Previn", "London Symphony Orchestra", "EMI", "1972"),
    ],
    "tchaikovsky/eugene_onegin": [
        ("", "Georg Solti", "Orchestra of the Royal Opera House", "Decca", "1974"),
        ("", "James Levine", "Metropolitan Opera Orchestra", "Deutsche Grammophon", "1980s"),
    ],
    "tchaikovsky/romeo_juliet": [
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
        ("", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1960s"),
    ],
    "tchaikovsky/serenade_strings": [
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
        ("", "Neville Marriner", "Academy of St Martin in the Fields", "Argo", "1970s"),
    ],
    "tchaikovsky/overture_1812": [
        ("", "Antal Doráti", "Minneapolis Symphony Orchestra", "Mercury", "1954"),
        ("", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1960s"),
    ],
    "tchaikovsky/piano_trio": [
        ("Beaux Arts Trio", "", "", "Philips", "1970s"),
        ("Vladimir Ashkenazy; Itzhak Perlman; Lynn Harrell", "", "", "EMI", "1980s"),
    ],
    "wagner/tristan": [
        ("Kirsten Flagstad, Ludwig Suthaus", "Wilhelm Furtwängler", "Philharmonia", "EMI", "1952"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "EMI", "1972"),
    ],
    "wagner/walkure": [
        ("", "Georg Solti", "Wiener Philharmoniker", "Decca", "1965"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1966"),
    ],
    "wagner/rheingold": [
        ("", "Georg Solti", "Wiener Philharmoniker", "Decca", "1958"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1968"),
    ],
    "wagner/siegfried": [
        ("", "Georg Solti", "Wiener Philharmoniker", "Decca", "1962"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1969"),
    ],
    "wagner/gotterdammerung": [
        ("", "Georg Solti", "Wiener Philharmoniker", "Decca", "1964"),
        ("", "Karl Böhm", "Bayreuth Festival Orchestra", "Philips", "1967"),
    ],
    "wagner/meistersinger": [
        ("", "Eugen Jochum", "Deutsche Oper Berlin", "Deutsche Grammophon", "1976"),
        ("", "Herbert von Karajan", "Dresden Staatskapelle", "EMI", "1970"),
    ],
    "wagner/parsifal": [
        ("", "Hans Knappertsbusch", "Bayreuth Festival Orchestra", "Philips", "1962"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1980"),
    ],
    "wagner/lohengrin": [
        ("", "Rudolf Kempe", "Wiener Philharmoniker", "EMI", "1962–63"),
        ("", "Georg Solti", "Wiener Philharmoniker", "Decca", "1986"),
    ],
    "wagner/tannhauser": [
        ("", "Georg Solti", "Wiener Philharmoniker", "Decca", "1970"),
        ("", "Bernard Haitink", "Bavarian Radio Symphony Orchestra", "EMI", "1985"),
    ],
    "wagner/hollander": [
        ("", "Otto Klemperer", "Philharmonia", "EMI", "1968"),
        ("", "Georg Solti", "Chicago Symphony Orchestra", "Decca", "1976"),
    ],
    "wagner/wesendonck": [
        ("Kirsten Flagstad; Gerald Moore, piano", "", "", "EMI", "1950s"),
        ("Jessye Norman", "Colin Davis", "London Symphony Orchestra", "Philips", "1970s"),
    ],
    "wagner/siegfried_idyll": [
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
        ("", "Bruno Walter", "Columbia Symphony Orchestra", "Columbia", "1950s"),
    ],
    "verdi/traviata": [
        ("Maria Callas", "Carlo Maria Giulini", "Teatro alla Scala", "EMI", "1955"),
        ("Ileana Cotrubas, Plácido Domingo", "Carlos Kleiber", "Bayerisches Staatsorchester", "Deutsche Grammophon", "1977"),
    ],
    "verdi/rigoletto": [
        ("Maria Callas, Tito Gobbi", "Tullio Serafin", "Teatro alla Scala", "EMI", "1955"),
        ("Joan Sutherland, Luciano Pavarotti", "Richard Bonynge", "London Symphony Orchestra", "Decca", "1971"),
    ],
    "verdi/trovatore": [
        ("Maria Callas", "Herbert von Karajan", "Teatro alla Scala", "EMI", "1956"),
        ("Leontyne Price", "Zubin Mehta", "New Philharmonia", "RCA", "1969"),
    ],
    "verdi/aida": [
        ("Maria Callas", "Tullio Serafin", "Teatro alla Scala", "EMI", "1955"),
        ("Leontyne Price", "Georg Solti", "Rome Opera", "Decca", "1961"),
    ],
    "verdi/otello": [
        ("Jon Vickers", "Tullio Serafin", "Rome Opera", "RCA", "1960"),
        ("Plácido Domingo", "James Levine", "National Philharmonic Orchestra", "RCA", "1978"),
    ],
    "verdi/falstaff": [
        ("Tito Gobbi", "Herbert von Karajan", "Philharmonia", "EMI", "1956"),
        ("Renato Bruson", "Carlo Maria Giulini", "Los Angeles Philharmonic", "Deutsche Grammophon", "1982"),
    ],
    "verdi/don_carlos": [
        ("Plácido Domingo", "Carlo Maria Giulini", "Orchestra of the Royal Opera House", "EMI", "1970"),
        ("José Carreras", "Herbert von Karajan", "Berliner Philharmoniker", "EMI", "1979"),
    ],
    "verdi/ballo": [
        ("Maria Callas", "Antonino Votto", "Teatro alla Scala", "EMI", "1956"),
        ("Leontyne Price", "Erich Leinsdorf", "RCA Italiana Orchestra", "RCA", "1966"),
    ],
    "verdi/requiem": [
        ("", "Arturo Toscanini", "NBC Symphony Orchestra", "RCA", "1951"),
        ("", "Carlo Maria Giulini", "Philharmonia", "EMI", "1964"),
    ],
    "verdi/macbeth": [
        ("Maria Callas", "Victor de Sabata", "Teatro alla Scala", "EMI", "1952"),
        ("Piero Cappuccilli", "Claudio Abbado", "Teatro alla Scala", "Deutsche Grammophon", "1976"),
    ],
    "verdi/boccanegra": [
        ("Piero Cappuccilli", "Claudio Abbado", "Teatro alla Scala", "Deutsche Grammophon", "1977"),
        ("Tito Gobbi", "Gabriele Santini", "Rome Opera", "EMI", "1957"),
    ],
    "verdi/nabucco": [
        ("Tito Gobbi", "Lamberto Gardelli", "Vienna Opera Orchestra", "Decca", "1965"),
        ("Piero Cappuccilli", "Lamberto Gardelli", "Orchestra of the Royal Opera House", "Philips", "1970s"),
    ],
    "mahler/sym1": [
        ("", "Rafael Kubelík", "Bayerisches Rundfunk-Sinfonieorchester", "Deutsche Grammophon", "1967"),
        ("", "Leonard Bernstein", "Concertgebouw Orchestra", "Deutsche Grammophon", "1987"),
    ],
    "mahler/sym2": [
        ("", "Otto Klemperer", "Philharmonia", "EMI", "1962"),
        ("", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1963"),
    ],
    "mahler/sym3": [
        ("", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1960s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Philips", "1966"),
    ],
    "mahler/sym4": [
        ("", "George Szell", "Cleveland Orchestra", "Columbia", "1965"),
        ("", "Leonard Bernstein", "Concertgebouw Orchestra", "Deutsche Grammophon", "1987"),
    ],
    "mahler/sym5": [
        ("", "John Barbirolli", "New Philharmonia", "EMI", "1969"),
        ("", "Leonard Bernstein", "Wiener Philharmoniker", "Deutsche Grammophon", "1987"),
    ],
    "mahler/sym6": [
        ("", "Leonard Bernstein", "Wiener Philharmoniker", "Deutsche Grammophon", "1988"),
        ("", "Claudio Abbado", "Berliner Philharmoniker", "Deutsche Grammophon", "2005"),
    ],
    "mahler/sym9": [
        ("", "Leonard Bernstein", "Concertgebouw Orchestra", "Deutsche Grammophon", "1985"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1982"),
    ],
    "mahler/lied_von_der_erde": [
        ("Kathleen Ferrier, Julius Patzak", "Bruno Walter", "Wiener Philharmoniker", "Decca", "1952"),
        ("Christa Ludwig, Fritz Wunderlich", "Otto Klemperer", "Philharmonia", "EMI", "1964"),
    ],
    "mahler/kindertotenlieder": [
        ("Janet Baker", "John Barbirolli", "Hallé Orchestra", "EMI", "1967"),
        ("Dietrich Fischer-Dieskau", "Karl Böhm", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
    ],
    "mahler/knaben_wunderhorn": [
        ("Elisabeth Schwarzkopf; Dietrich Fischer-Dieskau", "George Szell", "London Symphony Orchestra", "EMI", "1968"),
        ("Anne Sofie von Otter; Thomas Quasthoff", "Claudio Abbado", "Berliner Philharmoniker", "Deutsche Grammophon", "1990s"),
    ],
    "mahler/sym7": [
        ("", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1965"),
        ("", "Claudio Abbado", "Chicago Symphony Orchestra", "Deutsche Grammophon", "1984"),
    ],
    "mahler/sym8": [
        ("", "Georg Solti", "Chicago Symphony Orchestra", "Decca", "1971"),
        ("", "Leonard Bernstein", "London Symphony Orchestra", "Columbia", "1966"),
    ],
    "debussy/apres_midi": [
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
        ("", "Pierre Boulez", "New Philharmonia", "CBS", "1960s"),
    ],
    "debussy/la_mer": [
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1964"),
        ("", "Arturo Toscanini", "NBC Symphony Orchestra", "RCA", "1950"),
    ],
    "debussy/nocturnes": [
        ("", "Pierre Boulez", "Cleveland Orchestra", "Deutsche Grammophon", "1990s"),
        ("", "Pierre Monteux", "Boston Symphony Orchestra", "RCA", "1950s"),
    ],
    "debussy/pelleas": [
        ("", "Roger Désormière", "Orchestre de la Société des Concerts du Conservatoire", "EMI", "1941"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "EMI", "1978"),
    ],
    "debussy/preludes": [
        ("Walter Gieseking", "", "", "EMI", "1953–54"),
        ("Arturo Benedetti Michelangeli", "", "", "Deutsche Grammophon", "1978"),
    ],
    "debussy/images": [
        ("Walter Gieseking", "", "", "EMI", "1950s"),
        ("Arturo Benedetti Michelangeli", "", "", "Deutsche Grammophon", "1971"),
    ],
    "debussy/string_quartet": [
        ("Quatuor Ébène", "", "", "Virgin Classics", "2008"),
        ("Quartetto Italiano", "", "", "Philips", "1965"),
    ],
    "debussy/childrens_corner": [
        ("Walter Gieseking", "", "", "EMI", "1950s"),
        ("Arturo Benedetti Michelangeli", "", "", "Deutsche Grammophon", "1971"),
    ],
    "debussy/suite_bergamasque": [
        ("Walter Gieseking", "", "", "EMI", "1950s"),
        ("Claudio Arrau", "", "", "Philips", "1970s"),
    ],
    "debussy/jeux": [
        ("", "Pierre Boulez", "Orchestre National de la RTF", "Columbia", "1960s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Philips", "1970s"),
    ],
    "debussy/sonata_flute_viola_harp": [
        ("Melos Ensemble", "", "", "L'Oiseau-Lyre", "1960s"),
        ("members of the Berliner Philharmoniker", "", "", "Deutsche Grammophon", "1970s"),
    ],
    "debussy/etudes": [
        ("Mitsuko Uchida", "", "", "Philips", "1989"),
        ("Pierre-Laurent Aimard", "", "", "Warner", "2000s"),
    ],

}


def _merged_candidates():
    out = {k: list(v) for k, v in CANDIDATES.items()}
    try:
        from seed_candidates_dense import EXTRA_CANDIDATES
    except ImportError:
        import importlib.util
        import pathlib
        p = pathlib.Path(__file__).with_name("seed_candidates_dense.py")
        spec = importlib.util.spec_from_file_location("seed_candidates_dense", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        EXTRA_CANDIDATES = mod.EXTRA_CANDIDATES
    for k, rows in EXTRA_CANDIDATES.items():
        seen = set(out.get(k, []))
        for row in rows:
            if row not in seen:
                out.setdefault(k, []).append(row)
                seen.add(row)
    return out


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

BRAHMS = [
    ("sym1", "Symphony No. 1", "Op. 68", "1876", "C minor; the long-delayed first symphony."),
    ("sym4", "Symphony No. 4", "Op. 98", "1885", "E minor; passacaglia finale on a Bach bass."),
    ("pc1", "Piano Concerto No. 1", "Op. 15", "1858", "D minor; begun as a symphony after Schumann's collapse."),
    ("pc2", "Piano Concerto No. 2", "Op. 83", "1881", "B-flat; four movements, with a cello solo in the Andante."),
    ("violin_concerto", "Violin Concerto", "Op. 77", "1878", "Written for Joachim; the double-stop opening of the finale."),
    ("german_requiem", "Ein deutsches Requiem", "Op. 45", "1868", "Lutheran scripture in German, not the Latin Mass for the dead."),
    ("clarinet_quintet", "Clarinet Quintet", "Op. 115", "1891", "Late chamber music for Mühlfeld."),
    ("piano_quintet", "Piano Quintet", "Op. 34", "1864", "Reworked from a two-piano sonata and earlier string quintet."),
    ("haydn_variations", "Variations on a Theme by Haydn", "Op. 56a", "1873", "Orchestral set on the St Antoni Chorale (attribution disputed)."),
    ("liebeslieder", "Liebeslieder Waltzes", "Op. 52", "1869", "Vocal waltzes with piano duet."),
    ("academic_festival", "Academic Festival Overture", "Op. 80", "1880", "Breslau doctorate thank-you built from student songs."),
    ("tragic_overture", "Tragic Overture", "Op. 81", "1880", "Companion piece to the Academic Festival Overture."),
]

HAYDN = [
    ("sym104", "Symphony No. 104, London", "Hob. I:104", "1795", "Last of the London symphonies."),
    ("sym94", "Symphony No. 94, Surprise", "Hob. I:94", "1791", "Andante with the sudden fortissimo chord."),
    ("creation", "The Creation", "Hob. XXI:2", "1798", "Oratorio after Genesis and Milton."),
    ("op76", "String Quartets, Op. 76", "Hob. III:75–80", "1797", "Includes the Emperor and Fifths quartets."),
    ("trumpet_concerto", "Trumpet Concerto", "Hob. VIIe:1", "1796", "Written for Weidinger's keyed trumpet."),
    ("cello_concerto1", "Cello Concerto No. 1", "Hob. VIIb:1", "c. 1765", "C major; rediscovered in Prague in 1961."),
    ("seasons", "The Seasons", "Hob. XXI:3", "1801", "Secular oratorio after Thomson."),
    ("nelson_mass", "Missa in angustiis (Nelson Mass)", "Hob. XXII:11", "1798", "D minor Mass associated with Nelson's victories."),
    ("piano_sonatas", "Piano Sonatas (selection)", "Hob. XVI", "1760s–1790s", "Scope set: late sonatas including Hob. XVI:49–52."),
    ("sym44", "Symphony No. 44, Trauer", "Hob. I:44", "c. 1772", "E minor Sturm und Drang symphony."),
    ("sym45", "Symphony No. 45, Farewell", "Hob. I:45", "1772", "Finale with progressive dismissal of the players."),
    ("seven_last_words", "The Seven Last Words of Christ", "Hob. XX/1A", "1786", "Orchestral original later arranged for quartet and chorus."),
]

SCHUBERT = [
    ("sym8", "Symphony No. 8, Unfinished", "D. 759", "1822", "Two completed movements in B minor."),
    ("sym9", "Symphony No. 9, Great", "D. 944", "1825–26", "C major; length that long deterred early performances."),
    ("winterreise", "Winterreise", "D. 911", "1827", "Twenty-four Müller songs for voice and piano."),
    ("schone_mullerin", "Die schöne Müllerin", "D. 795", "1823", "Twenty Müller songs; the earlier song cycle."),
    ("string_quintet", "String Quintet", "D. 956", "1828", "Two cellos; C major."),
    ("death_maiden", "String Quartet No. 14, Death and the Maiden", "D. 810", "1824", "Variations on the earlier song in the Andante."),
    ("sonata_d960", "Piano Sonata in B-flat", "D. 960", "1828", "Last piano sonata; long first-movement exposition repeat."),
    ("trout", "Piano Quintet, Trout", "D. 667", "1819", "Piano and string quartet with double bass; variations on Die Forelle."),
    ("mass_e_flat", "Mass in E-flat", "D. 950", "1828", "Last completed Mass."),
    ("impromptus", "Impromptus", "D. 899 & D. 935", "1827", "Two sets of four piano pieces."),
    ("schwanengesang", "Schwanengesang", "D. 957", "1828", "Fourteen songs published posthumously as a collection."),
    ("rosamunde", "Rosamunde (incidental music)", "D. 797", "1823", "Overture and entr'actes for von Chézy's play."),
]

HANDEL = [
    ("messiah", "Messiah", "HWV 56", "1741", "Oratorio; Dublin premiere 1742."),
    ("water_music", "Water Music", "HWV 348–350", "1717", "Suites for the Thames royal water party."),
    ("fireworks", "Music for the Royal Fireworks", "HWV 351", "1749", "Outdoor wind-band original for Green Park."),
    ("giulio_cesare", "Giulio Cesare", "HWV 17", "1724", "Opera seria for the Royal Academy."),
    ("alcina", "Alcina", "HWV 34", "1735", "Magic-opera for Covent Garden."),
    ("op6", "Concerti grossi, Op. 6", "HWV 319–330", "1739", "Twelve concerti after Corelli's model."),
    ("organ_concertos", "Organ Concertos", "Opp. 4 & 7", "1730s", "Interval concertos for Handel at the organ."),
    ("israel_in_egypt", "Israel in Egypt", "HWV 54", "1739", "Chorus-heavy Exodus oratorio."),
    ("solomon", "Solomon", "HWV 67", "1748", "Oratorio; includes the Arrival of the Queen of Sheba."),
    ("agrippina", "Agrippina", "HWV 6", "1709", "Venetian opera on imperial intrigue."),
    ("rodelinda", "Rodelinda", "HWV 19", "1725", "Opera seria for Cuzzoni and Senesino."),
    ("dixit_dominus", "Dixit Dominus", "HWV 232", "1707", "Psalm setting from the Italian years."),
]

CHOPIN = [
    ("ballades", "Ballades Nos. 1–4", "Opp. 23, 38, 47, 52", "1835–42", "Four large single-movement piano works."),
    ("etudes", "Études", "Opp. 10 & 25", "1833 / 1837", "Twenty-four studies published in two books."),
    ("preludes", "Preludes", "Op. 28", "1839", "Twenty-four preludes through the keys."),
    ("sonata2", "Piano Sonata No. 2", "Op. 35", "1839", "B-flat minor; funeral-march third movement."),
    ("sonata3", "Piano Sonata No. 3", "Op. 58", "1844", "B minor; four-movement sonata."),
    ("pc1", "Piano Concerto No. 1", "Op. 11", "1830", "E minor; published second, composed after Op. 21."),
    ("pc2", "Piano Concerto No. 2", "Op. 21", "1830", "F minor; the earlier of the two concertos."),
    ("nocturnes", "Nocturnes", "Opp. 9–62", "1830–46", "Scope set across the published nocturne groups."),
    ("polonaises", "Polonaises", "Opp. 26–53", "1830s–40s", "Including the Heroic, Op. 53."),
    ("mazurkas", "Mazurkas (selection)", "Opp. 6–63", "1825–49", "Scope set from the published mazurka groups."),
    ("scherzi", "Scherzi Nos. 1–4", "Opp. 20, 31, 39, 54", "1832–42", "Four scherzi for solo piano."),
    ("impromptus", "Impromptus / Fantaisie-Impromptu", "Opp. 29, 36, 51; Op. 66", "1830s–40s", "Three published impromptus plus the posthumous Fantaisie-Impromptu."),
]

TCHAIKOVSKY = [
    ("sym6", "Symphony No. 6, Pathétique", "Op. 74", "1893", "B minor; finale Adagio lamentoso."),
    ("sym4", "Symphony No. 4", "Op. 36", "1878", "F minor; fate-motif opening."),
    ("sym5", "Symphony No. 5", "Op. 64", "1888", "E minor; motto returns in the finale."),
    ("pc1", "Piano Concerto No. 1", "Op. 23", "1875", "B-flat minor; revised after the 1875 premiere."),
    ("violin_concerto", "Violin Concerto", "Op. 35", "1878", "D major; written in Clarens."),
    ("swan_lake", "Swan Lake", "Op. 20", "1877", "Ballet; complete-score versus suite choice."),
    ("nutcracker", "The Nutcracker", "Op. 71", "1892", "Ballet and concert suite Op. 71a."),
    ("eugene_onegin", "Eugene Onegin", "Op. 24", "1879", "Lyric scenes after Pushkin."),
    ("romeo_juliet", "Romeo and Juliet", "—", "1880", "Overture-fantasy; third version."),
    ("serenade_strings", "Serenade for Strings", "Op. 48", "1880", "C major; four movements."),
    ("overture_1812", "1812 Overture", "Op. 49", "1880", "Festival overture with optional artillery."),
    ("piano_trio", "Piano Trio", "Op. 50", "1882", "A minor; in memory of Nikolai Rubinstein."),
]

WAGNER = [
    ("tristan", "Tristan und Isolde", "WWV 90", "1865", "Music drama; prelude and Liebestod often excerpted."),
    ("walkure", "Die Walküre", "WWV 86B", "1870", "Second evening of Der Ring des Nibelungen."),
    ("rheingold", "Das Rheingold", "WWV 86A", "1869", "Vorabend of the Ring cycle."),
    ("siegfried", "Siegfried", "WWV 86C", "1876", "Third evening of the Ring."),
    ("gotterdammerung", "Götterdämmerung", "WWV 86D", "1876", "Final evening of the Ring."),
    ("meistersinger", "Die Meistersinger von Nürnberg", "WWV 96", "1868", "Comedy in three acts."),
    ("parsifal", "Parsifal", "WWV 111", "1882", "Bühnenweihfestspiel for Bayreuth."),
    ("lohengrin", "Lohengrin", "WWV 75", "1850", "Romantic opera; Weimar premiere under Liszt."),
    ("tannhauser", "Tannhäuser", "WWV 70", "1845/1861", "Dresden and Paris versions."),
    ("hollander", "Der fliegende Holländer", "WWV 63", "1843", "Romantic opera in one or three acts."),
    ("wesendonck", "Wesendonck Lieder", "WWV 91", "1857–58", "Five songs; piano and orchestral versions."),
    ("siegfried_idyll", "Siegfried Idyll", "WWV 103", "1870", "Chamber-orchestra birthday piece."),
]

VERDI = [
    ("traviata", "La traviata", "—", "1853", "After Dumas fils; Violetta."),
    ("rigoletto", "Rigoletto", "—", "1851", "After Hugo; Mantua court."),
    ("trovatore", "Il trovatore", "—", "1853", "Spanish melodrama; Anvil Chorus."),
    ("aida", "Aida", "—", "1871", "Commissioned for Cairo."),
    ("otello", "Otello", "—", "1887", "After Shakespeare; Boito libretto."),
    ("falstaff", "Falstaff", "—", "1893", "Final opera; after Merry Wives and Henry IV."),
    ("don_carlos", "Don Carlos", "—", "1867/1884", "French grand opera; Italian revisions."),
    ("ballo", "Un ballo in maschera", "—", "1859", "Gustavus / Riccardo versions."),
    ("requiem", "Messa da Requiem", "—", "1874", "For Manzoni; four soloists, chorus, orchestra."),
    ("macbeth", "Macbeth", "—", "1847/1865", "First Shakespeare opera; Paris revision."),
    ("boccanegra", "Simon Boccanegra", "—", "1857/1881", "Revised with Boito."),
    ("nabucco", "Nabucco", "—", "1842", "Third opera; Va, pensiero."),
]

MAHLER = [
    ("sym1", "Symphony No. 1", "—", "1888", "D major; Blumine movement sometimes restored."),
    ("sym2", "Symphony No. 2, Resurrection", "—", "1894", "C minor; chorus and soloists in the finale."),
    ("sym3", "Symphony No. 3", "—", "1896", "Six movements; alto solo and choirs."),
    ("sym4", "Symphony No. 4", "—", "1900", "G major; soprano finale."),
    ("sym5", "Symphony No. 5", "—", "1902", "C-sharp minor; Adagietto."),
    ("sym6", "Symphony No. 6, Tragic", "—", "1904", "A minor; order of the middle movements disputed."),
    ("sym9", "Symphony No. 9", "—", "1909", "D major; last completed symphony."),
    ("lied_von_der_erde", "Das Lied von der Erde", "—", "1909", "Symphony for two voices and orchestra after Bethge."),
    ("kindertotenlieder", "Kindertotenlieder", "—", "1904", "Five Rückert songs for voice and orchestra."),
    ("knaben_wunderhorn", "Des Knaben Wunderhorn", "—", "1892–1901", "Song settings from the Arnim/Brentano collection."),
    ("sym7", "Symphony No. 7", "—", "1905", "E minor; five movements with two Nachtmusiken."),
    ("sym8", "Symphony No. 8", "—", "1906", "E-flat; Veni creator and Faust Part II."),
]

DEBUSSY = [
    ("apres_midi", "Prélude à l'après-midi d'un faune", "—", "1894", "Orchestral prelude after Mallarmé."),
    ("la_mer", "La mer", "—", "1905", "Three symphonic sketches."),
    ("nocturnes", "Nocturnes", "—", "1899", "Nuages, Fêtes, Sirènes; female chorus in III."),
    ("pelleas", "Pelléas et Mélisande", "—", "1902", "Opera after Maeterlinck."),
    ("preludes", "Préludes, Books I & II", "—", "1910 / 1913", "Twenty-four piano preludes."),
    ("images", "Images (piano)", "—", "1905 / 1907", "Two books of piano Images."),
    ("string_quartet", "String Quartet", "—", "1893", "G minor, Op. 10."),
    ("childrens_corner", "Children's Corner", "—", "1908", "Six piano pieces dedicated to Chou-Chou."),
    ("suite_bergamasque", "Suite bergamasque", "—", "1905", "Piano suite; includes Clair de lune."),
    ("jeux", "Jeux", "—", "1913", "Poème dansé for Diaghilev."),
    ("sonata_flute_viola_harp", "Sonata for flute, viola and harp", "—", "1915", "Late chamber sonata."),
    ("etudes", "Études", "—", "1915", "Twelve piano studies in two books."),
]


COMPOSERS = [
    ("bach", "Johann Sebastian Bach", "1685–1750", BACH),
    ("beethoven", "Ludwig van Beethoven", "1770–1827", BEETHOVEN),
    ("mozart", "Wolfgang Amadeus Mozart", "1756–1791", MOZART),
    ("puccini", "Giacomo Puccini", "1858–1924", PUCCINI),
    ("shostakovich", "Dmitri Shostakovich", "1906–1975", SHOSTAKOVICH),
    ("brahms", "Johannes Brahms", "1833–1897", BRAHMS),
    ("haydn", "Joseph Haydn", "1732–1809", HAYDN),
    ("schubert", "Franz Schubert", "1797–1828", SCHUBERT),
    ("handel", "George Frideric Handel", "1685–1759", HANDEL),
    ("chopin", "Frédéric Chopin", "1810–1849", CHOPIN),
    ("tchaikovsky", "Pyotr Ilyich Tchaikovsky", "1840–1893", TCHAIKOVSKY),
    ("wagner", "Richard Wagner", "1813–1883", WAGNER),
    ("verdi", "Giuseppe Verdi", "1813–1901", VERDI),
    ("mahler", "Gustav Mahler", "1860–1911", MAHLER),
    ("debussy", "Claude Debussy", "1862–1918", DEBUSSY),
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
            } for i, (s, d, e, lab, yr) in enumerate(_merged_candidates().get(key, []))]
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
