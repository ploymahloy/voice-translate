.PHONY: deps run test test-integration typecheck check

deps:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest -v -m "not integration"

test-integration:
	PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest -v -m integration

typecheck:
	.venv/bin/pyright

check: test typecheck
