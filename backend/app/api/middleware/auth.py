"""API key authentication middleware."""
from fastapi import Header, HTTPException, status
from ...config import settings
import logging

logger = logging.getLogger(__name__)


async def verify_api_key(x_api_key: str = Header(..., description="API Key")):
    """Verify API key from header."""
    valid_keys = settings.api_keys_list

    if x_api_key not in valid_keys:
        logger.warning(f"Invalid API key attempted: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key", headers={"WWW-Authenticate": "ApiKey"}
        )

    return x_api_key
