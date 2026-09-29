import json
import hmac
import os
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, Header, HTTPException
from app.models.document import DocumentCreate
from app.ranking.ranker import WhyRanker
from app.indexing.crawler import canonicalize, calculate_content_hash

router = APIRouter(tags=["documents"])


def require_write_token(token: str | None):
    expected = os.getenv("API_WRITE_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="Document mutations are disabled: API_WRITE_TOKEN is not configured")
    if not token or not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")

# Global shared ranker instance
global_ranker = WhyRanker()
_indexed_documents: List[Dict[str, Any]] = []
_indexed_links: List[Dict[str, Any]] = []
_current_index_version = 1


def load_seed_documents():
    """Load seed dataset into global document store on startup."""
    global _indexed_documents, _indexed_links, _current_index_version
    seed_path = Path(__file__).parent.parent.parent.parent / "data" / "seed_documents.json"
    if seed_path.exists():
        try:
            with open(seed_path, "r", encoding="utf-8") as f:
                raw_docs = json.load(f)

            _indexed_documents = []
            _indexed_links = []

            for idx, item in enumerate(raw_docs):
                doc_id = f"doc_{idx+1}"
                url = canonicalize(item.get("url", f"https://example.org/doc/{doc_id}"))
                content = item.get("content", "")
                title = item.get("title", f"Document {idx+1}")
                published_at = item.get("published_at")

                doc_obj = {
                    "id": doc_id,
                    "url": url,
                    "title": title,
                    "content": content,
                    "content_hash": calculate_content_hash(content),
                    "published_at": published_at,
                    "metadata": {"domain": "example.org"},
                }
                _indexed_documents.append(doc_obj)

                # Extract outgoing link relationships
                for target_url in item.get("outgoing_urls", []):
                    _indexed_links.append({
                        "source_url": url,
                        "source_id": doc_id,
                        "target_url": canonicalize(target_url),
                    })

            global_ranker.index_corpus(_indexed_documents, _indexed_links)
            _current_index_version += 1
        except Exception as e:
            print(f"Error loading seed documents: {e}")


# Initialize seed data on import
load_seed_documents()


@router.get("/api/documents")
def list_documents():
    """List summary of indexed documents."""
    return {
        "count": len(_indexed_documents),
        "index_version": _current_index_version,
        "documents": [
            {
                "id": d["id"],
                "title": d["title"],
                "url": d["url"],
                "published_at": d.get("published_at"),
            }
            for d in _indexed_documents
        ]
    }


@router.post("/api/documents")
def add_document(doc_in: DocumentCreate, x_api_write_token: str | None = Header(default=None)):
    """Add a new document to the index corpus."""
    require_write_token(x_api_write_token)
    global _current_index_version
    doc_id = f"doc_{len(_indexed_documents) + 1}"
    url = canonicalize(doc_in.source_url)
    c_hash = calculate_content_hash(doc_in.content)

    # Check for duplicates
    for existing in _indexed_documents:
        if existing["content_hash"] == c_hash or existing["url"] == url:
            raise HTTPException(status_code=400, detail="Document with matching URL or content already exists.")

    new_doc = {
        "id": doc_id,
        "url": url,
        "title": doc_in.title,
        "content": doc_in.content,
        "content_hash": c_hash,
        "published_at": doc_in.published_at.isoformat() if doc_in.published_at else None,
        "metadata": doc_in.metadata or {},
    }

    _indexed_documents.append(new_doc)
    global_ranker.index_corpus(_indexed_documents, _indexed_links)
    _current_index_version += 1

    return {"status": "success", "document_id": doc_id, "index_version": _current_index_version}


@router.post("/api/index")
def trigger_indexing(x_api_write_token: str | None = Header(default=None)):
    """Trigger full index rebuild over document collection."""
    require_write_token(x_api_write_token)
    global _current_index_version
    global_ranker.index_corpus(_indexed_documents, _indexed_links)
    _current_index_version += 1

    return {
        "version": _current_index_version,
        "document_count": len(_indexed_documents),
        "retrieval": {"bm25": True, "tfidf": True},
        "semantic": global_ranker.semantic.active_mode == "embedding",
    }
