"""Output formatters for CLI."""
from typing import Dict, Any


def format_confidence(confidence: float) -> str:
    """Format confidence score with stars."""
    percentage = f"{confidence * 100:.0f}%"

    if confidence >= 0.8:
        stars = "⭐⭐⭐⭐⭐"
    elif confidence >= 0.6:
        stars = "⭐⭐⭐⭐"
    elif confidence >= 0.4:
        stars = "⭐⭐⭐"
    else:
        stars = "⭐⭐"

    return f"{stars} {percentage}"


def format_result(result: Dict[str, Any], idx: int) -> str:
    """Format result as markdown."""
    md = f"## {idx}. {result['title']}\n\n"
    md += f"**Confidence:** {format_confidence(result['confidence'])}\n\n"
    md += f"**Category:** {result['category']}\n"
    md += f"**Problem:** {result['problem']}\n"
    md += f"**Type:** {result['type']}\n\n"
    md += f"**IRC Reference:** {result['irc_reference']['code']} {result['irc_reference']['clause']}\n\n"
    md += f"**Cost Estimate:** {result['cost_estimate']}\n"

    if result.get("installation_time"):
        md += f"**Installation Time:** {result['installation_time']}\n"

    md += f"\n**Explanation:**\n{result['explanation']}\n"

    return md
