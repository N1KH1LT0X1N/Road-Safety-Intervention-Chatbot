"""WOW Features API routes - Visual Generation, PDF Reports, Image Analysis."""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Response
from fastapi.responses import StreamingResponse
from typing import Annotated, List
import logging
import io
from ...models.schemas import SearchResponse
from ...services import VisualGenerator, PDFReportGenerator, ImageAnalyzer
from ..middleware.auth import verify_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wow", tags=["wow-features"])

# Service instances (will be injected)
visual_generator_dependency = None
pdf_generator_dependency = None
image_analyzer_dependency = None


def get_visual_generator() -> VisualGenerator:
    """Get visual generator instance."""
    if visual_generator_dependency is None:
        raise HTTPException(status_code=500, detail="Visual generator not initialized")
    return visual_generator_dependency


def get_pdf_generator() -> PDFReportGenerator:
    """Get PDF generator instance."""
    if pdf_generator_dependency is None:
        raise HTTPException(status_code=500, detail="PDF generator not initialized")
    return pdf_generator_dependency


def get_image_analyzer() -> ImageAnalyzer:
    """Get image analyzer instance."""
    if image_analyzer_dependency is None:
        raise HTTPException(status_code=500, detail="Image analyzer not initialized")
    return image_analyzer_dependency


@router.post("/generate-sign-visual")
async def generate_sign_visual(
    sign_type: str,
    shape: str,
    colors: List[str],
    dimensions: str,
    text: str = None,
    api_key: Annotated[str, Depends(verify_api_key)] = None,
    visual_gen: Annotated[VisualGenerator, Depends(get_visual_generator)] = None,
):
    """
    Generate visual representation of a road sign.

    Args:
        sign_type: Type of sign (e.g., "STOP Sign")
        shape: Shape (octagonal, circular, triangular, rectangular)
        colors: List of colors
        dimensions: Dimension specifications
        text: Optional text to display

    Returns:
        Base64 encoded image
    """
    try:
        image_base64 = visual_gen.generate_road_sign(
            sign_type=sign_type, shape=shape, colors=colors, dimensions=dimensions, text=text
        )

        return {"image": image_base64, "format": "base64", "success": True}

    except Exception as e:
        logger.error(f"Error generating sign visual: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-marking-visual")
async def generate_marking_visual(
    marking_type: str,
    colors: List[str],
    dimensions: str,
    api_key: Annotated[str, Depends(verify_api_key)] = None,
    visual_gen: Annotated[VisualGenerator, Depends(get_visual_generator)] = None,
):
    """
    Generate visual representation of a road marking.

    Args:
        marking_type: Type of marking (e.g., "Broken Line", "Arrow")
        colors: List of colors
        dimensions: Dimension specifications

    Returns:
        Base64 encoded image
    """
    try:
        image_base64 = visual_gen.generate_road_marking_diagram(
            marking_type=marking_type, colors=colors, dimensions=dimensions
        )

        return {"image": image_base64, "format": "base64", "success": True}

    except Exception as e:
        logger.error(f"Error generating marking visual: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-pdf-report", response_class=StreamingResponse)
async def generate_pdf_report(
    search_response: SearchResponse,
    api_key: Annotated[str, Depends(verify_api_key)] = None,
    pdf_gen: Annotated[PDFReportGenerator, Depends(get_pdf_generator)] = None,
):
    """
    Generate comprehensive PDF report from search results.

    Args:
        search_response: Complete search response object

    Returns:
        PDF file stream
    """
    try:
        # Convert response to dict format
        interventions = [result.dict() for result in search_response.results]

        pdf_bytes = pdf_gen.generate_intervention_report(
            query=search_response.query,
            interventions=interventions,
            synthesis=search_response.synthesis or "",
            metadata=search_response.metadata.dict(),
        )

        # Create streaming response
        pdf_stream = io.BytesIO(pdf_bytes)

        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="road_safety_report.pdf"'},
        )

    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    api_key: Annotated[str, Depends(verify_api_key)] = None,
    image_analyzer: Annotated[ImageAnalyzer, Depends(get_image_analyzer)] = None,
):
    """
    Analyze uploaded road sign/marking image using Gemini Vision.

    Args:
        file: Image file (JPEG, PNG, etc.)

    Returns:
        Detailed analysis of the image
    """
    try:
        # Read image data
        image_data = await file.read()

        # Analyze image
        analysis = await image_analyzer.analyze_road_sign_image(image_data)

        # Generate search query from analysis
        if analysis.get("image_processed"):
            suggested_query = await image_analyzer.generate_search_query_from_image(image_data)
            analysis["suggested_search_query"] = suggested_query

        return analysis

    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-to-query")
async def image_to_query(
    file: UploadFile = File(...),
    api_key: Annotated[str, Depends(verify_api_key)] = None,
    image_analyzer: Annotated[ImageAnalyzer, Depends(get_image_analyzer)] = None,
):
    """
    Convert uploaded image to search query.

    Args:
        file: Image file

    Returns:
        Generated search query
    """
    try:
        image_data = await file.read()

        query = await image_analyzer.generate_search_query_from_image(image_data)

        return {"query": query, "success": True}

    except Exception as e:
        logger.error(f"Error converting image to query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
