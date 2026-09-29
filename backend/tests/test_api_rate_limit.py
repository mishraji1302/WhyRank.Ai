from fastapi.testclient import TestClient

from app.main import app
import app.main as main_module


def test_api_rate_limit_returns_429(monkeypatch):
    monkeypatch.setattr(main_module, "_rate_limit", 2)
    client = TestClient(app, client=("192.0.2.77", 12345))

    assert client.get("/api/health").status_code == 200
    assert client.get("/api/health").status_code == 200
    response = client.get("/api/health")
    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"
