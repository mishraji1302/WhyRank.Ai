import pytest
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.tfidf import TFIDFRetriever
from app.retrieval.semantic import SemanticRetriever


@pytest.fixture
def sample_corpus():
    return [
        {
            "id": "doc1",
            "title": "PageRank Algorithm",
            "content": "PageRank algorithm calculates link importance using power iteration and damping factor."
        },
        {
            "id": "doc2",
            "title": "TF-IDF Vector Model",
            "content": "TF-IDF vector space model measures term frequency and inverse document frequency."
        },
        {
            "id": "doc3",
            "title": "BM25 Retrieval Function",
            "content": "BM25 is a probabilistic retrieval algorithm with k1 and b parameters for search ranking."
        },
        {
            "id": "doc4",
            "title": "Database B-Trees",
            "content": "Database indexing uses B-trees and B+ trees for logarithmic storage lookup."
        }
    ]


def test_bm25_non_negative_idf(sample_corpus):
    bm25 = BM25Retriever()
    bm25.fit(sample_corpus)

    # Test IDF for a term appearing in >50% of documents (e.g. "algorithm" or "retrieval")
    for term, n_q in bm25.df.items():
        idf = bm25.calculate_idf(n_q)
        # Fix v2 §B: Lucene non-negative IDF must be >= 0.0 for all terms
        assert idf >= 0.0, f"Term '{term}' with n_q={n_q}/{bm25.doc_count} produced negative IDF: {idf}"


def test_bm25_retrieval_ranking(sample_corpus):
    bm25 = BM25Retriever()
    bm25.fit(sample_corpus)

    scores = bm25.get_scores("PageRank algorithm")
    assert scores["doc1"] > scores["doc4"]
    assert scores["doc1"] > 0.0


def test_tfidf_cosine_similarity(sample_corpus):
    tfidf = TFIDFRetriever()
    tfidf.fit(sample_corpus)

    scores = tfidf.get_scores("TF-IDF vector space")
    assert "doc2" in scores
    assert 0.0 <= scores["doc2"] <= 1.0
    assert scores["doc2"] > scores["doc4"]


def test_semantic_retriever(sample_corpus):
    # Test with TF-IDF fallback preference
    sem = SemanticRetriever(prefer_embeddings=False)
    sem.fit(sample_corpus)
    assert sem.active_mode == "tfidf"

    scores = sem.get_scores("search algorithm")
    assert len(scores) == len(sample_corpus)
    for doc_id, score in scores.items():
        assert 0.0 <= score <= 1.0
