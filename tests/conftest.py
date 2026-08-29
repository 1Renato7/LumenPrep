import json
from pathlib import Path

import pytest

from app.config import settings
from app.ingestion import storage
from app.streaming import reset_transaction_pipeline

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = json.loads((ROOT / "contracts" / "fixtures" / "canonical-attempt.json").read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _isolated_db():
    settings.duckdb_path = ":memory:"
    storage.reset_connection()
    reset_transaction_pipeline()
    yield
    storage.reset_connection()
    reset_transaction_pipeline()


@pytest.fixture
def valid_attempt() -> dict:
    return dict(FIXTURE)
