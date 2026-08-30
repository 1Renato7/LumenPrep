from unittest.mock import patch
from pathlib import Path

import duckdb
import pytest
from fastapi.testclient import TestClient

from app.config import Settings, settings
from app.ingestion import storage
from main import create_app


def test_docker_uses_frozen_uv_lock_and_installs_neo4j_extra():
    dockerfile = (Path(__file__).resolve().parent.parent / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY pyproject.toml uv.lock" in dockerfile
    assert "COPY config ./config" in dockerfile
    assert "COPY data ./data" in dockerfile
    assert "uv sync --frozen --no-dev --extra neo4j" in dockerfile
    assert "mkdir -p /data" in dockerfile
    assert 'ENV PATH="/app/.venv/bin:$PATH"' in dockerfile
    dockerignore = (Path(__file__).resolve().parent.parent / ".dockerignore").read_text(encoding="utf-8").splitlines()
    assert "web" in dockerignore


def test_cors_accepts_only_configured_browser_origin():
    app = create_app(
        Settings(cors_allowed_origins="https://lumen.vercel.app, http://localhost:3000")
    )
    with TestClient(app) as client:
        allowed = client.options(
            "/v1/transaction-catalog",
            headers={
                "Origin": "https://lumen.vercel.app",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,idempotency-key",
            },
        )
        denied = client.options(
            "/v1/transaction-catalog",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "https://lumen.vercel.app"
    assert "idempotency-key" in allowed.headers["access-control-allow-headers"].lower()
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers


def test_cors_rejects_wildcards_and_non_absolute_origins():
    with pytest.raises(ValueError, match="must not contain"):
        _ = Settings(cors_allowed_origins="*").cors_origins
    with pytest.raises(ValueError, match="absolute"):
        _ = Settings(cors_allowed_origins="lumen.vercel.app").cors_origins
    with pytest.raises(ValueError, match="absolute"):
        _ = Settings(cors_allowed_origins="https://lumen.vercel.app/preview").cors_origins


def test_health_is_degraded_when_startup_reconciliation_fails():
    with patch("main.reconcile_stuck", side_effect=RuntimeError("storage unavailable")):
        app = create_app(Settings())
        with TestClient(app) as client:
            response = client.get("/v1/health")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["dependencies"]["worker"]["status"] == "unavailable"


def test_startup_reconciliation_skips_remote_agent_suggestions():
    with patch("main.reconcile_stuck", return_value=0) as reconciliation:
        app = create_app(Settings())
        with TestClient(app) as client:
            assert client.get("/v1/health").status_code == 200

    reconciliation.assert_called_once_with(run_suggestions=False)


def test_existing_volume_is_migrated_before_worker_reconciliation(tmp_path):
    database_path = tmp_path / "lumen.duckdb"
    legacy = duckdb.connect(str(database_path))
    legacy.execute(
        """CREATE TABLE transaction_records (
            transaction_id VARCHAR PRIMARY KEY,
            batch_id VARCHAR NOT NULL,
            batch_position INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            status VARCHAR NOT NULL,
            input_json VARCHAR NOT NULL,
            processing_json VARCHAR NOT NULL,
            outcome_json VARCHAR,
            classification_json VARCHAR,
            correlation_id VARCHAR NOT NULL
        )"""
    )
    legacy.close()

    with patch("app.ingestion.storage.settings.duckdb_path", str(database_path)):
        storage.reset_connection()
        columns = {row[0] for row in storage.get_connection().execute("DESCRIBE transaction_records").fetchall()}

    assert {"lease_owner", "lease_expires_at"} <= columns


def test_volume_database_preserves_a_batch_across_runtime_restart(tmp_path):
    database_path = tmp_path / "lumen.duckdb"
    payload = {
        "schema_version": "1.0",
        "idempotency_key": "volume-restart-0001",
        "transactions": [
            {
                "merchant_id": "merchant_br_01",
                "provider_id": "provider_alpha",
                "issuer_bank": "bank_br_a",
                "country": "BR",
                "currency": "BRL",
                "amount_minor": 12990,
                "payment_method_category": "CARD",
                "card_brand": "VISA",
                "card_type": "CREDIT",
            }
        ],
    }

    with patch.object(settings, "duckdb_path", str(database_path)):
        storage.reset_connection()
        with TestClient(create_app()) as first_runtime:
            accepted = first_runtime.post(
                "/v1/transaction-batches",
                json=payload,
                headers={"Idempotency-Key": payload["idempotency_key"]},
            ).json()
        storage.reset_connection()
        with TestClient(create_app()) as restarted_runtime:
            restored = restarted_runtime.get(f"/v1/transactions/{accepted['transaction_ids'][0]}")

    assert restored.status_code == 200
    assert restored.json()["transaction_id"] == accepted["transaction_ids"][0]
    assert restored.json()["processing"]["progress_percent"] == 100
