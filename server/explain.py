from __future__ import annotations

import os
from pathlib import Path


class LocalExplainer:
    """Generate explanations with a local Phi/Llama ONNX Runtime GenAI model."""

    def __init__(self, model_dir: Path | None = None) -> None:
        self.model_dir = model_dir or Path(os.environ.get("CIVILDIALOG_EXPLAINER_MODEL", "models/explainer"))
        nested = self.model_dir / "cpu_and_mobile" / "cpu-int4-awq-block-128-acc-level-4"
        if not (self.model_dir / "genai_config.json").exists() and (nested / "genai_config.json").exists():
            self.model_dir = nested
        self._model = None
        self._tokenizer = None

    @property
    def configured(self) -> bool:
        return (self.model_dir / "genai_config.json").exists() and any(self.model_dir.glob("*.onnx"))

    def _load(self) -> None:
        if self._model is not None:
            return
        import onnxruntime_genai as og

        if not self.model_dir.exists():
            raise FileNotFoundError(f"Local explanation model not found: {self.model_dir}")
        self._model = og.Model(str(self.model_dir))
        self._tokenizer = og.Tokenizer(self._model)

    def explain(self, text: str) -> dict[str, str]:
        try:
            self._load()
            import onnxruntime_genai as og

            prompt = (
                "Explain briefly why this comment may attack a person rather than an argument. "
                "Return exactly two lines starting with Explanation: and Rewrite:.\nComment: " + text
            )
            params = og.GeneratorParams(self._model)
            params.set_search_options(max_length=160, temperature=0.2, top_p=0.9)
            generator = og.Generator(self._model, params)
            generator.append_tokens(self._tokenizer.encode(prompt))
            while not generator.is_done():
                generator.generate_next_token()
            output = self._tokenizer.decode(generator.get_sequence(0))
            explanation, rewrite = "", ""
            for line in output.splitlines():
                if line.lower().startswith("explanation:"):
                    explanation = line.split(":", 1)[1].strip()
                elif line.lower().startswith("rewrite:"):
                    rewrite = line.split(":", 1)[1].strip()
            if not explanation or not rewrite:
                raise ValueError("Explanation model returned an unexpected format")
            return {"explanation": explanation, "suggested_rewrite": rewrite}
        except (FileNotFoundError, ImportError, RuntimeError, ValueError):
            return {
                "explanation": "The local explanation model is unavailable.",
                "suggested_rewrite": "Please rephrase this to address the claim rather than the person.",
            }
