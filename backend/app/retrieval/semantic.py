from typing import List, Dict, Optional
import numpy as np
from app.retrieval.tfidf import TFIDFRetriever


class SemanticRetriever:
    """
    Semantic Retriever supporting Dense Sentence-Transformer Embeddings (all-MiniLM-L6-v2)
    with automatic fallback to TF-IDF vector space model.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", prefer_embeddings: bool = True):
        self.model_name = model_name
        self.prefer_embeddings = prefer_embeddings
        self.active_mode: str = "tfidf"
        self._model = None
        self.doc_ids: List[str] = []
        self.doc_embeddings: Optional[np.ndarray] = None
        self.tfidf_fallback = TFIDFRetriever()

    @property
    def model(self):
        """Lazy-load the SentenceTransformer model to avoid startup crashes."""
        if self._model is None and self.prefer_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                self.active_mode = "embedding"
            except Exception as e:
                print(f"Failed to load SentenceTransformer: {e}")
                self._model = None
                self.active_mode = "tfidf"
        return self._model

    def fit(self, documents: List[Dict[str, str]]):
        """Precompute embeddings or fit fallback TF-IDF vectorizer."""
        self.doc_ids = [d["id"] for d in documents]
        if not documents:
            return

        # Fit a lexical backup and initialize MiniLM before checking the active mode.
        self.tfidf_fallback.fit(documents)
        model = self.model

        if self.active_mode == "embedding" and model is not None:
            try:
                corpus = [f"{d.get('title', '')}: {d['content']}" for d in documents]
                # Encode and normalize embeddings for fast cosine similarity dot products
                embeddings = model.encode(corpus, normalize_embeddings=True, show_progress_bar=False)
                self.doc_embeddings = np.array(embeddings)
            except Exception:
                self.active_mode = "tfidf"

    def get_scores(self, query: str) -> Dict[str, float]:
        """Calculate semantic relevance scores [0.0, 1.0]."""
        scores: Dict[str, float] = {doc_id: 0.0 for doc_id in self.doc_ids}
        if not self.doc_ids or not query.strip():
            return scores

        if self.active_mode == "embedding" and self.model is not None and self.doc_embeddings is not None:
            try:
                query_embedding = self.model.encode([query], normalize_embeddings=True, show_progress_bar=False)[0]
                # Cosine similarity via dot product of normalized vectors
                similarities = np.dot(self.doc_embeddings, query_embedding)
                for idx, doc_id in enumerate(self.doc_ids):
                    val = float(similarities[idx])
                    scores[doc_id] = max(0.0, min(1.0, val))
                return scores
            except Exception:
                pass

        # Fallback to TF-IDF vector space scores
        return self.tfidf_fallback.get_scores(query)
