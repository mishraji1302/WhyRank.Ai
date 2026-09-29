import numpy as np
from typing import List, Dict, Tuple, Set, Optional
from app.retrieval.tfidf import TFIDFRetriever


class PageRankCalculator:
    """
    PageRank Authority Calculator with Sink-Node Mass Redistribution (Fix v2 §C)
    and Graph Density Check + TF-IDF Topical Fallback (Fix v1 §4b).
    """

    def __init__(self, alpha: float = 0.85, max_iter: int = 100, tol: float = 1e-6):
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol

    def calculate(
        self,
        documents: List[Dict[str, str]],
        links: List[Dict[str, str]],
        fallback_density_threshold: float = 0.01,
    ) -> Dict[str, float]:
        """
        Calculate normalized authority scores [0, 1] for each document ID.
        documents: list of {"id": str, "url": str, "title": str, "content": str}
        links: list of {"source_url": str, "target_url": str} or {"source_id": str, "target_id": str}
        """
        doc_ids = [d["id"] for d in documents]
        N = len(doc_ids)
        if N == 0:
            return {}
        if N == 1:
            return {doc_ids[0]: 1.0}

        url_to_id: Dict[str, str] = {d["url"]: d["id"] for d in documents if "url" in d}
        id_set: Set[str] = set(doc_ids)

        # Build adjacency graph
        adj_in: Dict[str, List[str]] = {doc_id: [] for doc_id in doc_ids}
        out_degree: Dict[str, int] = {doc_id: 0 for doc_id in doc_ids}
        total_edges = 0

        for link in links:
            source_id = link.get("source_id") or url_to_id.get(link.get("source_url", ""))
            target_id = link.get("target_id") or url_to_id.get(link.get("target_url", ""))

            if source_id and target_id and source_id in id_set and target_id in id_set and source_id != target_id:
                adj_in[target_id].append(source_id)
                out_degree[source_id] += 1
                total_edges += 1

        # Citation graphs are naturally sparse. A density threshold would
        # classify real citation links as insufficient and build a costly
        # all-pairs similarity graph instead. Fall back only if no valid
        # citation links were found.
        if total_edges == 0:
            adj_in, out_degree = self._build_tfidf_similarity_graph(documents)

        # Power iteration PageRank with Sink-Node Mass Redistribution (Fix v2 §C)
        pr = {doc_id: 1.0 / N for doc_id in doc_ids}

        for _ in range(self.max_iter):
            # Collect rank mass held by sink nodes (OutDegree = 0)
            leaked_mass = sum(pr[node] for node in doc_ids if out_degree[node] == 0)
            redistribution = leaked_mass / N

            new_pr = {}
            for node in doc_ids:
                # Sum PR(p) / OutDegree(p) for incoming links
                in_sum = sum(pr[in_node] / out_degree[in_node] for in_node in adj_in[node] if out_degree[in_node] > 0)

                # PageRank equation with sink node mass redistribution:
                # PR(d) = (1 - alpha)/N + alpha * in_sum + alpha * (leaked_mass / N)
                node_pr = ((1.0 - self.alpha) / N) + self.alpha * in_sum + self.alpha * redistribution
                new_pr[node] = node_pr

            # Check convergence
            diff = sum(abs(new_pr[node] - pr[node]) for node in doc_ids)
            pr = new_pr
            if diff < self.tol:
                break

        # Normalize PageRank values to [0.0, 1.0] using Min-Max
        pr_values = list(pr.values())
        min_val = min(pr_values)
        max_val = max(pr_values)

        normalized_pr: Dict[str, float] = {}
        for doc_id, raw_score in pr.items():
            if max_val == min_val:
                normalized_pr[doc_id] = 1.0 if max_val > 0 else 0.0
            else:
                normalized_pr[doc_id] = (raw_score - min_val) / (max_val - min_val)

        return normalized_pr

    def _build_tfidf_similarity_graph(
        self, documents: List[Dict[str, str]], similarity_threshold: float = 0.2
    ) -> Tuple[Dict[str, List[str]], Dict[str, int]]:
        """Construct a TF-IDF cosine similarity graph fallback (TextRank style)."""
        doc_ids = [d["id"] for d in documents]
        adj_in: Dict[str, List[str]] = {doc_id: [] for doc_id in doc_ids}
        out_degree: Dict[str, int] = {doc_id: 0 for doc_id in doc_ids}

        tfidf = TFIDFRetriever()
        tfidf.fit(documents)

        if tfidf.tfidf_matrix is not None:
            from sklearn.metrics.pairwise import cosine_similarity
            sim_matrix = cosine_similarity(tfidf.tfidf_matrix)

            for i, source_id in enumerate(doc_ids):
                for j, target_id in enumerate(doc_ids):
                    if i != j and sim_matrix[i, j] > similarity_threshold:
                        adj_in[target_id].append(source_id)
                        out_degree[source_id] += 1

        return adj_in, out_degree
