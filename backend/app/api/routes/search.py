"""Search API routes."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import logging
from ...models.schemas import SearchRequest, SearchResponse
from ...core.orchestrator import QueryOrchestrator
from ..middleware.auth import verify_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])

# Dependency injection will be set up in main.py
orchestrator_dependency = None


def get_orchestrator() -> QueryOrchestrator:
    """Get orchestrator instance."""
    if orchestrator_dependency is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    return orchestrator_dependency


@router.post("", response_model=SearchResponse)
async def search_interventions(
    request: SearchRequest,
    api_key: Annotated[str, Depends(verify_api_key)],
    orchestrator: Annotated[QueryOrchestrator, Depends(get_orchestrator)],
):
    """
    Search for road safety interventions.

    Args:
        request: Search request with query and optional filters
        api_key: API key for authentication
        orchestrator: Query orchestrator instance

    Returns:
        SearchResponse with ranked interventions and AI synthesis
    """
    try:
        logger.info(f"Search request: {request.query}")

        response = await orchestrator.process_query(request)

        logger.info(f"Search completed: {response.metadata.total_results} results")
        return response

    except Exception as e:
        logger.error(f"Error processing search: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing search: {str(e)}")
