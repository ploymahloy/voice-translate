import os
from pathlib import Path

from server.env import _DEFAULT_ENV_FILE, load_env_file, project_root


def test_default_env_file_is_repo_root_dotenv():
    repo_root = Path(__file__).resolve().parent.parent.parent
    assert project_root() == repo_root
    assert _DEFAULT_ENV_FILE == repo_root / ".env"

def test_load_env_file_sets_missing_variables(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment\n"
        "export FIRST=one\n"
        "SECOND='two'\n"
        "THIRD=\"three\"\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("FIRST", raising=False)
    monkeypatch.delenv("SECOND", raising=False)
    monkeypatch.delenv("THIRD", raising=False)

    load_env_file(env_file)

    assert os.environ["FIRST"] == "one"
    assert os.environ["SECOND"] == "two"
    assert os.environ["THIRD"] == "three"

def test_load_env_file_does_not_override_existing_variables(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("KEEP=from-file\n", encoding="utf-8")
    monkeypatch.setenv("KEEP", "from-shell")

    load_env_file(env_file)

    assert os.environ["KEEP"] == "from-shell"
