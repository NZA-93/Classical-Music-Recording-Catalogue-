# Critical Discography — build targets
# Python 3.11+, standard library only.

.PHONY: all seed score render plan harvest validate clean

all: seed score render

seed:
	python3 engine/seed_catalogue.py

score:
	python3 engine/aggregation_engine_v2.py

render:
	python3 site/render.py site/template.html build/catalogue.json docs/entries.html
	python3 site/build_site.py

plan:
	python3 agents/harvest.py data/seed.json --contact $${CONTACT:-maintainer@example.org} --dry-run --budget 300

harvest:
	@if [ -z "$$CONTACT" ]; then echo "Set CONTACT=you@example.org"; exit 1; fi
	python3 agents/harvest.py data/seed.json --contact $$CONTACT --budget 300

validate:
	python3 agents/validate.py

clean:
	rm -f build/catalogue.json data/seed.json docs/index.html docs/entries.html
