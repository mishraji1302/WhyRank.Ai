import pytest
import sys
from pathlib import Path

# Insert project root for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evaluation.eval_harness import (
    binary_relevant,
    calculate_precision_at_k,
    calculate_dcg_at_k,
    calculate_ndcg_at_k,
    IREvaluator,
)


def test_binary_relevance_threshold():
    # Fix v1 §1: grade >= 2 -> 1, grade < 2 -> 0
    assert binary_relevant(0) == 0
    assert binary_relevant(1) == 0
    assert binary_relevant(2) == 1
    assert binary_relevant(3) == 1


def test_ndcg_calculation_accuracy():
    results = [
        {"doc_id": "doc1"},
        {"doc_id": "doc2"},
        {"doc_id": "doc3"},
    ]
    # Perfect ranking matches ideal -> NDCG should be 1.0
    ideal_judgements = {"doc1": 3, "doc2": 2, "doc3": 1}
    ndcg_perfect = calculate_ndcg_at_k(results, ideal_judgements, k=3)
    assert pytest.approx(ndcg_perfect, abs=1e-3) == 1.0

    # Inverted ranking -> NDCG should be < 1.0
    inverted_results = [
        {"doc_id": "doc3"},
        {"doc_id": "doc2"},
        {"doc_id": "doc1"},
    ]
    ndcg_inverted = calculate_ndcg_at_k(inverted_results, ideal_judgements, k=3)
    assert ndcg_inverted < 1.0


def test_eval_harness_execution():
    evaluator = IREvaluator()
    summary = evaluator.run_eval()

    expected_keys = [
        "BM25 Baseline",
        "BM25 + TF-IDF (Balanced)",
        "BM25 + MiniLM Embeddings (Balanced)",
        "BM25 + MiniLM Embeddings + PyTorch Neural Re-Ranker",
    ]

    for key in expected_keys:
        assert key in summary

    for config, metrics in summary.items():
        assert 0.0 <= metrics["P@10"] <= 1.0
        assert 0.0 <= metrics["Recall@10"] <= 1.0
        assert 0.0 <= metrics["MAP"] <= 1.0
        assert 0.0 <= metrics["NDCG@10"] <= 1.0
