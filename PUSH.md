# Pushing this to GitHub

The repository is already initialised with one commit. Unzip it, then:

```bash
cd Classical-Music-Recording-Catalogue-
git remote add origin https://github.com/NZA-93/Classical-Music-Recording-Catalogue-.git
git push -u origin main
```

If the repository already has commits (a README created at setup, say), either:

```bash
git push -u origin main --force        # this bundle becomes the history
# or keep what is there:
git pull --rebase origin main && git push -u origin main
```

## Then, in the repository settings — two switches

**1 · Pages.** Settings → Pages → Build and deployment → Source: **GitHub Actions**.
Do *not* pick "Deploy from a branch"; the workflow publishes `docs/` as an artifact.
The site appears at `https://nza-93.github.io/Classical-Music-Recording-Catalogue-/`
about a minute after the first successful run.

**2 · Harvest contact.** Settings → Secrets and variables → Actions → Variables →
New variable, name `HARVEST_CONTACT`, value an email address you are willing to publish.
MusicBrainz requires a contact in the User-Agent, and will throttle or block clients
without one. Nothing else needs configuring: no API keys, no third-party actions, no
Python packages.

## First runs

```
Actions → Build and publish → Run workflow      # publishes the site
Actions → Agent harvest → Run workflow          # tick "dry_run" the first time
```

The dry run reports what a real round would cost — 58 requests for identity resolution —
without contacting anyone. When you are satisfied, run it live. It opens a pull request
titled `Harvest <date>` with a review checklist. Nothing from **harvest** enters the
catalogue until a human merges it.

Signed editorial is the Critic path (`docs/automation/CRITIC.md`): Critic (or Developer
shipping Critic content) lands `data/editorial/` on `main` so Pages updates. Do not
wait for a harvest-style merge babysit on that register.

## What to check on the first live harvest

The identity stage is where errors are cheapest to catch and most expensive to miss.
MusicBrainz search will happily return a budget compilation for a famous recording. The
pull request lists every match with its score and first release date — reject anything
that looks like a sampler, a "Best of", or a date more than a year or two off.

## Local build

```bash
make            # score and render into docs/
make plan       # cost a harvest round without making requests
```

Python 3.11+, standard library only.
