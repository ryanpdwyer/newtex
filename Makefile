# Helper commands for checking the installation and uploading to PyPI

ANACONDA_DIR=$$HOME/anaconda
CONDA=$(ANACONDA_DIR)/bin/conda
ENV_DIR=$(ANACONDA_DIR)/envs
PACKAGE=newtex
VERSION=$(shell python setup.py --version)
ENV_NAME=$(PACKAGE)-$(VERSION)
PY_VERSION=2.7
ENV_PREFIX=$(ENV_DIR)/$(ENV_NAME)/bin
PYTHON=$(ENV_PREFIX)/python
PIP=$(ENV_PREFIX)/pip
TWINE=$(ENV_PREFIX)/twine
ENV_CONDA=$(ENV_PREFIX)/conda

help:
	@echo "Helper command for testing and uploading to PyPI"

release: check_version make_env test_install test upload delete_env

upload:
	rm -rf dist
	$(PIP) install twine wheel
	$(PYTHON) setup.py sdist bdist_wheel
	$(TWINE) upload dist/*

make_env:
	$(CONDA) create -n $(ENV_NAME) --yes python=$(PY_VERSION) pip

delete_env:
	$(CONDA) remove --all -n --yes $(ENV_NAME)

test_install:
	$(ENV_CONDA) install pyYAML
	$(PYTHON) setup.py install

test:
	$(PYTHON) setup.py test

ifneq (,$(findstring -,$(VERSION)))
check_version:
	$(error "Not a valid PEP480 version ($(VERSION)). Run git tag and try again.")
else
check_version:
	@echo "Version okay."
endif


.PHONY: help upload release make_env delete_env test_install test check_version

