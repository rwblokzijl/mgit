.PHONY: all test run

all:
	echo "Run on commandline"

test:
	pipenv run python -m unittest

run:
	echo Nothing

