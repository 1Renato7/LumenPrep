import json
from pathlib import Path

import pytest

from app.config import settings
from app.ingestion import storage

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = json.loads((ROOT / "contracts" / "fixtures" / "canonical-attempt.json").read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _isolated_db():
    settings.duckdb_path = ":memory:"
    storage.reset_connection()
    yield
    storage.reset_connection()


@pytest.fixture
def valid_attempt() -> dict:
    return dict(FIXTURE)
