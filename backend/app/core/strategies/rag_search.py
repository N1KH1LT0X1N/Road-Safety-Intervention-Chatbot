"""RAG (Retrieval-Augmented Generation) search strategy."""
from typing import List, Dict, Any, Optional
import logging
from .base import BaseStrategy
from ...models.intervention import InterventionResult, Intervention
from ...services.vector_store import VectorStoreService
from ...services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class RAGSearchStrategy(BaseStrategy):
    """Vector similarity search strategy using embeddings."""

    def __init__(self, vector_store: VectorStoreService, gemini_service: GeminiService):
        """Initialize RAG strategy."""
        self.vector_store = vector_store
        self.gemini_service = gemini_service

    @property
    def name(self) -> str:
        return "rag"

    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, max_results: int = 10
    ) -> List[InterventionResult]:
        """Search using vector similarity."""
        try:
            # Generate query embedding
            query_embedding = await self.gemini_service.embed_query(query)

            # Build where clause for metadata filtering
            where = None
            if filters:
                where = {}
                if filters.get("category"):
                    where["category"] = {"$in": filters["category"]}
                if filters.get("problem"):
                    where["problem"] = {"$in": filters["problem"]}

            # Search vector store
            results = self.vector_store.search(query_embedding=query_embedding, n_results=max_results, where=where)

            # Convert to InterventionResult objects
            intervention_results = []

            if results and results["ids"] and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    # Get metadata
                    metadata = results["metadatas"][0][i]

                    # Convert distance to similarity score (cosine distance: 0=identical, 2=opposite)
                    distance = results["distances"][0][i]
                    similarity = 1.0 - (distance / 2.0)  # Convert to 0-1 range

                    # Create Intervention object
                    intervention = Intervention(
                        id=metadata.get("id", ""),
                        s_no=metadata.get("s_no", 0),
                        problem=metadata.get("problem", ""),
                        category=metadata.get("category", ""),
                        type=metadata.get("type", ""),
                        data=metadata.get("data", ""),
                        code=metadata.get("code", ""),
                        clause=metadata.get("clause", ""),
                        speed_min=metadata.get("speed_min"),
                        speed_max=metadata.get("speed_max"),
                        dimensions=metadata.get("dimensions", []),
                        colors=metadata.get("colors", []),
                        placement_distances=metadata.get("placement_distances", []),
                        priority=metadata.get("priority"),
                        keywords=metadata.get("keywords", []),
                        search_text=metadata.get("search_text"),
                    )

                    intervention_results.append(
                        InterventionResult(
                            intervention=intervention,
                            confidence=similarity,
                            relevance_score=similarity,
                            match_reason=f"Vector similarity: {similarity:.2f}",
                        )
                    )

            logger.info(f"RAG search found {len(intervention_results)} results")
            return intervention_results

        except Exception as e:
            logger.error(f"Error in RAG search: {e}")
            return []
