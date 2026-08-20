from __future__ import annotations


class LocalExplainer:
    """Adapter point for a local Phi/Llama ONNX generator; never calls a cloud API."""

    def explain(self, text: str) -> dict[str, str]:
        return {
            "explanation": "The wording targets a person with an insult instead of addressing their argument.",
            "suggested_rewrite": "I disagree with that point because it does not account for the evidence.",
        }
