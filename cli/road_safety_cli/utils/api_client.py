"""API client for CLI."""
import requests
from typing import Dict, Any, Optional, List
from .config_manager import ConfigManager


class CLIAPIClient:
    """API client for CLI."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize client."""
        config = ConfigManager()

        self.base_url = base_url or config.get("api_url") or "http://localhost:8000"
        self.api_key = api_key or config.get("api_key") or ""
        self.headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    def search(
        self,
        query: str,
        category: Optional[List[str]] = None,
        problem: Optional[List[str]] = None,
        speed_min: Optional[int] = None,
        speed_max: Optional[int] = None,
        strategy: str = "auto",
        max_results: int = 5,
    ) -> Dict[str, Any]:
        """Search for interventions."""
        url = f"{self.base_url}/api/v1/search"

        payload = {"query": query, "strategy": strategy, "max_results": max_results}

        filters = {}
        if category:
            filters["category"] = category
        if problem:
            filters["problem"] = problem
        if speed_min is not None:
            filters["speed_min"] = speed_min
        if speed_max is not None:
            filters["speed_max"] = speed_max

        if filters:
            payload["filters"] = filters

        response = requests.post(url, json=payload, headers=self.headers, timeout=30)
        response.raise_for_status()

        return response.json()


def get_api_client() -> CLIAPIClient:
    """Get configured API client."""
    return CLIAPIClient()
