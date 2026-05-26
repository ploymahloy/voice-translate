.PHONY: deps run test test-integration typecheck check client-install client-dev client-build client-test client-check

deps:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt -r requirements-dev.txt

run:
	PYTHONPATH=.. .venv/bin/uvicorn server.main:app --reload --host 0.0.0.0 --port 8000

test:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.. .venv/bin/pytest -v -m "not integration"

test-integration:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.. .venv/bin/pytest -v -m integration

typecheck:
	PYTHONPATH=.. .venv/bin/pyright

client-install:
	cd client && npm ci

client-dev:
	cd client && npm run dev

client-build:
	cd client && npm run build

client-test:
	cd client && npm test

client-check:
	cd client && npm run check

check: test typecheck client-test client-check
