"""Health check and status routes."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import logging
from ...models.schemas import HealthResponse, StatsResponse
from ...services.database import DatabaseService
from ...services.vector_store import VectorStoreService
from ...config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

# Dependencies
database_dependency = None
vector_store_dependency = None


def get_database() -> DatabaseService:
    """Get database instance."""
    if database_dependency is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return database_dependency


def get_vector_store() -> VectorStoreService:
    """Get vector store instance."""
    if vector_store_dependency is None:
        raise HTTPException(status_code=500, detail="Vector store not initialized")
    return vector_store_dependency


@router.get("/health", response_model=HealthResponse)
async def health_check(
    database: Annotated[DatabaseService, Depends(get_database)],
    vector_store: Annotated[VectorStoreService, Depends(get_vector_store)],
):
    """
    Health check endpoint.

    Returns:
        Health status of all components
    """
    try:
        # Check database
        db_healthy = len(database.get_all(limit=1)) >= 0

        # Check vector store
        vs_healthy = vector_store.count() >= 0

        return HealthResponse(
            status="healthy" if (db_healthy and vs_healthy) else "degraded",
            version=settings.app_version,
            database=db_healthy,
            vector_store=vs_healthy,
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(status="unhealthy", version=settings.app_version, database=False, vector_store=False)


@router.get("/stats", response_model=StatsResponse)
async def get_stats(database: Annotated[DatabaseService, Depends(get_database)]):
    """
    Get database statistics.

    Returns:
        Statistics about interventions in database
    """
    try:
        stats = database.get_stats()

        return StatsResponse(**stats)

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
