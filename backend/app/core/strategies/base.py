"""Base strategy interface."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ...models.intervention import InterventionResult


class BaseStrategy(ABC):
    """Base class for search strategies."""

    @abstractmethod
    async def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, max_results: int = 10
    ) -> List[InterventionResult]:
        """Execute search and return results."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name."""
        pass
