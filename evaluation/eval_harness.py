import json
import math
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

# Add backend directory to sys.path
backend_path = Path(__file__).parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.ranking.ranker import WhyRanker
from app.models.search import RankingWeights

INDEX_ANCHOR_DATE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def binary_relevant(grade: int) -> int:
    """Fix v1 §1: Graded (0-3) to Binary threshold conversion (grade >= 2)."""
    return 1 if grade >= 2 else 0


def calculate_precision_at_k(results: List[Dict[str, Any]], judgements: Dict[str, int], k: int = 10) -> float:
    top_k = results[:k]
    if not top_k:
        return 0.0
    relevant_count = sum(binary_relevant(judgements.get(res["doc_id"], 0)) for res in top_k)
    return relevant_count / float(k)


def calculate_recall_at_k(results: List[Dict[str, Any]], judgements: Dict[str, int], total_relevant: int, k: int = 10) -> float:
    if total_relevant == 0:
        return 1.0
    top_k = results[:k]
    relevant_retrieved = sum(binary_relevant(judgements.get(res["doc_id"], 0)) for res in top_k)
    return relevant_retrieved / float(total_relevant)


def calculate_average_precision(results: List[Dict[str, Any]], judgements: Dict[str, int], total_relevant: int, k: int = 10) -> float:
    if total_relevant == 0:
        return 1.0
    top_k = results[:k]
    ap_sum = 0.0
    relevant_so_far = 0

    for idx, res in enumerate(top_k, start=1):
        grade = judgements.get(res["doc_id"], 0)
        is_rel = binary_relevant(grade)
        if is_rel:
            relevant_so_far += 1
            precision_at_i = relevant_so_far / float(idx)
            ap_sum += precision_at_i

    return ap_sum / float(total_relevant)


def calculate_dcg_at_k(results: List[Dict[str, Any]], judgements: Dict[str, int], k: int = 10) -> float:
    top_k = results[:k]
    dcg = 0.0
    for idx, res in enumerate(top_k, start=1):
        grade = judgements.get(res["doc_id"], 0)
        gain = (2 ** grade) - 1.0
        discount = math.log2(idx + 1.0)
        dcg += gain / discount
    return dcg


def calculate_ndcg_at_k(results: List[Dict[str, Any]], judgements: Dict[str, int], k: int = 10) -> float:
    dcg = calculate_dcg_at_k(results, judgements, k)

    all_grades = list(judgements.values())
    all_grades.sort(reverse=True)
    ideal_top_k = all_grades[:k]

    idcg = 0.0
    for idx, grade in enumerate(ideal_top_k, start=1):
        gain = (2 ** grade) - 1.0
        discount = math.log2(idx + 1.0)
        idcg += gain / discount

    if idcg == 0.0:
        return 1.0

    return dcg / idcg


class IREvaluator:
    """TREC-style Pooling IR Evaluation Harness with 4-Way Deep Learning Ablation Study (§1.4)."""

    def __init__(self):
        self.rankers = {
            "tfidf": WhyRanker(prefer_embeddings=False),
            "embedding": WhyRanker(prefer_embeddings=True),
        }
        self.load_corpus()

    def load_corpus(self):
        seed_path = Path(__file__).parent.parent / "data" / "seed_documents.json"
        if seed_path.exists():
            with open(seed_path, "r", encoding="utf-8") as f:
                raw_docs = json.load(f)

            docs = []
            links = []
            for idx, item in enumerate(raw_docs):
                doc_id = f"doc_{idx+1}"
                url = item.get("url", f"http://a.com/{doc_id}")
                docs.append({
                    "id": doc_id,
                    "url": url,
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),
                    "published_at": item.get("published_at"),
                })
                for target_url in item.get("outgoing_urls", []):
                    links.append({"source_url": url, "source_id": doc_id, "target_url": target_url})

            for ranker in self.rankers.values():
                ranker.index_corpus(docs, links)

    def run_eval(self) -> Dict[str, Dict[str, float]]:
        eval_path = Path(__file__).parent.parent / "data" / "eval_queries.json"
        if not eval_path.exists():
            raise FileNotFoundError(f"Evaluation dataset not found at {eval_path}")

        with open(eval_path, "r", encoding="utf-8") as f:
            eval_queries = json.load(f)

        balanced = RankingWeights(semantic=0.40, keyword=0.25, authority=0.20, freshness=0.15)
        configs = {
            "BM25 Baseline": (self.rankers["tfidf"], RankingWeights(semantic=0.00, keyword=1.00, authority=0.00, freshness=0.00), "manual"),
            "BM25 + TF-IDF (Balanced)": (self.rankers["tfidf"], balanced, "manual"),
            "BM25 + MiniLM Embeddings (Balanced)": (self.rankers["embedding"], balanced, "manual"),
            "BM25 + MiniLM Embeddings + PyTorch Neural Re-Ranker": (self.rankers["embedding"], balanced, "neural"),
        }

        metrics_summary: Dict[str, Dict[str, float]] = {
            name: {"P@10": 0.0, "Recall@10": 0.0, "MAP": 0.0, "NDCG@5": 0.0, "NDCG@10": 0.0}
            for name in configs
        }

        query_count = len(eval_queries)

        for item in eval_queries:
            query = item["query"]
            judgements = item.get("judgements", {})

            total_relevant = sum(binary_relevant(g) for g in judgements.values())
            if total_relevant == 0:
                total_relevant = 1

            for name, (ranker, weights, scoring_mode) in configs.items():
                results = ranker.rank(
                    query=query,
                    weights=weights,
                    scoring_mode=scoring_mode,
                    limit=10,
                    anchor_date=INDEX_ANCHOR_DATE,
                )

                p10 = calculate_precision_at_k(results, judgements, k=10)
                r10 = calculate_recall_at_k(results, judgements, total_relevant, k=10)
                ap = calculate_average_precision(results, judgements, total_relevant, k=10)
                ndcg5 = calculate_ndcg_at_k(results, judgements, k=5)
                ndcg10 = calculate_ndcg_at_k(results, judgements, k=10)

                metrics_summary[name]["P@10"] += p10
                metrics_summary[name]["Recall@10"] += r10
                metrics_summary[name]["MAP"] += ap
                metrics_summary[name]["NDCG@5"] += ndcg5
                metrics_summary[name]["NDCG@10"] += ndcg10

        for name in configs:
            for metric in ["P@10", "Recall@10", "MAP", "NDCG@5", "NDCG@10"]:
                metrics_summary[name][metric] = round(metrics_summary[name][metric] / float(query_count), 4)

        return metrics_summary


def print_markdown_report(metrics: Dict[str, Dict[str, float]]):
    print("\n### 📊 WhyRank Deep Learning 4-Way Ablation Benchmark Results (§1.4)\n")
    print("| Configuration | Precision@10 | Recall@10 | MAP | NDCG@5 | NDCG@10 |")
    print("| :--- | :---: | :---: | :---: | :---: | :---: |")
    for config_name, res in metrics.items():
        print(f"| **{config_name}** | {res['P@10']:.4f} | {res['Recall@10']:.4f} | {res['MAP']:.4f} | {res['NDCG@5']:.4f} | {res['NDCG@10']:.4f} |")
    print("\n")


if __name__ == "__main__":
    evaluator = IREvaluator()
    results = evaluator.run_eval()
    print_markdown_report(results)
