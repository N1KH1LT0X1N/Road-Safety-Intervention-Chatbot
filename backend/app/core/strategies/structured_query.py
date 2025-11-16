"""Structured query strategy using database filters."""
from typing import List, Dict, Any, Optional
import logging
from .base import BaseStrategy
from ...models.intervention import InterventionResult, Intervention
from ...services.database import DatabaseService

logger = logging.getLogger(__name__)


class StructuredQueryStrategy(BaseStrategy):
    """Exact match search using structured database queries."""

    def __init__(self, database: DatabaseService):
        """Initialize structured query strategy."""
        self.database = database

    @property
    def name(self) -> str:
        return "structured"

    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, max_results: int = 10
    ) -> List[InterventionResult]:
        """Search using structured filters and text matching."""
        try:
            # If filters are provided, use them
            if filters:
                results = self.database.search_by_filters(
                    category=filters.get("category"),
                    problem=filters.get("problem"),
                    speed_min=filters.get("speed_min"),
                    speed_max=filters.get("speed_max"),
                    irc_code=filters.get("irc_code"),
                    limit=max_results,
                )
            else:
                # Otherwise, do text search
                results = self.database.text_search(query, limit=max_results)

            # Convert to InterventionResult objects
            intervention_results = []

            for result in results:
                # Calculate confidence based on exact matches
                confidence = self._calculate_confidence(query, result, filters)

                intervention = Intervention(**result)

                intervention_results.append(
                    InterventionResult(
                        intervention=intervention,
                        confidence=confidence,
                        relevance_score=confidence,
                        match_reason=self._get_match_reason(result, filters),
                    )
                )

            logger.info(f"Structured search found {len(intervention_results)} results")
            return intervention_results

        except Exception as e:
            logger.error(f"Error in structured search: {e}")
            return []

    def _calculate_confidence(
        self, query: str, result: Dict[str, Any], filters: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score based on exact matches."""
        score = 0.5  # Base score

        query_lower = query.lower()

        # Exact problem match
        if result.get("problem", "").lower() in query_lower:
            score += 0.2

        # Category match
        if result.get("category", "").lower() in query_lower:
            score += 0.15

        # Type match
        if result.get("type", "").lower() in query_lower:
            score += 0.15

        # Filter matches
        if filters:
            if filters.get("category") and result.get("category") in filters["category"]:
                score += 0.1
            if filters.get("problem") and result.get("problem") in filters["problem"]:
                score += 0.1

        return min(score, 1.0)

    def _get_match_reason(self, result: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> str:
        """Get human-readable match reason."""
        reasons = []

        if filters:
            if filters.get("category"):
                reasons.append("Category filter match")
            if filters.get("problem"):
                reasons.append("Problem type filter match")
            if filters.get("speed_min") or filters.get("speed_max"):
                reasons.append("Speed range match")

        if not reasons:
            reasons.append("Text search match")

        return ", ".join(reasons)
