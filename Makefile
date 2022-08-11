#* Variables
SHELL := /bin/bash
PYTHON := python3

.PHONY: help
help:
	@echo "Commands:"
	@echo "poetry-download : downloads and installs the poetry package manager"
	@echo "poetry-remove   : removes the poetry package manager"
	@echo "install         : installs required dependencies"
	@echo "install-gpu    : installs required dependencies, plus Torch GPU support"
	@echo "install-dev     : installs the dev dependencies for the project"
	@echo "install-dev-gpu : installs the dev dependencies for the project, plus Torch GPU support"
	@echo "update-deps     : updates the dependencies and writes them to requirements.txt"
	@echo "check-style     : run checks on all files without fixing them."
	@echo "fix-style       : run checks on files and potentially modifies them."
	@echo "check-safety    : run safety checks on all tests."
	@echo "lint            : run linting on all files (check-style + check-safety)"
	@echo "clean           : cleans all unecessary files."

#* Poetry
.PHONY: poetry-download
poetry-download:
	curl -sSL https://install.python-poetry.org | $(PYTHON) -

.PHONY: poetry-remove
poetry-remove:
	curl -sSL https://install.python-poetry.org | $(PYTHON) - --uninstall

#* Installation

.PHONY: add-torch-gpu
add-torch-gpu:
	poetry run poe upgrade-pip
	poetry run poe torch-cuda10

.PHONY: install
install:
	poetry install --no-dev

.PHONY: install-dev
install-dev:
	poetry install
	poetry run pre-commit install
	poetry run pre-commit autoupdate

.PHONY: install-gpu
install-gpu: install add-torch-gpu

.PHONY: install-dev-gpu
install-dev-gpu: install-dev add-torch-gpu

.PHONY: update-deps
update-deps:
	poetry update
	poetry lock && poetry export --without-hashes > requirements.txt

#* Linting
.PHONY: check-style
check-style:
	poetry run isort --diff --check-only --settings-path pyproject.toml ./
	poetry run black --diff --check --config pyproject.toml ./
	poetry run flake8 --config setup.cfg ./

.PHONY: fix-style
fix-style:
	poetry run pyupgrade --exit-zero-even-if-changed --py38-plus **/*.py
	poetry run isort --settings-path pyproject.toml ./
	poetry run black --config pyproject.toml ./

.PHONY: check-safety
check-safety:
	poetry check
	poetry run safety check --full-report
	poetry run bandit -ll --recursive stylelm tests

.PHONY: lint
lint: check-style check-safety

#* Cleaning
.PHONY: pycache-remove
pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: build-remove
build-remove:
	rm -rf build/

.PHONY: clean
clean: pycache-remove build-remove
