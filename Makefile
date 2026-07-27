# Critical Discography — build targets. Python 3.11+, no third-party packages.

.PHONY: all seed score site harvest test validate plan clean entry metrics queue

all: seed score site

seed:            ## regenerate data/seed.json from the editorial source
	python3 engine/seed_catalogue.py

score:           ## run the aggregation engine -> build/catalogue.json
	python3 engine/aggregation_engine_v2.py

metrics: score   ## citation ratio and coverage -> build/metrics.json
	python3 agents/metrics.py

site: metrics    ## render docs/ (the published site). No network.
	python3 site/render.py
	python3 site/build_site.py
	python3 site/build_gallery.py
	python3 site/build_divergence.py

harvest:         ## agent round. Network. Writes proposals/, never the catalogue.
	python3 agents/harvest.py data/seed.json --contact $(CONTACT) --budget 300

plan:            ## count what a harvest round would cost, without making requests
	python3 agents/harvest.py data/seed.json --dry-run --budget 300

entry: score     ## scaffold a signed-entry stub + facts-only brief (ADR-002)
	python3 agents/make_entry.py

clean:
	rm -rf docs/index.html docs/entries.html docs/gallery.html docs/divergence.html \
	       build/catalogue.json build/metrics.json proposals .cache

validate:        ## check contributions/ and data/ against the project's own rules
	python3 agents/validate.py

queue:           ## where a signed entry is worth the most
	python3 agents/editorial_queue.py

test:            ## run the test suite
	python3 -m unittest discover -s tests -q
