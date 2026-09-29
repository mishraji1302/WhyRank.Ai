from typing import List, Dict, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.indexing.normalizer import TextNormalizer


class TFIDFRetriever:
    """Vector space model retriever using TF-IDF vectors and Cosine Similarity."""

    def __init__(self):
        self.normalizer = TextNormalizer()
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.doc_ids: List[str] = []
        self.tfidf_matrix: Optional[np.ndarray] = None

    def _custom_tokenizer(self, text: str) -> List[str]:
        return self.normalizer.process(text)

    def fit(self, documents: List[Dict[str, str]]):
        """Fit TF-IDF matrix on document collection."""
        self.doc_ids = [d["id"] for d in documents]
        if not documents:
            self.tfidf_matrix = None
            return

        corpus = [f"{d.get('title', '')} {d['content']}" for d in documents]

        self.vectorizer = TfidfVectorizer(
            tokenizer=self._custom_tokenizer,
            token_pattern=None,
            lowercase=False,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def get_scores(self, query: str) -> Dict[str, float]:
        """Compute cosine similarity scores [0, 1] for all documents."""
        scores: Dict[str, float] = {doc_id: 0.0 for doc_id in self.doc_ids}
        if self.vectorizer is None or self.tfidf_matrix is None or not self.doc_ids:
            return scores

        query_tokens = self.normalizer.process(query)
        if not query_tokens:
            return scores

        try:
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            for idx, doc_id in enumerate(self.doc_ids):
                # Clamp cosine similarity to [0.0, 1.0]
                val = float(similarities[idx])
                scores[doc_id] = max(0.0, min(1.0, val))
        except Exception:
            pass

        return scores
