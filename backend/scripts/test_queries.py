"""Test script with sample queries."""
import sys
import asyncio
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.app.config import settings
from backend.app.services import GeminiService, VectorStoreService, DatabaseService, CacheService
from backend.app.core.orchestrator import QueryOrchestrator
from backend.app.core.strategies import RAGSearchStrategy, StructuredQueryStrategy, HybridFusionStrategy
from backend.app.models.schemas import SearchRequest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_query(orchestrator: QueryOrchestrator, query: str):
    """Test a single query."""
    logger.info(f"\n{'=' * 60}")
    logger.info(f"Query: {query}")
    logger.info("=" * 60)

    request = SearchRequest(query=query, max_results=3)

    response = await orchestrator.process_query(request)

    logger.info(f"\nFound {response.metadata.total_results} results in {response.metadata.query_time_ms}ms")
    logger.info(f"Strategy: {response.metadata.search_strategy}")

    for idx, result in enumerate(response.results, 1):
        logger.info(f"\n{idx}. {result.title}")
        logger.info(f"   Confidence: {result.confidence:.2%}")
        logger.info(f"   Category: {result.category}")
        logger.info(f"   Problem: {result.problem}")
        logger.info(f"   IRC: {result.irc_reference.code} {result.irc_reference.clause}")

    logger.info(f"\n📝 AI Synthesis:")
    logger.info(response.synthesis[:500] + "..." if len(response.synthesis) > 500 else response.synthesis)


async def main():
    """Run test queries."""
    logger.info("Initializing services...")

    # Initialize services
    gemini_service = GeminiService()
    vector_store = VectorStoreService(
        persist_directory=str(settings.chroma_dir), collection_name=settings.collection_name
    )
    database = DatabaseService(data_path=settings.processed_data_dir / "interventions.json")
    cache = CacheService()

    # Initialize strategies
    rag_strategy = RAGSearchStrategy(vector_store=vector_store, gemini_service=gemini_service)
    structured_strategy = StructuredQueryStrategy(database=database)
    hybrid_strategy = HybridFusionStrategy(rag_strategy=rag_strategy, structured_strategy=structured_strategy)

    # Initialize orchestrator
    orchestrator = QueryOrchestrator(
        rag_strategy=rag_strategy,
        structured_strategy=structured_strategy,
        hybrid_strategy=hybrid_strategy,
        gemini_service=gemini_service,
        cache_service=cache,
    )

    # Test queries
    test_queries = [
        "Faded STOP sign on 65 kmph highway",
        "Missing road markings at pedestrian crossing",
        "Damaged speed breaker on urban road",
        "Obstruction blocking road sign visibility",
    ]

    for query in test_queries:
        await test_query(orchestrator, query)
        await asyncio.sleep(1)  # Brief pause between queries

    logger.info("\n✅ Test queries completed!")


if __name__ == "__main__":
    asyncio.run(main())
