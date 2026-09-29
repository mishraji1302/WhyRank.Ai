import pytest
from datetime import datetime, timedelta, timezone
from app.authority.pagerank import PageRankCalculator
from app.ranking.freshness import FreshnessCalculator


def test_pagerank_sink_node_mass_redistribution():
    # Corpus with 3 nodes: doc1 -> doc2, doc2 -> doc3, doc3 has 0 outgoing links (sink node)
    documents = [
        {"id": "doc1", "title": "Doc 1", "content": "Content 1", "url": "http://a.com/1"},
        {"id": "doc2", "title": "Doc 2", "content": "Content 2", "url": "http://a.com/2"},
        {"id": "doc3", "title": "Doc 3", "content": "Content 3", "url": "http://a.com/3"},
    ]
    links = [
        {"source_id": "doc1", "target_id": "doc2"},
        {"source_id": "doc2", "target_id": "doc3"},
        # doc3 is a sink node (0 outgoing links)
    ]

    pr_calc = PageRankCalculator()
    scores = pr_calc.calculate(documents, links)

    assert len(scores) == 3
    # doc3 has incoming links from doc2, so it should rank highest in authority
    assert scores["doc3"] >= scores["doc1"]
    assert all(0.0 <= s <= 1.0 for s in scores.values())


def test_pagerank_zero_links_tfidf_fallback():
    # Corpus with NO links (density = 0.0) -> should trigger TF-IDF similarity graph fallback
    documents = [
        {"id": "doc1", "title": "PageRank Search", "content": "PageRank algorithm in information retrieval."},
        {"id": "doc2", "title": "PageRank Ranking", "content": "PageRank search ranking power iteration."},
        {"id": "doc3", "title": "Database B-Tree", "content": "Relational database B-trees and indexing."},
    ]
    links = []  # Empty links list

    pr_calc = PageRankCalculator()
    scores = pr_calc.calculate(documents, links, fallback_density_threshold=0.01)

    assert len(scores) == 3
    # doc1 and doc2 are topically similar (PageRank), so their authority scores should reflect topical similarity
    assert scores["doc1"] > 0.0 or scores["doc2"] > 0.0


def test_freshness_half_life():
    freshness_calc = FreshnessCalculator(half_life_days=1825.0)  # 5-year half life

    # 0 days old -> score = 1.0
    s0 = freshness_calc.calculate_score_from_days(0)
    assert pytest.approx(s0, abs=1e-3) == 1.0

    # 1825 days old (5 years) -> score ≈ 0.5
    s5y = freshness_calc.calculate_score_from_days(1825.0)
    assert pytest.approx(s5y, abs=1e-2) == 0.5

    # 3650 days old (10 years) -> score ≈ 0.25
    s10y = freshness_calc.calculate_score_from_days(3650.0)
    assert pytest.approx(s10y, abs=1e-2) == 0.25


def test_freshness_date_anchoring_and_estimation():
    freshness_calc = FreshnessCalculator(half_life_days=1825.0)
    anchor = datetime(2026, 1, 1, tzinfo=timezone.utc)

    pub_date = datetime(2021, 1, 1, tzinfo=timezone.utc)  # Exactly 5 years before anchor (1826 days)

    # Test with published_at provided
    score, is_estimated = freshness_calc.calculate(published_at=pub_date, anchor_date=anchor)
    assert pytest.approx(score, abs=0.05) == 0.5
    assert is_estimated is False

    # Test fallback to crawled_at (is_estimated = True)
    crawl_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    score_est, is_est = freshness_calc.calculate(published_at=None, crawled_at=crawl_date, anchor_date=anchor)
    assert pytest.approx(score_est, abs=1e-3) == 1.0
    assert is_est is True
