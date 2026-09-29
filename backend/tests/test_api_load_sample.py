from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

from app.main import app


def test_small_concurrent_search_burst():
    client = TestClient(app)
    query = {"query": "neural networks deep learning", "limit": 5}
    with ThreadPoolExecutor(max_workers=3) as pool:
        responses = list(pool.map(lambda _: client.post("/api/search", json=query), range(9)))

    assert all(response.status_code == 200 for response in responses)
    assert all(len(response.json()["results"]) <= 5 for response in responses)
