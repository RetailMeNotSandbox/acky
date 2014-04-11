PROJECT=acky
PYTHON := /usr/bin/env python

default:
	@echo "install: install the package and scripts"
	@echo "clean: remove build/test artifacts"
	@echo "lint: check syntax"
	@echo "test: run unit tests"

install:
	python setup.py install

clean:
	find . -name \*.pyc -exec rm -f {} \;
	find . -depth -type d -name __pycache__ -exec rm -rf {} \;
	rm -rf build dist $(PROJECT).egg-info

lint:
	@echo Checking for Python syntax...
	flake8 --ignore=E123,E501 $(PROJECT) && echo OK

test:
	@echo Running tests...
	nosetests --with-coverage --cover-package=$(PROJECT)
