"""Image analysis service using Gemini Vision."""
import google.generativeai as genai
import base64
from PIL import Image
import io
from typing import Dict, Any, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Analyze road safety images using Gemini Vision."""

    def __init__(self):
        """Initialize image analyzer."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("Image analyzer initialized")

    async def analyze_road_sign_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze uploaded road sign/marking image."""
        try:
            # Open image
            img = Image.open(io.BytesIO(image_data))

            # Create analysis prompt
            prompt = """Analyze this road safety image and identify:

1. **Type**: What type of road sign or marking is this? (e.g., STOP sign, speed limit, road marking, etc.)
2. **Condition**: What is the current condition? (Damaged, Faded, Missing parts, Good condition, etc.)
3. **Problems**: List any visible safety issues or problems
4. **Colors**: What colors are present?
5. **Shape**: Describe the shape (circular, triangular, octagonal, rectangular, etc.)
6. **Text/Symbols**: What text or symbols are visible?
7. **Urgency**: How urgent is the need for intervention? (Critical/High/Medium/Low)
8. **Recommended Action**: What should be done to address any issues?

Return your analysis in a structured format."""

            # Generate analysis
            response = self.model.generate_content([prompt, img])

            # Parse response
            analysis_text = response.text

            # Extract structured data (basic parsing)
            analysis = {
                "raw_analysis": analysis_text,
                "detected_type": self._extract_field(analysis_text, "Type"),
                "condition": self._extract_field(analysis_text, "Condition"),
                "problems": self._extract_field(analysis_text, "Problems"),
                "colors": self._extract_field(analysis_text, "Colors"),
                "shape": self._extract_field(analysis_text, "Shape"),
                "text_symbols": self._extract_field(analysis_text, "Text/Symbols"),
                "urgency": self._extract_field(analysis_text, "Urgency"),
                "recommended_action": self._extract_field(analysis_text, "Recommended Action"),
                "image_processed": True,
            }

            logger.info("Image analyzed successfully")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                "error": str(e),
                "image_processed": False,
                "message": "Failed to analyze image. Please try again.",
            }

    async def generate_search_query_from_image(self, image_data: bytes) -> str:
        """Generate a search query based on analyzed image."""
        try:
            analysis = await self.analyze_road_sign_image(image_data)

            if not analysis.get("image_processed"):
                return "road safety issue"

            # Build query from analysis
            query_parts = []

            if analysis.get("condition"):
                query_parts.append(analysis["condition"])

            if analysis.get("detected_type"):
                query_parts.append(analysis["detected_type"])

            if not query_parts:
                return "road safety issue requiring intervention"

            query = " ".join(query_parts)
            logger.info(f"Generated query from image: {query}")

            return query

        except Exception as e:
            logger.error(f"Error generating query from image: {e}")
            return "road safety issue"

    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract field value from analysis text."""
        try:
            # Look for field in format "Field: value" or "**Field**: value"
            patterns = [f"{field_name}:", f"**{field_name}**:", f"{field_name.upper()}:"]

            for pattern in patterns:
                if pattern in text:
                    # Find the line containing this pattern
                    lines = text.split("\n")
                    for i, line in enumerate(lines):
                        if pattern in line:
                            # Extract value after the pattern
                            value = line.split(pattern, 1)[1].strip()
                            # Remove markdown symbols
                            value = value.replace("**", "").replace("*", "").strip()
                            # Take only first sentence/line
                            if "." in value:
                                value = value.split(".")[0].strip()
                            return value[:200]  # Limit length

            return "Not detected"

        except Exception as e:
            logger.debug(f"Could not extract field {field_name}: {e}")
            return "Not detected"

    async def compare_intervention_with_image(
        self, image_data: bytes, intervention_description: str
    ) -> Dict[str, Any]:
        """Compare an intervention description with actual image to verify match."""
        try:
            img = Image.open(io.BytesIO(image_data))

            prompt = f"""Compare the road safety element in this image with the following intervention description:

INTERVENTION: {intervention_description}

Analyze:
1. Does this image match the intervention type?
2. Would this intervention address the issues visible in the image?
3. What's the match confidence (0-100%)?
4. Any discrepancies or additional issues noticed?

Provide a concise assessment."""

            response = self.model.generate_content([prompt, img])

            return {"comparison": response.text, "success": True}

        except Exception as e:
            logger.error(f"Error comparing intervention with image: {e}")
            return {"error": str(e), "success": False}

    def encode_image_to_base64(self, image_data: bytes) -> str:
        """Encode image to base64 for frontend display."""
        return base64.b64encode(image_data).decode("utf-8")
