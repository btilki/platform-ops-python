PYTHON ?= python3
VENV ?= .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help sync lint fmt typecheck test validate demo clean

help:
	@echo "Targets: sync lint typecheck test validate demo clean"

sync:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -U pip
	$(PIP) install -e ".[dev]"

lint:
	$(VENV)/bin/ruff check src tests
	$(VENV)/bin/ruff format --check src tests

fmt:
	$(VENV)/bin/ruff check --fix src tests
	$(VENV)/bin/ruff format src tests

typecheck:
	$(VENV)/bin/mypy

test:
	$(VENV)/bin/pytest

validate: lint typecheck test

demo:
	$(VENV)/bin/promotion-bot promote \
		--manifest examples/gitops/values-images.yaml \
		--service frontend \
		--digest sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \
		--from-env staging \
		--to-env prod
	$(VENV)/bin/slo-kit compile --spec examples/slo/boutique.yaml --stdout
	$(VENV)/bin/slo-kit report --sli 0.9992 --objective 0.999
	$(VENV)/bin/platform-tenant apply --config examples/tenant/payments.yaml

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build *.egg-info src/*.egg-info
