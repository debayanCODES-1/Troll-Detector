from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .explain import LocalExplainer
from .inference import FallacyClassifier

ROOT = Path(__file__).resolve().parents[1]
BLOCKLIST_PATH = ROOT / "config" / "blocklist.json"
MODEL_PATH = ROOT / "models" / "fallacy_classifier.onnx"
TOKENIZER_PATH = ROOT / "models" / "tokenizer"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("civildialog")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_DIR / "requests.log", encoding="utf-8")
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)

app = FastAPI(title="CivilDialog Local Inference", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"chrome-extension://[a-zA-Z0-9]+$",
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
classifier = FallacyClassifier(MODEL_PATH, TOKENIZER_PATH)
explainer = LocalExplainer()


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)


class FallacyResponse(BaseModel):
    flagged: bool
    confidence: float


def _log(endpoint: str, elapsed: float, flagged: bool | None = None) -> None:
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "endpoint": endpoint, "latency_ms": round(elapsed * 1000, 2)}
    if flagged is not None:
        entry["flagged"] = flagged
    logger.info(json.dumps(entry))


def _terms() -> list[str]:
    try:
        return [str(term).casefold() for term in json.loads(BLOCKLIST_PATH.read_text(encoding="utf-8")).get("terms", [])]
    except (OSError, json.JSONDecodeError):
        return []


def _matches(text: str) -> list[str]:
    return [term for term in _terms() if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.I)]


@app.middleware("http")
async def request_logging(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    _log(request.url.path, time.perf_counter() - started, getattr(request.state, "flagged", None))
    return response


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "civildialog-local",
        "classifier": "onnx" if classifier.session else "development-fallback",
        "explainer": "onnx-configured" if explainer.configured else "unavailable-until-model-installed",
    }


@app.post("/check/wordfilter")
def word_filter(request: Request, payload: TextRequest) -> dict[str, object]:
    matched = _matches(payload.text)
    request.state.flagged = bool(matched)
    return {"flagged": bool(matched), "matched_terms": matched}


@app.post("/check/fallacy", response_model=FallacyResponse)
def fallacy(request: Request, payload: TextRequest) -> FallacyResponse:
    flagged, confidence = classifier.predict(payload.text)
    request.state.flagged = flagged
    return FallacyResponse(flagged=flagged, confidence=round(confidence, 4))


@app.post("/explain")
def explain(payload: TextRequest) -> dict[str, str]:
    return explainer.explain(payload.text)
