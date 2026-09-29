import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ranking.ranker import WhyRanker, min_max_normalize
from app.models.search import RankingWeights
from app.explanation.explainer import ExplanationEngine


def test_min_max_normalize_zero_match():
    # Fix v2 §A: All scores zero (no matches) -> must normalize to 0.0, NOT 1.0!
    zero_scores = {"doc1": 0.0, "doc2": 0.0, "doc3": 0.0}
    norm_zero = min_max_normalize(zero_scores)
    assert all(val == 0.0 for val in norm_zero.values()), f"Expected 0.0 for zero-matches, got {norm_zero}"

    # Genuine non-zero ties -> normalize to 1.0
    tied_positive = {"doc1": 5.2, "doc2": 5.2}
    norm_tied = min_max_normalize(tied_positive)
    assert all(val == 1.0 for val in norm_tied.values())


def test_dynamic_tie_breaking():
    # Fix v2 §E: Tie-breaking by argmax(active_weights)
    ranker = WhyRanker()
    docs = [
        {"id": "doc1", "title": "A", "content": "test text", "url": "http://a.com/1"},
        {"id": "doc2", "title": "B", "content": "test text", "url": "http://a.com/2"},
    ]
    ranker.index_corpus(docs)

    # Keyword first weight profile -> tie break by keyword score
    weights_kw = RankingWeights(semantic=0.1, keyword=0.7, authority=0.1, freshness=0.1)
    results = ranker.rank("test", weights_kw)
    assert len(results) == 2


def test_explanation_engine():
    explainer = ExplanationEngine()
    candidate = {
        "doc_id": "doc1",
        "document": {"title": "PageRank Search", "content": "PageRank algorithm in information retrieval."},
        "scores": {"semantic": 0.9, "keyword": 0.8, "authority": 0.2, "freshness": 0.5, "final": 0.75},
        "is_estimated_freshness": True,
    }
    explanation = explainer.generate("pagerank algorithm", candidate)
    assert "Strong semantic similarity" in explanation.positive_factors
    assert "Strong keyword match" in explanation.positive_factors
    assert "pagerank" in explanation.matched_terms


def test_api_search_endpoint():
    client = TestClient(app)

    # 1. Standard search query
    response = client.post(
        "/api/search",
        json={
            "query": "neural networks deep learning",
            "weights": {"semantic": 0.4, "keyword": 0.25, "authority": 0.20, "freshness": 0.15},
            "limit": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "neural networks deep learning"
    assert len(data["results"]) > 0

    first_result = data["results"][0]
    assert first_result["rank"] == 1
    assert "scores" in first_result
    assert "contributions" in first_result
    assert "explanation" in first_result
    assert len(first_result["explanation"]["positive_factors"]) > 0

    # Irrelevant out-of-domain queries must not receive freshness-only results.
    irrelevant_res = client.post(
        "/api/search",
        json={"query": "blue cow is dancing", "limit": 5},
    )
    assert irrelevant_res.status_code == 200
    irrelevant_data = irrelevant_res.json()
    assert irrelevant_data["results"] == []
    assert set(irrelevant_data["missing_keywords"]) == {"blue", "cow", "dancing"}

    # 2. Invalid weights sum -> 422 Unprocessable Entity
    bad_weights_res = client.post(
        "/api/search",
        json={
            "query": "test",
            "weights": {"semantic": 0.9, "keyword": 0.9, "authority": 0.9, "freshness": 0.9},
        },
    )
    assert bad_weights_res.status_code == 422
