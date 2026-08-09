"""
seed_candidates_dense.py — supplementary candidate recordings for the editorial seed.

Facts only: soloists, director, ensemble, label, year. No scores or assessments.
Merged into CANDIDATES by seed_catalogue.py at build time.
"""

# (soloists, director, ensemble, label, year)
EXTRA_CANDIDATES: dict[str, list[tuple]] = {
    # ── Bach: empty works (priority) ──────────────────────────────────────────
    "bach/suites": [
        ("", "Trevor Pinnock", "The English Concert", "Archiv", "1980s"),
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1960s"),
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Archiv", "1994"),
        ("", "Karl Richter", "Münchener Bach-Orchester", "Archiv", "1960s"),
        ("", "Christopher Hogwood", "Academy of Ancient Music", "L'Oiseau-Lyre", "1980s"),
    ],
    "bach/violin_concertos": [
        ("Itzhak Perlman", "Daniel Barenboim", "English Chamber Orchestra", "EMI", "1978"),
        ("Nathan Milstein", "", "New Philharmonia", "EMI", "1970s"),
        ("Gidon Kremer", "", "Chamber Orchestra of Europe", "Deutsche Grammophon", "1988"),
        ("Yehudi Menuhin", "Wilhelm Furtwängler", "Berliner Philharmoniker", "EMI", "1951"),
        ("Rachel Podger", "", "Brecon Baroque", "Channel Classics", "2009"),
    ],
    "bach/wtc": [
        ("Glenn Gould", "", "", "Columbia", "1955"),
        ("Glenn Gould", "", "", "CBS", "1972"),
        ("Wanda Landowska", "", "", "RCA", "1940s"),
        ("András Schiff", "", "", "Decca", "1980s"),
        ("Angela Hewitt", "", "", "Hyperion", "2000s"),
    ],
    "bach/john": [
        ("", "Otto Klemperer", "Philharmonia", "EMI", "1961"),
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Archiv", "1986"),
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1965"),
        ("", "Karl Richter", "Münchener Bach-Orchester", "Archiv", "1964"),
        ("", "Philippe Herreweghe", "Collegium Vocale Gent", "Harmonia Mundi", "1990s"),
    ],
    "bach/art_of_fugue": [
        ("Glenn Gould", "", "", "CBS", "1962"),
        ("Tatiana Nikolayeva", "", "", "Hyperion", "1980s"),
        ("Davitt Moroney", "", "", "Harmonia Mundi", "2000"),
        ("Emerson String Quartet", "", "", "Deutsche Grammophon", "2003"),
        ("Gustav Leonhardt", "", "", "Deutsche Harmonia Mundi", "1969"),
    ],
    "bach/harpsichord_concertos": [
        ("Trevor Pinnock", "Trevor Pinnock", "The English Concert", "Archiv", "1980s"),
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1960s"),
        ("Gustav Leonhardt", "Gustav Leonhardt", "Leonhardt Consort", "Deutsche Harmonia Mundi", "1970s"),
        ("Murray Perahia", "", "English Chamber Orchestra", "Sony", "1980s"),
        ("András Schiff", "Karl Richter", "Münchener Bach-Orchester", "Deutsche Grammophon", "1990s"),
    ],
    # Bach: boost thin / two-candidate works
    "bach/mass_b_minor": [
        ("", "Karl Richter", "Münchener Bach-Orchester", "Archiv", "1969"),
        ("", "Philippe Herreweghe", "Collegium Vocale Gent", "Harmonia Mundi", "1990s"),
    ],
    "bach/matthew": [
        ("", "Wilhelm Furtwängler", "Wiener Philharmoniker", "EMI", "1954"),
        ("", "Karl Richter", "Münchener Bach-Orchester", "Archiv", "1964"),
    ],
    "bach/sonatas_partitas": [
        ("Henryk Szeryng", "", "", "Philips", "1960s"),
        ("Arthur Grumiaux", "", "", "Philips", "1970s"),
    ],
    "bach/cello_suites": [
        ("Yo-Yo Ma", "", "", "Sony", "1983"),
        ("Mstislav Rostropovich", "", "", "EMI", "1991"),
    ],
    "bach/goldberg": [
        ("Murray Perahia", "", "", "Deutsche Grammophon", "2000"),
        ("András Schiff", "", "", "Decca", "1982"),
    ],
    "bach/brandenburg": [
        ("", "Karl Richter", "Münchener Bach-Orchester", "Archiv", "1960s"),
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Archiv", "1990s"),
    ],
    # ── Beethoven ───────────────────────────────────────────────────────────
    "beethoven/sym6": [
        ("", "Carlos Kleiber", "Wiener Philharmoniker", "Deutsche Grammophon", "1983"),
        ("", "Bruno Walter", "Columbia Symphony Orchestra", "Columbia", "1950s"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
        ("", "John Eliot Gardiner", "Orchestre Révolutionnaire et Romantique", "Archiv", "1990s"),
        ("", "Wilhelm Furtwängler", "Berliner Philharmoniker", "EMI", "1954"),
    ],
    "beethoven/pc4": [
        ("Wilhelm Kempff", "Ferdinand Leitner", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
        ("Maurizio Pollini", "Claudio Abbado", "Berliner Philharmoniker", "Deutsche Grammophon", "1979"),
        ("Emil Gilels", "George Szell", "Cleveland Orchestra", "EMI", "1960s"),
        ("Martha Argerich", "Claudio Abbado", "Berliner Philharmoniker", "Deutsche Grammophon", "1980s"),
        ("Claudio Arrau", "Colin Davis", "Boston Symphony", "Philips", "1970s"),
    ],
    "beethoven/hammerklavier": [
        ("Wilhelm Kempff", "", "", "Deutsche Grammophon", "1950s"),
        ("Sviatoslav Richter", "", "", "Philips", "1970s"),
        ("Maurizio Pollini", "", "", "Deutsche Grammophon", "1975"),
        ("Alfred Brendel", "", "", "Philips", "1970s"),
        ("Igor Levit", "", "", "Sony", "2019"),
    ],
    "beethoven/fidelio": [
        ("Christine Schäfer, Jonas Kaufmann", "Claudio Abbado", "Chamber Orchestra of Europe", "Deutsche Grammophon", "2010"),
        ("Lucia Popp, Plácido Domingo", "Leonard Bernstein", "Vienna State Opera", "Deutsche Grammophon", "1979"),
        ("", "Ferdinand Leitner", "Wiener Philharmoniker", "Deutsche Grammophon", "1960s"),
    ],
    "beethoven/missa_solemnis": [
        ("", "Leonard Bernstein", "Concertgebouw Orchestra", "Deutsche Grammophon", "1978"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1966"),
        ("", "John Eliot Gardiner", "Orchestre Révolutionnaire et Romantique", "Archiv", "1990s"),
    ],
    "beethoven/sym7": [
        ("", "Arturo Toscanini", "NBC Symphony Orchestra", "RCA", "1930s"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
        ("", "Bruno Walter", "Columbia Symphony Orchestra", "Columbia", "1950s"),
    ],
    "beethoven/sym3": [
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1962"),
        ("", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1964"),
    ],
    "beethoven/sym5": [
        ("", "Arturo Toscanini", "NBC Symphony Orchestra", "RCA", "1952"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1962"),
    ],
    "beethoven/late_quartets": [
        ("Alban Berg Quartet", "", "", "EMI", "1980s"),
        ("Vienna Philharmonic Quartet", "", "", "Deutsche Grammophon", "1960s"),
    ],
    "beethoven/pc5": [
        ("Emil Gilels", "George Szell", "Cleveland Orchestra", "EMI", "1960s"),
        ("Daniel Barenboim", "Otto Klemperer", "New Philharmonia", "EMI", "1967"),
    ],
    "beethoven/violin_concerto": [
        ("David Oistrakh", "Franz Konwitschny", "Staatskapelle Dresden", "Deutsche Grammophon", "1960s"),
        ("Anne-Sophie Mutter", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1980s"),
    ],
    "beethoven/sym9": [
        ("", "Leonard Bernstein", "Concertgebouw Orchestra", "Deutsche Grammophon", "1985"),
        ("", "Claudio Abbado", "Berliner Philharmoniker", "Deutsche Grammophon", "2000"),
    ],
    # ── Mozart ────────────────────────────────────────────────────────────────
    "mozart/pc23": [
        ("Friedrich Gulda", "Claudio Abbado", "Wiener Philharmoniker", "Deutsche Grammophon", "1970s"),
        ("Murray Perahia", "", "English Chamber Orchestra", "Sony", "1980s"),
        ("Mitsuko Uchida", "", "English Chamber Orchestra", "Philips", "1981"),
        ("Vladimir Ashkenazy", "", "Philharmonia", "Decca", "1960s"),
        ("Daniel Barenboim", "", "English Chamber Orchestra", "EMI", "1970s"),
    ],
    "mozart/pc27": [
        ("Vladimir Horowitz", "", "", "RCA", "1950s"),
        ("Mitsuko Uchida", "", "English Chamber Orchestra", "Philips", "1981"),
        ("Friedrich Gulda", "", "Wiener Philharmoniker", "Orfeo", "1989"),
        ("Alfred Brendel", "", "Scottish Chamber Orchestra", "Philips", "1990s"),
        ("Ingrid Haebler", "", "Salzburg Mozarteum Orchestra", "Philips", "1970s"),
    ],
    "mozart/mass_c_minor": [
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Archiv", "1990s"),
        ("", "Neville Marriner", "Academy of St Martin in the Fields", "Philips", "1970s"),
        ("", "Karl Böhm", "Wiener Symphoniker", "Deutsche Grammophon", "1960s"),
        ("", "Leonard Bernstein", "Concertgebouw Orchestra", "Deutsche Grammophon", "1978"),
        ("", "Christopher Hogwood", "Academy of Ancient Music", "L'Oiseau-Lyre", "1980s"),
    ],
    "mozart/string_quintets": [
        ("Quintetto Boccherini", "", "", "Philips", "1970s"),
        ("", "Neville Marriner", "Academy of St Martin in the Fields", "Philips", "1970s"),
        ("Grumiaux Trio and colleagues", "", "", "Philips", "1960s"),
        ("L'Archibudelli", "", "", "Sony", "1990s"),
        ("", "Christopher Hogwood", "Academy of Ancient Music", "L'Oiseau-Lyre", "1980s"),
    ],
    "mozart/cosi": [
        ("", "James Levine", "Metropolitan Opera", "Deutsche Grammophon", "1990s"),
        ("", "Neville Marriner", "Academy of St Martin in the Fields", "Philips", "1970s"),
        ("", "Riccardo Muti", "Wiener Philharmoniker", "EMI", "1980s"),
    ],
    "mozart/clarinet_concerto": [
        ("Sabine Meyer", "Claudio Abbado", "Berliner Philharmoniker", "Deutsche Grammophon", "1990s"),
        ("Richard Stoltzman", "Raymond Leppard", "English Chamber Orchestra", "RCA", "1980s"),
    ],
    "mozart/don_giovanni": [
        ("", "Dimitri Mitropoulos", "Metropolitan Opera", "Sony", "1950s"),
        ("", "Colin Davis", "Royal Opera House", "Philips", "1970s"),
    ],
    "mozart/figaro": [
        ("", "Karl Böhm", "Deutsche Oper Berlin", "Deutsche Grammophon", "1960s"),
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Archiv", "1990s"),
    ],
    "mozart/late_symphonies": [
        ("", "Charles Mackerras", "Scottish Chamber Orchestra", "Telarc", "1990s"),
        ("", "Leonard Bernstein", "Wiener Philharmoniker", "Deutsche Grammophon", "1980s"),
    ],
    "mozart/pc20": [
        ("Friedrich Gulda", "Bernard Haitink", "Concertgebouw Orchestra", "Philips", "1970s"),
        ("Mitsuko Uchida", "Jeffrey Tate", "English Chamber Orchestra", "Philips", "1980s"),
    ],
    "mozart/requiem": [
        ("", "Herbert von Karajan", "Wiener Philharmoniker", "Deutsche Grammophon", "1960s"),
        ("", "Christopher Hogwood", "Academy of Ancient Music", "L'Oiseau-Lyre", "1980s"),
    ],
    "mozart/zauberflote": [
        ("", "Colin Davis", "Staatskapelle Dresden", "Philips", "1980s"),
        ("", "James Levine", "Metropolitan Opera", "Deutsche Grammophon", "1990s"),
    ],
    # ── Puccini ─────────────────────────────────────────────────────────────
    "puccini/edgar": [
        ("Montserrat Caballé, Plácido Domingo", "James Levine", "Metropolitan Opera", "Sony", "1990s"),
        ("", "Gianandrea Gavazzeni", "RAI Symphony Orchestra", "RAI", "1970s"),
        ("", "Alberto Erede", "Orchestra Sinfonica di Torino", "Decca", "1950s"),
        ("", "Daniele Gatti", "Orchestra dell'Accademia Nazionale di Santa Cecilia", "Decca", "2000s"),
        ("", "Gianandrea Gavazzeni", "La Scala", "EMI", "1960s"),
    ],
    "puccini/messa_gloria": [
        ("", "Riccardo Muti", "Philharmonia", "EMI", "1980s"),
        ("", "Antonio Pappano", "Orchestra dell'Accademia Nazionale di Santa Cecilia", "EMI", "2000s"),
        ("", "Daniele Gatti", "Orchestra Sinfonica di Milano", "Decca", "1990s"),
        ("", "Alberto Erede", "Orchestra Sinfonica di Torino", "Decca", "1950s"),
        ("", "Gianandrea Gavazzeni", "RAI Symphony Orchestra", "RAI", "1960s"),
    ],
    "puccini/rondine": [
        ("Mirella Freni, José Carreras", "Gianandrea Gavazzeni", "La Scala", "EMI", "1960s"),
        ("Angela Gheorghiu, Roberto Alagna", "Antonio Pappano", "London Symphony Orchestra", "EMI", "1990s"),
        ("", "Alberto Zedda", "Orchestra Sinfonica di Torino", "Decca", "1980s"),
        ("", "Daniele Gatti", "Orchestra dell'Accademia Nazionale di Santa Cecilia", "Decca", "2000s"),
        ("", "Gianandrea Gavazzeni", "RAI Symphony Orchestra", "RAI", "1970s"),
    ],
    "puccini/trittico": [
        ("Renata Scotto, Plácido Domingo", "Lorin Maazel", "Metropolitan Opera", "Sony", "1990s"),
        ("", "Antonio Pappano", "Orchestra dell'Accademia Nazionale di Santa Cecilia", "EMI", "2000s"),
        ("", "Gianandrea Gavazzeni", "La Scala", "EMI", "1960s"),
        ("", "Alberto Erede", "Orchestra Sinfonica di Torino", "Decca", "1950s"),
        ("", "Daniele Gatti", "Orchestra Sinfonica di Milano", "Decca", "1990s"),
    ],
    "puccini/villi": [
        ("", "Gianandrea Gavazzeni", "RAI Symphony Orchestra", "RAI", "1960s"),
        ("", "Alberto Erede", "Orchestra Sinfonica di Torino", "Decca", "1950s"),
        ("", "Daniele Gatti", "Orchestra dell'Accademia Nazionale di Santa Cecilia", "Decca", "2000s"),
        ("", "Antonio Pappano", "Orchestra dell'Accademia Nazionale di Santa Cecilia", "EMI", "1990s"),
        ("", "Alberto Zedda", "Orchestra Sinfonica di Torino", "Decca", "1980s"),
    ],
    "puccini/fanciulla": [
        ("Renata Tebaldi, Mario Del Monaco", "Tullio Serafin", "La Scala", "EMI", "1960s"),
        ("Plácido Domingo, Carol Neblett", "Zubin Mehta", "Los Angeles Philharmonic", "Deutsche Grammophon", "1980s"),
        ("", "Lorin Maazel", "Metropolitan Opera", "Sony", "1990s"),
    ],
    "puccini/manon_lescaut": [
        ("Mirella Freni, José Carreras", "Gianandrea Gavazzeni", "La Scala", "EMI", "1970s"),
        ("Renata Scotto, Plácido Domingo", "James Levine", "Metropolitan Opera", "Sony", "1990s"),
        ("", "Riccardo Muti", "Philharmonia", "EMI", "1980s"),
    ],
    "puccini/boheme": [
        ("", "Tullio Serafin", "La Scala", "EMI", "1960s"),
        ("Renata Tebaldi, Carlo Bergonzi", "Tullio Serafin", "La Scala", "Decca", "1959"),
    ],
    "puccini/butterfly": [
        ("Maria Callas, Giuseppe Di Stefano", "Tullio Serafin", "La Scala", "EMI", "1955"),
        ("Angela Gheorghiu, Roberto Alagna", "Antonio Pappano", "London Symphony Orchestra", "EMI", "1990s"),
    ],
    "puccini/turandot": [
        ("Maria Callas, Giuseppe Di Stefano", "Tullio Serafin", "La Scala", "EMI", "1957"),
        ("", "Erich Leinsdorf", "Metropolitan Opera", "RCA", "1960s"),
    ],
    "puccini/tosca": [
        ("Renata Tebaldi, Carlo Bergonzi", "Victor de Sabata", "La Scala", "Decca", "1959"),
        ("Angela Gheorghiu, Roberto Alagna", "Antonio Pappano", "Royal Opera House", "EMI", "2000"),
    ],
    # ── Shostakovich ────────────────────────────────────────────────────────
    "shostakovich/sym1": [
        ("", "Yevgeny Mravinsky", "Leningrad Philharmonic Orchestra", "Melodiya", "1950s"),
        ("", "Mstislav Rostropovich", "London Symphony Orchestra", "LSO Live", "2000s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Decca", "1980s"),
        ("", "Andris Nelsons", "Boston Symphony Orchestra", "Deutsche Grammophon", "2018"),
        ("", "Vasily Petrenko", "Royal Liverpool Philharmonic", "Naxos", "2009"),
    ],
    "shostakovich/sym4": [
        ("", "Kirill Kondrashin", "Moscow Philharmonic", "Melodiya", "1960s"),
        ("", "Mstislav Rostropovich", "London Symphony Orchestra", "LSO Live", "2000s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Decca", "1980s"),
        ("", "Andris Nelsons", "Boston Symphony Orchestra", "Deutsche Grammophon", "2018"),
        ("", "Vasily Petrenko", "Royal Liverpool Philharmonic", "Naxos", "2011"),
    ],
    "shostakovich/sym6": [
        ("", "Yevgeny Mravinsky", "Leningrad Philharmonic Orchestra", "Melodiya", "1960s"),
        ("", "Mstislav Rostropovich", "National Symphony Orchestra", "Teldec", "1990s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Decca", "1980s"),
        ("", "Andris Nelsons", "Boston Symphony Orchestra", "Deutsche Grammophon", "2018"),
        ("", "Vasily Petrenko", "Royal Liverpool Philharmonic", "Naxos", "2010"),
    ],
    "shostakovich/sym9": [
        ("", "Yevgeny Mravinsky", "Leningrad Philharmonic Orchestra", "Melodiya", "1960s"),
        ("", "Mstislav Rostropovich", "London Symphony Orchestra", "LSO Live", "2000s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Decca", "1980s"),
        ("", "Andris Nelsons", "Boston Symphony Orchestra", "Deutsche Grammophon", "2018"),
        ("", "Vasily Petrenko", "Royal Liverpool Philharmonic", "Naxos", "2010"),
    ],
    "shostakovich/sym11": [
        ("", "Yevgeny Mravinsky", "Leningrad Philharmonic Orchestra", "Melodiya", "1960s"),
        ("", "Mstislav Rostropovich", "London Symphony Orchestra", "LSO Live", "2000s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Decca", "1980s"),
        ("", "Andris Nelsons", "Boston Symphony Orchestra", "Deutsche Grammophon", "2018"),
        ("", "Vasily Petrenko", "Royal Liverpool Philharmonic", "Naxos", "2010"),
    ],
    "shostakovich/sym14": [
        ("", "Kirill Kondrashin", "Moscow Philharmonic", "Melodiya", "1970s"),
        ("", "Mstislav Rostropovich", "London Symphony Orchestra", "LSO Live", "2000s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Decca", "1980s"),
        ("", "Andris Nelsons", "Boston Symphony Orchestra", "Deutsche Grammophon", "2018"),
        ("", "Vasily Petrenko", "Royal Liverpool Philharmonic", "Naxos", "2012"),
    ],
    "shostakovich/sym15": [
        ("", "Kirill Kondrashin", "Moscow Philharmonic", "Melodiya", "1970s"),
        ("", "Mstislav Rostropovich", "London Symphony Orchestra", "LSO Live", "2000s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Decca", "1980s"),
        ("", "Andris Nelsons", "Boston Symphony Orchestra", "Deutsche Grammophon", "2018"),
        ("", "Vasily Petrenko", "Royal Liverpool Philharmonic", "Naxos", "2012"),
    ],
    "shostakovich/sym13": [
        ("", "Mstislav Rostropovich", "London Symphony Orchestra", "LSO Live", "2000s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Decca", "1980s"),
        ("", "Andris Nelsons", "Boston Symphony Orchestra", "Deutsche Grammophon", "2018"),
    ],
    "shostakovich/sym7": [
        ("", "Yevgeny Mravinsky", "Leningrad Philharmonic Orchestra", "Melodiya", "1960s"),
        ("", "Mstislav Rostropovich", "National Symphony Orchestra", "Teldec", "1990s"),
        ("", "Andris Nelsons", "Boston Symphony Orchestra", "Deutsche Grammophon", "2018"),
    ],
    "shostakovich/sym8": [
        ("", "Kirill Kondrashin", "Moscow Philharmonic", "Melodiya", "1970s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Decca", "1980s"),
    ],
    "shostakovich/sym10": [
        ("", "Yevgeny Mravinsky", "Leningrad Philharmonic Orchestra", "Melodiya", "1960s"),
        ("", "Mstislav Rostropovich", "London Symphony Orchestra", "LSO Live", "2000s"),
    ],
    # ── Brahms ──────────────────────────────────────────────────────────────
    "brahms/liebeslieder": [
        ("", "Wolfgang Sawallisch", "Bavarian Radio Symphony Orchestra", "EMI", "1980s"),
        ("", "John Eliot Gardiner", "Monteverdi Choir", "Philips", "1990s"),
        ("", "Bernard Haitink", "Concertgebouw Orchestra", "Philips", "1970s"),
    ],
    "brahms/tragic_overture": [
        ("", "Otto Klemperer", "Philharmonia", "EMI", "1950s"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
        ("", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1960s"),
    ],
    "brahms/academic_festival": [
        ("", "Otto Klemperer", "Philharmonia", "EMI", "1950s"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
    ],
    "brahms/clarinet_quintet": [
        ("Karl Leister; Berlin Philharmonic Quartet", "", "", "Deutsche Grammophon", "1980s"),
        ("Sabine Meyer; Vienna Philharmonic Quartet", "", "", "EMI", "1990s"),
    ],
    "brahms/german_requiem": [
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
        ("", "Wilhelm Furtwängler", "Wiener Philharmoniker", "EMI", "1950s"),
    ],
    "brahms/haydn_variations": [
        ("", "Otto Klemperer", "Philharmonia", "EMI", "1950s"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
    ],
    "brahms/pc1": [
        ("Leonard Bernstein", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1960s"),
        ("Krystian Zimerman", "Leonard Bernstein", "Wiener Philharmoniker", "Deutsche Grammophon", "1980s"),
    ],
    "brahms/pc2": [
        ("Leonard Bernstein", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1960s"),
        ("Daniel Barenboim", "Sir Simon Rattle", "Berliner Philharmoniker", "Deutsche Grammophon", "2000s"),
    ],
    "brahms/piano_quintet": [
        ("Leonard Bernstein; Vienna Philharmonic Quartet", "", "", "Deutsche Grammophon", "1960s"),
        ("Murray Perahia; Guarneri Quartet", "", "", "Sony", "1990s"),
    ],
    "brahms/sym4": [
        ("", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1960s"),
        ("", "John Eliot Gardiner", "Orchestre Révolutionnaire et Romantique", "Archiv", "1990s"),
    ],
    "brahms/violin_concerto": [
        ("Anne-Sophie Mutter", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1980s"),
        ("David Oistrakh", "Kirill Kondrashin", "Moscow Philharmonic", "Melodiya", "1960s"),
    ],
    "brahms/sym1": [
        ("", "Leonard Bernstein", "New York Philharmonic", "Columbia", "1960s"),
        ("", "John Eliot Gardiner", "Orchestre Révolutionnaire et Romantique", "Archiv", "1990s"),
    ],
    # ── Haydn ───────────────────────────────────────────────────────────────
    "haydn/cello_concerto1": [
        ("Mstislav Rostropovich", "Colin Davis", "English Chamber Orchestra", "EMI", "1970s"),
        ("Yo-Yo Ma", "José Luis García", "English Chamber Orchestra", "CBS", "1980s"),
    ],
    "haydn/creation": [
        ("", "Colin Davis", "Royal Opera House Orchestra", "Philips", "1970s"),
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1990s"),
    ],
    "haydn/nelson_mass": [
        ("", "Colin Davis", "Bavarian Radio Symphony Orchestra", "Philips", "1970s"),
        ("", "Christopher Hogwood", "Academy of Ancient Music", "L'Oiseau-Lyre", "1980s"),
    ],
    "haydn/op76": [
        ("Esterházy Quartet", "", "", "Deutsche Grammophon", "1960s"),
        ("Tafelmusik Baroque Orchestra", "", "", "Sony", "1990s"),
    ],
    "haydn/piano_sonatas": [
        ("Paul Badura-Skoda", "", "", "Archiv", "1970s"),
        ("John McCabe", "", "", "Hyperion", "1990s"),
    ],
    "haydn/seasons": [
        ("", "Colin Davis", "Royal Opera House Orchestra", "Philips", "1970s"),
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1990s"),
    ],
    "haydn/seven_last_words": [
        ("", "Orchestra of the 18th Century", "Frans Brüggen", "Philips", "1990s"),
        ("", "Berlin Philharmonic", "Herbert von Karajan", "Deutsche Grammophon", "1960s"),
    ],
    "haydn/sym104": [
        ("", "Antal Doráti", "Philharmonia Hungarica", "Decca", "1970s"),
        ("", "Adam Fischer", "Austro-Hungarian Haydn Orchestra", "Nimbus", "1990s"),
    ],
    "haydn/sym44": [
        ("", "Adam Fischer", "Austro-Hungarian Haydn Orchestra", "Nimbus", "1990s"),
        ("", "Thomas Beecham", "Royal Philharmonic", "EMI", "1950s"),
    ],
    "haydn/sym45": [
        ("", "Adam Fischer", "Austro-Hungarian Haydn Orchestra", "Nimbus", "1990s"),
        ("", "Antal Doráti", "Philharmonia Hungarica", "Decca", "1970s"),
    ],
    "haydn/sym94": [
        ("", "Antal Doráti", "Philharmonia Hungarica", "Decca", "1970s"),
        ("", "Adam Fischer", "Austro-Hungarian Haydn Orchestra", "Nimbus", "1990s"),
    ],
    "haydn/trumpet_concerto": [
        ("Timofei Dokschitzer", "Karl Richter", "Münchener Bach-Orchester", "Archiv", "1960s"),
        ("Håkan Hardenberger", "Colin Davis", "London Symphony Orchestra", "Philips", "1990s"),
    ],
    # ── Schubert ────────────────────────────────────────────────────────────
    "schubert/death_maiden": [
        ("Vienna Philharmonic Quartet", "", "", "Deutsche Grammophon", "1960s"),
        ("Emerson String Quartet", "", "", "Deutsche Grammophon", "1990s"),
    ],
    "schubert/impromptus": [
        ("Imogen Cooper", "", "", "Hyperion", "1990s"),
        ("Paul Badura-Skoda", "", "", "Archiv", "1970s"),
    ],
    "schubert/mass_e_flat": [
        ("", "Wolfgang Sawallisch", "Bavarian Radio Symphony Orchestra", "EMI", "1980s"),
        ("", "Philippe Herreweghe", "Collegium Vocale Gent", "Harmonia Mundi", "1990s"),
    ],
    "schubert/rosamunde": [
        ("", "Karl Böhm", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
        ("", "John Eliot Gardiner", "Orchestre Révolutionnaire et Romantique", "Archiv", "1990s"),
    ],
    "schubert/schone_mullerin": [
        ("Ian Bostridge; Julius Drake, piano", "", "", "Hyperion", "1990s"),
        ("Hermann Prey; Karl Engel, piano", "", "", "Deutsche Grammophon", "1970s"),
    ],
    "schubert/schwanengesang": [
        ("Ian Bostridge; Julius Drake, piano", "", "", "Hyperion", "1990s"),
        ("Matthias Goerne; Christoph Eschenbach, piano", "", "", "Deutsche Grammophon", "2000s"),
    ],
    "schubert/string_quintet": [
        ("Vienna Philharmonic Quartet; Heinrich Schiff, cello", "", "", "Deutsche Grammophon", "1990s"),
        ("Yo-Yo Ma; Emerson String Quartet", "", "", "Deutsche Grammophon", "2000s"),
    ],
    "schubert/sym8": [
        ("", "Bruno Walter", "Columbia Symphony Orchestra", "Columbia", "1950s"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
    ],
    "schubert/sym9": [
        ("", "Bruno Walter", "Columbia Symphony Orchestra", "Columbia", "1950s"),
        ("", "Herbert von Karajan", "Berliner Philharmoniker", "Deutsche Grammophon", "1960s"),
    ],
    "schubert/trout": [
        ("Daniel Barenboim; members of the Vienna Octet", "", "", "Deutsche Grammophon", "1980s"),
        ("Murray Perahia; members of the Vienna Octet", "", "", "Sony", "1990s"),
    ],
    "schubert/winterreise": [
        ("Ian Bostridge; Julius Drake, piano", "", "", "Hyperion", "1990s"),
        ("Matthias Goerne; Christoph Eschenbach, piano", "", "", "Deutsche Grammophon", "2000s"),
    ],
    "schubert/sonata_d960": [
        ("Daniel Barenboim", "", "", "Deutsche Grammophon", "1980s"),
        ("Murray Perahia", "", "", "Sony", "1990s"),
    ],
    # ── Handel ──────────────────────────────────────────────────────────────
    "handel/agrippina": [
        ("", "René Jacobs", "Akademie für Alte Musik Berlin", "Harmonia Mundi", "2000s"),
        ("", "John Eliot Gardiner", "English Baroque Soloists", "Philips", "1990s"),
        ("Joyce DiDonato", "Maxim Emelyanychev", "Il Pomo d'Oro", "Erato", "2020"),
    ],
    "handel/alcina": [
        ("Joyce DiDonato", "William Christie", "Les Arts Florissants", "Erato", "2000s"),
        ("", "René Jacobs", "Akademie für Alte Musik Berlin", "Harmonia Mundi", "2000s"),
    ],
    "handel/dixit_dominus": [
        ("", "Andrew Parrott", "Taverner Choir and Players", "EMI", "1990"),
        ("", "William Christie", "Les Arts Florissants", "Erato", "1990s"),
    ],
    "handel/fireworks": [
        ("", "Charles Mackerras", "English Chamber Orchestra", "Decca", "1970s"),
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1990s"),
    ],
    "handel/giulio_cesare": [
        ("Anne Sofie von Otter", "William Christie", "Les Arts Florissants", "Erato", "1990s"),
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1990s"),
    ],
    "handel/israel_in_egypt": [
        ("", "Charles Mackerras", "English Chamber Orchestra", "Decca", "1970s"),
        ("", "William Christie", "Les Arts Florissants", "Erato", "1990s"),
    ],
    "handel/op6": [
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1990s"),
        ("", "Charles Mackerras", "English Chamber Orchestra", "Decca", "1970s"),
    ],
    "handel/organ_concertos": [
        ("Simon Standage", "Trevor Pinnock", "The English Concert", "Archiv", "1990s"),
        ("Richard Egarr", "Richard Egarr", "Academy of Ancient Music", "Harmonia Mundi", "2000s"),
    ],
    "handel/rodelinda": [
        ("Joyce DiDonato", "William Christie", "Les Arts Florissants", "Erato", "2000s"),
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1990s"),
    ],
    "handel/solomon": [
        ("", "Charles Mackerras", "English Chamber Orchestra", "Decca", "1970s"),
        ("", "William Christie", "Les Arts Florissants", "Erato", "1990s"),
    ],
    "handel/water_music": [
        ("", "Nikolaus Harnoncourt", "Concentus Musicus Wien", "Teldec", "1990s"),
        ("", "Charles Mackerras", "English Chamber Orchestra", "Decca", "1970s"),
    ],
    "handel/messiah": [
        ("", "Colin Davis", "London Symphony Orchestra", "Philips", "1966"),
        ("", "William Christie", "Les Arts Florissants", "Erato", "1990s"),
    ],
    # ── Chopin ──────────────────────────────────────────────────────────────
    "chopin/ballades": [
        ("Claudio Arrau", "", "", "Philips", "1978"),
        ("Martha Argerich", "", "", "Deutsche Grammophon", "1984"),
    ],
    "chopin/etudes": [
        ("Claudio Arrau", "", "", "Philips", "1970s"),
        ("Vladimir Ashkenazy", "", "", "Deutsche Grammophon", "1970s"),
    ],
    "chopin/impromptus": [
        ("Claudio Arrau", "", "", "Philips", "1970s"),
        ("Martha Argerich", "", "", "Deutsche Grammophon", "1980s"),
    ],
    "chopin/mazurkas": [
        ("Claudio Arrau", "", "", "Philips", "1970s"),
        ("Murray Perahia", "", "", "Sony", "1990s"),
    ],
    "chopin/nocturnes": [
        ("Maria João Pires", "", "", "Deutsche Grammophon", "1990s"),
        ("Maurizio Pollini", "", "", "Deutsche Grammophon", "1980s"),
    ],
    "chopin/pc1": [
        ("Martha Argerich", "Charles Dutoit", "Orchestre Symphonique de Montréal", "EMI", "1999"),
        ("Maurizio Pollini", "Paul Kletzki", "Philharmonia", "EMI", "1960s"),
    ],
    "chopin/pc2": [
        ("Maurizio Pollini", "Paul Kletzki", "Philharmonia", "EMI", "1960s"),
        ("Krystian Zimerman", "Stanisław Skrowaczewski", "Polish Festival Orchestra", "Deutsche Grammophon", "1999"),
    ],
    "chopin/polonaises": [
        ("Claudio Arrau", "", "", "Philips", "1970s"),
        ("Martha Argerich", "", "", "Deutsche Grammophon", "1980s"),
    ],
    "chopin/preludes": [
        ("Maurizio Pollini", "", "", "Deutsche Grammophon", "1970s"),
        ("Murray Perahia", "", "", "Sony", "1990s"),
    ],
    "chopin/scherzi": [
        ("Martha Argerich", "", "", "Deutsche Grammophon", "1980s"),
        ("Murray Perahia", "", "", "Sony", "1990s"),
    ],
    "chopin/sonata2": [
        ("Martha Argerich", "", "", "Deutsche Grammophon", "1984"),
        ("Claudio Arrau", "", "", "Philips", "1970s"),
    ],
    "chopin/sonata3": [
        ("Maurizio Pollini", "", "", "Deutsche Grammophon", "1980s"),
        ("Claudio Arrau", "", "", "Philips", "1970s"),
    ],
}
