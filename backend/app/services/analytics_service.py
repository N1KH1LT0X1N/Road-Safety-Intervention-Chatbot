"""Analytics service for dashboard insights and trends."""
from typing import List, Dict, Any
from collections import Counter
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Provide analytics and insights on interventions."""

    def __init__(self, database_service):
        """Initialize analytics service."""
        self.database = database_service
        self.search_history = []
        logger.info("Analytics service initialized")

    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Get comprehensive dashboard analytics."""
        try:
            interventions = self.database.get_all()

            analytics = {
                "overview": self._get_overview_stats(interventions),
                "category_breakdown": self._get_category_breakdown(interventions),
                "problem_distribution": self._get_problem_distribution(interventions),
                "priority_analysis": self._get_priority_analysis(interventions),
                "cost_analysis": self._get_cost_analysis(interventions),
                "irc_standards": self._get_irc_standards_stats(interventions),
                "insights": self._generate_insights(interventions),
            }

            logger.info("Generated dashboard analytics")
            return analytics

        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            return {"error": str(e)}

    def _get_overview_stats(self, interventions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get overview statistics."""
        return {
            "total_interventions": len(interventions),
            "total_searches_today": len([s for s in self.search_history if self._is_today(s.get("timestamp"))]),
            "unique_categories": len(set(i.get("category", "") for i in interventions)),
            "unique_problems": len(set(i.get("problem", "") for i in interventions)),
            "unique_irc_codes": len(set(i.get("code", "") for i in interventions if i.get("code"))),
        }

    def _get_category_breakdown(self, interventions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get breakdown by category."""
        categories = Counter(i.get("category", "Unknown") for i in interventions)

        total = sum(categories.values())

        return {
            "categories": [
                {
                    "name": cat,
                    "count": count,
                    "percentage": round((count / total) * 100, 1) if total > 0 else 0,
                }
                for cat, count in categories.most_common()
            ],
            "total": total,
        }

    def _get_problem_distribution(self, interventions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get problem type distribution."""
        problems = Counter(i.get("problem", "Unknown") for i in interventions)

        return {
            "problems": [{"name": prob, "count": count} for prob, count in problems.most_common(10)],
            "top_problem": problems.most_common(1)[0] if problems else ("None", 0),
        }

    def _get_priority_analysis(self, interventions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze intervention priorities."""
        # Estimate priorities based on problem types
        priority_map = {
            "Critical": ["damaged", "missing", "critical"],
            "High": ["faded", "visibility", "obstruction"],
            "Medium": ["spacing", "placement", "height"],
            "Low": ["non-standard", "wrongly"],
        }

        priority_counts = Counter()

        for intervention in interventions:
            problem = intervention.get("problem", "").lower()

            assigned = False
            for priority, keywords in priority_map.items():
                if any(keyword in problem for keyword in keywords):
                    priority_counts[priority] += 1
                    assigned = True
                    break

            if not assigned:
                priority_counts["Medium"] += 1

        return {
            "distribution": [{"level": level, "count": count} for level, count in priority_counts.most_common()],
            "critical_count": priority_counts.get("Critical", 0),
            "high_count": priority_counts.get("High", 0),
        }

    def _get_cost_analysis(self, interventions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cost distribution."""
        # Cost categories from existing data
        cost_categories = {
            "Road Sign": {"Low": 0, "Medium": 0, "High": 0},
            "Road Marking": {"Low": 0, "Medium": 0, "High": 0},
            "Traffic Calming Measures": {"Low": 0, "Medium": 0, "High": 0},
        }

        # Estimate costs based on category and problem
        for intervention in interventions:
            category = intervention.get("category", "Unknown")
            problem = intervention.get("problem", "")

            if category in cost_categories:
                # Simple heuristic
                if "Traffic Calming" in category:
                    cost_categories[category]["High"] += 1
                elif any(p in problem for p in ["Damaged", "Missing"]):
                    cost_categories[category]["Medium"] += 1
                else:
                    cost_categories[category]["Low"] += 1

        return {
            "by_category": cost_categories,
            "estimated_total_low": "₹50,000 - ₹200,000",
            "estimated_total_medium": "₹200,000 - ₹500,000",
            "estimated_total_high": "₹500,000 - ₹2,000,000",
        }

    def _get_irc_standards_stats(self, interventions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get IRC standards statistics."""
        irc_codes = Counter(i.get("code", "Unknown") for i in interventions if i.get("code"))

        return {
            "standards": [{"code": code, "interventions": count} for code, count in irc_codes.most_common()],
            "most_referenced": irc_codes.most_common(1)[0] if irc_codes else ("None", 0),
        }

    def _generate_insights(self, interventions: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable insights."""
        insights = []

        # Category insights
        categories = Counter(i.get("category", "") for i in interventions)
        top_category = categories.most_common(1)[0] if categories else None

        if top_category:
            insights.append(
                f"📊 {top_category[0]} represents {(top_category[1]/len(interventions)*100):.0f}% "
                f"of interventions in the database"
            )

        # Problem insights
        problems = Counter(i.get("problem", "") for i in interventions)
        critical_problems = ["Damaged", "Missing", "Faded"]
        critical_count = sum(problems.get(p, 0) for p in critical_problems)

        if critical_count > len(interventions) * 0.5:
            insights.append(
                f"⚠️ Over 50% of interventions address critical issues (damaged/missing/faded). "
                f"Regular maintenance could prevent these."
            )

        # IRC standards insights
        irc_codes = set(i.get("code", "") for i in interventions if i.get("code"))
        if len(irc_codes) > 1:
            insights.append(
                f"📚 Database covers {len(irc_codes)} different IRC standards, "
                f"providing comprehensive guidance"
            )

        # Speed-related insights
        speed_interventions = [
            i for i in interventions if i.get("speed_min") is not None or i.get("speed_max") is not None
        ]

        if speed_interventions:
            insights.append(
                f"🚗 {len(speed_interventions)} interventions include speed-specific requirements, "
                f"ensuring appropriate solutions for different road types"
            )

        return insights

    def track_search(self, query: str, results_count: int, search_strategy: str):
        """Track search for analytics."""
        self.search_history.append(
            {"query": query, "results_count": results_count, "strategy": search_strategy, "timestamp": datetime.now()}
        )

        # Keep only last 1000 searches
        if len(self.search_history) > 1000:
            self.search_history = self.search_history[-1000:]

    def get_search_analytics(self) -> Dict[str, Any]:
        """Get search analytics."""
        if not self.search_history:
            return {"message": "No search history available"}

        recent = self.search_history[-100:]

        # Most common queries
        queries = Counter(s["query"] for s in recent)

        # Strategy distribution
        strategies = Counter(s["strategy"] for s in recent)

        # Average results
        avg_results = sum(s["results_count"] for s in recent) / len(recent) if recent else 0

        return {
            "total_searches": len(self.search_history),
            "recent_searches": len(recent),
            "popular_queries": [{"query": q, "count": c} for q, c in queries.most_common(5)],
            "strategy_distribution": dict(strategies),
            "average_results": round(avg_results, 1),
        }

    def _is_today(self, timestamp) -> bool:
        """Check if timestamp is today."""
        if not timestamp:
            return False

        return timestamp.date() == datetime.now().date()
