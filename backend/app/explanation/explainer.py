from typing import List, Dict, Any
from app.indexing.normalizer import TextNormalizer
from app.models.search import ExplanationDetail


class ExplanationEngine:
    """Deterministic explanation generator for WhyRank search results."""

    def __init__(self):
        self.normalizer = TextNormalizer()

    def generate(self, query: str, candidate: Dict[str, Any]) -> ExplanationDetail:
        scores = candidate["scores"]
        doc = candidate["document"]
        is_est_freshness = candidate.get("is_estimated_freshness", False)

        positive_factors: List[str] = []

        # High score positive factors
        if scores["semantic"] >= 0.70:
            positive_factors.append("Strong semantic similarity")
        if scores["keyword"] >= 0.70:
            positive_factors.append("Strong keyword match")
        if scores["authority"] >= 0.70:
            positive_factors.append("High document authority")
        if scores["freshness"] >= 0.70:
            positive_factors.append("Recently published / high freshness")

        # Medium / Moderate positive factors if list is still empty
        if not positive_factors:
            if scores["semantic"] >= 0.40:
                positive_factors.append("Moderate semantic relevance")
            if scores["keyword"] >= 0.40:
                positive_factors.append("Partial keyword match")
            if scores["authority"] >= 0.40:
                positive_factors.append("Moderate authority score")
            if scores["freshness"] >= 0.40:
                positive_factors.append("Acceptable freshness")

        # Low score notes
        if scores["keyword"] < 0.30:
            positive_factors.append("Limited keyword overlap")
        if scores["authority"] < 0.30:
            positive_factors.append("Limited authority in graph")

        if is_est_freshness:
            positive_factors.append("Freshness estimated from ingestion date")

        # Find matched query terms in document title and content
        query_tokens = set(self.normalizer.process(query))
        doc_text = f"{doc.get('title', '')} {doc.get('content', '')}"
        doc_tokens = set(self.normalizer.process(doc_text))

        matched_terms = list(query_tokens.intersection(doc_tokens))
        matched_terms.sort()

        return ExplanationDetail(
            positive_factors=positive_factors,
            matched_terms=matched_terms,
        )
