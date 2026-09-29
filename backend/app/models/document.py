from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
from pydantic_core import core_schema
from bson import ObjectId


class PyObjectId(str):
    """Custom ObjectId type for Pydantic v2 compatibility."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        if isinstance(v, str):
            return v
        raise ValueError("Invalid ObjectId or string ID")


class DocumentMetadata(BaseModel):
    domain: Optional[str] = None
    author: Optional[str] = None
    content_type: str = "text/html"


class DocumentFeatures(BaseModel):
    authority: float = 0.0
    freshness: float = 1.0


class DocumentModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, json_encoders={ObjectId: str})

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    url: str
    title: str
    content: str
    content_hash: str
    published_at: Optional[datetime] = None
    crawled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    features: DocumentFeatures = Field(default_factory=DocumentFeatures)


class DocumentLinkModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, json_encoders={ObjectId: str})

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    source_document_id: str
    target_document_id: str
    source_url: str
    target_url: str


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1, max_length=200_000)
    source_url: str = Field(..., min_length=1, max_length=2_048)
    published_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
