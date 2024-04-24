.PHONY: build tests update

build:
	poetry build

test:
	poetry run python test.py

tests:
	pytest

# package fait tout planter dans pip/poetry
#update:
#	poetry update
