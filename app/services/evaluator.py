from typing import Dict

class Evaluator:
    """Heuristic evaluator that scores a JSON spec in [0, 1].
    BHIV Core: exposes `run(input: dict) -> dict` returning {'score': float, 'comments': str}
    """
    def run(self, json_spec: Dict) -> Dict:
        if not isinstance(json_spec, dict):
            raise ValueError("json_spec must be a dictionary")
        
        score = 0.0
        comments = []

        title = json_spec.get("title", "").strip()
        desc = json_spec.get("description", "").strip()
        priority = json_spec.get("priority", "").strip().lower()

        if title:
            score += 0.35
        else:
            comments.append("Add a concise Title.")

        # Description quality
        if len(desc) >= 20:
            score += 0.45
        elif desc:
            score += 0.25
            comments.append("Expand the Description to at least 20 characters for clarity.")
        else:
            comments.append("Provide a Description.")

        if priority in {"high", "medium", "low"}:
            score += 0.20
        else:
            comments.append("Set priority to one of: high|medium|low.")

        score = min(score, 1.0)
        if not comments:
            comments.append("Spec looks good.")

        return {"score": round(score, 2), "comments": " ".join(comments)}
