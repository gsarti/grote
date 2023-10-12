#* Variables
SHELL := /bin/bash
PYTHON := python3

.PHONY: help
help:
	@echo "Commands:"
	@echo "poetry-download : downloads and installs the poetry package manager"
	@echo "poetry-remove   : removes the poetry package manager"
	@echo "install         : installs required dependencies"
	@echo "install-dev     : installs the dev dependencies for the project"
	@echo "update-deps     : updates the dependencies and writes them to requirements.txt"
	@echo "check-style     : run checks on all files without fixing them."
	@echo "fix-style       : run checks on files and potentially modifies them."
	@echo "check-safety    : run safety checks on all tests."
	@echo "lint            : run linting on all files (check-style + check-safety)"
	@echo "test            : run all tests."
	@echo "clean           : cleans all unecessary files."

#* Poetry
.PHONY: poetry-download
poetry-download:
	curl -sSL https://install.python-poetry.org | $(PYTHON) -

.PHONY: poetry-remove
poetry-remove:
	curl -sSL https://install.python-poetry.org | $(PYTHON) - --uninstall

#* Installation

.PHONY: install
install:
	poetry install

.PHONY: install-dev
install-dev:
	poetry install --all-extras --with lint --sync
	poetry run pre-commit install
	poetry run pre-commit autoupdate

.PHONY: update-deps
update-deps:
	poetry lock
	poetry export --without-hashes > requirements.txt
	poetry export --without-hashes -E notebook --with lint > requirements-dev.txt

#* Linting
.PHONY: check-style
check-style:
	poetry run black --diff --check --config pyproject.toml ./
	poetry run ruff  --no-fix --config pyproject.toml ./

.PHONY: fix-style
fix-style:
	poetry run black --config pyproject.toml ./
	poetry run ruff --config pyproject.toml ./


.PHONY: check-safety
check-safety:
	poetry check
	poetry run safety check --full-report -i 53048

.PHONY: lint
lint: fix-style check-safety

#* Linting
.PHONY: test
test:
	poetry run pytest -c pyproject.toml -v

#* Cleaning
.PHONY: pycache-remove
pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: build-remove
build-remove:
	rm -rf build/

.PHONY: clean
clean: pycache-remove build-remove