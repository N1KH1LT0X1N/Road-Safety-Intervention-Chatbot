"""Main query orchestrator."""
from typing import List, Dict, Any, Optional
import time
import logging
from ..models.schemas import SearchRequest, SearchResponse, SearchMetadata, ExtractedEntities
from ..models.intervention import InterventionResult, InterventionRecommendation, Specifications, IRCReference
from ..services.gemini_service import GeminiService
from ..services.cache import CacheService
from ..utils.helpers import generate_cache_key, estimate_cost, estimate_installation_time, extract_maintenance_info
from .entity_extractor import EntityExtractor
from .ranker import ResultRanker
from .strategies import RAGSearchStrategy, StructuredQueryStrategy, HybridFusionStrategy

logger = logging.getLogger(__name__)


class QueryOrchestrator:
    """Orchestrate query processing through all strategies."""

    def __init__(
        self,
        rag_strategy: RAGSearchStrategy,
        structured_strategy: StructuredQueryStrategy,
        hybrid_strategy: HybridFusionStrategy,
        gemini_service: GeminiService,
        cache_service: CacheService,
    ):
        """Initialize orchestrator."""
        self.rag_strategy = rag_strategy
        self.structured_strategy = structured_strategy
        self.hybrid_strategy = hybrid_strategy
        self.gemini_service = gemini_service
        self.cache_service = cache_service
        self.entity_extractor = EntityExtractor(gemini_service)
        self.ranker = ResultRanker()

    async def process_query(self, request: SearchRequest) -> SearchResponse:
        """Process search query end-to-end."""
        start_time = time.time()

        try:
            # Check cache
            cache_key = generate_cache_key(request.query, request.filters.dict() if request.filters else None)
            cached_response = self.cache_service.get(cache_key)

            if cached_response:
                logger.info("Returning cached response")
                return cached_response

            # Extract entities
            entities = await self.entity_extractor.extract(request.query)
            logger.info(f"Extracted entities: {entities}")

            # Merge entities into filters if not provided
            filters = self._merge_filters(request.filters.dict() if request.filters else {}, entities)

            # Select strategy
            strategy = self._select_strategy(request.strategy)
            logger.info(f"Using strategy: {strategy.name}")

            # Execute search
            results = await strategy.search(query=request.query, filters=filters, max_results=request.max_results * 2)

            # Post-process results
            results = self.ranker.apply_boost(results, request.query)
            results = self.ranker.deduplicate(results)
            results = self.ranker.rank_by_confidence(results)
            results = results[: request.max_results]

            # Convert to recommendations
            recommendations = self._convert_to_recommendations(results)

            # Generate synthesis
            synthesis = await self._generate_synthesis(request.query, results, entities)

            # Build metadata
            query_time_ms = int((time.time() - start_time) * 1000)
            metadata = SearchMetadata(
                search_strategy=strategy.name,
                total_results=len(results),
                query_time_ms=query_time_ms,
                gemini_tokens=self.gemini_service.get_token_usage(),
                entities_extracted=entities,
            )

            # Build response
            response = SearchResponse(
                query=request.query, results=recommendations, synthesis=synthesis, metadata=metadata
            )

            # Cache response
            self.cache_service.set(cache_key, response)

            logger.info(f"Query processed in {query_time_ms}ms")
            return response

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise

    def _select_strategy(self, strategy_name: Optional[str] = None):
        """Select appropriate search strategy."""
        if strategy_name == "rag":
            return self.rag_strategy
        elif strategy_name == "structured":
            return self.structured_strategy
        elif strategy_name == "hybrid":
            return self.hybrid_strategy
        else:
            # Auto-select (default to hybrid)
            return self.hybrid_strategy

    def _merge_filters(self, filters: Dict[str, Any], entities: ExtractedEntities) -> Dict[str, Any]:
        """Merge extracted entities into filters."""
        # Add category from entities
        if entities.category and not filters.get("category"):
            filters["category"] = [entities.category]

        # Add problem types from entities
        if entities.problems and not filters.get("problem"):
            filters["problem"] = entities.problems

        # Add speed range from entities
        if entities.speed:
            if not filters.get("speed_min") and not filters.get("speed_max"):
                # Create a range around the speed
                filters["speed_min"] = max(0, entities.speed - 20)
                filters["speed_max"] = entities.speed + 20

        return filters

    def _convert_to_recommendations(self, results: List[InterventionResult]) -> List[InterventionRecommendation]:
        """Convert intervention results to detailed recommendations."""
        recommendations = []

        for result in results:
            intervention = result.intervention

            # Build specifications
            specs = Specifications(
                dimensions=", ".join(intervention.dimensions) if intervention.dimensions else None,
                colors=intervention.colors if intervention.colors else None,
                placement=", ".join(intervention.placement_distances) if intervention.placement_distances else None,
            )

            # Build IRC reference
            irc_ref = IRCReference(
                code=intervention.code, clause=intervention.clause, excerpt=intervention.data[:200] + "..."
            )

            # Create recommendation
            recommendation = InterventionRecommendation(
                id=intervention.id,
                title=f"{intervention.problem} - {intervention.type}",
                confidence=result.confidence,
                problem=intervention.problem,
                category=intervention.category,
                type=intervention.type,
                specifications=specs,
                explanation=result.match_reason or "Matched based on query relevance",
                irc_reference=irc_ref,
                cost_estimate=estimate_cost(intervention.problem, intervention.category),
                installation_time=estimate_installation_time(intervention.category, intervention.problem),
                maintenance=extract_maintenance_info(intervention.data),
                raw_data=intervention.data,
            )

            recommendations.append(recommendation)

        return recommendations

    async def _generate_synthesis(
        self, query: str, results: List[InterventionResult], entities: ExtractedEntities
    ) -> str:
        """Generate AI synthesis of results."""
        if not results:
            return "No interventions found matching your query. Please try rephrasing or broadening your search."

        # Convert results to dict format for Gemini
        interventions_data = [result.intervention.dict() for result in results[:3]]  # Top 3 for context

        # Generate synthesis
        synthesis = await self.gemini_service.synthesize_recommendation(query, interventions_data, entities)

        return synthesis
