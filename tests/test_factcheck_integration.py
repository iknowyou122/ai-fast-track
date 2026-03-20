import pytest
from typing import List
from unittest.mock import MagicMock, AsyncMock
from types import SimpleNamespace
from app.services.factcheck_service import FactCheckCoordinator
from app.db.author_database import AuthorDatabase
from app.schemas.factcheck import Claim, AuthorProfile, FactCheckReport, Evidence

@pytest.fixture
def mock_llm(monkeypatch):
    """
    Mock LLM responses for DecomposerAgent and ReasoningAgent.
    """
    class FakeCompletions:
        def create(self, **kwargs):
            response_model = kwargs.get("response_model")
            
            # Check if it's the decomposition step
            # It might be List[Claim] or list[Claim] depending on python version/imports
            if "Claim" in str(response_model) and "List" in str(response_model):
                 return [
                     Claim(id="claim-1", text="The earth is flat.", category="factual", context="Context 1"),
                     Claim(id="claim-2", text="The moon is made of cheese.", category="factual", context="Context 2")
                 ]
            
            if response_model == FactCheckReport:
                # Extract author name from prompt if possible
                author_name = "John Doe"
                for msg in kwargs.get("messages", []):
                    content = msg.get("content", "")
                    if "AUTHOR PROFILE" in content:
                        import re
                        match = re.search(r'"author_name":\s*"([^"]+)"', content)
                        if match:
                            author_name = match.group(1)
                
                # Check if it's the reasoning step
                return FactCheckReport(
                    article_title=None,
                    article_summary="A summary of mock claims.",
                    claims_verified=[
                        {"claim_id": "claim-1", "verdict": "False", "reasoning": "Science says so."},
                        {"claim_id": "claim-2", "verdict": "False", "reasoning": "Astronauts tasted it."}
                    ],
                    author_background=AuthorProfile(
                        author_name=author_name,
                        historical_score=80,
                        total_articles=10,
                        reliability_assessment="Good",
                        trust_level="High"
                    ),
                    total_reliability_score=10,
                    final_verdict="Highly Unreliable"
                )
            
            return None

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr("app.extractors.llm_extractor.OpenAI", FakeClient)
    monkeypatch.setattr("app.extractors.llm_extractor.instructor.patch", lambda client: client)
    # Ensure API keys are present for the mock to work
    monkeypatch.setattr("app.config.config.OPENAI_API_KEY", "mock-key")

@pytest.fixture
def mock_http(monkeypatch):
    """
    Mock HTTP requests for ContentExtractor.
    """
    class MockResponse:
        def __init__(self, text, status_code=200):
            self.text = text
            self.status_code = status_code
        def raise_for_status(self):
            if self.status_code >= 400:
                import httpx
                raise httpx.HTTPStatusError("Error", request=None, response=self)

    async def mock_get(self, url, **kwargs):
        html = f"<html><title>Extracted Title</title><body><meta name='author' content='Jane Smith'><p>Extracted content from {url}</p></body></html>"
        return MockResponse(html)

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

@pytest.mark.asyncio
async def test_factcheck_pipeline_with_url(mock_llm, mock_http, tmp_path):
    # Setup mock DB
    db_file = tmp_path / "authors.json"
    db_file.write_text("{}")
    db = AuthorDatabase(str(db_file))
    
    coordinator = FactCheckCoordinator(author_db=db)
    
    url = "https://example.com/article"
    report = await coordinator.fact_check(url)
    
    assert isinstance(report, FactCheckReport)
    assert report.article_title == "Extracted Title"
    assert len(report.claims_verified) == 2
    assert report.author_background.author_name == "Jane Smith"
    assert report.total_reliability_score == 10

@pytest.mark.asyncio
async def test_factcheck_pipeline_with_raw_text(mock_llm, tmp_path):
    # Setup mock DB
    db_file = tmp_path / "authors.json"
    db_file.write_text("{}")
    db = AuthorDatabase(str(db_file))
    
    coordinator = FactCheckCoordinator(author_db=db)
    
    raw_text = "The earth is flat. The moon is made of cheese."
    report = await coordinator.fact_check(raw_text)
    
    assert isinstance(report, FactCheckReport)
    assert report.article_title == "Raw Text"
    assert len(report.claims_verified) == 2
    assert report.author_background.author_name == "Unknown"
    assert report.total_reliability_score == 10
