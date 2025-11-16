"""API client for backend communication."""
import requests
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

load_dotenv()


class APIClient:
    """Client for Road Safety API."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize API client."""
        self.base_url = base_url or os.getenv("API_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("API_KEY", "")
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

        # Add filters if provided
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

        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def get_intervention(self, intervention_id: str) -> Dict[str, Any]:
        """Get specific intervention by ID."""
        url = f"{self.base_url}/api/v1/interventions/{intervention_id}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def list_interventions(
        self, category: Optional[str] = None, problem: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List interventions with filters."""
        url = f"{self.base_url}/api/v1/interventions"

        params = {"limit": limit}
        if category:
            params["category"] = category
        if problem:
            params["problem"] = problem

        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def get_categories(self) -> List[str]:
        """Get list of categories."""
        url = f"{self.base_url}/api/v1/interventions/categories/list"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def get_problems(self) -> List[str]:
        """Get list of problem types."""
        url = f"{self.base_url}/api/v1/interventions/problems/list"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        url = f"{self.base_url}/stats"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        url = f"{self.base_url}/health"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()
