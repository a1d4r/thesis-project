#* Variables
SHELL := /usr/bin/env bash
PYTHON := python

#* Docker variables
IMAGE := geocoding
VERSION := latest

#* Directories with source code
CODE = geocoding tests
TESTS = tests

#* Poetry
.PHONY: poetry-download
poetry-download:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) -

.PHONY: poetry-remove
poetry-remove:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(PYTHON) - --uninstall

#* Installation
.PHONY: install
install:
	poetry lock -n
	poetry install -n

.PHONY: pre-commit-install
pre-commit-install:
	poetry run pre-commit install

#* Formatters
.PHONY: codestyle
codestyle:
	poetry run pyupgrade --exit-zero-even-if-changed --py39-plus **/*.py
	poetry run autoflake --recursive --in-place --remove-all-unused-imports --ignore-init-module-imports $(CODE)
	poetry run isort --settings-path pyproject.toml $(CODE)
	poetry run black --config pyproject.toml $(CODE)

.PHONY: format
format: codestyle

#* Test
.PHONY: test
test:
	poetry run pytest -c pyproject.toml --cov-report=html --cov=geocoding $(TESTS)

# Validate pyproject.toml
.PHONY: check-poetry
check-poetry:
	poetry check

#* Check code style
.PHONY: check-isort
check-isort:
	poetry run isort --diff --check-only --settings-path pyproject.toml $(CODE)

.PHONY: check-black
check-black:
	poetry run black --diff --check --config pyproject.toml $(CODE)

.PHONY: check-darglint
check-darglint:
	poetry run darglint --verbosity 2 $(CODE)

.PHONY: check-codestyle
check-codestyle: check-isort check-black check-darglint

#* Static linters

.PHONY: check-pylint
check-pylint:
	poetry run pylint --rcfile=pyproject.toml $(CODE)

.PHONY: check-mypy
check-mypy:
	poetry run mypy --install-types --non-interactive --config-file pyproject.toml $(CODE)

.PHONY: static-lint
static-lint: check-pylint check-mypy

#* Check security issues

.PHONY: check-bandit
check-bandit:
	poetry run bandit -ll --recursive $(CODE)

.PHONY: check-safety
check-safety:
	poetry run safety check --full-report

.PHONY: check-security
check-security: check-safety check-bandit

.PHONY: lint
lint: check-poetry check-codestyle static-lint check-security

.PHONY: update-dev-deps
update-dev-deps:
	poetry add -D autoflake@latest bandit@latest darglint@latest "isort[colors]@latest" mypy@latest pre-commit@latest pydocstyle@latest pylint@latest pytest@latest pyupgrade@latest safety@latest coverage@latest coverage-badge@latest pytest-html@latest pytest-cov@latest
	poetry add -D --allow-prereleases black@latest

#* Cleaning
.PHONY: pycache-remove
pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: dsstore-remove
dsstore-remove:
	find . | grep -E ".DS_Store" | xargs rm -rf

.PHONY: mypycache-remove
mypycache-remove:
	find . | grep -E ".mypy_cache" | xargs rm -rf

.PHONY: ipynbcheckpoints-remove
ipynbcheckpoints-remove:
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

.PHONY: pytestcache-remove
pytestcache-remove:
	find . | grep -E ".pytest_cache" | xargs rm -rf

.PHONY: build-remove
build-remove:
	rm -rf build/

.PHONY: cleanup
cleanup: pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove
