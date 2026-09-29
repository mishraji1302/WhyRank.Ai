import math
from typing import List, Dict, Tuple
from app.indexing.normalizer import TextNormalizer

QUERY_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but",
    "by", "for", "from", "had", "has", "have", "he", "her", "hers",
    "him", "his", "how", "i", "if", "in", "into", "is", "it", "its",
    "me", "my", "of", "on", "or", "our", "ours", "she", "so", "that",
    "the", "their", "them", "there", "these", "they", "this", "those",
    "to", "too", "us", "was", "we", "were", "what", "when", "where",
    "which", "who", "why", "will", "with", "you", "your", "yours",
}


class BM25Retriever:
    """
    Okapi BM25 Lexical Retriever with Lucene-style non-negative IDF (Fix v2 §B).
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_tokens: Dict[str, List[str]] = {}
        self.doc_lengths: Dict[str, int] = {}
        self.avgdl: float = 0.0
        self.doc_count: int = 0
        self.df: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.normalizer = TextNormalizer()

    def calculate_idf(self, n_q: int) -> float:
        """
        Lucene-style non-negative BM25 IDF formula (Fix v2 §B):
        IDF(q) = max(0.0, ln(1 + (N - n(q) + 0.5) / (n(q) + 0.5)))
        """
        if self.doc_count == 0:
            return 0.0
        val = (self.doc_count - n_q + 0.5) / (n_q + 0.5)
        # 1 + val ensures logarithm argument is >= 1, preventing negative IDF values
        idf_val = math.log(1.0 + max(0.0, val))
        return max(0.0, idf_val)

    def fit(self, documents: List[Dict[str, str]]):
        """
        Build BM25 index over document corpus.
        documents item schema: {"id": str, "content": str, "title": Optional[str]}
        """
        self.doc_tokens.clear()
        self.doc_lengths.clear()
        self.df.clear()
        self.idf.clear()

        self.doc_count = len(documents)
        if self.doc_count == 0:
            self.avgdl = 0.0
            return

        total_length = 0

        for doc in documents:
            doc_id = doc["id"]
            # Combine title and content for indexing
            text = f"{doc.get('title', '')} {doc['content']}"
            tokens = self.normalizer.process(text)
            self.doc_tokens[doc_id] = tokens
            length = len(tokens)
            self.doc_lengths[doc_id] = length
            total_length += length

            # Calculate document frequency for unique terms
            unique_terms = set(tokens)
            for term in unique_terms:
                self.df[term] = self.df.get(term, 0) + 1

        self.avgdl = total_length / self.doc_count if self.doc_count > 0 else 0.0

        # Precompute IDF for all index terms
        for term, n_q in self.df.items():
            self.idf[term] = self.calculate_idf(n_q)

    def get_scores(self, query: str) -> Dict[str, float]:
        """Calculate raw BM25 score for all documents against normalized query."""
        query_tokens = self.normalizer.process(query)
        scores: Dict[str, float] = {doc_id: 0.0 for doc_id in self.doc_tokens}

        if not query_tokens or self.doc_count == 0 or self.avgdl == 0:
            return scores

        for doc_id, tokens in self.doc_tokens.items():
            doc_len = self.doc_lengths[doc_id]
            # Calculate term frequencies for this document
            tf_map: Dict[str, int] = {}
            for t in tokens:
                tf_map[t] = tf_map.get(t, 0) + 1

            doc_score = 0.0
            for q_term in query_tokens:
                if q_term not in tf_map:
                    continue
                f = tf_map[q_term]
                idf = self.idf.get(q_term, 0.0)

                # BM25 term score formula
                numerator = f * (self.k1 + 1.0)
                denominator = f + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avgdl))
                term_score = idf * (numerator / denominator)
                doc_score += term_score

            scores[doc_id] = doc_score

        return scores

    def find_unknown_terms(self, query: str) -> List[str]:
        """Return normalized query terms that do not occur in the indexed corpus."""
        return list(dict.fromkeys(
            term for term in self.get_content_terms(query)
            if term not in self.df
        ))

    def get_content_terms(self, query: str) -> List[str]:
        """Return unique query terms after dropping common English stopwords."""
        return list(dict.fromkeys(
            term for term in self.normalizer.process(query)
            if term not in QUERY_STOPWORDS
        ))
