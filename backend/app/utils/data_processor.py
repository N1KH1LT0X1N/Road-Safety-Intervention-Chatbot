"""Data processing utilities for cleaning and enriching intervention data."""
import pandas as pd
import re
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and enrich road safety intervention data."""

    PRIORITY_KEYWORDS = {
        "Critical": ["crash prone", "accident", "pedestrian crossing", "school"],
        "High": ["damaged", "missing", "faded", "visibility", "obstruction"],
        "Medium": ["spacing", "placement", "height", "non-standard"],
        "Low": ["wrongly placed", "non-retroreflective"],
    }

    COLORS = ["red", "white", "yellow", "black", "blue", "green", "orange"]

    def __init__(self, csv_path: Path):
        """Initialize data processor."""
        self.csv_path = csv_path
        self.df: Optional[pd.DataFrame] = None
        self.issues: List[str] = []

    def load_csv(self) -> pd.DataFrame:
        """Load CSV with multiple encoding attempts."""
        encodings = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]

        for encoding in encodings:
            try:
                df = pd.read_csv(self.csv_path, encoding=encoding)
                logger.info(f"Successfully loaded CSV with {encoding} encoding")
                self.df = df
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"Error loading CSV with {encoding}: {e}")
                continue

        raise ValueError("Could not load CSV with any supported encoding")

    def clean_data(self) -> pd.DataFrame:
        """Clean and validate data."""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_csv() first")

        df = self.df.copy()

        # Standardize column names
        df.columns = df.columns.str.strip()

        # Remove completely empty rows
        df = df.dropna(how="all")

        # Trim whitespace from all string columns
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str).str.strip()

        # Handle missing values
        df["problem"] = df["problem"].fillna("Unknown")
        df["category"] = df["category"].fillna("Unknown")
        df["type"] = df["type"].fillna("Unknown")
        df["data"] = df["data"].fillna("")
        df["code"] = df["code"].fillna("")
        df["clause"] = df["clause"].fillna("")

        # Remove rows with invalid data
        initial_count = len(df)
        df = df[df["data"].str.len() > 10]  # Data should have meaningful content
        removed = initial_count - len(df)

        if removed > 0:
            self.issues.append(f"Removed {removed} rows with insufficient data")

        # Fix malformed rows (merge multi-line entries)
        df = self._fix_multiline_entries(df)

        self.df = df
        logger.info(f"Cleaned data: {len(df)} rows")
        return df

    def _fix_multiline_entries(self, df: pd.DataFrame) -> pd.DataFrame:
        """Attempt to fix malformed multi-line CSV entries."""
        # This is a simple heuristic: if 'problem' or 'category' looks like continuation text,
        # it might be a broken row. For now, we'll keep valid rows only.

        valid_categories = ["Road Sign", "Road Marking", "Traffic Calming Measures"]
        df = df[df["category"].isin(valid_categories)]

        return df

    def extract_speed_range(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract speed range from text."""
        # Patterns: "50 km/h", "51-65 km/h", "up to 50 km/h", "over 65 km/h"
        patterns = [
            r"(\d+)\s*-\s*(\d+)\s*km[/h]",  # 51-65 km/h
            r"up\s+to\s+(\d+)\s*km[/h]",  # up to 50 km/h
            r"over\s+(\d+)\s*km[/h]",  # over 65 km/h
            r"(\d+)\s*km[/h]",  # 50 km/h
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    return int(match.group(1)), int(match.group(2))
                elif "up to" in pattern:
                    return 0, int(match.group(1))
                elif "over" in pattern:
                    return int(match.group(1)), 200  # Max speed assumption
                else:
                    speed = int(match.group(1))
                    return speed, speed

        return None, None

    def extract_dimensions(self, text: str) -> List[str]:
        """Extract dimensions from text."""
        # Patterns: "900 mm", "1.5 m", "600mm x 800mm"
        pattern = r"\d+\.?\d*\s*(?:mm|m|km|cm)(?:\s*x\s*\d+\.?\d*\s*(?:mm|m|km|cm))?"
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches[:5]  # Limit to 5 dimensions

    def extract_colors(self, text: str) -> List[str]:
        """Extract colors from text."""
        found_colors = []
        text_lower = text.lower()

        for color in self.COLORS:
            if color in text_lower:
                found_colors.append(color)

        return list(set(found_colors))  # Remove duplicates

    def extract_placement_distances(self, text: str) -> List[str]:
        """Extract placement distances."""
        # Patterns: "45m from", "1.5 m from", "5-6 m away"
        pattern = r"\d+\.?\d*\s*-?\s*\d*\.?\d*\s*[km]?\s*(?:m|meters?)\s+(?:from|away|ahead|before)"
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches[:3]

    def assign_priority(self, row: pd.Series) -> str:
        """Assign priority based on problem and content."""
        text = f"{row['problem']} {row['type']} {row['data']}".lower()

        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return priority

        return "Medium"  # Default

    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        # Remove common words and extract meaningful terms
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "be",
            "shall",
        }

        words = re.findall(r"\b[a-z]{4,}\b", text.lower())
        keywords = [w for w in words if w not in stop_words]

        # Count frequency and return top keywords
        from collections import Counter

        counter = Counter(keywords)
        return [word for word, _ in counter.most_common(10)]

    def create_search_text(self, row: pd.Series) -> str:
        """Create concatenated searchable text."""
        parts = [
            f"Problem: {row['problem']}",
            f"Category: {row['category']}",
            f"Type: {row['type']}",
            f"Details: {row['data']}",
            f"Standard: {row['code']} {row['clause']}",
        ]
        return " ".join(parts)

    def enrich_data(self) -> pd.DataFrame:
        """Enrich data with extracted features."""
        if self.df is None:
            raise ValueError("Data not loaded and cleaned")

        df = self.df.copy()

        # Generate unique IDs
        df["id"] = df.apply(
            lambda row: f"{row['category'][:2].upper()}{row['problem'][:2].upper()}_{row.name + 1:03d}",
            axis=1,
        )

        # Extract speed ranges
        speed_ranges = df["data"].apply(self.extract_speed_range)
        df["speed_min"] = speed_ranges.apply(lambda x: x[0])
        df["speed_max"] = speed_ranges.apply(lambda x: x[1])

        # Extract other features
        df["dimensions"] = df["data"].apply(self.extract_dimensions)
        df["colors"] = df["data"].apply(self.extract_colors)
        df["placement_distances"] = df["data"].apply(self.extract_placement_distances)

        # Assign priority
        df["priority"] = df.apply(self.assign_priority, axis=1)

        # Extract keywords
        df["keywords"] = df["data"].apply(self.extract_keywords)

        # Create search text
        df["search_text"] = df.apply(self.create_search_text, axis=1)

        self.df = df
        logger.info(f"Enriched data with {len(df.columns)} columns")
        return df

    def save_processed_data(self, output_dir: Path) -> Dict[str, Path]:
        """Save processed data in multiple formats."""
        if self.df is None:
            raise ValueError("No data to save")

        output_dir.mkdir(parents=True, exist_ok=True)
        saved_files = {}

        # Save as JSON
        json_path = output_dir / "interventions.json"
        records = self.df.to_dict(orient="records")

        # Convert lists to JSON-serializable format
        for record in records:
            for key, value in record.items():
                if isinstance(value, list):
                    record[key] = value
                elif pd.isna(value):
                    record[key] = None

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        saved_files["json"] = json_path
        logger.info(f"Saved JSON to {json_path}")

        # Save as cleaned CSV
        csv_path = output_dir / "interventions_cleaned.csv"
        self.df.to_csv(csv_path, index=False, encoding="utf-8")
        saved_files["csv"] = csv_path
        logger.info(f"Saved CSV to {csv_path}")

        # Save data quality report
        report_path = output_dir / "data_quality_report.txt"
        self._save_quality_report(report_path)
        saved_files["report"] = report_path

        return saved_files

    def _save_quality_report(self, report_path: Path):
        """Save data quality report."""
        if self.df is None:
            return

        report = []
        report.append("=" * 60)
        report.append("DATA QUALITY REPORT")
        report.append("=" * 60)
        report.append("")

        report.append(f"Total Records: {len(self.df)}")
        report.append(f"Total Columns: {len(self.df.columns)}")
        report.append("")

        report.append("Categories:")
        for cat, count in self.df["category"].value_counts().items():
            report.append(f"  - {cat}: {count}")
        report.append("")

        report.append("Problem Types:")
        for prob, count in self.df["problem"].value_counts().items():
            report.append(f"  - {prob}: {count}")
        report.append("")

        report.append("IRC Standards:")
        for code in self.df["code"].unique():
            if code:
                report.append(f"  - {code}")
        report.append("")

        if self.issues:
            report.append("Issues Found and Fixed:")
            for issue in self.issues:
                report.append(f"  - {issue}")
        else:
            report.append("No issues found during processing")

        report.append("")
        report.append("=" * 60)

        with open(report_path, "w") as f:
            f.write("\n".join(report))

        logger.info(f"Saved quality report to {report_path}")

    def process(self) -> pd.DataFrame:
        """Run complete processing pipeline."""
        logger.info("Starting data processing pipeline...")

        self.load_csv()
        self.clean_data()
        self.enrich_data()

        logger.info("Data processing complete!")
        return self.df
