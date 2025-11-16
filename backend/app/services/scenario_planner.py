"""Multi-intervention scenario planner and optimizer."""
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class ScenarioPlanner:
    """Plan and optimize multiple road safety interventions."""

    # Cost ranges (in rupees)
    COST_RANGES = {
        "Low": (500, 3000),
        "Medium": (3000, 10000),
        "High": (10000, 50000),
    }

    # Time ranges (in hours)
    TIME_RANGES = {"2-4 hours": 3, "4-8 hours": 6, "1-3 days": 48, "Variable": 24}

    # Priority weights
    PRIORITY_WEIGHTS = {"Critical": 100, "High": 75, "Medium": 50, "Low": 25}

    def __init__(self):
        """Initialize scenario planner."""
        logger.info("Scenario planner initialized")

    def create_implementation_plan(
        self,
        interventions: List[Dict[str, Any]],
        budget: Optional[float] = None,
        timeline_days: Optional[int] = None,
        priority_optimization: bool = True,
    ) -> Dict[str, Any]:
        """Create comprehensive implementation plan for multiple interventions."""
        try:
            # Calculate costs and priorities
            enriched_interventions = []

            for intervention in interventions:
                enriched = self._enrich_intervention(intervention)
                enriched_interventions.append(enriched)

            # Sort by priority if optimization is enabled
            if priority_optimization:
                enriched_interventions.sort(key=lambda x: x["priority_score"], reverse=True)

            # Apply budget constraints
            if budget:
                enriched_interventions = self._apply_budget_constraint(enriched_interventions, budget)

            # Create timeline
            timeline = self._create_timeline(enriched_interventions, timeline_days)

            # Calculate totals
            total_cost = sum(i["estimated_cost_avg"] for i in enriched_interventions)
            total_time_hours = sum(i["estimated_time_hours"] for i in enriched_interventions)

            # Generate plan
            plan = {
                "interventions": enriched_interventions,
                "timeline": timeline,
                "summary": {
                    "total_interventions": len(enriched_interventions),
                    "total_cost_estimate": f"₹{total_cost:,.0f}",
                    "total_time_estimate": f"{total_time_hours / 24:.1f} days ({total_time_hours:.0f} hours)",
                    "completion_date": (datetime.now() + timedelta(hours=total_time_hours)).strftime("%Y-%m-%d"),
                    "budget_compliant": total_cost <= budget if budget else True,
                },
                "recommendations": self._generate_recommendations(enriched_interventions, budget, timeline_days),
            }

            logger.info(f"Created implementation plan with {len(enriched_interventions)} interventions")
            return plan

        except Exception as e:
            logger.error(f"Error creating implementation plan: {e}")
            raise

    def _enrich_intervention(self, intervention: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich intervention with cost and time estimates."""
        enriched = intervention.copy()

        # Parse cost estimate
        cost_text = intervention.get("cost_estimate", "Medium")
        cost_min, cost_max = self._parse_cost(cost_text)
        cost_avg = (cost_min + cost_max) / 2

        enriched["estimated_cost_min"] = cost_min
        enriched["estimated_cost_max"] = cost_max
        enriched["estimated_cost_avg"] = cost_avg

        # Parse time estimate
        time_text = intervention.get("installation_time", "Variable")
        time_hours = self._parse_time(time_text)

        enriched["estimated_time_hours"] = time_hours

        # Calculate priority score
        problem = intervention.get("problem", "")
        category = intervention.get("category", "")
        confidence = intervention.get("confidence", 0.5)

        priority_score = self._calculate_priority_score(problem, category, confidence)
        enriched["priority_score"] = priority_score
        enriched["priority_level"] = self._get_priority_level(priority_score)

        return enriched

    def _parse_cost(self, cost_text: str) -> tuple:
        """Parse cost estimate text."""
        # Try to extract numbers from text
        numbers = re.findall(r"₹?([\d,]+)", cost_text)

        if len(numbers) >= 2:
            # Found min and max
            cost_min = float(numbers[0].replace(",", ""))
            cost_max = float(numbers[1].replace(",", ""))
            return (cost_min, cost_max)
        elif "Low" in cost_text:
            return self.COST_RANGES["Low"]
        elif "High" in cost_text:
            return self.COST_RANGES["High"]
        else:
            return self.COST_RANGES["Medium"]

    def _parse_time(self, time_text: str) -> float:
        """Parse time estimate text to hours."""
        for pattern, hours in self.TIME_RANGES.items():
            if pattern in time_text:
                return hours

        # Try to extract numbers
        if "hour" in time_text.lower():
            numbers = re.findall(r"(\d+)", time_text)
            if numbers:
                return float(numbers[0])

        if "day" in time_text.lower():
            numbers = re.findall(r"(\d+)", time_text)
            if numbers:
                return float(numbers[0]) * 24

        return 24  # Default: 1 day

    def _calculate_priority_score(self, problem: str, category: str, confidence: float) -> float:
        """Calculate priority score for intervention."""
        # Base score from problem type
        problem_weight = 50

        if any(keyword in problem.lower() for keyword in ["damaged", "missing", "critical"]):
            problem_weight = 100
        elif any(keyword in problem.lower() for keyword in ["faded", "visibility", "obstruction"]):
            problem_weight = 75
        elif any(keyword in problem.lower() for keyword in ["spacing", "placement", "height"]):
            problem_weight = 50
        else:
            problem_weight = 30

        # Category multiplier
        category_multiplier = 1.0
        if "Traffic Calming" in category:
            category_multiplier = 1.2
        elif "Road Sign" in category:
            category_multiplier = 1.1
        elif "Road Marking" in category:
            category_multiplier = 1.0

        # Confidence factor
        confidence_factor = confidence

        # Final score
        score = problem_weight * category_multiplier * confidence_factor

        return min(100, score)  # Cap at 100

    def _get_priority_level(self, score: float) -> str:
        """Get priority level from score."""
        if score >= 80:
            return "Critical"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        else:
            return "Low"

    def _apply_budget_constraint(self, interventions: List[Dict[str, Any]], budget: float) -> List[Dict[str, Any]]:
        """Filter interventions to fit within budget."""
        selected = []
        running_cost = 0

        for intervention in interventions:
            cost = intervention["estimated_cost_avg"]

            if running_cost + cost <= budget:
                selected.append(intervention)
                running_cost += cost
            else:
                # Try to fit within remaining budget
                if running_cost + intervention["estimated_cost_min"] <= budget:
                    selected.append(intervention)
                    running_cost += intervention["estimated_cost_min"]

        logger.info(f"Selected {len(selected)}/{len(interventions)} interventions within budget")
        return selected

    def _create_timeline(
        self, interventions: List[Dict[str, Any]], timeline_days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Create implementation timeline."""
        timeline = []
        current_date = datetime.now()

        for idx, intervention in enumerate(interventions, 1):
            task = {
                "sequence": idx,
                "intervention": intervention["title"],
                "priority": intervention["priority_level"],
                "start_date": current_date.strftime("%Y-%m-%d"),
                "duration_hours": intervention["estimated_time_hours"],
                "duration_days": intervention["estimated_time_hours"] / 24,
                "cost": f"₹{intervention['estimated_cost_avg']:,.0f}",
                "end_date": (current_date + timedelta(hours=intervention["estimated_time_hours"])).strftime(
                    "%Y-%m-%d"
                ),
            }

            timeline.append(task)

            # Move to next start date
            current_date += timedelta(hours=intervention["estimated_time_hours"])

        return timeline

    def _generate_recommendations(
        self, interventions: List[Dict[str, Any]], budget: Optional[float], timeline_days: Optional[int]
    ) -> List[str]:
        """Generate recommendations based on plan."""
        recommendations = []

        # Priority-based recommendations
        critical_count = sum(1 for i in interventions if i["priority_level"] == "Critical")
        high_count = sum(1 for i in interventions if i["priority_level"] == "High")

        if critical_count > 0:
            recommendations.append(
                f"⚠️ {critical_count} critical intervention(s) identified. Prioritize these for immediate implementation."
            )

        if high_count > 0:
            recommendations.append(f"🔴 {high_count} high-priority intervention(s) should be addressed soon.")

        # Budget recommendations
        total_cost = sum(i["estimated_cost_avg"] for i in interventions)

        if budget and total_cost > budget * 1.2:
            recommendations.append(
                f"💰 Consider phased implementation. Current plan exceeds budget. Focus on critical items first."
            )

        # Timeline recommendations
        total_days = sum(i["estimated_time_hours"] for i in interventions) / 24

        if total_days > 30:
            recommendations.append("📅 Implementation will take over 30 days. Consider parallel execution where possible.")

        # Efficiency recommendations
        sign_interventions = [i for i in interventions if "Road Sign" in i["category"]]
        marking_interventions = [i for i in interventions if "Road Marking" in i["category"]]

        if len(sign_interventions) > 2:
            recommendations.append("🚦 Multiple road signs need intervention. Consider bulk procurement for cost savings.")

        if len(marking_interventions) > 2:
            recommendations.append("🛣️ Multiple road markings identified. Schedule together to minimize road closures.")

        return recommendations

    def optimize_budget_allocation(
        self, interventions: List[Dict[str, Any]], budget: float
    ) -> Dict[str, Any]:
        """Optimize intervention selection for maximum impact within budget."""
        try:
            # Enrich all interventions
            enriched = [self._enrich_intervention(i) for i in interventions]

            # Calculate value/cost ratio (priority score per rupee)
            for intervention in enriched:
                intervention["value_ratio"] = intervention["priority_score"] / intervention["estimated_cost_avg"]

            # Sort by value ratio
            enriched.sort(key=lambda x: x["value_ratio"], reverse=True)

            # Greedy selection
            selected = []
            remaining_budget = budget

            for intervention in enriched:
                if intervention["estimated_cost_avg"] <= remaining_budget:
                    selected.append(intervention)
                    remaining_budget -= intervention["estimated_cost_avg"]

            return {
                "selected_interventions": selected,
                "total_cost": budget - remaining_budget,
                "budget_utilized": f"{((budget - remaining_budget) / budget * 100):.1f}%",
                "total_priority_score": sum(i["priority_score"] for i in selected),
                "optimized": True,
            }

        except Exception as e:
            logger.error(f"Error optimizing budget: {e}")
            return {"error": str(e), "optimized": False}
