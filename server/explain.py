from __future__ import annotations

from .ai import AIClient, AIServiceError, parse_json_object


class LocalExplainer:
    """Generate explanations through the configured external AI service."""

    def __init__(self, client: AIClient | None = None) -> None:
        self.client = client or AIClient()

    @property
    def configured(self) -> bool:
        return self.client.configured

    def explain(self, text: str) -> dict[str, str]:
        try:
            prompt = (
                "Explain briefly whether this comment attacks a person rather than an argument. "
                "Return only JSON with string fields `explanation` and `suggested_rewrite`.\n"
                "Comment: " + text
            )
            result = parse_json_object(self.client.complete(prompt))
            explanation = str(result["explanation"]).strip()
            rewrite = str(result["suggested_rewrite"]).strip()
            if not explanation or not rewrite:
                raise ValueError("AI response was missing explanation fields")
            return {"explanation": explanation, "suggested_rewrite": rewrite}
        except (AIServiceError, KeyError, TypeError, ValueError):
            return {
                "explanation": "The AI service is unavailable, so this comment could not be analyzed.",
                "suggested_rewrite": "Please rephrase this to address the claim rather than the person.",
            }
