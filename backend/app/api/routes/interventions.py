"""Interventions API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated, List, Optional
import logging
from ...models.intervention import Intervention
from ...services.database import DatabaseService
from ..middleware.auth import verify_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interventions", tags=["interventions"])

# Dependency injection
database_dependency = None


def get_database() -> DatabaseService:
    """Get database instance."""
    if database_dependency is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return database_dependency


@router.get("", response_model=List[Intervention])
async def list_interventions(
    api_key: Annotated[str, Depends(verify_api_key)],
    database: Annotated[DatabaseService, Depends(get_database)],
    category: Optional[str] = Query(None, description="Filter by category"),
    problem: Optional[str] = Query(None, description="Filter by problem type"),
    limit: int = Query(20, description="Maximum results", ge=1, le=100),
):
    """
    List interventions with optional filters.

    Args:
        category: Filter by category
        problem: Filter by problem type
        limit: Maximum number of results

    Returns:
        List of interventions
    """
    try:
        filters = {}
        if category:
            filters["category"] = [category]
        if problem:
            filters["problem"] = [problem]

        results = database.search_by_filters(**filters, limit=limit)

        interventions = [Intervention(**r) for r in results]

        logger.info(f"Listed {len(interventions)} interventions")
        return interventions

    except Exception as e:
        logger.error(f"Error listing interventions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{intervention_id}", response_model=Intervention)
async def get_intervention(
    intervention_id: str,
    api_key: Annotated[str, Depends(verify_api_key)],
    database: Annotated[DatabaseService, Depends(get_database)],
):
    """
    Get specific intervention by ID.

    Args:
        intervention_id: Intervention ID

    Returns:
        Intervention details
    """
    try:
        result = database.get_by_id(intervention_id)

        if not result:
            raise HTTPException(status_code=404, detail="Intervention not found")

        intervention = Intervention(**result)

        logger.info(f"Retrieved intervention: {intervention_id}")
        return intervention

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting intervention: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/list", response_model=List[str])
async def list_categories(
    api_key: Annotated[str, Depends(verify_api_key)], database: Annotated[DatabaseService, Depends(get_database)]
):
    """Get list of all categories."""
    try:
        categories = database.get_categories()
        return categories
    except Exception as e:
        logger.error(f"Error listing categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/problems/list", response_model=List[str])
async def list_problems(
    api_key: Annotated[str, Depends(verify_api_key)], database: Annotated[DatabaseService, Depends(get_database)]
):
    """Get list of all problem types."""
    try:
        problems = database.get_problems()
        return problems
    except Exception as e:
        logger.error(f"Error listing problems: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/standards/list", response_model=List[str])
async def list_standards(
    api_key: Annotated[str, Depends(verify_api_key)], database: Annotated[DatabaseService, Depends(get_database)]
):
    """Get list of all IRC standards."""
    try:
        standards = database.get_irc_codes()
        return standards
    except Exception as e:
        logger.error(f"Error listing standards: {e}")
        raise HTTPException(status_code=500, detail=str(e))
