from typing import Dict, Tuple, List
from .prompt_agent import PromptAgent
from .evaluator import Evaluator
from .feedback import FeedbackEngine

class RLAgent:
    """Simple iterative improvement loop (not RLHF, but useful for demo).
    BHIV Core: exposes `run(input: dict) -> dict`
    """
    def __init__(self):
        self.generator = PromptAgent()
        self.evaluator = Evaluator()
        self.feedback = FeedbackEngine()

    def _apply_feedback(self, spec: Dict, suggestions: List[str]) -> Dict:
        improved = dict(spec)
        for s in suggestions:
            if s.startswith("Add a short") and not improved.get("title"):
                improved["title"] = (improved.get("description", "") or "Untitled")[:80]
            if s.startswith("Expand the description"):
                base = improved.get("description", "")
                if len(base) < 20:
                    improved["description"] = (base + " This spec includes goals, inputs, and expected outputs.").strip()
            if s.startswith("Set 'priority'"):
                improved["priority"] = improved.get("priority") or "medium"
        return improved

    def run(self, prompt: str, max_iters: int = 2):
        spec = self.generator.run(prompt)
        history = []
        for i in range(1, max_iters + 1):
            eval_before = self.evaluator.run(spec)
            suggestions = self.feedback.run(eval_before, spec)
            improved = self._apply_feedback(spec, suggestions)
            eval_after = self.evaluator.run(improved)
            history.append({
                "iteration_number": i,
                "before_json": spec,
                "after_json": improved,
                "score_before": eval_before["score"],
                "score_after": eval_after["score"],
                "feedback": "; ".join(suggestions),
            })
            spec = improved
        return history
