import math
from datetime import datetime, timezone
from typing import Optional, Tuple, Union


class FreshnessCalculator:
    """
    Freshness Calculator with Exponential Decay 5-Year Half-Life (Fix v1 §5)
    and Evaluation Date Anchoring (Fix v2 §F).
    """

    def __init__(self, half_life_days: float = 1825.0):
        self.half_life_days = half_life_days
        # Decay constant lambda = ln(2) / half_life_days
        self.decay_lambda = math.log(2.0) / self.half_life_days

    def calculate_score_from_days(self, age_days: float) -> float:
        """Calculate exponential decay score: e^(-lambda * age_days)."""
        if age_days < 0:
            age_days = 0.0
        score = math.exp(-self.decay_lambda * age_days)
        return max(0.0, min(1.0, score))

    def _parse_datetime(self, val: Union[datetime, str, None]) -> Optional[datetime]:
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        if isinstance(val, str):
            try:
                # Parse ISO string format
                clean_str = val.replace("Z", "+00:00")
                return datetime.fromisoformat(clean_str)
            except Exception:
                return None
        return None

    def calculate(
        self,
        published_at: Optional[Union[datetime, str]],
        crawled_at: Optional[Union[datetime, str]] = None,
        anchor_date: Optional[datetime] = None,
    ) -> Tuple[float, bool]:
        """
        Calculate freshness score [0.0, 1.0] and return (score, is_estimated).
        - If published_at is None, fallback to crawled_at and set is_estimated=True.
        - If anchor_date is provided (Fix v2 §F), calculate age relative to anchor_date.
        """
        is_estimated = False
        parsed_pub = self._parse_datetime(published_at)
        parsed_crawl = self._parse_datetime(crawled_at)

        target_doc_date = parsed_pub

        if target_doc_date is None:
            target_doc_date = parsed_crawl
            is_estimated = True

        if target_doc_date is None:
            # Complete date missing fallback
            return 0.5, True

        # Ensure timezone-aware datetime comparison
        now = anchor_date if anchor_date is not None else datetime.now(timezone.utc)
        if target_doc_date.tzinfo is None:
            target_doc_date = target_doc_date.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        delta = now - target_doc_date
        age_days = max(0.0, delta.total_seconds() / 86400.0)

        score = self.calculate_score_from_days(age_days)
        return score, is_estimated
