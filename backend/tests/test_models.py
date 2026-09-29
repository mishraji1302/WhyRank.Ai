import pytest
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models.document import DocumentModel, DocumentCreate, PyObjectId
from app.models.search import RankingWeights, SearchRequest


def test_py_object_id_validation():
    # Valid BSON ObjectId
    oid = ObjectId()
    str_id = str(oid)
    assert PyObjectId.validate(oid) == str_id
    assert PyObjectId.validate(str_id) == str_id

    # Invalid ObjectId
    with pytest.raises(ValueError):
        PyObjectId.validate(12345)


def test_ranking_weights_validation():
    # Valid weights (sum = 1.0)
    w = RankingWeights(semantic=0.4, keyword=0.25, authority=0.20, freshness=0.15)
    assert pytest.approx(w.semantic + w.keyword + w.authority + w.freshness) == 1.0

    # Invalid weights sum
    with pytest.raises(ValueError):
        RankingWeights(semantic=0.5, keyword=0.5, authority=0.5, freshness=0.5)

    # Negative weight
    with pytest.raises(ValueError):
        RankingWeights(semantic=-0.1, keyword=0.5, authority=0.3, freshness=0.3)


def test_document_model_serialization():
    doc = DocumentModel(
        _id=str(ObjectId()),
        url="https://example.com/test",
        title="Test Title",
        content="Test content...",
        content_hash="sha256:123",
    )
    doc_dict = doc.model_dump(by_alias=True)
    assert "_id" in doc_dict
    assert isinstance(doc_dict["_id"], str)
    assert doc_dict["title"] == "Test Title"


def test_health_check_endpoint():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "whyrank-backend"
