from server.ai import AIClient
from server.inference import FallacyClassifier


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_classifier_parses_external_ai_response(monkeypatch):
    monkeypatch.setenv("AI_API_KEY", "test-key")
    client = AIClient()

    def fake_post(*args, **kwargs):
        return FakeResponse({"choices": [{"message": {"content": '{"flagged": "false", "confidence": 0.2}'}}]})

    monkeypatch.setattr("httpx.post", fake_post)
    assert FallacyClassifier(client).predict("I disagree with the evidence") == (False, 0.2)


def test_classifier_falls_back_when_api_is_not_configured(monkeypatch):
    monkeypatch.delenv("AI_API_KEY", raising=False)
    flagged, confidence = FallacyClassifier(AIClient()).predict("You are an idiot")
    assert (flagged, confidence) == (True, 0.9)
