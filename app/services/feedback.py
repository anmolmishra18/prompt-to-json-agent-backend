from typing import Dict, List

class FeedbackEngine:
    """Generates actionable feedback based on evaluator results.
    BHIV Core: exposes `run(input: dict) -> list[str]`
    """
    def run(self, evaluation: Dict, json_spec: Dict) -> List[str]:
        suggestions = []
        comments = evaluation.get("comments", "")
        if "Title" in comments and not json_spec.get("title"):
            suggestions.append("Add a short, descriptive title (≤ 80 chars).")
        if "Description" in comments and len(json_spec.get("description", "")) < 20:
            suggestions.append("Expand the description with goals, inputs, and outputs (≥ 20 chars).")
        if "priority" in comments.lower():
            suggestions.append("Set 'priority' to one of: high | medium | low.")
        if not suggestions:
            suggestions.append("Refine wording for clarity and add acceptance criteria if needed.")
        return suggestions
