"""Advanced Features API routes - Scenario Planning, Comparison, Analytics."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated, List, Optional
import logging
from pydantic import BaseModel
from ...models.intervention import InterventionRecommendation
from ...services import ScenarioPlanner, ComparisonService, AnalyticsService
from ..middleware.auth import verify_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advanced", tags=["advanced-features"])

# Service instances (will be injected)
scenario_planner_dependency = None
comparison_service_dependency = None
analytics_service_dependency = None


def get_scenario_planner() -> ScenarioPlanner:
    """Get scenario planner instance."""
    if scenario_planner_dependency is None:
        raise HTTPException(status_code=500, detail="Scenario planner not initialized")
    return scenario_planner_dependency


def get_comparison_service() -> ComparisonService:
    """Get comparison service instance."""
    if comparison_service_dependency is None:
        raise HTTPException(status_code=500, detail="Comparison service not initialized")
    return comparison_service_dependency


def get_analytics_service() -> AnalyticsService:
    """Get analytics service instance."""
    if analytics_service_dependency is None:
        raise HTTPException(status_code=500, detail="Analytics service not initialized")
    return analytics_service_dependency


class ImplementationPlanRequest(BaseModel):
    """Request for creating implementation plan."""

    interventions: List[InterventionRecommendation]
    budget: Optional[float] = None
    timeline_days: Optional[int] = None
    priority_optimization: bool = True


class BudgetOptimizationRequest(BaseModel):
    """Request for budget optimization."""

    interventions: List[InterventionRecommendation]
    budget: float


class ComparisonRequest(BaseModel):
    """Request for intervention comparison."""

    interventions: List[InterventionRecommendation]


@router.post("/create-implementation-plan")
async def create_implementation_plan(
    request: ImplementationPlanRequest,
    api_key: Annotated[str, Depends(verify_api_key)] = None,
    planner: Annotated[ScenarioPlanner, Depends(get_scenario_planner)] = None,
):
    """
    Create comprehensive implementation plan for multiple interventions.

    Features:
    - Timeline generation with start/end dates
    - Cost calculations
    - Priority-based optimization
    - Budget constraint application
    - Implementation recommendations

    Args:
        request: Implementation plan request with interventions and constraints

    Returns:
        Detailed implementation plan
    """
    try:
        # Convert to dict format
        interventions_dict = [i.dict() for i in request.interventions]

        plan = planner.create_implementation_plan(
            interventions=interventions_dict,
            budget=request.budget,
            timeline_days=request.timeline_days,
            priority_optimization=request.priority_optimization,
        )

        logger.info(f"Created implementation plan with {len(plan['interventions'])} interventions")
        return plan

    except Exception as e:
        logger.error(f"Error creating implementation plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-budget")
async def optimize_budget(
    request: BudgetOptimizationRequest,
    api_key: Annotated[str, Depends(verify_api_key)] = None,
    planner: Annotated[ScenarioPlanner, Depends(get_scenario_planner)] = None,
):
    """
    Optimize intervention selection to maximize impact within budget.

    Uses value-cost ratio algorithm to select best interventions
    within budget constraints.

    Args:
        request: Budget optimization request

    Returns:
        Optimized intervention selection
    """
    try:
        interventions_dict = [i.dict() for i in request.interventions]

        result = planner.optimize_budget_allocation(interventions=interventions_dict, budget=request.budget)

        logger.info(f"Optimized budget allocation: {result.get('budget_utilized')}")
        return result

    except Exception as e:
        logger.error(f"Error optimizing budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-interventions")
async def compare_interventions(
    request: ComparisonRequest,
    api_key: Annotated[str, Depends(verify_api_key)] = None,
    comparison: Annotated[ComparisonService, Depends(get_comparison_service)] = None,
):
    """
    Compare multiple interventions side-by-side.

    Provides:
    - Comparison matrix
    - Winner analysis with scoring
    - Trade-off analysis
    - Recommendations

    Args:
        request: Comparison request with interventions

    Returns:
        Detailed comparison analysis
    """
    try:
        interventions_dict = [i.dict() for i in request.interventions]

        result = comparison.compare_interventions(interventions=interventions_dict)

        logger.info(f"Compared {len(interventions_dict)} interventions")
        return result

    except Exception as e:
        logger.error(f"Error comparing interventions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/dashboard")
async def get_dashboard_analytics(
    api_key: Annotated[str, Depends(verify_api_key)] = None,
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)] = None,
):
    """
    Get comprehensive dashboard analytics.

    Includes:
    - Overview statistics
    - Category breakdown
    - Problem distribution
    - Priority analysis
    - Cost analysis
    - IRC standards statistics
    - Actionable insights

    Returns:
        Dashboard analytics
    """
    try:
        result = analytics.get_dashboard_analytics()

        logger.info("Generated dashboard analytics")
        return result

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/search-history")
async def get_search_analytics(
    api_key: Annotated[str, Depends(verify_api_key)] = None,
    analytics: Annotated[AnalyticsService, Depends(get_analytics_service)] = None,
):
    """
    Get search history analytics.

    Includes:
    - Total searches
    - Popular queries
    - Strategy distribution
    - Average results

    Returns:
        Search analytics
    """
    try:
        result = analytics.get_search_analytics()

        return result

    except Exception as e:
        logger.error(f"Error getting search analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick-estimate")
async def quick_estimate(
    problem: str = Query(..., description="Problem type"),
    category: str = Query(..., description="Intervention category"),
    api_key: Annotated[str, Depends(verify_api_key)] = None,
):
    """
    Get quick cost and time estimate.

    Args:
        problem: Problem type (e.g., "Damaged", "Faded")
        category: Category (e.g., "Road Sign")

    Returns:
        Quick estimates
    """
    try:
        # Simple heuristic estimates
        cost_map = {
            "Road Sign": {"Damaged": "₹2,500 - ₹5,000", "Faded": "₹2,000 - ₹4,000", "Missing": "₹3,000 - ₹6,000"},
            "Road Marking": {"Damaged": "₹1,000 - ₹3,000", "Faded": "₹800 - ₹2,500", "Missing": "₹2,000 - ₹4,000"},
            "Traffic Calming Measures": {
                "Damaged": "₹12,000 - ₹28,000",
                "Missing": "₹15,000 - ₹30,000",
                "Non-Standard": "₹10,000 - ₹25,000",
            },
        }

        time_map = {
            "Road Sign": "2-4 hours",
            "Road Marking": "4-8 hours",
            "Traffic Calming Measures": "1-3 days",
        }

        cost = cost_map.get(category, {}).get(problem, "Medium (₹5,000 - ₹15,000)")
        time = time_map.get(category, "Variable")

        return {"problem": problem, "category": category, "estimated_cost": cost, "estimated_time": time}

    except Exception as e:
        logger.error(f"Error getting quick estimate: {e}")
        raise HTTPException(status_code=500, detail=str(e))
