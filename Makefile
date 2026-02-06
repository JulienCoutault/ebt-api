.PHONY: build tests update

build:
	poetry build

tests:
	poetry run pytest

# package fait tout planter dans pip/poetry
#update:
#	poetry update
