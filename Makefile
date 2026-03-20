PYTHON ?= python3

.PHONY: install-dev format lint typecheck test check

install-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

format:
	$(PYTHON) -m ruff format .

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy app

test:
	$(PYTHON) -m pytest

check:
	$(PYTHON) -m ruff format --check .
	$(PYTHON) -m ruff check .
	$(PYTHON) -m mypy app
	$(PYTHON) -m pytest
