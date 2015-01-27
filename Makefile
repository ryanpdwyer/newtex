# Helper commands for checking the installation and uploading to PyPI
# Package name
PACKAGE:=newtex

# Conda packages
# List of packages to install using conda, because they are difficult
# or time-consuming to install with pip
CONDA_PKGS:=PyYAML fabric

# Assumes default location for anaconda and anaconda environments
ANACONDA_DIR:=$$HOME/anaconda
ENV_DIR:=$(ANACONDA_DIR)/envs

# Python version for test environment
PY_VERSION:=2.7
# You should not have to change these; as long as ANACONDA_DIR and ENV_DIR
# are set correctly
CONDA:=$(ANACONDA_DIR)/bin/conda
VERSION:=$(shell python setup.py --version)
ENV_NAME:=$(PACKAGE)-$(VERSION)
ENV_PREFIX:=$(ENV_DIR)/$(ENV_NAME)/bin
ENV_PYTHON:=$(ENV_PREFIX)/python
ENV_PIP:=$(ENV_PREFIX)/pip
ENV_TWINE:=$(ENV_PREFIX)/twine
ENV_CONDA:=$(ENV_PREFIX)/conda

help:
	@echo "Commands:"
	@echo ""
	@echo "clean			Remove python object files"
	@echo "clean-build		Remove build folders"
	@echo "release  		Test newtex and upload to PyPI"
	@echo "clean-test		Test newtex in a new virtual environment"

clean:
	rm -rf *.pyc
	rm -rf *.pyo

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

release: check-version make-env install-env test-env upload delete-env

clean-test: make-env install-env test-env delete-env

# In the future, add docs build commands here; possibly their own env too

# Helper commands for release and clean-test
upload:
	rm -rf dist/
	$(ENV_PIP) install twine wheel
	$(ENV_PYTHON) setup.py sdist bdist_wheel
	$(ENV_TWINE) upload dist/*

make-env:
	$(CONDA) create --yes -n $(ENV_NAME) python=$(PY_VERSION) pip

delete-env:
	$(CONDA) remove --all --yes -n $(ENV_NAME)

install-env:
	$(CONDA) install --yes -n $(ENV_NAME) $(CONDA_PKGS)
	$(ENV_PYTHON) setup.py install

test-env:
	$(ENV_PYTHON) setup.py test

# Check version string for PEP440 compatibility
# The regular expression used to do the check is taken from pip
# See https://github.com/pypa/pip/search?utf8=✓&q=pep440
PEP440=$(shell [[ $(VERSION) =~ ^v?(\d+)((a|b|c|rc)(\d+))?$$ ]] && echo "yes" || echo "no")
ifeq (no,$(PEP440))
check-version:
	$(error "Not a valid PEP440 version ($(VERSION)). Run git tag and try again.")
else
check-version:
	@echo "Version okay."
endif

.PHONY: help upload release make-env delete-env install-env test-env check-version clean-test clean-build clean

