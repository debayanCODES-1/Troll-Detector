from __future__ import annotations

import re
from .ai import AIClient, AIServiceError, parse_json_object


class FallacyClassifier:
    """Classify comments through the configured external AI service."""

    def __init__(self, client: AIClient | None = None) -> None:
        self.client = client or AIClient()

    def predict(self, text: str, threshold: float | None = None) -> tuple[bool, float]:
        del threshold
        prompt = (
            "Analyze this comment for a personal attack or toxic fallacy. "
            "Return only JSON with boolean `flagged` and number `confidence` from 0 to 1.\n"
            f"Comment: {text}"
        )
        try:
            result = parse_json_object(self.client.complete(prompt))
            confidence = min(1.0, max(0.0, float(result["confidence"])))
            flagged = result["flagged"]
            if isinstance(flagged, str):
                flagged = flagged.strip().casefold() == "true"
            return bool(flagged), confidence
        except (AIServiceError, KeyError, TypeError, ValueError):
            pass

        attack = re.search(r"\b(you(?:'re| are)|he(?:'s| is)|she(?:'s| is))\s+(an?\s+)?(idiot|moron|stupid|dumb|loser)\b", text, re.I)
        return bool(attack), 0.9 if attack else 0.05
