.PHONY: deps test test-integration

deps:
	pipx install pytest
	pipx inject pytest fastapi httpx python-multipart mutagen 'uvicorn[standard]'
	ln -sfn "$(HOME)/.local/pipx/venvs/pytest" .pipx-pytest

test:
	PYTHONDONTWRITEBYTECODE=1 pytest -v -m "not integration"

test-integration:
	PYTHONDONTWRITEBYTECODE=1 pytest -v -m integration
