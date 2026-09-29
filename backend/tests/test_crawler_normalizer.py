import json
from pathlib import Path
from app.indexing.crawler import canonicalize, calculate_content_hash, SimpleCrawler
from app.indexing.normalizer import TextNormalizer


def test_url_canonicalization():
    # Fragment stripping & trailing slash normalization
    url1 = "https://Example.com/IR/PageRank/?ref=google#section1"
    canon1 = canonicalize(url1)
    assert canon1 == "https://example.com/ir/pagerank"

    # Tracking param removal & query param sorting
    url2 = "https://example.com/search?utm_source=twitter&q=python&b=2&a=1"
    canon2 = canonicalize(url2)
    assert canon2 == "https://example.com/search?a=1&b=2&q=python"

    # Root path preservation
    assert canonicalize("https://example.com/") == "https://example.com/"
    assert canonicalize("https://example.com") == "https://example.com/"


def test_text_normalizer():
    normalizer = TextNormalizer()

    raw_html = "<p>The <b>PageRank</b> algorithm measures link importance!</p>"
    tokens = normalizer.process(raw_html)

    # "the" is a stop word, "pagerank", "algorithm", "measures", "link", "importance" remain
    assert "pagerank" in tokens
    assert "algorithm" in tokens
    assert "the" not in tokens
    assert "importance" in tokens


def test_content_hash():
    h1 = calculate_content_hash("PageRank algorithm details...")
    h2 = calculate_content_hash("  pagerank   algorithm details...  ")
    assert h1 == h2
    assert h1.startswith("sha256:")


def test_seed_dataset_loading():
    seed_path = Path(__file__).resolve().parents[2] / "data" / "seed_documents.json"
    assert seed_path.exists()

    with open(seed_path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    assert isinstance(docs, list)
    assert len(docs) >= 10
    first = docs[0]
    assert "title" in first
    assert "content" in first
    assert "outgoing_urls" in first
