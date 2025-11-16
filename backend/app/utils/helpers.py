"""Helper utility functions."""
import time
import hashlib
from typing import Any, Dict
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def timer(func):
    """Decorator to time function execution."""

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = int((time.time() - start) * 1000)
        logger.debug(f"{func.__name__} took {elapsed}ms")
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = int((time.time() - start) * 1000)
        logger.debug(f"{func.__name__} took {elapsed}ms")
        return result

    import asyncio

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def generate_cache_key(query: str, filters: Dict[str, Any] = None) -> str:
    """Generate cache key from query and filters."""
    key_data = {"query": query.lower().strip()}

    if filters:
        key_data["filters"] = str(sorted(filters.items()))

    key_string = str(key_data)
    return hashlib.md5(key_string.encode()).hexdigest()


def estimate_cost(problem: str, category: str) -> str:
    """Estimate implementation cost based on problem and category."""
    cost_matrix = {
        ("Damaged", "Road Sign"): "Medium (₹2,000 - ₹5,000)",
        ("Faded", "Road Sign"): "Medium (₹2,500 - ₹4,000)",
        ("Missing", "Road Sign"): "Medium (₹3,000 - ₹6,000)",
        ("Damaged", "Road Marking"): "Low (₹500 - ₹2,000)",
        ("Faded", "Road Marking"): "Low (₹800 - ₹2,500)",
        ("Missing", "Road Marking"): "Medium (₹2,000 - ₹4,000)",
        ("Damaged", "Traffic Calming Measures"): "High (₹10,000 - ₹25,000)",
        ("Missing", "Traffic Calming Measures"): "High (₹15,000 - ₹30,000)",
    }

    # Default estimates by category
    category_defaults = {
        "Road Sign": "Medium (₹2,000 - ₹5,000)",
        "Road Marking": "Low (₹1,000 - ₹3,000)",
        "Traffic Calming Measures": "High (₹12,000 - ₹28,000)",
    }

    return cost_matrix.get((problem, category), category_defaults.get(category, "Medium"))


def estimate_installation_time(category: str, problem: str) -> str:
    """Estimate installation time."""
    time_matrix = {
        "Road Sign": "2-4 hours",
        "Road Marking": "4-8 hours",
        "Traffic Calming Measures": "1-3 days",
    }

    return time_matrix.get(category, "Variable")


def extract_maintenance_info(data: str) -> str:
    """Extract maintenance information from intervention data."""
    # Look for maintenance-related keywords
    maintenance_keywords = [
        "replace",
        "maintain",
        "inspect",
        "warranty",
        "reflectivity",
        "year",
        "month",
    ]

    sentences = data.split(".")
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in maintenance_keywords):
            # Found a maintenance-related sentence
            return sentence.strip()

    # Default maintenance schedules
    return "Inspect annually and replace when deteriorated"


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_irc_reference(code: str, clause: str) -> str:
    """Format IRC reference string."""
    if code and clause:
        return f"{code}, Clause {clause}"
    elif code:
        return code
    return "N/A"
