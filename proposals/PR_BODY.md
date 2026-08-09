# Harvest 20260809

`harvest/1.1` · contact `harvest@example.invalid` · budget **300** · **76** requests · **69** proposals

## Expected cost

- Seed: **59** works · **72** candidates · **0** already have an mbid
- Budget cap: **300** requests (MusicBrainz ~1 req/s; CAA ~0.6s gap)
- This run: **76** network requests
- Wall-clock if live: ~76–106s under polite rate limits

| Stage | Planned |
|---|---|
| identity | 72 |

## Identity confidence

- Identity proposals: **69** / 72 candidates
- `auto_accept_eligible` (confidence ≥ 80, no compilation/date flags): **26**
- Uncertain / must stay for human review: **43**
- Unresolved (no MusicBrainz hit this run): **3**
- **Do not auto-accept below 80.** Reject compilations, samplers, wrong-decade matches.

## Covers (Cover Art Archive only)

- Cover proposals: **0** · hits **0** · misses **0**
- Cover stage stays gated until identity mbids are human-merged (pipeline does not build on unreviewed guesses).
- When covers run: CAA JSON hotlinks only — no image binaries, no Discogs. Misses include an upstream upload prompt.

### Unresolved candidates

- `beethoven/pc5/0`
- `shostakovich/sym10/1`
- `shostakovich/sym10/2`

### Identity review table

| Target | Seed | MusicBrainz | Conf. | Eligible | Flags |
|---|---|---|---|---|---|
| `bach/brandenburg/1` | Nikolaus Harnoncourt; Teldec, 1964 | Brandenburgische Konzerte (1967) | 56 | **no** | confidence 56 < 80 |
| `bach/cello_suites/1` | Pierre Fournier; Archiv, 1961 | Sechs Suiten für Violoncello solo, BWV 1007–1012 (1961) | 88 | yes |  |
| `bach/sonatas_partitas/0` | Nathan Milstein; Deutsche Grammophon, 1973 | Sonatas and Partitas for Solo Violin (1975) | 100 | yes |  |
| `bach/goldberg/0` | Glenn Gould; Columbia, 1955 | The Goldberg Variations (1956-03-01) | 100 | yes |  |
| `bach/goldberg/2` | Wanda Landowska; RCA, 1945 | Goldberg Variations / Italian Concerto / Chromatic Fantasy and Fugue (1987) | 62 | **no** | confidence 62 < 80; date off by 42 years (1945 vs 1987) |
| `bach/mass_b_minor/1` | Nikolaus Harnoncourt; Teldec, 1968 | Messe in h-Moll (1984) | 52 | **no** | confidence 52 < 80; date off by 16 years (1968 vs 1984) |
| `bach/matthew/0` | Otto Klemperer; EMI, 1961 | St. Matthew Passion (1962) | 100 | yes |  |
| `beethoven/sym3/0` | Otto Klemperer; EMI, 1959 | Symphony no. 3 in E-flat "Eroica" / Grosse Fuge in B-flat (1985) | 82 | **no** | date off by 26 years (1959 vs 1985) |
| `beethoven/sym5/0` | Carlos Kleiber; Deutsche Grammophon, 1974 | Symphonie Nr. 5 (1975) | 100 | yes |  |
| `beethoven/sym5/1` | Wilhelm Furtwängler; EMI, 1954 | Symphony n. 4 op. 60 / Symphony n. 5 op. 67 / “Coriolan”, Overture (1994) | 70 | **no** | confidence 70 < 80; date off by 40 years (1954 vs 1994) |
| `beethoven/sym9/0` | Wilhelm Furtwängler; EMI, 1951 | Sinfonie Nr.7 (Nr. 9) C-dur op. posth. (1958-12) | 71 | **no** | confidence 71 < 80; date off by 7 years (1951 vs 1958) |
| `beethoven/sym9/1` | Herbert von Karajan; Deutsche Grammophon, 1962 | Symphonie No. 9 (1986) | 100 | **no** | date off by 24 years (1962 vs 1986) |
| `beethoven/violin_concerto/0` | Charles Munch; RCA, 1955 | Concerto No. 1 (1959) | 58 | **no** | confidence 58 < 80; date off by 4 years (1955 vs 1959) |
| `beethoven/missa_solemnis/0` | Otto Klemperer; EMI, 1965 | Missa solemnis (1966-07) | 100 | yes |  |
| `beethoven/fidelio/0` | Otto Klemperer; EMI, 1962 | Fidelio (1989) | 94 | **no** | date off by 27 years (1962 vs 1989) |
| `mozart/pc20/0` | Igor Markevitch; Philips, 1960 | Piano Concertos Nos. 20 & 24 (2001) | 100 | **no** | date off by 41 years (1960 vs 2001) |
| `mozart/clarinet_concerto/0` | Thomas Beecham; EMI, 1959 | Clarinet Concerto / Bassoon Concerto (1987) | 100 | **no** | date off by 28 years (1959 vs 1987) |
| `mozart/requiem/0` | Karl Böhm; Deutsche Grammophon, 1971 | Requiem (1971) | 100 | yes |  |
| `mozart/figaro/0` | Erich Kleiber; Decca, 1955 | Le nozze di Figaro (1989) | 100 | **no** | date off by 34 years (1955 vs 1989) |
| `mozart/figaro/1` | Carlo Maria Giulini; EMI, 1959 | Le nozze di Figaro (1961) | 100 | yes |  |
| `mozart/don_giovanni/0` | Carlo Maria Giulini; EMI, 1959 | Don Carlo (1971) | 26 | **no** | confidence 26 < 80; date off by 12 years (1959 vs 1971) |
| `mozart/don_giovanni/1` | Wilhelm Furtwängler; EMI, 1954 | Don Giovanni (1991) | 97 | **no** | date off by 37 years (1954 vs 1991) |
| `mozart/cosi/0` | Karl Böhm; EMI, 1962 | Così fan tutte (1988-10) | 98 | **no** | date off by 26 years (1962 vs 1988) |
| `mozart/zauberflote/0` | Otto Klemperer; EMI, 1964 | Die Zauberflöte (1964) | 100 | yes |  |
| `mozart/zauberflote/1` | Karl Böhm; Deutsche Grammophon, 1964 | Die Zauberflöte (1964) | 100 | yes |  |
| `puccini/manon_lescaut/0` | Tullio Serafin; EMI, 1957 | Manon Lescaut (1959) | 100 | yes |  |
| `puccini/boheme/0` | Thomas Beecham; EMI, 1956 | La bohème (1956-12) | 97 | yes |  |
| `puccini/boheme/1` | Herbert von Karajan; Decca, 1972 | La bohème (1973) | 100 | yes |  |
| `puccini/tosca/0` | Victor de Sabata; EMI, 1953 | Tosca (1985-11-10) | 100 | **no** | date off by 32 years (1953 vs 1985) |
| `puccini/tosca/1` | Herbert von Karajan; Decca, 1962 | Tosca (1984-11-22) | 93 | **no** | date off by 22 years (1962 vs 1984) |
| `puccini/tosca/2` | Georges Prêtre; EMI, 1964 | Tosca (1989-05-16) | 100 | **no** | date off by 25 years (1964 vs 1989) |
| `puccini/butterfly/0` | John Barbirolli; EMI, 1966 | Madama Butterfly (1986) | 100 | **no** | date off by 20 years (1966 vs 1986) |
| `puccini/butterfly/1` | Herbert von Karajan; Decca, 1974 | Madama Butterfly (1974) | 100 | yes |  |
| `puccini/fanciulla/0` | Franco Capuana; Decca, 1958 | La fanciulla del West (1988-10-26) | 100 | **no** | date off by 30 years (1958 vs 1988) |
| `puccini/turandot/0` | Francesco Molinari-Pradelli; EMI, 1965 | Turandot (1988) | 100 | **no** | date off by 23 years (1965 vs 1988) |
| `puccini/turandot/1` | Zubin Mehta; Decca, 1972 | Turandot (1973) | 89 | yes |  |
| `shostakovich/sym5/0` | Yevgeny Mravinsky; various, 1954 | Symphony no. 5, op. 47 / Symphony no. 12 "The Year 1917" (2016-04-15) | 100 | **no** | date off by 62 years (1954 vs 2016) |
| `shostakovich/sym5/1` | Leonard Bernstein; Columbia, 1959 | Symphony no. 5, op. 47 (1959) | 52 | **no** | confidence 52 < 80 |
| `shostakovich/sym5/3` | André Previn; EMI, 1965 | The 5 Piano Concertos (1989) | 89 | **no** | date off by 24 years (1965 vs 1989) |
| `shostakovich/sym10/0` | Herbert von Karajan; Deutsche Grammophon, 1966 | Symphonie No. 10 (1990-05-02) | 100 | **no** | date off by 24 years (1966 vs 1990) |
| `shostakovich/sym13/0` | Kirill Kondrashin; Melodiya, 1967 | Symphony No. 13, Op. 113 "Babi Yar" (2017-11-22) | 100 | **no** | date off by 50 years (1967 vs 2017) |
| `bach/brandenburg/0` | Trevor Pinnock; Archiv, 1982 | Brandenburg Concertos nos. 4-6 (1983-10-17) | 100 | yes |  |
| `bach/brandenburg/2` | Claudio Abbado; Deutsche Grammophon, 2007 | Piano Concertos (2006-09-01) | 37 | **no** | confidence 37 < 80 |
| `bach/cello_suites/0` | Pablo Casals; EMI, 1936–39 | Suites pour violoncelle seul N° 5 en do mineur / N° 6 en ré majeur (1957-07) | 38 | **no** | confidence 38 < 80; date off by 21 years (1936 vs 1957) |
| `bach/cello_suites/2` | Anner Bylsma; Sony Vivarte, 1992 | Suites for Violoncello Solo, BWV 1007-1012 (1992-01-31) | 53 | **no** | confidence 53 < 80 |
| `bach/sonatas_partitas/1` | Rachel Podger; Channel Classics, 1999 | Complete Sonatas & Partitas for Solo Violin (2002) | 100 | yes |  |
| `bach/goldberg/1` | Glenn Gould; CBS, 1981 | The Goldberg Variations (1982) | 100 | yes |  |
| `bach/mass_b_minor/0` | John Eliot Gardiner; Archiv, 1985 | Mass in B minor (1984-12-09) | 100 | yes |  |
| `bach/matthew/1` | John Eliot Gardiner; Archiv, 1988 | St. Matthew Passion (1989-09-15) | 100 | yes |  |
| `beethoven/sym3/1` | John Eliot Gardiner; Archiv, 1993 | Symphony no. 3 "Eroica" (None) | 100 | yes |  |
| `beethoven/sym7/0` | Carlos Kleiber; Deutsche Grammophon, 1976 | Symphonie Nr. 7 (1976) | 75 | **no** | confidence 75 < 80 |
| `beethoven/sym9/2` | John Eliot Gardiner; Archiv, 1992 | Symphonies no. 8 & 9 (1993) | 64 | **no** | confidence 64 < 80 |
| `beethoven/pc5/1` | Karl Böhm; Deutsche Grammophon, 1978 | Klavierkonzert no. 5 Es-Dur op. 73 (1979) | 55 | **no** | confidence 55 < 80 |
| `beethoven/violin_concerto/1` | Carlo Maria Giulini; EMI, 1980 | Violin Concerto (1981) | 100 | yes |  |
| `beethoven/late_quartets/0` | Busch Quartet; EMI, 1930s | Beethoven: The Late String Quartets (vol.2) (1993) | 82 | **no** | date off by 63 years (1930 vs 1993) |
| `beethoven/late_quartets/1` | Quartetto Italiano; Philips, 1967–75 | The Late String Quartets (1989) | 100 | **no** | date off by 22 years (1967 vs 1989) |
| `mozart/late_symphonies/0` | Karl Böhm; Deutsche Grammophon, 1960s | Symphonies Nos. 39, 40 & 41 (1999) | 100 | **no** | date off by 39 years (1960 vs 1999) |
| `mozart/late_symphonies/1` | Nikolaus Harnoncourt; Teldec, 1980s | Symphonies nos. 40 & 41 “Jupiter” (1992) | 99 | **no** | date off by 12 years (1980 vs 1992) |
| `mozart/pc20/1` | Neville Marriner; Philips, 1970s | Piano Concertos no. 20, K. 466, & no. 24, K. 491 / Concert Rondo, K. 382 (1982) | 99 | **no** | date off by 12 years (1970 vs 1982) |
| `mozart/clarinet_concerto/1` | Christopher Hogwood; L'Oiseau-Lyre, 1980s | Clarinet and Oboe Concertos (1986) | 76 | **no** | confidence 76 < 80; date off by 6 years (1980 vs 1986) |
| `mozart/requiem/1` | John Eliot Gardiner; Philips, 1986 | Requiem in D minor / Kyrie in D minor (1987-09-03) | 71 | **no** | confidence 71 < 80 |
| `shostakovich/sym5/2` | Bernard Haitink; Decca, 1981 | 5 Klavierkonzerte (1977) | 100 | **no** | date off by 4 years (1981 vs 1977) |
| `shostakovich/sym5/4` | Mstislav Rostropovich; Teldec, 1993 | Cello Concerto no. 2 / Symphony no. 5 (1993) | 100 | yes |  |
| `shostakovich/sym5/5` | Vasily Petrenko; Naxos, 2009 | Symphonies nos. 5 & 9 (2009-10) | 100 | yes |  |
| `shostakovich/sym5/6` | Andris Nelsons; Deutsche Grammophon, 2016 | Under Stalin’s Shadow: Symphonies nos. 5 / 8 / 9 (2016-05-27) | 37 | **no** | confidence 37 < 80 |
| `shostakovich/sym7/0` | Leonard Bernstein; Deutsche Grammophon, 1988 | Symphony no. 1 / Symphony no. 7 “Leningrad” (1989-09) | 86 | yes |  |
| `shostakovich/sym8/0` | Yevgeny Mravinsky; Praga, 1982 | Shostakovich: Symphony no. 8, op. 65 / Scriabin: Le Poème de l'extase, op. 54 (2015-05-05) | 100 | **no** | date off by 33 years (1982 vs 2015) |
| `shostakovich/sym8/1` | Andris Nelsons; Deutsche Grammophon, 2016 | Under Stalin’s Shadow: Symphonies nos. 5 / 8 / 9 (2016-05-27) | 100 | yes |  |
| `bach/brandenburg/3` | Benjamin Britten; Decca, 1968 | Piano Concertos (1988) | 29 | **no** | confidence 29 < 80; date off by 20 years (1968 vs 1988) |

## Review checklist

- [ ] Identity matches are the right recording, not a compilation / sampler
- [ ] No identity with confidence < 80 is treated as auto-accept
- [ ] Uncertain rows reviewed against MusicBrainz (`mb_url`) before merge
- [ ] Cover payloads are CAA / MusicBrainz hotlinks only (no binaries, no Discogs)
- [ ] Barcodes belong to the edition claimed (editions stage)
- [ ] No review text has been copied into any payload
- [ ] Every score carries a locator, or it stays `draft`

## Stop

Human identity review gate. Do not begin editions/covers apply until mbids are ratified.

## Agent notes (Role B)

- User-Agent contact used for this run: `harvest@example.invalid` (placeholder; replace with `HARVEST_CONTACT` in CI when set).
- Dry-run plan: **72** identity requests planned against budget **300** (well inside cap).
- Live spend this session: ~76 MusicBrainz requests (initial pass + retries after 503/timeouts).
- MusicBrainz returned intermittent **HTTP 503** / timeouts; transient failures no longer advance the harvest cursor into a multi-day backoff.
- Covers were **not** harvested from unreviewed identity mbids (gated per PROGRAM.md). Cover adapter in `agents/harvest.py` uses CAA JSON hotlinks only for the post-merge round.
- Review helper: `python3 agents/review.py proposals/proposals-20260809.json --markdown` (mirrored in `proposals/IDENTITY_REVIEW.md`).

