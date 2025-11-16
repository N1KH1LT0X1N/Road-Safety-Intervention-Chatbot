"""Google Gemini API service."""
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import logging
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config import settings
from ..models.schemas import ExtractedEntities

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self):
        """Initialize Gemini service."""
        genai.configure(api_key=settings.gemini_api_key)

        self.flash_model = genai.GenerativeModel(settings.gemini_flash_model)
        self.pro_model = genai.GenerativeModel(settings.gemini_pro_model)

        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0

        logger.info("Gemini service initialized")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts using Gemini Embedding API."""
        try:
            embeddings = []

            # Process in batches of 20 (API limit)
            batch_size = 20
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]

                batch_embeddings = []
                for text in batch:
                    result = genai.embed_content(
                        model=f"models/{settings.gemini_embedding_model}",
                        content=text,
                        task_type="retrieval_document",
                    )
                    batch_embeddings.append(result["embedding"])

                embeddings.extend(batch_embeddings)

                logger.debug(f"Generated {len(batch_embeddings)} embeddings")

            logger.info(f"Generated {len(embeddings)} total embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        try:
            result = genai.embed_content(
                model=f"models/{settings.gemini_embedding_model}",
                content=query,
                task_type="retrieval_query",
            )

            return result["embedding"]

        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            raise

    async def extract_entities(self, query: str) -> ExtractedEntities:
        """Extract structured entities from query using Gemini Flash."""
        prompt = f"""You are an expert in road safety interventions. Analyze the following query and extract structured information.

Query: "{query}"

Extract the following information (return valid JSON only, no markdown):
{{
    "problems": ["list of problem types mentioned: Damaged, Faded, Missing, Spacing Issue, Height Issue, etc."],
    "category": "Road Sign, Road Marking, or Traffic Calming Measures (if mentioned)",
    "type": "specific type mentioned (e.g., STOP Sign, Speed Breaker, etc.)",
    "speed": "speed value in km/h as integer (null if not mentioned)",
    "road_type": "Highway, Urban, Rural, Arterial, etc. (if mentioned)",
    "environment": ["environmental factors: visibility, weather, obstruction, trees, etc."],
    "urgency": "Critical, High, Medium, or Low based on safety impact"
}}

Return only the JSON object, no additional text."""

        try:
            response = self.flash_model.generate_content(prompt)
            text = response.text.strip()

            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()

            # Parse JSON
            data = json.loads(text)

            # Track tokens
            if hasattr(response, "usage_metadata"):
                self.total_input_tokens += response.usage_metadata.prompt_token_count
                self.total_output_tokens += response.usage_metadata.candidates_token_count

            return ExtractedEntities(**data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {text}")
            logger.error(f"JSON error: {e}")
            # Return empty entities on parse failure
            return ExtractedEntities()
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return ExtractedEntities()

    async def synthesize_recommendation(
        self, query: str, interventions: List[Dict[str, Any]], entities: Optional[ExtractedEntities] = None
    ) -> str:
        """Generate comprehensive recommendation using Gemini Pro."""
        # Build context from interventions
        context_parts = []
        for idx, intervention in enumerate(interventions, 1):
            context_parts.append(f"""
Intervention {idx}:
- ID: {intervention.get('id')}
- Problem: {intervention.get('problem')}
- Category: {intervention.get('category')}
- Type: {intervention.get('type')}
- IRC Reference: {intervention.get('code')} {intervention.get('clause')}
- Details: {intervention.get('data', '')[:500]}...
""")

        context = "\n".join(context_parts)

        prompt = f"""You are a road safety engineer expert. Based on the following query and intervention database entries, provide a comprehensive recommendation.

User Query: "{query}"

Retrieved Interventions from IRC Standards Database:
{context}

Provide a detailed recommendation that includes:
1. **Primary Recommendation**: The most suitable intervention with confidence level
2. **Detailed Specifications**: Dimensions, colors, placement requirements
3. **Installation Guidelines**: Step-by-step implementation instructions
4. **IRC Citation**: Specific IRC code and clause references
5. **Maintenance Requirements**: Long-term maintenance schedule
6. **Safety Impact**: Expected safety improvements
7. **Alternative Options**: If applicable, mention other suitable interventions

Format your response in clear markdown with proper headings and bullet points.
Be specific, cite the IRC standards, and ensure all recommendations are traceable to the database.
"""

        try:
            response = self.pro_model.generate_content(prompt)
            synthesis = response.text

            # Track tokens
            if hasattr(response, "usage_metadata"):
                self.total_input_tokens += response.usage_metadata.prompt_token_count
                self.total_output_tokens += response.usage_metadata.candidates_token_count

            logger.info("Generated synthesis with Gemini Pro")
            return synthesis

        except Exception as e:
            logger.error(f"Error generating synthesis: {e}")
            return "Error generating detailed recommendation. Please try again."

    async def answer_followup(self, question: str, context: str) -> str:
        """Answer follow-up questions about interventions."""
        prompt = f"""Based on the following context about road safety interventions, answer the user's question concisely.

Context:
{context}

Question: {question}

Provide a clear, concise answer with specific details from the context."""

        try:
            response = self.flash_model.generate_content(prompt)
            answer = response.text

            # Track tokens
            if hasattr(response, "usage_metadata"):
                self.total_input_tokens += response.usage_metadata.prompt_token_count
                self.total_output_tokens += response.usage_metadata.candidates_token_count

            return answer

        except Exception as e:
            logger.error(f"Error answering follow-up: {e}")
            return "I'm unable to answer that question at the moment."

    def get_token_usage(self) -> Dict[str, int]:
        """Get total token usage."""
        return {"input": self.total_input_tokens, "output": self.total_output_tokens}

    def reset_token_counter(self):
        """Reset token counters."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
