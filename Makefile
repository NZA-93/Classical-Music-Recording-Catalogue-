# Critical Discography — build targets. Python 3.11+, no third-party packages.

.PHONY: all seed score site harvest test validate plan clean queue queue-week expand-brief targets loop \
	review-queue review-board review-apply-dry review-apply

all: seed score site

seed:            ## regenerate data/seed.json from the editorial source
	python3 engine/seed_catalogue.py

score:           ## run the aggregation engine -> build/catalogue.json
	python3 engine/aggregation_engine_v2.py

site: score      ## render docs/ (the published site). No network.
	python3 site/render.py
	python3 site/build_site.py
	python3 site/build_gallery.py
	python3 site/build_review.py
	# Legacy GitHub Pages still serves repo root (/); keep mirrors in sync
	# until the Actions publish workflow (#1) is live and Pages uses docs/.
	cp docs/entries.html entries.html
	cp docs/index.html index.html
	cp docs/gallery.html gallery.html
	rm -rf composers && cp -R docs/composers composers

PROPOSALS ?= proposals/proposals-20260809.json
DECISIONS ?= proposals/review-decisions.json

review-queue:    ## build human review packs + decisions template from proposals
	python3 agents/review_queue.py --proposals $(PROPOSALS)
	python3 site/build_review.py

review-board:    ## rebuild online review board only
	python3 site/build_review.py

review-apply-dry: ## dry-run owner accepts from review-decisions.json
	python3 agents/apply.py --proposals $(PROPOSALS) --decisions $(DECISIONS) --only identity --dry-run

review-apply:    ## apply owner accepts (facts only — never statements/editorial)
	python3 agents/apply.py --proposals $(PROPOSALS) --decisions $(DECISIONS) --only identity
	python3 site/build_review.py

# CONTACT / HARVEST_CONTACT: publishable address for the MusicBrainz User-Agent.
# Placeholder for local/agent runs: harvest@example.invalid
CONTACT ?= $(or $(HARVEST_CONTACT),harvest@example.invalid)

harvest:         ## agent round. Network. Writes proposals/, never the catalogue.
	python3 agents/harvest.py data/seed.json --contact $(CONTACT) --budget 300

plan:            ## count what a harvest round would cost, without making requests
	python3 agents/harvest.py data/seed.json --contact $(CONTACT) --dry-run --budget 300

clean:
	rm -rf docs/index.html docs/entries.html docs/composers composers build/catalogue.json .cache

validate:        ## check contributions/ against the project's own rules
	python3 agents/validate.py
	python3 agents/community_comments.py validate

queue:           ## where a signed entry is worth the most
	python3 agents/editorial_queue.py

queue-week:      ## next five composers from proposals/composer-queue.json
	python3 agents/weekly_expand.py

expand-brief:    ## write proposals/WEEK_BRIEF.md for Cursor agent launch
	python3 agents/weekly_expand.py --write

targets:         ## 10 composers · 100 works · 500 recordings floor (exit 1 if short)
	python3 agents/catalogue_loop.py

loop: targets expand-brief ## status + next week brief; keep iterating until targets exit 0

test:            ## run the test suite
	python3 -m unittest discover -s tests -q
