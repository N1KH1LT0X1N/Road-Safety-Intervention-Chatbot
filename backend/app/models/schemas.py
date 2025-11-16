"""API request and response schemas."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .intervention import InterventionRecommendation


class SearchFilters(BaseModel):
    """Search filter options."""

    category: Optional[List[str]] = Field(None, description="Filter by categories")
    problem: Optional[List[str]] = Field(None, description="Filter by problem types")
    speed_min: Optional[int] = Field(None, description="Minimum speed (km/h)")
    speed_max: Optional[int] = Field(None, description="Maximum speed (km/h)")
    irc_code: Optional[str] = Field(None, description="Filter by IRC code")


class SearchRequest(BaseModel):
    """Search request model."""

    query: str = Field(..., description="Search query", min_length=3)
    filters: Optional[SearchFilters] = Field(None, description="Optional filters")
    strategy: Optional[str] = Field(
        "auto", description="Search strategy: auto, rag, structured, hybrid"
    )
    max_results: Optional[int] = Field(5, description="Maximum results to return", ge=1, le=20)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Faded STOP sign on highway",
                "filters": {"category": ["Road Sign"], "speed_min": 50, "speed_max": 100},
                "strategy": "hybrid",
                "max_results": 5,
            }
        }


class ExtractedEntities(BaseModel):
    """Extracted entities from query."""

    problems: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    type: Optional[str] = None
    speed: Optional[int] = None
    road_type: Optional[str] = None
    environment: Optional[List[str]] = Field(default_factory=list)
    urgency: Optional[str] = None


class SearchMetadata(BaseModel):
    """Search metadata."""

    search_strategy: str
    total_results: int
    query_time_ms: int
    gemini_tokens: Optional[Dict[str, int]] = None
    entities_extracted: Optional[ExtractedEntities] = None


class SearchResponse(BaseModel):
    """Search response model."""

    query: str
    results: List[InterventionRecommendation]
    synthesis: Optional[str] = Field(None, description="AI-generated synthesis")
    metadata: SearchMetadata

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Faded STOP sign on highway",
                "results": [
                    {
                        "id": "RS_001",
                        "title": "Replace STOP Sign",
                        "confidence": 0.95,
                        "problem": "Faded",
                        "category": "Road Sign",
                    }
                ],
                "synthesis": "Based on your query...",
                "metadata": {
                    "search_strategy": "hybrid",
                    "total_results": 3,
                    "query_time_ms": 342,
                },
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    database: bool
    vector_store: bool


class StatsResponse(BaseModel):
    """Statistics response."""

    total_interventions: int
    categories: Dict[str, int]
    problems: Dict[str, int]
    irc_standards: List[str]


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: Optional[str] = None
    timestamp: str
