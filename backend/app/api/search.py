from fastapi import APIRouter, HTTPException
from app.models.search import (
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    ScoreBreakdown,
    ContributionBreakdown,
)
from app.api.documents import global_ranker
from app.explanation.explainer import ExplanationEngine

router = APIRouter(tags=["search"])
explainer = ExplanationEngine()

# Calibrated against this project's judged search queries: relevant examples
# have BM25 scores >= 2.6 and their best lexical match covers at least half
# the query's content terms. MiniLM can independently accept strong paraphrases.
MIN_BM25_RELEVANCE = 2.0
MIN_LEXICAL_QUERY_COVERAGE = 0.5
MIN_SEMANTIC_RELEVANCE = 0.35


@router.post("/api/search", response_model=SearchResponse)
def search(request: SearchRequest):
    """
    Search API endpoint accepting query, ranking weights, and scoring mode ('manual' vs 'neural').
    Returns ranked document list with numerical scores, contributions, and human-readable explanations.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    missing_keywords = global_ranker.bm25.find_unknown_terms(request.query)
    query_terms = set(global_ranker.bm25.get_content_terms(request.query))

    # Execute multi-signal ranking engine
    ranked_candidates = global_ranker.rank(
        query=request.query,
        weights=request.weights,
        scoring_mode=request.scoring_mode,
        limit=len(global_ranker.documents),
    )

    best_semantic_score = max(
        (candidate["scores"]["semantic"] for candidate in ranked_candidates),
        default=0.0,
    )
    best_lexical_match = max(
        ranked_candidates,
        key=lambda candidate: candidate["raw_bm25"],
        default=None,
    )
    lexical_match_is_relevant = False
    if best_lexical_match and query_terms:
        matched_terms = query_terms.intersection(
            global_ranker.bm25.doc_tokens.get(best_lexical_match["doc_id"], [])
        )
        coverage = len(matched_terms) / len(query_terms)
        lexical_match_is_relevant = (
            best_lexical_match["raw_bm25"] >= MIN_BM25_RELEVANCE
            and coverage >= MIN_LEXICAL_QUERY_COVERAGE
        )

    # Freshness and authority are useful ranking signals, but cannot establish
    # query relevance by themselves. Accept a result set only with substantial
    # lexical evidence or a strong MiniLM similarity match.
    if (
        best_semantic_score < MIN_SEMANTIC_RELEVANCE
        and not lexical_match_is_relevant
    ):
        ranked_candidates = []

    ranked_candidates = ranked_candidates[:request.limit]

    results = []
    for rank_idx, candidate in enumerate(ranked_candidates, start=1):
        doc = candidate["document"]
        explanation = explainer.generate(request.query, candidate)

        content = doc.get("content", "")
        snippet = content[:180] + "..." if len(content) > 180 else content

        item = SearchResultItem(
            rank=rank_idx,
            document_id=candidate["doc_id"],
            title=doc.get("title", "Untitled Document"),
            url=doc.get("url"),
            snippet=snippet,
            scores=ScoreBreakdown(**candidate["scores"]),
            contributions=ContributionBreakdown(**candidate["contributions"]),
            explanation=explanation,
        )
        results.append(item)

    return SearchResponse(
        query=request.query,
        weights=request.weights,
        scoring_mode=request.scoring_mode,
        results=results,
        missing_keywords=missing_keywords,
    )
