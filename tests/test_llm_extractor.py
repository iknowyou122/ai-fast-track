from types import SimpleNamespace

import pytest

from app.config import config
from app.extractors.llm_extractor import LLMExtractor
from app.services.extraction_service import ExtractionService


def test_service_can_initialize_without_api_key(monkeypatch):
    monkeypatch.setattr(config, "OPENAI_API_KEY", None)
    monkeypatch.setattr(config, "GEMINI_API_KEY", None)

    service = ExtractionService()

    assert service.extractor is not None


def test_openai_provider_uses_openai_key(monkeypatch):
    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured["create_kwargs"] = kwargs
            return kwargs["response_model"](
                document_type="general",
                summary="ok",
                key_entities=["OpenAI"],
                action_items=["Ship feature"],
                deadlines=[],
                risks=[],
            )

    class FakeClient:
        def __init__(self):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    def fake_openai(**kwargs):
        captured["client_kwargs"] = kwargs
        return FakeClient()

    monkeypatch.setattr(config, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(config, "DEFAULT_MODEL", None)
    monkeypatch.setattr(config, "OPENAI_API_KEY", "openai-test-key")
    monkeypatch.setattr(config, "OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setattr("app.extractors.llm_extractor.OpenAI", fake_openai)
    monkeypatch.setattr("app.extractors.llm_extractor.instructor.patch", lambda client: client)

    extractor = LLMExtractor()
    result = extractor.extract("hello")

    assert captured["client_kwargs"] == {"api_key": "openai-test-key"}
    assert captured["create_kwargs"]["model"] == "gpt-4o-mini"
    assert result.key_entities == ["OpenAI"]


def test_gemini_provider_uses_compatible_base_url(monkeypatch):
    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured["create_kwargs"] = kwargs
            return kwargs["response_model"](
                document_type="news",
                summary="ok",
                key_entities=["Gemini"],
                action_items=["Run extraction"],
                deadlines=[],
                risks=[],
            )

    class FakeClient:
        def __init__(self):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    def fake_openai(**kwargs):
        captured["client_kwargs"] = kwargs
        return FakeClient()

    monkeypatch.setattr(config, "DEFAULT_MODEL", None)
    monkeypatch.setattr(config, "GEMINI_API_KEY", "gemini-test-key")
    monkeypatch.setattr(config, "GEMINI_MODEL", "gemini-1.5-flash")
    monkeypatch.setattr(
        config,
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    monkeypatch.setattr("app.extractors.llm_extractor.OpenAI", fake_openai)
    monkeypatch.setattr("app.extractors.llm_extractor.instructor.patch", lambda client: client)

    extractor = LLMExtractor(provider="gemini")
    result = extractor.extract("hello")

    assert captured["client_kwargs"] == {
        "api_key": "gemini-test-key",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    }
    assert captured["create_kwargs"]["model"] == "gemini-1.5-flash"
    assert result.key_entities == ["Gemini"]


def test_gemini_provider_requires_api_key(monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", None)

    extractor = LLMExtractor(provider="gemini")

    with pytest.raises(ValueError, match="GEMINI_API_KEY|GOOGLE_API_KEY"):
        extractor.extract("hello")
