"""Service for comparing multiple interventions side-by-side."""
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ComparisonService:
    """Compare and analyze multiple interventions."""

    def __init__(self):
        """Initialize comparison service."""
        logger.info("Comparison service initialized")

    def compare_interventions(self, interventions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create detailed comparison of interventions."""
        try:
            if len(interventions) < 2:
                return {"error": "Need at least 2 interventions to compare"}

            comparison = {
                "interventions_compared": len(interventions),
                "comparison_matrix": self._create_comparison_matrix(interventions),
                "winner_analysis": self._analyze_winner(interventions),
                "trade_offs": self._analyze_tradeoffs(interventions),
                "recommendations": self._generate_comparison_recommendations(interventions),
            }

            logger.info(f"Compared {len(interventions)} interventions")
            return comparison

        except Exception as e:
            logger.error(f"Error comparing interventions: {e}")
            return {"error": str(e)}

    def _create_comparison_matrix(self, interventions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create side-by-side comparison matrix."""
        matrix = []

        # Define comparison attributes
        attributes = [
            ("Title", "title"),
            ("Category", "category"),
            ("Problem", "problem"),
            ("Confidence", "confidence"),
            ("Cost", "cost_estimate"),
            ("Time", "installation_time"),
            ("IRC Code", lambda i: i.get("irc_reference", {}).get("code", "N/A")),
            ("Priority", lambda i: self._estimate_priority(i)),
        ]

        for attr_name, attr_key in attributes:
            row = {"attribute": attr_name, "values": []}

            for intervention in interventions:
                if callable(attr_key):
                    value = attr_key(intervention)
                else:
                    value = intervention.get(attr_key, "N/A")

                # Format specific types
                if attr_name == "Confidence" and isinstance(value, (int, float)):
                    value = f"{value * 100:.0f}%"

                row["values"].append(str(value))

            matrix.append(row)

        return matrix

    def _estimate_priority(self, intervention: Dict[str, Any]) -> str:
        """Estimate priority level for intervention."""
        problem = intervention.get("problem", "").lower()
        confidence = intervention.get("confidence", 0)

        if any(keyword in problem for keyword in ["damaged", "missing", "critical"]):
            return "High"
        elif any(keyword in problem for keyword in ["faded", "visibility"]):
            return "Medium"
        else:
            return "Low"

    def _analyze_winner(self, interventions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze which intervention is the best choice."""
        # Score each intervention on multiple factors
        scored = []

        for intervention in interventions:
            scores = {
                "confidence": intervention.get("confidence", 0) * 100,
                "cost_efficiency": self._calculate_cost_efficiency(intervention),
                "time_efficiency": self._calculate_time_efficiency(intervention),
                "priority": self._get_priority_score(intervention),
            }

            # Overall score (weighted average)
            overall = (
                scores["confidence"] * 0.3
                + scores["cost_efficiency"] * 0.2
                + scores["time_efficiency"] * 0.2
                + scores["priority"] * 0.3
            )

            scored.append(
                {
                    "intervention": intervention.get("title", "Unknown"),
                    "overall_score": overall,
                    "breakdown": scores,
                }
            )

        # Find winner
        winner = max(scored, key=lambda x: x["overall_score"])

        return {"winner": winner, "all_scores": scored}

    def _calculate_cost_efficiency(self, intervention: Dict[str, Any]) -> float:
        """Calculate cost efficiency score (0-100)."""
        cost_text = intervention.get("cost_estimate", "Medium")

        if "Low" in cost_text:
            return 90
        elif "Medium" in cost_text:
            return 60
        elif "High" in cost_text:
            return 30
        else:
            return 50

    def _calculate_time_efficiency(self, intervention: Dict[str, Any]) -> float:
        """Calculate time efficiency score (0-100)."""
        time_text = intervention.get("installation_time", "Variable")

        if "hour" in time_text and not "day" in time_text:
            return 90
        elif "day" in time_text:
            if "1" in time_text:
                return 70
            else:
                return 40
        else:
            return 50

    def _get_priority_score(self, intervention: Dict[str, Any]) -> float:
        """Get priority score based on problem type."""
        problem = intervention.get("problem", "").lower()

        if any(keyword in problem for keyword in ["damaged", "missing", "critical"]):
            return 100
        elif any(keyword in problem for keyword in ["faded", "visibility", "obstruction"]):
            return 75
        elif any(keyword in problem for keyword in ["spacing", "placement"]):
            return 50
        else:
            return 30

    def _analyze_tradeoffs(self, interventions: List[Dict[str, Any]]) -> List[str]:
        """Analyze trade-offs between interventions."""
        tradeoffs = []

        # Find highest confidence vs lowest cost
        highest_conf = max(interventions, key=lambda x: x.get("confidence", 0))
        costs = [("Low", 1), ("Medium", 2), ("High", 3)]
        cost_map = {c: v for c, v in costs}

        lowest_cost = min(interventions, key=lambda x: cost_map.get(x.get("cost_estimate", "Medium").split("(")[0].strip(), 2))

        if highest_conf != lowest_cost:
            tradeoffs.append(
                f"⚖️ Trade-off: '{highest_conf.get('title')}' has highest confidence ({highest_conf.get('confidence', 0)*100:.0f}%) "
                f"but '{lowest_cost.get('title')}' is more cost-effective"
            )

        # Check implementation time vs urgency
        urgent_problems = ["damaged", "missing", "critical"]
        urgent_interventions = [
            i
            for i in interventions
            if any(keyword in i.get("problem", "").lower() for keyword in urgent_problems)
        ]

        if urgent_interventions:
            quick_ones = [i for i in urgent_interventions if "hour" in i.get("installation_time", "")]
            slow_ones = [i for i in urgent_interventions if "day" in i.get("installation_time", "")]

            if quick_ones and slow_ones:
                tradeoffs.append(
                    f"⏱️ Some urgent interventions can be completed in hours, others take days. "
                    f"Consider quick fixes first for immediate safety improvement"
                )

        return tradeoffs

    def _generate_comparison_recommendations(self, interventions: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on comparison."""
        recommendations = []

        # Check if multiple interventions address same issue
        problems = {}
        for intervention in interventions:
            problem = intervention.get("problem", "Unknown")
            if problem not in problems:
                problems[problem] = []
            problems[problem].append(intervention.get("title"))

        for problem, titles in problems.items():
            if len(titles) > 1:
                recommendations.append(
                    f"📋 Multiple interventions available for '{problem}' issue. "
                    f"Compare costs and implementation complexity."
                )

        # Check budget optimization
        total_categories = set(i.get("category", "") for i in interventions)
        if len(total_categories) > 1:
            recommendations.append(
                "🏗️ Interventions span multiple categories. Consider bundling similar types for efficiency."
            )

        # Confidence-based recommendation
        high_conf_interventions = [i for i in interventions if i.get("confidence", 0) > 0.8]
        if high_conf_interventions:
            recommendations.append(
                f"✨ {len(high_conf_interventions)} intervention(s) have high confidence (>80%). "
                f"These are strongly recommended."
            )

        return recommendations
