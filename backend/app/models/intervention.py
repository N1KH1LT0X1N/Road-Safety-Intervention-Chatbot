"""Intervention data model."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Intervention(BaseModel):
    """Intervention model."""

    id: str = Field(..., description="Unique intervention ID")
    s_no: int = Field(..., description="Serial number from CSV")
    problem: str = Field(..., description="Problem type")
    category: str = Field(..., description="Category (Road Sign, Road Marking, etc.)")
    type: str = Field(..., description="Specific type of intervention")
    data: str = Field(..., description="Detailed intervention data")
    code: str = Field(..., description="IRC code reference")
    clause: str = Field(..., description="IRC clause number")

    # Enriched fields
    speed_min: Optional[int] = Field(None, description="Minimum speed (km/h)")
    speed_max: Optional[int] = Field(None, description="Maximum speed (km/h)")
    dimensions: Optional[List[str]] = Field(default_factory=list, description="Extracted dimensions")
    colors: Optional[List[str]] = Field(default_factory=list, description="Extracted colors")
    placement_distances: Optional[List[str]] = Field(default_factory=list, description="Placement distances")
    priority: Optional[str] = Field(None, description="Priority level")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Extracted keywords")
    search_text: Optional[str] = Field(None, description="Concatenated searchable text")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "RS_001",
                "s_no": 1,
                "problem": "Damaged",
                "category": "Road Sign",
                "type": "STOP Sign",
                "data": "The 'STOP' sign, used on Minor Roads...",
                "code": "IRC:67-2022",
                "clause": "14.4",
                "speed_min": 0,
                "speed_max": 50,
                "colors": ["red", "white"],
                "priority": "High",
            }
        }


class InterventionResult(BaseModel):
    """Intervention search result with metadata."""

    intervention: Intervention
    confidence: float = Field(..., description="Confidence score (0.0-1.0)", ge=0.0, le=1.0)
    relevance_score: float = Field(..., description="Relevance score", ge=0.0)
    match_reason: Optional[str] = Field(None, description="Reason for match")

    class Config:
        json_schema_extra = {
            "example": {
                "intervention": {
                    "id": "RS_001",
                    "problem": "Damaged",
                    "category": "Road Sign",
                    "type": "STOP Sign",
                },
                "confidence": 0.95,
                "relevance_score": 0.89,
                "match_reason": "Exact problem match and category match",
            }
        }


class Specifications(BaseModel):
    """Detailed specifications extracted from intervention."""

    shape: Optional[str] = None
    dimensions: Optional[str] = None
    colors: Optional[List[str]] = None
    placement: Optional[str] = None
    materials: Optional[str] = None
    additional: Optional[Dict[str, Any]] = None


class IRCReference(BaseModel):
    """IRC standard reference."""

    code: str = Field(..., description="IRC code (e.g., IRC:67-2022)")
    clause: str = Field(..., description="Clause number")
    excerpt: Optional[str] = Field(None, description="Relevant excerpt from data")


class InterventionRecommendation(BaseModel):
    """Complete intervention recommendation."""

    id: str
    title: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    problem: str
    category: str
    type: str
    specifications: Specifications
    explanation: str
    irc_reference: IRCReference
    cost_estimate: str
    installation_time: Optional[str] = None
    maintenance: Optional[str] = None
    raw_data: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "RS_001",
                "title": "Replace STOP Sign with Retro-reflective Material",
                "confidence": 0.95,
                "problem": "Damaged",
                "category": "Road Sign",
                "type": "STOP Sign",
                "specifications": {
                    "shape": "Octagonal",
                    "dimensions": "900mm height, 30mm border",
                    "colors": ["red", "white"],
                    "placement": "1.5m from stop line",
                },
                "explanation": "The STOP sign should be replaced...",
                "irc_reference": {
                    "code": "IRC:67-2022",
                    "clause": "14.4",
                    "excerpt": "The 'STOP' sign, used on...",
                },
                "cost_estimate": "Medium (₹2,500 - ₹3,500)",
                "installation_time": "2-3 hours",
                "maintenance": "Replace when reflectivity < 80%",
            }
        }
