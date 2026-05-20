.PHONY: deps test

deps:
	pipx install pytest
	pipx inject pytest fastapi httpx python-multipart 'uvicorn[standard]'
	ln -sfn "$(HOME)/.local/pipx/venvs/pytest" .pipx-pytest

test:
	PYTHONDONTWRITEBYTECODE=1 pytest -v
