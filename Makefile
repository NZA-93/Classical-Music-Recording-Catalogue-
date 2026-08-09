# Critical Discography — build targets. Python 3.11+, no third-party packages.

.PHONY: all seed score site harvest test validate plan clean queue queue-week expand-brief

all: seed score site

seed:            ## regenerate data/seed.json from the editorial source
	python3 engine/seed_catalogue.py

score:           ## run the aggregation engine -> build/catalogue.json
	python3 engine/aggregation_engine_v2.py

site: score      ## render docs/ (the published site). No network.
	python3 site/render.py
	python3 site/build_site.py
	python3 site/build_gallery.py

harvest:         ## agent round. Network. Writes proposals/, never the catalogue.
	python3 agents/harvest.py data/seed.json --contact $(CONTACT) --budget 300

plan:            ## count what a harvest round would cost, without making requests
	python3 agents/harvest.py data/seed.json --dry-run --budget 300

clean:
	rm -rf docs/index.html docs/entries.html build/catalogue.json .cache

validate:        ## check contributions/ against the project's own rules
	python3 agents/validate.py

queue:           ## where a signed entry is worth the most
	python3 agents/editorial_queue.py

queue-week:      ## next five composers from proposals/composer-queue.json
	python3 agents/weekly_expand.py

expand-brief:    ## write proposals/WEEK_BRIEF.md for Cursor agent launch
	python3 agents/weekly_expand.py --write

test:            ## run the test suite
	python3 -m unittest discover -s tests -q
