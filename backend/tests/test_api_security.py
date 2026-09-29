from fastapi.testclient import TestClient

from app.main import app


def test_write_routes_require_configured_token(monkeypatch):
    monkeypatch.delenv("API_WRITE_TOKEN", raising=False)
    client = TestClient(app)

    assert client.post("/api/index").status_code == 503
    assert client.post("/api/index", headers={"X-API-Write-Token": "wrong"}).status_code == 503


def test_write_routes_reject_invalid_token(monkeypatch):
    monkeypatch.setenv("API_WRITE_TOKEN", "test-secret-value")
    client = TestClient(app)
    response = client.post("/api/index", headers={"X-API-Write-Token": "wrong"})
    assert response.status_code == 401


def test_search_rejects_overlong_query():
    client = TestClient(app)
    response = client.post("/api/search", json={"query": "x" * 501})
    assert response.status_code == 422


def test_cors_only_allows_configured_local_origins():
    client = TestClient(app)
    response = client.options(
        "/api/health",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in response.headers
