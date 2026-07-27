# Ingesting Diapason, lawfully
### Working note · 26 July 2026

**I am not a lawyer, and French intellectual property is a specialist field.** What
follows is a structured way to think about it and a set of steps ordered from
plainly safe to genuinely risky. Before any systematic extraction, take advice
from a French *avocat* in *propriété intellectuelle*. The cost of an hour of
that is trivial against the cost of being wrong.

---

## 1. Know what you are actually dealing with

The *Dictionnaire des disques et des compacts — guide critique de la musique
classique enregistrée* is not one object with one owner.

| | Rights holder | Notes |
|---|---|---|
| The book (Bouquins, editions 1981 · 1984 · 1988 · 1991) | **Éditions Robert Laffont**, now part of **Editis** | 4th edition 1991, 1367 pp., ISBN 978-2-221-06682-9. Editorial direction Jean-Michel Damian. Roughly ten thousand recordings. Project conceived 1971 by Guy Schoeller. |
| The magazine, its archive, and the *Diapason d'Or* | **Reworld Media** (previously Mondadori) | diapasonmag.fr |

So a request about the 1991 book goes to Editis. A request about award lists or
current reviews goes to Reworld. Sending one letter to "Diapason" gets you
nowhere on the book.

**Three distinct legal objects are tangled together here**, and conflating them
is where projects like this go wrong:

1. **The prose** — each critical notice. Protected by *droit d'auteur* for the
   author's life plus seventy years. Contributors to a 1981–91 work are in many
   cases still living. This is unambiguously in copyright and will remain so
   well beyond any plan you are making.
2. **The compilation** — selection and arrangement, protectable under CPI
   L112-3 if original.
3. **The database right** — the *sui generis* right (CPI L341-1, from Directive
   96/9/EC) protecting substantial investment in obtaining and verifying the
   contents. It runs **fifteen years** from completion. For the 1991 edition
   that term almost certainly lapsed around 2006.

That third point is the one people seize on, so be careful with it: **the lapse
of the database right does nothing whatsoever to the copyright in the notices.**
It means the *structure* is no longer separately protected. It does not license
copying a single paragraph.

---

## 2. What you actually want, and why that helps

The guide needs, per recording:

- which work and which recording
- the Diapason rating (or *Diapason d'Or*)
- a locator: edition and page
- **one sentence, in your own words**, on what the notice claims

It does **not** want the notice. That is not a legal concession — the schema was
built this way for editorial reasons, and `validate.py` already rejects any
characterisation over 240 characters or containing a long quoted run. The
architecture and the law happen to want the same thing, which is a comfortable
place to be.

A rating attached to a recording is a **fact**. Facts are not protected by
copyright in France or anywhere else. The prose expressing the judgement is.

---

## 3. The ladder, safest first

### Tier 0 — Award lists. Do this now.
*Diapason d'Or*, *Diapason d'Or de l'Année*, *Choc de Classica*, and the rest
are publicly announced events. That a recording won one is a fact with a public
locator. Zero risk, high yield, and the normaliser already handles the `award`
scale. This is where the Shostakovich round should have started.

### Tier 1 — Buy the books; a human transcribes ratings with locators.
Second-hand copies of all four editions cost less than a restaurant meal. A
contributor reads, and enters a structured record per recording: rating,
edition, page, own-words sentence. This is **citation**, and it is what every
scholar does.

Two cautions. France's *courte citation* exception (CPI L122-5, 3°a) is
markedly narrower than American fair use: the quotation must be short, serve a
critical or pedagogical purpose, sit inside a work of your own, and name author
and source. It does not authorise systematic harvesting. And even where each
individual act is lawful, an *exhaustive* transcription of all ten thousand
ratings starts to look like reconstructing the work, which invites a
*parasitisme* or unfair-competition argument independent of copyright. Transcribe
where the guide has works; do not set out to transcribe the book.

### Tier 2 — Ask. This is the highest-value action available.
Write to both holders. A non-commercial reference project that cites ratings,
links back, and republishes nothing is a reasonable request, and a granted
permission survives a change of counsel in a way that a clever reading never
does. Drafts are in `docs/legal/`.

The 1991 book has been out of print for decades and competes with nothing you
are building. Frame it as historical reception, because that is what it is.

### Tier 3 — TDM, and only with advice.
France implemented the DSM Directive at CPI L122-5-3. Two exceptions matter:

- **Article 3** (research): text and data mining by research organisations and
  heritage institutions, on lawfully accessed works, and it cannot be overridden
  by contract. A private project is not a research organisation — but a
  partnership with a university library or a conservatoire could be, and the
  historical-reception angle is genuinely research-shaped.
- **Article 4** (general): TDM on lawfully accessed works unless the rightsholder
  has reserved the right, which online must be done in a machine-readable way.

**The decisive limit on both:** they permit the *mining*. They do not permit
publishing the protected expression. Output that reproduces or closely tracks a
notice infringes whether a model produced it or a photocopier did.

### Never
- OCR the volume and have a model paraphrase the notices at scale. Non-literal
  copying is still copying; a close paraphrase of a critical notice is a
  derivative work. This is the tempting shortcut and it is the one that ends the
  project.
- Scrape diapasonmag.fr behind its paywall, or against its terms or robots.
- Bulk-load the ratings as a dataset and publish it as one.

Note that `AGENTS.md` and ADR-002 already forbid the first of these for entirely
separate reasons: a machine paraphrase of a critic reads like judgement while
having no listener behind it. The legal rule and the editorial rule point the
same way.

---

## 4. The trademark, which people forget

*Diapason* and *Diapason d'Or* are marks belonging to the magazine's publisher.

- Saying a recording "won a Diapason d'Or" is nominative use, and fine.
- Describing your project as being in the tradition of the Diapason guides, as
  the README does, is descriptive, and defensible.
- Using the name or the logo **in your branding**, or anything implying
  endorsement or continuity, is not. Do not let "Diapason" drift into the
  product name as the project grows. That is a much faster route to a letter
  than any copying question.

---

## 5. What this means for the pipeline

Nothing in the harvest changes. Diapason enters through the same door as every
other print source: a human with the book, filing a contribution with a locator
that another human can check.

```json
{
  "recording": "…",
  "axis": "interpretation",
  "source": "Dictionnaire des disques et des compacts (Diapason), 4e éd., Robert Laffont, 1991",
  "locator": "p. 842",
  "scale": "stars_5",
  "value": 4,
  "characterisation": "Preferred among modern-instrument versions for its orchestral weight.",
  "conflict": false
}
```

That record is lawful, checkable, and worth more than a scraped paragraph would
be — because a reader can go to page 842 and disagree with you.


---

## 6. "It is out of print and forgotten" — the argument, examined

This is the most natural thought anyone has about a 1991 guide, and it deserves
a real answer rather than a reflex.

### The premise is half wrong

The *book* is out of print. The **editorial legacy is an active commercial
asset**. Since January 2008 Diapason has run *Les Indispensables de Diapason*, a
CD series built on exactly the judgements the guide embodied — reissued as
forty-disc boxes (DIAPBOX01, vol. 2 and after), sold today through Fnac,
Clicmusique and Qobuz. The *Diapason d'Or* is awarded every month.

So the position is not "an abandoned work nobody exploits". It is "a publisher
who monetises this precise editorial heritage, and whose out-of-print volume is
one expression of it". A free catalogue built on the same judgements is
adjacent to a live product, not to a void.

### Neglect does not extinguish copyright

There is no doctrine of forfeiture through disuse in *droit d'auteur*. The
contrast with trade marks is instructive and worth holding onto: a mark **can**
be revoked for five years' genuine non-use. Copyright cannot. The rights in
those notices run for the authors' lives plus seventy years whether or not
anyone prints them, and whether or not anyone remembers.

### France already tried this argument, and lost

In 2012 France created **ReLIRE**, a register of twentieth-century
*livres indisponibles*, allowing a collecting society to license out-of-print
books digitally unless the author objected. The reasoning was exactly yours:
these books are unavailable, letting them be used serves the public.

In *Soulier and Doke* (CJEU, C-301/15, 16 November 2016) the Court struck it
down. Consent must be **explicit and prior**; an opt-out imposed on authors who
may never learn of the scheme does not satisfy the Directive. A national
legislature, acting for the public good, with a statute and a register and a
collecting society, could not make this work. An individual project will not.

### But there is now a lawful version of your instinct

The DSM Directive (Articles 8–11), transposed into French law, created a real
mechanism for **out-of-commerce works**: extended collective licensing, with a
fallback exception where no representative collecting society exists.

The conditions matter:

- the beneficiary is a **cultural heritage institution** — a library, archive,
  museum, or an educational establishment's library, **not a private project**;
- use must be **non-commercial**;
- the work must be published on the **EUIPO Out-of-Commerce Works Portal** for
  **six months** before use;
- **rightsholders may opt out at any time**, including afterwards.

This is the route your argument actually opens: not "nobody will mind", but a
partnership with a conservatoire library or a music-department library that
holds the volumes and can act as the institutional beneficiary. That is a real
conversation to have, and the historical-reception framing makes it a natural
one.

### Who is harmed, honestly

- **The critics.** These notices are signed work by named people, several still
  living. Their professional judgement carries their name. Taking it without
  asking takes their voice, and it is the one thing a critic owns.
- **Editis.** An out-of-print backlist is an option on a future digital edition.
  A free, complete, well-made version forecloses it.
- **Reworld.** Actively selling the same editorial heritage, this month.
- **Anyone downstream of you.** Your data is CC0. Copied prose is not yours to
  place under CC0, and everyone who reuses it inherits a problem they cannot see.
- **The project.** This is the largest one. A guide whose entire proposition is
  that every claim shows its receipt cannot be built on unlicensed copying.
  The asymmetry is brutal: one letter from a rights holder and the story stops
  being the catalogue and becomes the copying.

### What you actually want does not require the prose

Strip the question back. What is worth rescuing from that guide is **which
recordings its critics rated highest, and how that judgement shifted across the
1981, 1984, 1988 and 1991 editions**. That is a set of facts, a locator per
fact, and a sentence of your own — lawful today, no permission required, and
genuinely valuable because nobody has assembled it.

The prose adds flavour. It does not add function. The public good you are
reaching for is almost entirely available without touching the one thing that
would put the project at risk.
