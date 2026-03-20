import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.factcheck_service import FactCheckCoordinator
from app.schemas.factcheck import FactCheckReport, Claim, Evidence, AuthorProfile
from app.utils.content_extractor import ContentExtractionResult

@pytest.fixture
def mock_agents():
    with patch("app.services.factcheck_service.ContentExtractor") as mock_extractor, \
         patch("app.services.factcheck_service.DecomposerAgent") as mock_decomposer, \
         patch("app.services.factcheck_service.SearchAgent") as mock_search, \
         patch("app.services.factcheck_service.AuthorAgent") as mock_author, \
         patch("app.services.factcheck_service.ReasoningAgent") as mock_reasoning:
        
        yield {
            "extractor": mock_extractor,
            "decomposer": mock_decomposer,
            "search": mock_search,
            "author": mock_author,
            "reasoning": mock_reasoning
        }

@pytest.mark.asyncio
async def test_fact_check_orchestration(mock_agents):
    # Setup mocks
    extractor_instance = mock_agents["extractor"].return_value
    extractor_instance.extract = AsyncMock(return_value=ContentExtractionResult(
        text="Sample article text",
        title="Sample Title",
        author="John Doe",
        type="text",
        error=None
    ))

    decomposer_instance = mock_agents["decomposer"].return_value
    claims = [Claim(id="c1", text="Claim 1", category="factual", context="")]
    decomposer_instance.decompose = MagicMock(return_value=claims)

    search_instance = mock_agents["search"].return_value
    evidences = [Evidence(claim_id="c1", source_url="http://src", title="T", content="C", credibility_score=0.9)]
    search_instance.search = AsyncMock(return_value=evidences)

    author_instance = mock_agents["author"].return_value
    author_profile = AuthorProfile(author_name="John Doe", historical_score=80, total_articles=10, reliability_assessment="Good", trust_level="High")
    author_instance.get_profile = AsyncMock(return_value=author_profile)

    reasoning_instance = mock_agents["reasoning"].return_value
    expected_report = FactCheckReport(
        article_title="Sample Title",
        article_summary="Summary",
        claims_verified=[],
        author_background=author_profile,
        total_reliability_score=85,
        final_verdict="True"
    )
    reasoning_instance.reason = AsyncMock(return_value=expected_report)

    # Initialize coordinator with a mock DB
    mock_db = MagicMock()
    coordinator = FactCheckCoordinator(author_db=mock_db)
    
    # Run fact_check
    report = await coordinator.fact_check("Sample article text")

    # Assertions
    assert report == expected_report
    extractor_instance.extract.assert_called_once_with("Sample article text")
    decomposer_instance.decompose.assert_called_once_with("Sample article text")
    search_instance.search.assert_called_once_with(claims[0])
    author_instance.get_profile.assert_called_once_with("John Doe")
    reasoning_instance.reason.assert_called_once_with(claims=claims, evidences=evidences, author=author_profile)
