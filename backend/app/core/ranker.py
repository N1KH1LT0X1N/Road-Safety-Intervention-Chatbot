"""Result ranking and fusion utilities."""
from typing import List
from ..models.intervention import InterventionResult
import logging

logger = logging.getLogger(__name__)


class ResultRanker:
    """Rank and deduplicate search results."""

    @staticmethod
    def deduplicate(results: List[InterventionResult]) -> List[InterventionResult]:
        """Remove duplicate results, keeping highest confidence."""
        seen_ids = {}

        for result in results:
            intervention_id = result.intervention.id

            if intervention_id not in seen_ids:
                seen_ids[intervention_id] = result
            else:
                # Keep the one with higher confidence
                if result.confidence > seen_ids[intervention_id].confidence:
                    seen_ids[intervention_id] = result

        return list(seen_ids.values())

    @staticmethod
    def rank_by_confidence(results: List[InterventionResult]) -> List[InterventionResult]:
        """Sort results by confidence score (descending)."""
        return sorted(results, key=lambda x: x.confidence, reverse=True)

    @staticmethod
    def apply_boost(results: List[InterventionResult], query: str) -> List[InterventionResult]:
        """Apply boost to results based on query matching."""
        query_lower = query.lower()

        for result in results:
            boost = 0.0

            # Boost for exact problem type match
            if result.intervention.problem.lower() in query_lower:
                boost += 0.1

            # Boost for category match
            if result.intervention.category.lower() in query_lower:
                boost += 0.05

            # Boost for type match
            if result.intervention.type.lower() in query_lower:
                boost += 0.05

            # Boost for high priority
            if result.intervention.priority == "Critical":
                boost += 0.05
            elif result.intervention.priority == "High":
                boost += 0.03

            # Apply boost
            result.confidence = min(result.confidence + boost, 1.0)
            result.relevance_score = result.confidence

        return results
