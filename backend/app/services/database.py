"""Database service for structured queries."""
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for structured database queries."""

    def __init__(self, data_path: Path):
        """Initialize database service."""
        self.data_path = data_path
        self.df: Optional[pd.DataFrame] = None
        self.interventions_dict: Dict[str, Dict[str, Any]] = {}

        self._load_data()

    def _load_data(self):
        """Load data from JSON file."""
        try:
            if self.data_path.suffix == ".json":
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.df = pd.DataFrame(data)

                # Create dictionary for fast ID lookup
                for item in data:
                    self.interventions_dict[item["id"]] = item

                logger.info(f"Loaded {len(self.df)} interventions from database")

            else:
                raise ValueError("Database file must be JSON format")

        except Exception as e:
            logger.error(f"Error loading database: {e}")
            self.df = pd.DataFrame()

    def search_by_filters(
        self,
        category: Optional[List[str]] = None,
        problem: Optional[List[str]] = None,
        speed_min: Optional[int] = None,
        speed_max: Optional[int] = None,
        irc_code: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search interventions by filters."""
        if self.df is None or len(self.df) == 0:
            return []

        # Start with all data
        result_df = self.df.copy()

        # Apply filters
        if category:
            result_df = result_df[result_df["category"].isin(category)]

        if problem:
            result_df = result_df[result_df["problem"].isin(problem)]

        if irc_code:
            result_df = result_df[result_df["code"] == irc_code]

        if speed_min is not None and speed_max is not None:
            # Filter by speed range overlap
            result_df = result_df[
                (
                    (result_df["speed_min"].notna())
                    & (result_df["speed_max"].notna())
                    & (result_df["speed_min"] <= speed_max)
                    & (result_df["speed_max"] >= speed_min)
                )
                | (result_df["speed_min"].isna())  # Include entries without speed info
            ]

        # Convert to list of dicts
        results = result_df.head(limit).to_dict(orient="records")

        logger.debug(f"Found {len(results)} results with filters")
        return results

    def get_by_id(self, intervention_id: str) -> Optional[Dict[str, Any]]:
        """Get intervention by ID."""
        return self.interventions_dict.get(intervention_id)

    def get_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all interventions."""
        if self.df is None:
            return []

        df = self.df if limit is None else self.df.head(limit)
        return df.to_dict(orient="records")

    def get_categories(self) -> List[str]:
        """Get unique categories."""
        if self.df is None:
            return []
        return self.df["category"].unique().tolist()

    def get_problems(self) -> List[str]:
        """Get unique problem types."""
        if self.df is None:
            return []
        return self.df["problem"].unique().tolist()

    def get_irc_codes(self) -> List[str]:
        """Get unique IRC codes."""
        if self.df is None:
            return []
        return self.df["code"].unique().tolist()

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if self.df is None:
            return {}

        return {
            "total_interventions": len(self.df),
            "categories": self.df["category"].value_counts().to_dict(),
            "problems": self.df["problem"].value_counts().to_dict(),
            "irc_standards": self.get_irc_codes(),
        }

    def text_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Simple text search across all fields."""
        if self.df is None:
            return []

        query_lower = query.lower()

        # Search in search_text field if available, otherwise combine fields
        if "search_text" in self.df.columns:
            mask = self.df["search_text"].str.lower().str.contains(query_lower, na=False)
        else:
            # Search across multiple columns
            mask = (
                self.df["problem"].str.lower().str.contains(query_lower, na=False)
                | self.df["category"].str.lower().str.contains(query_lower, na=False)
                | self.df["type"].str.lower().str.contains(query_lower, na=False)
                | self.df["data"].str.lower().str.contains(query_lower, na=False)
            )

        results = self.df[mask].head(limit).to_dict(orient="records")

        logger.debug(f"Text search found {len(results)} results")
        return results
