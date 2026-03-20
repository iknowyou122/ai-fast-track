import pytest
from types import SimpleNamespace
from typing import List
from app.agents.decomposer import DecomposerAgent
from app.schemas.factcheck import Claim
from app.config import config

def test_decomposer_extracts_claims(monkeypatch):
    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured["create_kwargs"] = kwargs
            # Return a list of claims as requested by instructor response_model
            # Note: instructor supports List[BaseModel] or a wrapper model.
            # In DecomposerAgent, we'll use a wrapper or just List[Claim] if supported.
            return [
                Claim(id="1", text="The sky is blue", category="factual", context="Weather report"),
                Claim(id="2", text="2+2=4", category="factual", context="Math class")
            ]

    class FakeClient:
        def __init__(self):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    def fake_openai(**kwargs):
        return FakeClient()

    monkeypatch.setattr(config, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("app.extractors.llm_extractor.OpenAI", fake_openai)
    monkeypatch.setattr("app.extractors.llm_extractor.instructor.patch", lambda client: client)

    agent = DecomposerAgent()
    claims = agent.decompose("The sky is blue and 2+2=4")

    assert len(claims) == 2
    assert isinstance(claims[0], Claim)
    assert claims[0].text == "The sky is blue"
    assert claims[1].text == "2+2=4"
    assert captured["create_kwargs"]["response_model"] == List[Claim]

def test_decomposer_with_sample_text(monkeypatch):
    class FakeCompletions:
        def create(self, **kwargs):
            return [
                Claim(id="c1", text="Unemployment fell to 4%", category="statistical", context="Economic report"),
                Claim(id="c2", text="The report was released on Tuesday", category="temporal", context="Timeline")
            ]

    class FakeClient:
        def __init__(self):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(config, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("app.extractors.llm_extractor.OpenAI", lambda **kw: FakeClient())
    monkeypatch.setattr("app.extractors.llm_extractor.instructor.patch", lambda client: client)

    agent = DecomposerAgent()
    text = "The latest economic report released on Tuesday shows that unemployment fell to 4%."
    claims = agent.decompose(text)

    assert len(claims) == 2
    categories = [c.category for c in claims]
    assert "statistical" in categories
    assert "temporal" in categories
