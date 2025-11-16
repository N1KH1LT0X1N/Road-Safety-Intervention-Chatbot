"""Entity extraction from user queries."""
from ..services.gemini_service import GeminiService
from ..models.schemas import ExtractedEntities
import logging

logger = logging.getLogger(__name__)


class EntityExtractor:
    """Extract structured entities from natural language queries."""

    def __init__(self, gemini_service: GeminiService):
        """Initialize entity extractor."""
        self.gemini_service = gemini_service

    async def extract(self, query: str) -> ExtractedEntities:
        """Extract entities from query using Gemini."""
        return await self.gemini_service.extract_entities(query)
