from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class RankingWeights(BaseModel):
    semantic: float = 0.40
    keyword: float = 0.25
    authority: float = 0.20
    freshness: float = 0.15

    @model_validator(mode="after")
    def validate_and_normalize_weights(self) -> "RankingWeights":
        """
        Validate weights sum to ~1.0 (0.85 - 1.15), and auto-normalize floating point slider rounding discrepancies.
        """
        for name in ["semantic", "keyword", "authority", "freshness"]:
            val = getattr(self, name, 0.0)
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"Weight '{name}' must be between 0.0 and 1.0 (got {val})")

        total = self.semantic + self.keyword + self.authority + self.freshness
        if not (0.85 <= total <= 1.15):
            raise ValueError(f"Ranking weights must sum to 1.0 (got {total:.3f})")

        # Auto-normalize floating point rounding discrepancies within [0.85, 1.15]
        if total > 0 and abs(total - 1.0) > 1e-6:
            s_norm = round(self.semantic / total, 4)
            k_norm = round(self.keyword / total, 4)
            a_norm = round(self.authority / total, 4)
            f_norm = round(1.0 - (s_norm + k_norm + a_norm), 4)

            self.semantic = max(0.0, s_norm)
            self.keyword = max(0.0, k_norm)
            self.authority = max(0.0, a_norm)
            self.freshness = max(0.0, f_norm)

        return self


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    weights: RankingWeights = Field(default_factory=RankingWeights)
    scoring_mode: str = Field(default="manual", pattern="^(manual|neural)$")
    limit: int = Field(default=10, ge=1, le=100)


class ScoreBreakdown(BaseModel):
    semantic: float
    keyword: float
    authority: float
    freshness: float
    final: float


class ContributionBreakdown(BaseModel):
    semantic: float
    keyword: float
    authority: float
    freshness: float


class ExplanationDetail(BaseModel):
    positive_factors: List[str]
    matched_terms: List[str]


class SearchResultItem(BaseModel):
    rank: int
    document_id: str
    title: str
    url: Optional[str] = None
    snippet: Optional[str] = None
    scores: ScoreBreakdown
    contributions: ContributionBreakdown
    explanation: ExplanationDetail


class SearchResponse(BaseModel):
    query: str
    weights: RankingWeights
    scoring_mode: str = "manual"
    results: List[SearchResultItem]
    missing_keywords: List[str] = Field(default_factory=list)
