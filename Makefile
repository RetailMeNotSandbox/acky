PROJECT=acky
PYTHON := /usr/bin/env python
PYTHON_VERSION=$(shell $(PYTHON) -c 'import sys; print sys.version_info[0]')
ACKY_VERSION=$(shell $(PYTHON) -c 'import acky; print acky.__version__')

default:
	@echo "install: install the package and scripts"
	@echo "clean: remove build/test artifacts"
	@echo "lint: check syntax"
	@echo "test: run unit tests"
	@echo 
	@echo "Python Version: $(PYTHON_VERSION)"
	@echo "  Acky Version: $(ACKY_VERSION)"

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

wheel: dist/acky-$(ACKY_VERSION)-py$(PYTHON_VERSION)-none-any.whl

sdist: dist/acky-$(ACKY_VERSION).tar.gz

dist/acky-$(ACKY_VERSION)-py$(PYTHON_VERSION)-none-any.whl:
	$(PYTHON) setup.py bdist_wheel

dist/acky-$(ACKY_VERSION).tar.gz:
	$(PYTHON) setup.py sdist
