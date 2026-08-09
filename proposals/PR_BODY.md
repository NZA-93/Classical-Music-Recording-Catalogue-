# Harvest 20260809

`harvest/1.2` · contact `harvest@example.invalid` · budget **300** · **300** requests · **310** proposals

## Expected cost

- Seed: **119** works · **511** candidates · **0** already have an mbid
- Budget cap: **300** requests (MusicBrainz ~1 req/s; CAA ~0.6s gap)
- This run: **300** network requests
- Wall-clock if live: ~300–330s under polite rate limits

| Stage | Planned |
|---|---|
| citation | 69 |
| identity | 301 |

## Identity confidence

- Identity proposals: **241** / 511 candidates
- `auto_accept_eligible` (confidence ≥ 80, no compilation/date flags): **71**
- Uncertain / must stay for human review: **170**
- Unresolved (no MusicBrainz hit this run): **270**
- **Do not auto-accept below 80.** Reject compilations, samplers, wrong-decade matches.

## Covers (Cover Art Archive only)

- Cover proposals: **0** · hits **0** · misses **0**
- Cover stage stays gated until identity mbids are human-merged (pipeline does not build on unreviewed guesses).
- When covers run: CAA JSON hotlinks only — no image binaries, no Discogs. Misses include an upstream upload prompt.

### Unresolved candidates

- `bach/brandenburg/5`
- `bach/violin_concertos/4`
- `bach/cello_suites/4`
- `bach/wtc/2`
- `bach/wtc/4`
- `bach/john/4`
- `bach/art_of_fugue/2`
- `bach/harpsichord_concertos/0`
- `bach/harpsichord_concertos/2`
- `beethoven/sym3/3`
- `beethoven/sym6/0`
- `beethoven/pc4/1`
- `beethoven/pc5/0`
- `beethoven/violin_concerto/3`
- `beethoven/late_quartets/3`
- `beethoven/hammerklavier/1`
- `beethoven/hammerklavier/3`
- `beethoven/missa_solemnis/1`
- `beethoven/fidelio/3`
- `mozart/pc20/2`
- `mozart/pc23/0`
- `mozart/pc23/2`
- `mozart/pc23/4`
- `mozart/pc27/0`
- `mozart/pc27/1`
- `mozart/pc27/3`
- `mozart/pc27/4`
- `mozart/clarinet_concerto/2`
- `mozart/requiem/2`
- `mozart/don_giovanni/3`
- `mozart/cosi/2`
- `mozart/zauberflote/2`
- `mozart/mass_c_minor/0`
- `mozart/mass_c_minor/2`
- `mozart/mass_c_minor/4`
- `mozart/string_quintets/1`
- `mozart/string_quintets/2`
- `mozart/string_quintets/3`
- `mozart/string_quintets/4`
- `puccini/manon_lescaut/1`
- `puccini/fanciulla/1`
- `puccini/rondine/0`
- `puccini/rondine/1`
- `puccini/rondine/2`
- `puccini/rondine/3`
- `puccini/rondine/4`
- `puccini/trittico/1`
- `puccini/trittico/2`
- `puccini/trittico/3`
- `puccini/trittico/4`
- `puccini/turandot/3`
- `puccini/villi/0`
- `puccini/villi/1`
- `puccini/villi/2`
- `puccini/villi/3`
- `puccini/villi/4`
- `puccini/edgar/0`
- `puccini/edgar/1`
- `puccini/edgar/2`
- `puccini/edgar/3`
- `puccini/edgar/4`
- `puccini/messa_gloria/0`
- `puccini/messa_gloria/2`
- `puccini/messa_gloria/3`
- `puccini/messa_gloria/4`
- `shostakovich/sym1/1`
- `shostakovich/sym1/3`
- `shostakovich/sym4/0`
- `shostakovich/sym6/4`
- `shostakovich/sym7/2`
- `shostakovich/sym8/2`
- `shostakovich/sym9/0`
- `shostakovich/sym9/2`
- `shostakovich/sym9/4`
- `shostakovich/sym10/1`
- `shostakovich/sym10/2`
- `shostakovich/sym11/1`
- `shostakovich/sym13/1`
- `shostakovich/sym13/2`
- `shostakovich/sym13/3`
- `shostakovich/sym14/0`
- `shostakovich/sym14/2`
- `shostakovich/sym14/4`
- `shostakovich/sym15/1`
- `shostakovich/sym15/3`
- `shostakovich/sym15/4`
- `brahms/sym1/0`
- `brahms/sym4/1`
- `brahms/pc1/3`
- `brahms/pc2/3`
- `brahms/violin_concerto/0`
- `brahms/violin_concerto/3`
- `brahms/german_requiem/2`
- `brahms/clarinet_quintet/1`
- `brahms/clarinet_quintet/2`
- `brahms/clarinet_quintet/3`
- `brahms/piano_quintet/0`
- `brahms/piano_quintet/1`
- `brahms/piano_quintet/2`
- `brahms/piano_quintet/3`
- `brahms/liebeslieder/0`
- `brahms/liebeslieder/2`
- `brahms/liebeslieder/3`
- `brahms/academic_festival/2`
- `brahms/tragic_overture/0`
- `brahms/tragic_overture/2`
- `haydn/sym104/0`
- `haydn/sym104/2`
- `haydn/sym94/3`
- `haydn/creation/3`
- `haydn/op76/2`
- `haydn/op76/3`
- `haydn/trumpet_concerto/0`
- `haydn/trumpet_concerto/2`
- `haydn/cello_concerto1/1`
- `haydn/cello_concerto1/3`
- `haydn/seasons/0`
- `haydn/seasons/2`
- `haydn/nelson_mass/3`
- `haydn/piano_sonatas/0`
- `haydn/piano_sonatas/1`
- `haydn/piano_sonatas/2`
- `haydn/piano_sonatas/3`
- `haydn/sym44/0`
- `haydn/sym44/1`
- `haydn/sym44/2`
- `haydn/sym44/3`
- `haydn/sym45/0`
- `haydn/sym45/1`
- `haydn/sym45/2`
- `haydn/seven_last_words/0`
- `haydn/seven_last_words/1`
- `haydn/seven_last_words/2`
- `haydn/seven_last_words/3`
- `schubert/sym8/0`
- `schubert/sym8/1`
- `schubert/sym8/2`
- `schubert/sym8/3`
- `schubert/sym9/1`
- `schubert/sym9/2`
- `schubert/sym9/3`
- `schubert/winterreise/0`
- `schubert/winterreise/1`
- `schubert/winterreise/2`
- `schubert/winterreise/3`
- `schubert/schone_mullerin/0`
- `schubert/schone_mullerin/1`
- `schubert/schone_mullerin/2`
- `schubert/schone_mullerin/3`
- `schubert/string_quintet/0`
- `schubert/string_quintet/1`
- `schubert/string_quintet/2`
- `schubert/string_quintet/3`
- `schubert/death_maiden/0`
- `schubert/death_maiden/1`
- `schubert/death_maiden/2`
- `schubert/death_maiden/3`
- `schubert/sonata_d960/0`
- `schubert/sonata_d960/1`
- `schubert/sonata_d960/2`
- `schubert/sonata_d960/3`
- `schubert/sonata_d960/4`
- `schubert/trout/1`
- `schubert/trout/2`
- `schubert/trout/3`
- `schubert/mass_e_flat/0`
- `schubert/mass_e_flat/1`
- `schubert/mass_e_flat/2`
- `schubert/mass_e_flat/3`
- `schubert/impromptus/0`
- `schubert/impromptus/1`
- `schubert/impromptus/2`
- `schubert/impromptus/3`
- `schubert/schwanengesang/0`
- `schubert/schwanengesang/1`
- `schubert/schwanengesang/2`
- `schubert/schwanengesang/3`
- `schubert/rosamunde/0`
- `schubert/rosamunde/1`
- `schubert/rosamunde/2`
- `schubert/rosamunde/3`
- `handel/messiah/0`
- `handel/messiah/2`
- `handel/messiah/3`
- `handel/water_music/0`
- `handel/water_music/1`
- `handel/water_music/2`
- `handel/water_music/3`
- `handel/fireworks/0`
- `handel/fireworks/2`
- `handel/fireworks/3`
- `handel/giulio_cesare/0`
- `handel/giulio_cesare/1`
- `handel/giulio_cesare/2`
- `handel/giulio_cesare/3`
- `handel/alcina/1`
- `handel/alcina/2`
- `handel/alcina/3`
- `handel/op6/0`
- `handel/op6/1`
- `handel/op6/2`
- `handel/op6/3`
- `handel/organ_concertos/0`
- `handel/organ_concertos/1`
- `handel/organ_concertos/2`
- `handel/organ_concertos/3`
- `handel/israel_in_egypt/0`
- `handel/israel_in_egypt/1`
- `handel/israel_in_egypt/2`
- `handel/israel_in_egypt/3`
- `handel/solomon/0`
- `handel/solomon/1`
- `handel/solomon/2`
- `handel/solomon/3`
- `handel/agrippina/0`
- `handel/agrippina/1`
- `handel/agrippina/2`
- `handel/rodelinda/0`
- `handel/rodelinda/1`
- `handel/rodelinda/2`
- `handel/rodelinda/3`
- `handel/dixit_dominus/0`
- `handel/dixit_dominus/1`
- `handel/dixit_dominus/2`
- `handel/dixit_dominus/3`
- `chopin/ballades/0`
- `chopin/ballades/1`
- `chopin/ballades/2`
- `chopin/ballades/3`
- `chopin/etudes/1`
- `chopin/etudes/2`
- `chopin/etudes/3`
- `chopin/preludes/0`
- `chopin/preludes/1`
- `chopin/preludes/2`
- `chopin/preludes/3`
- `chopin/sonata2/1`
- `chopin/sonata2/2`
- `chopin/sonata2/3`
- `chopin/sonata3/0`
- `chopin/sonata3/1`
- `chopin/sonata3/2`
- `chopin/sonata3/3`
- `chopin/pc1/0`
- `chopin/pc1/2`
- `chopin/pc1/3`
- `chopin/pc2/0`
- `chopin/pc2/1`
- `chopin/pc2/2`
- `chopin/pc2/3`
- `chopin/nocturnes/0`
- `chopin/nocturnes/1`
- `chopin/nocturnes/2`
- `chopin/nocturnes/3`
- `chopin/polonaises/0`
- `chopin/polonaises/1`
- `chopin/polonaises/2`
- `chopin/polonaises/3`
- `chopin/mazurkas/0`
- `chopin/mazurkas/1`
- `chopin/mazurkas/2`
- `chopin/mazurkas/3`
- `chopin/scherzi/0`
- `chopin/scherzi/1`
- `chopin/scherzi/2`
- `chopin/scherzi/3`
- `chopin/impromptus/0`
- `chopin/impromptus/1`
- `chopin/impromptus/2`
- `chopin/impromptus/3`

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
| `beethoven/violin_concerto/0` | Charles Munch; RCA, 1955 | Concerto No. 1 (1959) | 58 | **no** | confidence 58 < 80; date off by 4 years (1955 vs 1959); wrong work: MusicBrainz 'Concerto No. 1' does not match seed 'Violin Concerto' |
| `beethoven/missa_solemnis/0` | Otto Klemperer; EMI, 1965 | Missa solemnis (1966-07) | 100 | yes |  |
| `beethoven/fidelio/0` | Otto Klemperer; EMI, 1962 | Fidelio (1989) | 94 | **no** | date off by 27 years (1962 vs 1989) |
| `mozart/pc20/0` | Igor Markevitch; Philips, 1960 | Piano Concertos Nos. 20 & 24 (2001) | 100 | **no** | date off by 41 years (1960 vs 2001) |
| `mozart/clarinet_concerto/0` | Thomas Beecham; EMI, 1959 | Clarinet Concerto / Bassoon Concerto (1987) | 100 | **no** | date off by 28 years (1959 vs 1987) |
| `mozart/requiem/0` | Karl Böhm; Deutsche Grammophon, 1971 | Requiem (1971) | 100 | yes |  |
| `mozart/figaro/0` | Erich Kleiber; Decca, 1955 | Le nozze di Figaro (1989) | 100 | **no** | date off by 34 years (1955 vs 1989) |
| `mozart/figaro/1` | Carlo Maria Giulini; EMI, 1959 | Le nozze di Figaro (1961) | 100 | yes |  |
| `mozart/don_giovanni/0` | Carlo Maria Giulini; EMI, 1959 | Don Carlo (1971) | 26 | **no** | confidence 26 < 80; date off by 12 years (1959 vs 1971); wrong work: MusicBrainz 'Don Carlo' does not match seed 'Don Giovanni' |
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
| `shostakovich/sym5/3` | André Previn; EMI, 1965 | The 5 Piano Concertos (1989) | 89 | **no** | date off by 24 years (1965 vs 1989); wrong work: MusicBrainz 'The 5 Piano Concertos' does not match seed 'Symphony No. 5' |
| `shostakovich/sym10/0` | Herbert von Karajan; Deutsche Grammophon, 1966 | Symphonie No. 10 (1990-05-02) | 100 | **no** | date off by 24 years (1966 vs 1990) |
| `shostakovich/sym13/0` | Kirill Kondrashin; Melodiya, 1967 | Symphony No. 13, Op. 113 "Babi Yar" (2017-11-22) | 100 | **no** | date off by 50 years (1967 vs 2017) |
| `bach/brandenburg/0` | Trevor Pinnock; Archiv, 1982 | Brandenburg Concertos nos. 4-6 (1983-10-17) | 100 | yes |  |
| `bach/brandenburg/2` | Claudio Abbado; Deutsche Grammophon, 2007 | Piano Concertos (2006-09-01) | 37 | **no** | confidence 37 < 80; wrong work: MusicBrainz 'Piano Concertos' does not match seed 'Brandenburg Concertos' |
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
| `shostakovich/sym5/2` | Bernard Haitink; Decca, 1981 | 5 Klavierkonzerte (1977) | 100 | **no** | date off by 4 years (1981 vs 1977); wrong work: MusicBrainz '5 Klavierkonzerte' does not match seed 'Symphony No. 5' |
| `shostakovich/sym5/4` | Mstislav Rostropovich; Teldec, 1993 | Cello Concerto no. 2 / Symphony no. 5 (1993) | 100 | yes |  |
| `shostakovich/sym5/5` | Vasily Petrenko; Naxos, 2009 | Symphonies nos. 5 & 9 (2009-10) | 100 | yes |  |
| `shostakovich/sym5/6` | Andris Nelsons; Deutsche Grammophon, 2016 | Under Stalin’s Shadow: Symphonies nos. 5 / 8 / 9 (2016-05-27) | 37 | **no** | confidence 37 < 80 |
| `shostakovich/sym7/0` | Leonard Bernstein; Deutsche Grammophon, 1988 | Symphony no. 1 / Symphony no. 7 “Leningrad” (1989-09) | 86 | yes |  |
| `shostakovich/sym8/0` | Yevgeny Mravinsky; Praga, 1982 | Shostakovich: Symphony no. 8, op. 65 / Scriabin: Le Poème de l'extase, op. 54 (2015-05-05) | 100 | **no** | date off by 33 years (1982 vs 2015) |
| `shostakovich/sym8/1` | Andris Nelsons; Deutsche Grammophon, 2016 | Under Stalin’s Shadow: Symphonies nos. 5 / 8 / 9 (2016-05-27) | 100 | yes |  |
| `bach/brandenburg/3` | Benjamin Britten; Decca, 1968 | Piano Concertos (1988) | 29 | **no** | confidence 29 < 80; date off by 20 years (1968 vs 1988); wrong work: MusicBrainz 'Piano Concertos' does not match seed 'Brandenburg Concertos' |
| `bach/violin_concertos/3` | Wilhelm Furtwängler; EMI, 1951 | Violin Concertos (1984) | 100 | **no** | date off by 33 years (1951 vs 1984) |
| `bach/wtc/0` | Glenn Gould; Columbia, 1955 | Glenn Gould Plays Bach: The Well-Tempered Clavier Books I & II (1993) | 100 | **no** | date off by 38 years (1955 vs 1993) |
| `bach/wtc/1` | Glenn Gould; CBS, 1972 | Glenn Gould Plays Bach: The Well-Tempered Clavier Books I & II (1993) | 100 | **no** | date off by 21 years (1972 vs 1993) |
| `bach/mass_b_minor/2` | Karl Richter; Archiv, 1969 | Messe in h‐moll (1961) | 59 | **no** | confidence 59 < 80; date off by 8 years (1969 vs 1961) |
| `bach/matthew/2` | Wilhelm Furtwängler; EMI, 1954 | Matthäus‐Passion (1988) | 100 | **no** | date off by 34 years (1954 vs 1988) |
| `bach/matthew/3` | Karl Richter; Archiv, 1964 | Matthäus-Passion (1980) | 22 | **no** | confidence 22 < 80; date off by 16 years (1964 vs 1980) |
| `bach/john/0` | Otto Klemperer; EMI, 1961 | St. Matthew Passion (1962) | 100 | **no** | wrong work: MusicBrainz 'St. Matthew Passion' does not match seed 'St John Passion' |
| `bach/john/2` | Nikolaus Harnoncourt; Teldec, 1965 | Matthäus-Passion (1971) | 45 | **no** | confidence 45 < 80; date off by 6 years (1965 vs 1971); wrong work: MusicBrainz 'Matthäus-Passion' does not match seed 'St John Passion' |
| `bach/john/3` | Karl Richter; Archiv, 1964 | Matthäus-Passion (1980) | 64 | **no** | confidence 64 < 80; date off by 16 years (1964 vs 1980); wrong work: MusicBrainz 'Matthäus-Passion' does not match seed 'St John Passion' |
| `bach/art_of_fugue/0` | Glenn Gould; CBS, 1962 | The Art of the Fugue (1962) | 84 | yes |  |
| `bach/art_of_fugue/4` | Gustav Leonhardt; Deutsche Harmonia Mundi, 1969 | Suite BWV 996 / Toccata BWV 914 / Capriccio BWV 992 / Fantasia & Fugue BWV 904 / Prelude, Allegro, and Fugue BWV 998 (1985) | 28 | **no** | confidence 28 < 80; date off by 16 years (1969 vs 1985); wrong work: MusicBrainz 'Suite BWV 996 / Toccata BWV 914 / Capriccio BWV 992 / Fantasia & Fugue BWV 904 / Prelude, Allegro, and Fugue BWV 998' does not match seed 'The Art of Fugue' |
| `beethoven/sym3/2` | Herbert von Karajan; Deutsche Grammophon, 1962 | Symphonie Nr. 3 'Eroica' (1978-05-08) | 91 | **no** | date off by 16 years (1962 vs 1978) |
| `beethoven/sym5/2` | Arturo Toscanini; RCA, 1952 | Symphony 5½ (1948-03) | 100 | **no** | date off by 4 years (1952 vs 1948) |
| `beethoven/sym5/3` | Herbert von Karajan; Deutsche Grammophon, 1962 | Symphonie Nr. 5 (1977) | 48 | **no** | confidence 48 < 80; date off by 15 years (1962 vs 1977) |
| `beethoven/sym6/4` | Wilhelm Furtwängler; EMI, 1954 | Symphony no. 6 “Pastoral” / Symphony no. 8 (1989) | 100 | **no** | date off by 35 years (1954 vs 1989) |
| `beethoven/pc5/3` | Otto Klemperer; EMI, 1967 | Piano Concertos nos. 3, 4 & 5 "Emperor" (2023-04-21) | 100 | **no** | date off by 56 years (1967 vs 2023) |
| `beethoven/missa_solemnis/2` | Herbert von Karajan; Deutsche Grammophon, 1966 | Missa Solemnis (1966) | 97 | yes |  |
| `puccini/boheme/3` | Tullio Serafin; Decca, 1959 | Arias from Faust, La bohème, Dinorah, Carmen, Semiramide, Turandot, Lakmé (1961) | 58 | **no** | confidence 58 < 80 |
| `puccini/tosca/3` | Victor de Sabata; Decca, 1959 | Tosca (1985-11-10) | 100 | **no** | date off by 26 years (1959 vs 1985) |
| `puccini/butterfly/2` | Tullio Serafin; EMI, 1955 | Madama Butterfly (1987) | 100 | **no** | date off by 32 years (1955 vs 1987) |
| `puccini/turandot/2` | Tullio Serafin; EMI, 1957 | Arias from Faust, La bohème, Dinorah, Carmen, Semiramide, Turandot, Lakmé (1961) | 69 | **no** | confidence 69 < 80; date off by 4 years (1957 vs 1961) |
| `brahms/sym1/1` | Otto Klemperer; EMI, 1957 | Symphony no. 3 "Eroica" / Overtures "Leonore" nos. 1 & 2 (2002-03-11) | 73 | **no** | confidence 73 < 80; date off by 45 years (1957 vs 2002) |
| `brahms/pc1/0` | Eugen Jochum; Deutsche Grammophon, 1972 | Piano Concertos nos. 1, 2 / Seven Fantasias, op. 116 (1984) | 100 | **no** | date off by 12 years (1972 vs 1984) |
| `brahms/pc1/1` | George Szell; Decca, 1962 | Piano Concertos No. 1, No. 2 (1972) | 100 | **no** | date off by 10 years (1962 vs 1972) |
| `brahms/pc2/0` | Eugen Jochum; Deutsche Grammophon, 1972 | Pianos Concertos no. 2 & 4 (1976) | 72 | **no** | confidence 72 < 80; date off by 4 years (1972 vs 1976) |
| `brahms/pc2/1` | Erich Leinsdorf; RCA, 1960 | Prokofiev - Piano Concertos No. 1 & 2 (None) | 100 | yes |  |
| `brahms/violin_concerto/1` | Fritz Reiner; RCA, 1955 | Violin Concerto (1958) | 100 | yes |  |
| `brahms/german_requiem/0` | Otto Klemperer; EMI, 1961 | Ein deutsches Requiem (1962-02) | 98 | yes |  |
| `brahms/clarinet_quintet/0` | Reginald Kell; Busch Quartet; EMI, 1937 | Horn Trio & Clarinet Quintet (1990) | 100 | **no** | date off by 53 years (1937 vs 1990) |
| `brahms/haydn_variations/0` | Arturo Toscanini; RCA, 1952 | Concerto for Violin and Cello In A Minor / Variations On a Theme By Haydn / Gesang Der Parzen (1972) | 79 | **no** | confidence 79 < 80; date off by 20 years (1952 vs 1972) |
| `haydn/creation/0` | Herbert von Karajan; Deutsche Grammophon, 1969 | Die Schöpfung (1991) | 100 | **no** | date off by 22 years (1969 vs 1991) |
| `haydn/cello_concerto1/0` | Daniel Barenboim; EMI, 1967 | Sonaten Für Violoncello Und Klavier Nr. 1 Und Nr. 2 (1968) | 67 | **no** | confidence 67 < 80 |
| `haydn/nelson_mass/0` | David Willcocks; EMI, 1962 | Haydn: Nelson Mass / Vivaldi: Gloria (1988) | 88 | **no** | date off by 26 years (1962 vs 1988) |
| `schubert/sym9/0` | Josef Krips; Decca, 1958 | Great C Major Symphony (1958-11) | 100 | yes |  |
| `schubert/trout/0` | Clifford Curzon; members of the Vienna Octet; Decca, 1957 | Trout Quintet / Death and the Maiden (1988-04-13) | 100 | **no** | date off by 31 years (1957 vs 1988) |
| `handel/messiah/1` | Charles Mackerras; EMI, 1967 | Messiah (Highlights) (1987) | 97 | **no** | date off by 20 years (1967 vs 1987); compilation-like title: 'Messiah (Highlights)' |
| `handel/fireworks/1` | Charles Mackerras; Pye, 1959 | Music for the Royal Fireworks (in the original version for wind band) / Concertos in F & D / Concerto in F “a due cori” (1977-11) | 56 | **no** | confidence 56 < 80; date off by 18 years (1959 vs 1977) |
| `handel/alcina/0` | Richard Bonynge; Decca, 1962 | Alcina / Giulio Cesare: Highlights (1992-11-10) | 100 | **no** | date off by 30 years (1962 vs 1992); compilation-like title: 'Alcina / Giulio Cesare: Highlights' |
| `chopin/etudes/0` | Maurizio Pollini; Deutsche Grammophon, 1972 | Études op. 10 & op. 25 (1973) | 95 | yes |  |
| `chopin/sonata2/0` | Arthur Rubinstein; RCA, 1961 | The Rubinstein Collection, Volume 5: Piano Concertos nos. 1 & 2 / 19 Nocturnes (2001-08-07) | 75 | **no** | confidence 75 < 80; date off by 40 years (1961 vs 2001); compilation-like title: 'The Rubinstein Collection, Volume 5: Piano Concertos nos. 1 & 2 / 19 Nocturnes' |
| `chopin/pc1/1` | Stanisław Skrowaczewski; RCA, 1961 | Piano Concertos No. 1 & 2 (2001) | 80 | **no** | date off by 40 years (1961 vs 2001) |
| `bach/brandenburg/4` | Karl Richter; Archiv, 1960s | Brandenburg Concertos nos. 1 - 6 / Concertos, BWV 1055 & 1060 (1989-09-08) | 100 | **no** | date off by 29 years (1960 vs 1989) |
| `bach/suites/0` | Trevor Pinnock; Archiv, 1980s | 6 Brandenburg Concertos / 4 Orchestral Suites (1988-07-01) | 100 | **no** | date off by 8 years (1980 vs 1988) |
| `bach/suites/1` | Nikolaus Harnoncourt; Teldec, 1960s | Orchestral Suites 3 & 4 (1985) | 87 | **no** | date off by 25 years (1960 vs 1985) |
| `bach/suites/2` | John Eliot Gardiner; Archiv, 1994 | Overtures / Suites BWV 1066 - 1069 (1985) | 100 | **no** | date off by 9 years (1994 vs 1985) |
| `bach/suites/3` | Karl Richter; Archiv, 1960s | Suites for Orchestra no. 2, no. 3 / Brandenburg Concerto no. 5 (2006-11-08) | 37 | **no** | confidence 37 < 80; date off by 46 years (1960 vs 2006) |
| `bach/suites/4` | Christopher Hogwood; L'Oiseau-Lyre, 1980s | The Orchestral Suites (1988) | 100 | **no** | date off by 8 years (1980 vs 1988) |
| `bach/violin_concertos/0` | Daniel Barenboim; EMI, 1978 | Violin Concertos (1972) | 96 | **no** | date off by 6 years (1978 vs 1972) |
| `bach/violin_concertos/1` | Nathan Milstein; EMI, 1970s | Violin Concertos (complete) (1964-05) | 87 | **no** | date off by 6 years (1970 vs 1964) |
| `bach/violin_concertos/2` | Gidon Kremer; Deutsche Grammophon, 1988 | Violin Concertos nos. 1 & 2 / Double Concerto (1985) | 59 | **no** | confidence 59 < 80 |
| `bach/cello_suites/3` | Yo-Yo Ma; Sony, 1983 | The Unaccompanied Cello Suites no. 1 & no. 2 (1984) | 93 | yes |  |
| `bach/sonatas_partitas/2` | Henryk Szeryng; Philips, 1960s | Sonatas and Partitas for Solo Violin (1955) | 100 | **no** | date off by 5 years (1960 vs 1955) |
| `bach/sonatas_partitas/3` | Arthur Grumiaux; Philips, 1970s | 12 Sonatas for Violin and Harpsichord (1975) | 35 | **no** | confidence 35 < 80; date off by 5 years (1970 vs 1975) |
| `bach/goldberg/3` | Murray Perahia; Deutsche Grammophon, 2000 | Goldberg Variations (2000-09-01) | 100 | yes |  |
| `bach/goldberg/4` | András Schiff; Decca, 1982 | Goldberg Variations (1986-07-21) | 100 | **no** | date off by 4 years (1982 vs 1986) |
| `bach/wtc/3` | András Schiff; Decca, 1980s | The Well-Tempered Clavier, Book II (1986-12-04) | 100 | **no** | date off by 6 years (1980 vs 1986) |
| `bach/mass_b_minor/3` | Philippe Herreweghe; Harmonia Mundi, 1990s | Messe in H-Moll (1989) | 66 | **no** | confidence 66 < 80 |
| `bach/john/1` | John Eliot Gardiner; Archiv, 1986 | St. John Passion (1986-11-11) | 100 | yes |  |
| `bach/art_of_fugue/1` | Tatiana Nikolayeva; Hyperion, 1980s | 24 Preludes and Fugues, op. 87 (1991-03-01) | 34 | **no** | confidence 34 < 80; date off by 11 years (1980 vs 1991); wrong work: MusicBrainz '24 Preludes and Fugues, op. 87' does not match seed 'The Art of Fugue' |
| `bach/art_of_fugue/3` | Emerson String Quartet; Deutsche Grammophon, 2003 | The Art of Fugue (2003-08-01) | 100 | yes |  |
| `bach/harpsichord_concertos/1` | Nikolaus Harnoncourt; Teldec, 1960s | Violin Concertos 2 & 3 (1984) | 85 | **no** | date off by 24 years (1960 vs 1984); wrong work: MusicBrainz 'Violin Concertos 2 & 3' does not match seed 'Harpsichord Concertos' |
| `bach/harpsichord_concertos/3` | Murray Perahia; Sony, 1980s | Horn Concertos (1984) | 88 | **no** | date off by 4 years (1980 vs 1984); wrong work: MusicBrainz 'Horn Concertos' does not match seed 'Harpsichord Concertos' |
| `bach/harpsichord_concertos/4` | Karl Richter; Deutsche Grammophon, 1990s | Brandenburg Concertos nos. 1 - 6 / Concertos, BWV 1055 & 1060 (1989-09-08) | 79 | **no** | confidence 79 < 80; wrong work: MusicBrainz 'Brandenburg Concertos nos. 1 - 6 / Concertos, BWV 1055 & 1060' does not match seed 'Harpsichord Concertos' |
| `beethoven/sym6/1` | Bruno Walter; Columbia, 1950s | Symphony no. 6 in F major op. 68 (“Pastorale”) (1958) | 90 | **no** | date off by 8 years (1950 vs 1958) |
| `beethoven/sym6/2` | Herbert von Karajan; Deutsche Grammophon, 1960s | Symphonie Nr. 6 "Pastorale" (1962) | 54 | **no** | confidence 54 < 80 |
| `beethoven/sym6/3` | John Eliot Gardiner; Archiv, 1990s | España / Suite Pastorale / Habanera / Marche Français / Fête Polonaise (1996-06-03) | 100 | **no** | date off by 6 years (1990 vs 1996) |
| `beethoven/sym7/1` | Arturo Toscanini; RCA, 1930s | Symphonies Nos. 2, 7 (1986) | 100 | **no** | date off by 56 years (1930 vs 1986) |
| `beethoven/sym7/2` | Herbert von Karajan; Deutsche Grammophon, 1960s | Symphony no. 7 (1962) | 100 | yes |  |
| `beethoven/sym7/3` | Bruno Walter; Columbia, 1950s | Symphonies 7 and 8 (1985) | 80 | **no** | date off by 35 years (1950 vs 1985) |
| `beethoven/sym9/3` | Leonard Bernstein; Deutsche Grammophon, 1985 | Ode to Freedom: Bernstein in Berlin: Beethoven Symphony no. 9 (1990-01-15) | 57 | **no** | confidence 57 < 80; date off by 5 years (1985 vs 1990) |
| `beethoven/sym9/4` | Claudio Abbado; Deutsche Grammophon, 2000 | Symphony no. 9 (2000-01-01) | 100 | yes |  |
| `beethoven/pc4/0` | Ferdinand Leitner; Deutsche Grammophon, 1960s | Concertos for Piano Nos. 3, 4 (1987-12-10) | 100 | **no** | date off by 27 years (1960 vs 1987) |
| `beethoven/pc4/2` | George Szell; EMI, 1960s | Piano Concertos nos. 2 & 4 (1992-06-02) | 100 | **no** | date off by 32 years (1960 vs 1992) |
| `beethoven/pc4/3` | Claudio Abbado; Deutsche Grammophon, 1980s | Piano Concertos Nos. 21 & 27 (1990) | 100 | **no** | date off by 10 years (1980 vs 1990) |
| `beethoven/pc4/4` | Colin Davis; Philips, 1970s | Piano Concerto no. 1 in B flat minor opus 23 / ‘Romeo and Juliet’ Fantasy Overture (1983) | 76 | **no** | confidence 76 < 80; date off by 13 years (1970 vs 1983) |
| `beethoven/pc5/2` | George Szell; EMI, 1960s | Piano Concerto no. 5 (1961-08-21) | 97 | yes |  |
| `beethoven/violin_concerto/2` | Franz Konwitschny; Deutsche Grammophon, 1960s | Violin Concerto in D major (1962) | 84 | yes |  |
| `beethoven/late_quartets/2` | Alban Berg Quartet; EMI, 1980s | The "Middle Period" String Quartets (1985) | 68 | **no** | confidence 68 < 80; date off by 5 years (1980 vs 1985) |
| `beethoven/hammerklavier/0` | Wilhelm Kempff; Deutsche Grammophon, 1950s | Piano Sonatas “Hammerklavier” “The Tempest” (1988) | 100 | **no** | date off by 38 years (1950 vs 1988) |
| `beethoven/hammerklavier/2` | Maurizio Pollini; Deutsche Grammophon, 1975 | Piano Sonatas No. 28 in A major, Op. 101 & No. 29 in B flat major, Op. 106 "Hammerklavier" (1990) | 75 | **no** | confidence 75 < 80; date off by 15 years (1975 vs 1990) |
| `beethoven/hammerklavier/4` | Igor Levit; Sony, 2019 | Piano Sonata 29 "Hammerklavier, op. 106 (2019-09-20) | 100 | yes |  |
| `beethoven/missa_solemnis/3` | John Eliot Gardiner; Archiv, 1990s | Missa Solemnis (1990-11-12) | 100 | yes |  |
| `beethoven/fidelio/1` | Claudio Abbado; Deutsche Grammophon, 2010 | Fidelio (2011-06-20) | 100 | yes |  |
| `beethoven/fidelio/2` | Leonard Bernstein; Deutsche Grammophon, 1979 | Fidelio (1978) | 100 | yes |  |
| `mozart/late_symphonies/2` | Charles Mackerras; Telarc, 1990s | Symphonies no. 40 & 41 (1986) | 94 | **no** | date off by 4 years (1990 vs 1986) |
| `mozart/late_symphonies/3` | Leonard Bernstein; Deutsche Grammophon, 1980s | Symphonien Nos. 40 & 41 "Jupiter" (1990) | 100 | **no** | date off by 10 years (1980 vs 1990) |
| `mozart/pc20/3` | Jeffrey Tate; Philips, 1980s | Piano Concertos Nos. 20 & 21 (1986-09) | 100 | **no** | date off by 6 years (1980 vs 1986) |
| `mozart/pc23/1` | Murray Perahia; Sony, 1980s | Piano Concertos no. 19, K. 459 and no. 23, K. 488 (1984) | 100 | **no** | date off by 4 years (1980 vs 1984) |
| `mozart/pc23/3` | Vladimir Ashkenazy; Decca, 1960s | Piano Concertos 23 & 27 (1982) | 100 | **no** | date off by 22 years (1960 vs 1982) |
| `mozart/pc27/2` | Friedrich Gulda; Orfeo, 1989 | Great Piano Concertos nos. 20, 21, 25 & 27 (1988) | 81 | yes |  |
| `mozart/clarinet_concerto/3` | Raymond Leppard; RCA, 1980s | Clarinet Concerto / Flute and Harp Concerto (1985) | 100 | **no** | date off by 5 years (1980 vs 1985) |
| `mozart/requiem/3` | Christopher Hogwood; L'Oiseau-Lyre, 1980s | Requiem (1984-09-17) | 100 | **no** | date off by 4 years (1980 vs 1984) |
| `mozart/figaro/2` | Karl Böhm; Deutsche Grammophon, 1960s | Le nozze di Figaro (1968) | 90 | **no** | date off by 8 years (1960 vs 1968) |
| `mozart/figaro/3` | John Eliot Gardiner; Archiv, 1990s | Le nozze di Figaro (1994-06) | 100 | **no** | date off by 4 years (1990 vs 1994) |
| `mozart/don_giovanni/2` | Dimitri Mitropoulos; Sony, 1950s | Don Giovanni (1994) | 100 | **no** | date off by 44 years (1950 vs 1994) |
| `mozart/cosi/1` | James Levine; Deutsche Grammophon, 1990s | Così fan tutte (1989-08-14) | 100 | yes |  |
| `mozart/cosi/3` | Riccardo Muti; EMI, 1980s | Così fan tutte (1992) | 100 | **no** | date off by 12 years (1980 vs 1992) |
| `mozart/zauberflote/3` | James Levine; Deutsche Grammophon, 1990s | Die Zauberflöte (None) | 100 | yes |  |
| `mozart/mass_c_minor/1` | Neville Marriner; Philips, 1970s | Mass in B minor (1986-03-21) | 41 | **no** | confidence 41 < 80; date off by 16 years (1970 vs 1986); wrong work: MusicBrainz 'Mass in B minor' does not match seed 'Great Mass in C minor' |
| `mozart/mass_c_minor/3` | Leonard Bernstein; Deutsche Grammophon, 1978 | Great Mass in C minor KV427 / Exsultate jubilate KV165 / Ave verum corpus KV618 (1991-10-28) | 75 | **no** | confidence 75 < 80; date off by 13 years (1978 vs 1991) |
| `mozart/string_quintets/0` | Quintetto Boccherini; Philips, 1970s | Boccherini Quintets, Album 4 (1957-09) | 100 | **no** | date off by 13 years (1970 vs 1957); wrong work: MusicBrainz 'Boccherini Quintets, Album 4' does not match seed 'String Quintets' |
| `puccini/manon_lescaut/2` | James Levine; Sony, 1990s | Manon Lescaut (1993) | 99 | yes |  |
| `puccini/manon_lescaut/3` | Riccardo Muti; EMI, 1980s | Manon Lescaut (2000-02-14) | 100 | **no** | date off by 20 years (1980 vs 2000) |
| `puccini/boheme/2` | Tullio Serafin; EMI, 1960s | Arias from Faust, La bohème, Dinorah, Carmen, Semiramide, Turandot, Lakmé (1961) | 58 | **no** | confidence 58 < 80 |
| `puccini/tosca/4` | Antonio Pappano; EMI, 2000 | Tosca (2001) | 100 | yes |  |
| `puccini/butterfly/3` | Antonio Pappano; EMI, 1990s | Madama Butterfly (2009-10-12) | 100 | **no** | date off by 19 years (1990 vs 2009) |
| `puccini/fanciulla/2` | Zubin Mehta; Deutsche Grammophon, 1980s | La fanciulla del West (1978) | 100 | yes |  |
| `puccini/fanciulla/3` | Lorin Maazel; Sony, 1990s | La fanciulla del West (1992-03-24) | 100 | yes |  |
| `puccini/trittico/0` | Lorin Maazel; Sony, 1990s | Il trittico: Il tabarro / Suor Angelica / Gianni Schicchi (1987-11-09) | 100 | yes |  |
| `puccini/messa_gloria/1` | Antonio Pappano; EMI, 2000s | Messa di Gloria / Preludio sinfonico / Crisantemi (2001) | 66 | **no** | confidence 66 < 80 |
| `shostakovich/sym1/0` | Yevgeny Mravinsky; Melodiya, 1950s | Symphonies Nos 1 & 6, 'Pastoral' (1992-02-01) | 100 | **no** | date off by 42 years (1950 vs 1992) |
| `shostakovich/sym1/2` | Bernard Haitink; Decca, 1980s | Symphonies nos. 1 & 9 (1985) | 100 | **no** | date off by 5 years (1980 vs 1985) |
| `shostakovich/sym1/4` | Vasily Petrenko; Naxos, 2009 | Symphonies 1, 2 and 5 (2006-06) | 98 | yes |  |
| `shostakovich/sym4/1` | Mstislav Rostropovich; LSO Live, 2000s | Symphonies Nos. 3 & 4 (2003) | 74 | **no** | confidence 74 < 80 |
| `shostakovich/sym4/2` | Bernard Haitink; Decca, 1980s | Symphony no. 4 (1967) | 100 | **no** | date off by 13 years (1980 vs 1967) |
| `shostakovich/sym4/3` | Andris Nelsons; Deutsche Grammophon, 2018 | Symphonies nos. 4 & 11 “The Year 1905” (2018-07-06) | 100 | yes |  |
| `shostakovich/sym4/4` | Vasily Petrenko; Naxos, 2011 | Symphony no. 3, op. 43 / Symphony no. 4, op. 54 (2015-10-23) | 100 | **no** | date off by 4 years (2011 vs 2015) |
| `shostakovich/sym6/0` | Yevgeny Mravinsky; Melodiya, 1960s | Symphony no. 6 (1961) | 100 | yes |  |
| `shostakovich/sym6/1` | Mstislav Rostropovich; Teldec, 1990s | Return to Russia (1991-08-23) | 100 | **no** | wrong work: MusicBrainz 'Return to Russia' does not match seed 'Symphony No. 6' |
| `shostakovich/sym6/2` | Bernard Haitink; Decca, 1980s | Symphony no. 14 / 6 Poems of Marina Tsvetaeva (1986) | 57 | **no** | confidence 57 < 80; date off by 6 years (1980 vs 1986) |
| `shostakovich/sym6/3` | Andris Nelsons; Deutsche Grammophon, 2018 | Under Stalin’s Shadow: Symphonies nos. 6 & 7 / Incidental Music to “King Lear” (2019-02-22) | 100 | yes |  |
| `shostakovich/sym7/1` | Yevgeny Mravinsky; Melodiya, 1960s | Sibelius: Symphony no. 3, op. 52 / The Swan of Tuonela, op. 22 no. 3 / Symphony no. 7, op. 105 / Debussy: Nocturnes: Nuages-Fêtes (2016) | 98 | **no** | date off by 56 years (1960 vs 2016) |
| `shostakovich/sym7/3` | Andris Nelsons; Deutsche Grammophon, 2018 | Symphony no. 7 in C major "Leningrad" (2012) | 100 | **no** | date off by 6 years (2018 vs 2012) |
| `shostakovich/sym8/3` | Bernard Haitink; Decca, 1980s | Bruckner: Symphony No. 8 / Wagner: Siegfried-Idyll (1990-10-25) | 100 | **no** | date off by 10 years (1980 vs 1990) |
| `shostakovich/sym9/1` | Mstislav Rostropovich; LSO Live, 2000s | Symphonies nos. 1 & 9 (1994) | 100 | **no** | date off by 6 years (2000 vs 1994) |
| `shostakovich/sym9/3` | Andris Nelsons; Deutsche Grammophon, 2018 | Bruckner: Symphonies nos. 6 & 9 / Wagner: Parsifal Prelude & Siegfried Idyll (2019-05-03) | 68 | **no** | confidence 68 < 80 |
| `shostakovich/sym10/3` | Yevgeny Mravinsky; Melodiya, 1960s | Symphonies nos. 6, 10 (2004) | 73 | **no** | confidence 73 < 80; date off by 44 years (1960 vs 2004) |
| `shostakovich/sym10/4` | Mstislav Rostropovich; LSO Live, 2000s | Concerto for Cello in E Flat, Op. 107 / Symphony No. 1 in F Major, Op. 10 (2006) | 100 | **no** | date off by 6 years (2000 vs 2006) |
| `shostakovich/sym11/0` | Yevgeny Mravinsky; Melodiya, 1960s | Symphony no. 11 in G minor, op. 103 "The Year 1905" (1994) | 100 | **no** | date off by 34 years (1960 vs 1994) |
| `shostakovich/sym11/2` | Bernard Haitink; Decca, 1980s | Symphony no. 11 in G minor, op. 103 “The Year 1905” (1993-07-05) | 100 | **no** | date off by 13 years (1980 vs 1993) |
| `shostakovich/sym11/3` | Andris Nelsons; Deutsche Grammophon, 2018 | Symphonies nos. 4 & 11 “The Year 1905” (2018-07-06) | 100 | yes |  |
| `shostakovich/sym11/4` | Vasily Petrenko; Naxos, 2010 | Symphony no. 11 "The Year 1905" (2009-03-31) | 100 | yes |  |
| `shostakovich/sym14/1` | Mstislav Rostropovich; LSO Live, 2000s | Catoire: Piano Trio in F minor, op. 14 / Goldenweiser: Piano Trio in E minor, op. 31 (1997) | 100 | **no** | wrong work: MusicBrainz 'Catoire: Piano Trio in F minor, op. 14 / Goldenweiser: Piano Trio in E minor, op. 31' does not match seed 'Symphony No. 14' |
| `shostakovich/sym14/3` | Andris Nelsons; Deutsche Grammophon, 2018 | Symphonies nos. 1, 14 & 15 / Chamber Symphony in C minor (2021-06-25) | 100 | yes |  |
| `shostakovich/sym15/0` | Kirill Kondrashin; Melodiya, 1970s | Symphonies 9 & 15 (None) | 100 | yes |  |
| `shostakovich/sym15/2` | Bernard Haitink; Decca, 1980s | Symphony no. 15, op. 141 / From Jewish Folk Poetry, op. 79 (1993-07-05) | 100 | **no** | date off by 13 years (1980 vs 1993) |
| `brahms/sym1/2` | Carlo Maria Giulini; Deutsche Grammophon, 1981 | Symphony no. 1 (1971) | 100 | **no** | date off by 10 years (1981 vs 1971) |
| `brahms/sym1/3` | Leonard Bernstein; Columbia, 1960s | Symphony No. 1 / Serenade No. 2 (1992) | 100 | **no** | date off by 32 years (1960 vs 1992) |
| `brahms/sym1/4` | John Eliot Gardiner; Archiv, 1990s | Symphonies Nos. 1 ("Spring") & 4 / Konzertstück for 4 horns (2003-09-01) | 72 | **no** | confidence 72 < 80; date off by 13 years (1990 vs 2003) |
| `brahms/sym4/0` | Carlos Kleiber; Deutsche Grammophon, 1980 | Symphonie No. 4 (1981) | 100 | yes |  |
| `brahms/sym4/2` | Leonard Bernstein; Columbia, 1960s | Symphonies nos. 4, 5 (1986) | 89 | **no** | date off by 26 years (1960 vs 1986) |
| `brahms/sym4/3` | John Eliot Gardiner; Archiv, 1990s | Symphonies nos. 3 & 4 (1995-07-03) | 34 | **no** | confidence 34 < 80; date off by 5 years (1990 vs 1995) |
| `brahms/pc1/2` | Leonard Bernstein; Columbia, 1960s | Klavierkonzerte = Piano Concertos Nos. 1 & 2 • Violinkonzert = Violin Concerto • Doppelkonzert = Double Concerto (1990) | 86 | **no** | date off by 30 years (1960 vs 1990) |
| `brahms/pc2/2` | Leonard Bernstein; Columbia, 1960s | Piano Concerto no. 2 / Rhapsody on a Theme of Paganini (1964) | 100 | **no** | date off by 4 years (1960 vs 1964) |
| `brahms/violin_concerto/2` | Herbert von Karajan; Deutsche Grammophon, 1980s | Violin Concerto (1980) | 98 | yes |  |
| `brahms/german_requiem/1` | John Eliot Gardiner; Philips, 1990 | Ein deutsches Requiem (1991-04-16) | 100 | yes |  |
| `brahms/german_requiem/3` | Wilhelm Furtwängler; EMI, 1950s | Ein deutsches Requiem / Symphony no. 1 (2002) | 100 | **no** | date off by 52 years (1950 vs 2002) |
| `brahms/haydn_variations/1` | Bernard Haitink; Philips, 1970s | Symphony no. 4 in E minor / Haydn Variations (1992-04) | 33 | **no** | confidence 33 < 80; date off by 22 years (1970 vs 1992) |
| `brahms/haydn_variations/2` | Otto Klemperer; EMI, 1950s | The Klemperer Legacy: Haydn: Symphony 98 & Tchkaikovsky: Symphony 5 (1999) | 62 | **no** | confidence 62 < 80; date off by 49 years (1950 vs 1999) |
| `brahms/haydn_variations/3` | Herbert von Karajan; Deutsche Grammophon, 1960s | Symphony No. 1, Op. 68 / Haydn Variations (1989-03-02) | 37 | **no** | confidence 37 < 80; date off by 29 years (1960 vs 1989) |
| `brahms/liebeslieder/1` | Wolfgang Sawallisch; EMI, 1980s | “Tales from the Vienna Woods” and Other Favourite Waltzes (None) | 100 | yes |  |
| `brahms/academic_festival/0` | George Szell; CBS, 1960s | Brahms - Symphony No.1 in C minor, Op.68, Academic Festival Overture, Op.80 (1985) | 84 | **no** | date off by 25 years (1960 vs 1985) |
| `brahms/academic_festival/1` | Bernard Haitink; Philips, 1970s | Symphony no. 1 / Academic Festival Overture / Tragic Overture (1991) | 100 | **no** | date off by 21 years (1970 vs 1991) |
| `brahms/academic_festival/3` | Herbert von Karajan; Deutsche Grammophon, 1960s | Symphony no. 1 / Tragic Overture (1987) | 86 | **no** | date off by 27 years (1960 vs 1987); wrong work: MusicBrainz 'Symphony no. 1 / Tragic Overture' does not match seed 'Academic Festival Overture' |
| `brahms/tragic_overture/1` | Otto Klemperer; EMI, 1950s | Symphonie no. 1 / Tragic Overture / Academic Festival Overture (1989) | 100 | **no** | date off by 39 years (1950 vs 1989) |
| `brahms/tragic_overture/3` | Leonard Bernstein; Columbia, 1960s | Symphony No. 4 / Tragic Overture (1983) | 100 | **no** | date off by 23 years (1960 vs 1983) |
| `haydn/sym104/1` | Nikolaus Harnoncourt; Teldec, 1990s | Symphony No. 103 “Drum Roll” / Symphony no. 104 “London” (1992) | 100 | yes |  |
| `haydn/sym104/3` | Adam Fischer; Nimbus, 1990s | Symphony no. 99 in E-flat / Symphony no. 104 in D "London" (1990) | 100 | yes |  |
| `haydn/sym94/0` | Thomas Beecham; EMI, 1950s | Symphonies No. 94 in G "Surprise" / No. 96 in D "Miracle" / No. 102 in B-flat (None) | 100 | yes |  |
| `haydn/sym94/1` | Christopher Hogwood; L'Oiseau-Lyre, 1980s | Symphony no. 94 “Surprise” / Symphony no. 96 “Miracle” (1985) | 100 | **no** | date off by 5 years (1980 vs 1985) |
| `haydn/sym94/2` | Antal Doráti; Decca, 1970s | Symphony no. 94 "Surprise" / Symphony no. 103 "Drum Roll" (1960) | 100 | **no** | date off by 10 years (1970 vs 1960) |
| `haydn/creation/1` | John Eliot Gardiner; Archiv, 1996 | Die Schöpfung (1997-01-03) | 100 | yes |  |
| `haydn/creation/2` | Colin Davis; Philips, 1970s | Die Schöpfung (The Creation) (2009) | 100 | **no** | date off by 39 years (1970 vs 2009) |
| `haydn/op76/0` | Quatuor Mosaïques; Astree, 1990s | String Quartets, op. 76 (2000-04-25) | 100 | **no** | date off by 10 years (1990 vs 2000) |
| `haydn/op76/1` | Amadeus Quartet; Deutsche Grammophon, 1960s | String Quartets Opp. 76 • 77 • 103 (2002) | 100 | **no** | date off by 42 years (1960 vs 2002) |
| `haydn/trumpet_concerto/1` | Raymond Leppard; CBS, 1982 | Trumpet Concertos (1983) | 100 | yes |  |
| `haydn/trumpet_concerto/3` | Colin Davis; Philips, 1990s | “Emperor” Concerto (1990) | 94 | **no** | wrong work: MusicBrainz '“Emperor” Concerto' does not match seed 'Trumpet Concerto' |
| `haydn/cello_concerto1/2` | Colin Davis; EMI, 1970s | Piano Concerto No.1; Sonata No.5, Op.10 No.1 (1970) | 97 | **no** | wrong work: MusicBrainz 'Piano Concerto No.1; Sonata No.5, Op.10 No.1' does not match seed 'Cello Concerto No. 1' |
| `haydn/seasons/1` | John Eliot Gardiner; Archiv, 1992 | Die Jahreszeiten (1992-03-02) | 100 | yes |  |
| `haydn/seasons/3` | Nikolaus Harnoncourt; Teldec, 1990s | The Four Seasons (1996) | 100 | **no** | date off by 6 years (1990 vs 1996) |
| `haydn/nelson_mass/1` | Trevor Pinnock; Archiv, 1980s | Missa in Augustiis "Lord Nelson" / Te Deum in C major (1987-11-02) | 100 | **no** | date off by 7 years (1980 vs 1987) |
| `haydn/nelson_mass/2` | Colin Davis; Philips, 1970s | Missa solemnis, Mass in C (1993) | 100 | **no** | date off by 23 years (1970 vs 1993) |

## Review checklist

- [ ] Identity matches are the right recording, not a compilation / sampler
- [ ] No identity with confidence < 80 is treated as auto-accept
- [ ] Rows flagged `wrong work:` are rejected — never apply (Piano Concertos must not land on Brandenburg, etc.)
- [ ] Ensemble names (e.g. The English Concert) are personnel, not work titles
- [ ] Uncertain rows reviewed against MusicBrainz (`mb_url`) before merge
- [ ] Cover payloads are CAA / MusicBrainz hotlinks only (no binaries, no Discogs)
- [ ] Barcodes belong to the edition claimed (editions stage)
- [ ] No review text has been copied into any payload
- [ ] Every score carries a locator, or it stays `draft`


## Role B notes

- Base: densified seed on `cursor/catalogue-loop-500-5458` (10 composers · 119 works · **511** candidates).
- Contact used: `harvest@example.invalid` (Makefile default / task placeholder). Prefer a real publishable `HARVEST_CONTACT` for future MusicBrainz runs.
- Prior 69 identity proposals were resumed via local `.cache/harvest_state.json` so this budget targeted new candidates.
- MusicBrainz returned many **HTTP 503** responses (~86); those cursors were **not** advanced and remain for the next round.
- Work-identity guard kept Piano Concertos off Brandenburg; false-positive wrong-work cases (Art of Fugue, Creation/Schöpfung, etc.) fixed in `agents/harvest.py` and flags recomputed.
- Covers/editions gated until humans merge mbids into the seed.
- **Do not apply** in this PR — human identity review gate only.

## Remaining for next round

- **270** candidates still lack an identity proposal after this round (241/511 covered).
- Re-run `make plan && make harvest CONTACT=…` with budget 300; state file resumes automatically when present.

## Stop

Human identity review gate. Do not begin editions/covers apply until mbids are ratified.
