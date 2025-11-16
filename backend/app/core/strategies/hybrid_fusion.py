"""Hybrid search strategy combining RAG and structured queries."""
from typing import List, Dict, Any, Optional
import logging
from .base import BaseStrategy
from .rag_search import RAGSearchStrategy
from .structured_query import StructuredQueryStrategy
from ...models.intervention import InterventionResult

logger = logging.getLogger(__name__)


class HybridFusionStrategy(BaseStrategy):
    """Combine RAG and structured search with Reciprocal Rank Fusion."""

    def __init__(self, rag_strategy: RAGSearchStrategy, structured_strategy: StructuredQueryStrategy):
        """Initialize hybrid strategy."""
        self.rag_strategy = rag_strategy
        self.structured_strategy = structured_strategy
        self.k = 60  # RRF constant

    @property
    def name(self) -> str:
        return "hybrid"

    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, max_results: int = 10
    ) -> List[InterventionResult]:
        """Search using hybrid fusion of RAG and structured search."""
        try:
            # Run both strategies in parallel
            rag_results = await self.rag_strategy.search(query, filters, max_results=max_results * 2)
            structured_results = await self.structured_strategy.search(query, filters, max_results=max_results * 2)

            # Combine results using Reciprocal Rank Fusion
            fused_results = self._reciprocal_rank_fusion(rag_results, structured_results)

            # Limit to max_results
            fused_results = fused_results[:max_results]

            logger.info(f"Hybrid search found {len(fused_results)} results")
            return fused_results

        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []

    def _reciprocal_rank_fusion(
        self, rag_results: List[InterventionResult], structured_results: List[InterventionResult]
    ) -> List[InterventionResult]:
        """Combine results using Reciprocal Rank Fusion algorithm."""
        # Create score dictionary
        scores: Dict[str, float] = {}
        interventions: Dict[str, InterventionResult] = {}

        # Add RAG results
        for rank, result in enumerate(rag_results, 1):
            intervention_id = result.intervention.id
            rrf_score = 1.0 / (self.k + rank)

            if intervention_id in scores:
                scores[intervention_id] += rrf_score
            else:
                scores[intervention_id] = rrf_score
                interventions[intervention_id] = result

        # Add structured results
        for rank, result in enumerate(structured_results, 1):
            intervention_id = result.intervention.id
            rrf_score = 1.0 / (self.k + rank)

            if intervention_id in scores:
                scores[intervention_id] += rrf_score
            else:
                scores[intervention_id] = rrf_score
                interventions[intervention_id] = result

        # Sort by combined score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        # Build final results
        final_results = []
        for intervention_id in sorted_ids:
            result = interventions[intervention_id]

            # Update confidence with fused score
            # Normalize fused score to 0-1 range
            fused_score = scores[intervention_id]
            max_possible_score = (1.0 / (self.k + 1)) * 2  # Max from both strategies at rank 1
            normalized_score = min(fused_score / max_possible_score, 1.0)

            result.confidence = normalized_score
            result.relevance_score = normalized_score
            result.match_reason = f"Hybrid fusion (RRF score: {fused_score:.4f})"

            final_results.append(result)

        return final_results
