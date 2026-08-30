from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_metrics_and_incidents_are_mounted_under_v1_per_openapi_servers_block():
    """CTR-API-001 v3's servers block is https://.../v1 for every documented path —
    these three routers were mounted at root instead, so the documented paths 404'd."""
    assert client.get("/v1/health").status_code == 200
    assert client.get("/v1/metrics/current").status_code == 200
    assert client.get("/v1/incidents").status_code == 200
