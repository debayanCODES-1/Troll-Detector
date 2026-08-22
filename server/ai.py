from __future__ import annotations

import json
import os
import time
from typing import Any

import httpx


class AIServiceError(RuntimeError):
    pass


class AIClient:
    """Small OpenAI-compatible client kept behind the local server."""

    def __init__(self) -> None:
        self.api_key = os.environ.get("AI_API_KEY", "").strip()
        self.api_url = os.environ.get("AI_API_URL", "https://api.groq.com/openai/v1/chat/completions").strip()
        self.model = os.environ.get("AI_MODEL", "llama-3.1-8b-instant").strip()
        self.timeout = float(os.environ.get("AI_TIMEOUT_SECONDS", "12"))

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.api_url and self.model)

    def complete(self, prompt: str) -> str:
        if not self.configured:
            raise AIServiceError("AI_API_KEY is not configured")

        payload = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 180,
            "messages": [
                {"role": "system", "content": "You are a concise, safety-focused comment moderator."},
                {"role": "user", "content": prompt},
            ],
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                response = httpx.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                if not isinstance(content, str) or not content.strip():
                    raise AIServiceError("AI response did not contain text")
                return content.strip()
            except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, AIServiceError) as error:
                last_error = error
                if attempt == 0:
                    time.sleep(0.15)
        raise AIServiceError("AI request failed") from last_error


def parse_json_object(content: str) -> dict[str, Any]:
    """Accept plain JSON and the fenced JSON commonly returned by chat APIs."""
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").removeprefix("json").strip()
    value = json.loads(cleaned)
    if not isinstance(value, dict):
        raise ValueError("AI response was not a JSON object")
    return value