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
def mock_crawler(monkeypatch):
    """
    Mock Crawl4AI's AsyncWebCrawler.
    """
    from unittest.mock import AsyncMock, MagicMock
    
    mock_crawler = AsyncMock()
    
    # Mock context manager
    mock_instance = MagicMock()
    mock_instance.__aenter__.return_value = mock_crawler
    
    def mock_crawler_init(*args, **kwargs):
        return mock_instance
        
    monkeypatch.setattr("app.utils.content_extractor.AsyncWebCrawler", mock_crawler_init)
    
    # Mock arun result
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.error_message = None
    mock_result.markdown = "Extracted content from URL"
    mock_result.metadata = {
        "title": "Extracted Title",
        "author": "Jane Smith",
        "date": "2023-10-27"
    }
    mock_crawler.arun.return_value = mock_result
    
    return mock_crawler

@pytest.mark.asyncio
async def test_factcheck_pipeline_with_url(mock_llm, mock_crawler, tmp_path):
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
@pytest.mark.integration
async def test_factcheck_pipeline_with_real_url(mock_llm, tmp_path):
    """
    Test with a real URL (example.com). This requires internet access.
    We still mock the LLM to avoid costs and keep it predictable.
    """
    # Setup mock DB
    db_file = tmp_path / "authors.json"
    db_file.write_text("{}")
    db = AuthorDatabase(str(db_file))
    
    coordinator = FactCheckCoordinator(author_db=db)
    
    # example.com is stable and fast
    url = "https://example.com"
    report = await coordinator.fact_check(url)
    
    assert isinstance(report, FactCheckReport)
    assert "Example Domain" in report.article_title
    assert len(report.claims_verified) == 2
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
