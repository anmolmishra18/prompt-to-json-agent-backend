import re
from typing import Dict, Union

class PromptAgent:
    """Simple heuristic agent to convert free-text prompt to a JSON spec.

    BHIV Core compatibility: exposes a `run(input: str) -> dict` method.
    """
    PRIORITY_WORDS = {
        "high": "high",
        "urgent": "high",
        "critical": "high",
        "medium": "medium",
        "normal": "medium",
        "low": "low",
        "minor": "low",
    }

    def _extract_field(self, text: str, key: str) -> Union[str, None]:
        pattern = rf"{key}\s*[:=-]\s*(.+?)(?:;|\n|$)"
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1).strip()
        return None

    def _infer_priority(self, text: str) -> str:
        # look for explicit priority
        p = self._extract_field(text, "priority")
        if p:
            p = p.lower().strip()
            return "high" if "high" in p else "medium" if "med" in p else "low" if "low" in p else "medium"
        # infer from words
        for word, level in self.PRIORITY_WORDS.items():
            if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
                return level
        return "medium"

    def run(self, prompt: str) -> Dict:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        title = self._extract_field(prompt, "title")
        desc = self._extract_field(prompt, "description")

        if not title and not desc:
            # Best effort: use the whole prompt as title/description
            title = prompt.strip()[:80]
            desc = prompt.strip()

        if not title:
            # If only desc provided, make a short title
            title = desc.split(".")[0][:80]

        if not desc:
            desc = title

        priority = self._infer_priority(prompt)

        return {
            "title": title,
            "description": desc,
            "priority": priority,
        }
