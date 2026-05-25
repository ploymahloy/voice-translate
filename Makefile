.PHONY: deps run test test-integration

deps:
	pipx install pytest
	pipx inject pytest fastapi httpx python-multipart mutagen 'uvicorn[standard]'
	ln -sfn "$(HOME)/.local/pipx/venvs/pytest" .pipx-pytest

run:
	.pipx-pytest/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	PYTHONDONTWRITEBYTECODE=1 pytest -v -m "not integration"

test-integration:
	PYTHONDONTWRITEBYTECODE=1 pytest -v -m integration
