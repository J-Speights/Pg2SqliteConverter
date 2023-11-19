import os
import pytest
from schema_formatter.schema_management import backup_postgresql_schema


def test_bad_env_vars(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_PORT", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_PASS", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)

    result = backup_postgresql_schema()
    assert result == 1


def test_subprocess():  # Not sure how to test this yet.
    pass
