import pytest
import numpy as np
import torch
from app.ranking.neural_ranker import NeuralRankerModel, NeuralRanker
from app.ranking.ranker import WhyRanker
from app.models.search import RankingWeights


def test_neural_ranker_model_forward():
    model = NeuralRankerModel()
    dummy_input = torch.tensor([[0.8, 0.9, 0.5, 0.4], [0.1, 0.2, 0.3, 0.4]], dtype=torch.float32)
    output = model(dummy_input)
    assert output.shape == (2, 1)
    assert (output >= 0.0).all() and (output <= 1.0).all()


def test_neural_ranker_prediction_and_attributions():
    ranker = NeuralRanker()
    dummy_matrix = np.array([[0.8, 0.9, 0.5, 0.4], [0.1, 0.2, 0.3, 0.4]], dtype=np.float32)
    preds = ranker.predict(dummy_matrix)
    assert len(preds) == 2
    assert all(0.0 <= p <= 1.0 for p in preds)

    attr = ranker.compute_feature_attributions(dummy_matrix[0])
    assert "semantic" in attr
    assert "keyword" in attr
    assert "authority" in attr
    assert "freshness" in attr


def test_whyrank_neural_scoring_mode():
    ranker = WhyRanker()
    docs = [
        {"id": "doc1", "title": "Neural Networks", "content": "Deep learning backpropagation neural networks.", "url": "http://a.com/1"},
        {"id": "doc2", "title": "PageRank", "content": "Link analysis algorithm.", "url": "http://a.com/2"},
    ]
    ranker.index_corpus(docs)

    weights = RankingWeights(semantic=0.4, keyword=0.25, authority=0.20, freshness=0.15)
    results = ranker.rank("neural networks", weights, scoring_mode="neural")
    assert len(results) > 0
    first = results[0]
    assert "scores" in first
    assert "contributions" in first
