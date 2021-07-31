PYTHON=python3

.PHONY: all deps build clean lint test tox

all: tox build

deps:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

build:
	$(PYTHON) -m build

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -name "*.pyc" -type f -delete
	find . -name __pycache__ -delete

lint:
	$(PYTHON) -m tox -e lint

tox:
	$(PYTHON) -m tox -p

test:
	$(PYTHON) -m tox -e test
