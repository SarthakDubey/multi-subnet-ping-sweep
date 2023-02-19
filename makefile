.PHONY: test pytest

pytest:
	python3 -m pytest $(ARGS)

test:
	python3 -m pytest ./tests

lint:
	python3 -m pylint ./**/*.py