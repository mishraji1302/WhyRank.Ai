from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from app.models.search import RankingWeights
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.tfidf import TFIDFRetriever
from app.retrieval.semantic import SemanticRetriever
from app.authority.pagerank import PageRankCalculator
from app.ranking.freshness import FreshnessCalculator
from app.ranking.neural_ranker import NeuralRanker


def min_max_normalize(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Min-Max normalization with Zero-Match Edge Case Fix (Fix v2 §A):
    - If max(D) == min(D): return 1.0 if max > 0 else 0.0.
    """
    if not scores:
        return {}

    vals = list(scores.values())
    min_val = min(vals)
    max_val = max(vals)

    normalized: Dict[str, float] = {}
    for doc_id, raw_val in scores.items():
        if max_val == min_val:
            normalized[doc_id] = 1.0 if max_val > 0 else 0.0
        else:
            normalized[doc_id] = (raw_val - min_val) / (max_val - min_val)

    return normalized


class WhyRanker:
    """
    WhyRank Multi-Signal Ranking Engine implementing:
    - Zero-Match Normalization (Fix v2 §A)
    - Candidate Pool Size K = N (Fix v2 §D)
    - Dynamic Tie-Breaking by argmax(weights) (Fix v2 §E)
    - PyTorch Neural Re-Ranker Mode (Fix Part 1 §1.2)
    """

    def __init__(self, prefer_embeddings: bool = True):
        self.bm25 = BM25Retriever()
        self.tfidf = TFIDFRetriever()
        self.semantic = SemanticRetriever(prefer_embeddings=prefer_embeddings)
        self.pagerank_calc = PageRankCalculator()
        self.freshness_calc = FreshnessCalculator(half_life_days=1825.0)
        self.neural_ranker = NeuralRanker()

        self.documents: List[Dict[str, Any]] = []
        self.links: List[Dict[str, Any]] = []
        self.precomputed_authority: Dict[str, float] = {}
        self.precomputed_freshness: Dict[str, Tuple[float, bool]] = {}

    def index_corpus(self, documents: List[Dict[str, Any]], links: Optional[List[Dict[str, Any]]] = None):
        """Build indexes and precompute document features (Authority and Freshness)."""
        self.documents = documents
        self.links = links if links is not None else []

        if not documents:
            return

        # 1. Fit Retrieval Engines
        self.bm25.fit(documents)
        self.tfidf.fit(documents)
        self.semantic.fit(documents)

        # 2. Precompute PageRank Authority
        self.precomputed_authority = self.pagerank_calc.calculate(documents, self.links)

        # 3. Precompute Freshness
        self.precomputed_freshness = {}
        for doc in documents:
            pub_at = doc.get("published_at")
            crawled_at = doc.get("crawled_at")
            score, is_est = self.freshness_calc.calculate(published_at=pub_at, crawled_at=crawled_at)
            self.precomputed_freshness[doc["id"]] = (score, is_est)

    def rank(
        self,
        query: str,
        weights: RankingWeights,
        limit: int = 10,
        scoring_mode: str = "manual",
        anchor_date=None,
    ) -> List[Dict[str, Any]]:
        """
        Perform candidate retrieval, feature normalization, weighted scoring or neural re-ranking, and dynamic tie-breaking.
        """
        if not self.documents:
            return []

        # 1. Retrieve Raw Signal Scores (K = N candidate pool, Fix v2 §D)
        raw_bm25 = self.bm25.get_scores(query)
        raw_semantic = self.semantic.get_scores(query)

        # 2. Normalize Signal Scores
        norm_keyword = min_max_normalize(raw_bm25)
        norm_semantic = raw_semantic

        # Determine tie-breaking signal based on argmax(active_weights) (Fix v2 §E)
        weight_dict = {
            "semantic": weights.semantic,
            "keyword": weights.keyword,
            "authority": weights.authority,
            "freshness": weights.freshness,
        }
        primary_signal_name = max(weight_dict, key=weight_dict.get)

        candidates = []

        # Prepare feature matrix if in neural mode
        doc_list = self.documents
        if scoring_mode == "neural" and self.neural_ranker.is_trained:
            feature_rows = []
            for doc in doc_list:
                d_id = doc["id"]
                sem = norm_semantic.get(d_id, 0.0)
                kw = norm_keyword.get(d_id, 0.0)
                auth = self.precomputed_authority.get(d_id, 0.0)
                fresh = self.precomputed_freshness.get(d_id, (0.5, True))[0]
                feature_rows.append([sem, kw, auth, fresh])

            f_matrix = np.array(feature_rows, dtype=np.float32)
            neural_scores = self.neural_ranker.predict(f_matrix)
        else:
            neural_scores = None

        for idx, doc in enumerate(doc_list):
            doc_id = doc["id"]

            sem_score = norm_semantic.get(doc_id, 0.0)
            kw_score = norm_keyword.get(doc_id, 0.0)
            auth_score = self.precomputed_authority.get(doc_id, 0.0)

            if anchor_date is not None:
                fresh_score, is_est = self.freshness_calc.calculate(
                    published_at=doc.get("published_at"),
                    crawled_at=doc.get("crawled_at"),
                    anchor_date=anchor_date,
                )
            else:
                fresh_score, is_est = self.precomputed_freshness.get(doc_id, (0.5, True))

            feat_vec = np.array([sem_score, kw_score, auth_score, fresh_score], dtype=np.float32)

            if scoring_mode == "neural" and neural_scores is not None:
                final_score = float(neural_scores[idx])
                # Compute SHAP-style gradient feature attributions for explainability (§1.2)
                attr_dict = self.neural_ranker.compute_feature_attributions(feat_vec)
                c_sem = attr_dict["semantic"]
                c_kw = attr_dict["keyword"]
                c_auth = attr_dict["authority"]
                c_fresh = attr_dict["freshness"]
            else:
                c_sem = sem_score * weights.semantic
                c_kw = kw_score * weights.keyword
                c_auth = auth_score * weights.authority
                c_fresh = fresh_score * weights.freshness
                final_score = c_sem + c_kw + c_auth + c_fresh

            signal_scores = {
                "semantic": sem_score,
                "keyword": kw_score,
                "authority": auth_score,
                "freshness": fresh_score,
            }
            tie_break_score = signal_scores.get(primary_signal_name, 0.0)

            candidates.append({
                "doc_id": doc_id,
                "document": doc,
                "scores": {
                    "semantic": round(sem_score, 4),
                    "keyword": round(kw_score, 4),
                    "authority": round(auth_score, 4),
                    "freshness": round(fresh_score, 4),
                    "final": round(final_score, 4),
                },
                "contributions": {
                    "semantic": round(c_sem, 4),
                    "keyword": round(c_kw, 4),
                    "authority": round(c_auth, 4),
                    "freshness": round(c_fresh, 4),
                },
                "is_estimated_freshness": is_est,
                "raw_bm25": raw_bm25.get(doc_id, 0.0),
                "tie_break_score": tie_break_score,
            })

        query_has_terms = len(query.strip()) > 0
        if query_has_terms:
            valid_candidates = [c for c in candidates if c["scores"]["final"] > 0.0]
            if valid_candidates:
                candidates = valid_candidates

        candidates.sort(key=lambda x: (-x["scores"]["final"], -x["tie_break_score"], x["doc_id"]))

        return candidates[:limit]
