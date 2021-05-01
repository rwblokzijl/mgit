.PHONY: all test run

all: test mypy

clean:
	find . -type d -name  "__pycache__" -exec rm -r {} +

test:
	export ACCEPTANCE=yes; pipenv run python -m unittest discover

mypy:
	pipenv run mypy . --ignore-missing-imports

run:
	echo Nothing

