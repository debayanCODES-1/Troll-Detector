from __future__ import annotations

import re
from pathlib import Path
import json


class FallacyClassifier:
    """ONNX classifier wrapper. A conservative heuristic keeps dev installs usable before training."""

    def __init__(self, model_path: Path | None = None, tokenizer_dir: Path | None = None) -> None:
        self.session = None
        self.tokenizer = None
        self.threshold = 0.75
        if model_path:
            try:
                self.threshold = float(json.loads((model_path.parent / "threshold.json").read_text(encoding="utf-8"))["positive_threshold"])
            except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
                pass
        if model_path and tokenizer_dir and model_path.exists() and tokenizer_dir.exists():
            try:
                import onnxruntime as ort
                from transformers import AutoTokenizer
                self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
                self.tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_dir))
            except Exception:
                self.session = None
                self.tokenizer = None

    def predict(self, text: str, threshold: float | None = None) -> tuple[bool, float]:
        threshold = self.threshold if threshold is None else threshold
        if self.session and self.tokenizer:
            import numpy as np
            encoded = self.tokenizer(text, return_tensors="np", truncation=True, padding="max_length", max_length=128)
            inputs = {name: encoded[name] for name in ("input_ids", "attention_mask") if name in encoded}
            logits = self.session.run(None, inputs)[0][0]
            probabilities = np.exp(logits - np.max(logits))
            confidence = float((probabilities / probabilities.sum())[1])
            return confidence >= threshold, confidence
        # Deliberately conservative development fallback; replace with the trained ONNX artifact.
        attack = re.search(r"\b(you(?:'re| are)|he(?:'s| is)|she(?:'s| is))\s+(an?\s+)?(idiot|moron|stupid|dumb|loser)\b", text, re.I)
        return bool(attack), 0.9 if attack else 0.05
