.PHONY: all test run

all:
	echo "Run on commandline"

clean:
	find . -type d -name  "__pycache__" -exec rm -r {} +

test:
	pipenv run python -m unittest discover

run:
	echo Nothing

