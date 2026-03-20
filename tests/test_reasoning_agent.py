import pytest
from unittest.mock import MagicMock, AsyncMock
from app.agents.reasoning_agent import ReasoningAgent
from app.schemas.factcheck import Claim, Evidence, AuthorProfile, FactCheckReport

@pytest.fixture
def reasoning_agent():
    return ReasoningAgent()

@pytest.fixture
def mock_claims():
    return [
        Claim(id="1", text="The moon is made of cheese.", category="factual", context="Scientific discussion"),
        Claim(id="2", text="Water boils at 100 degrees Celsius at sea level.", category="factual", context="Physics basics")
    ]

@pytest.fixture
def mock_evidences():
    return [
        Evidence(claim_id="1", source_url="https://nasa.gov", title="Moon Composition", content="The moon is made of rock.", credibility_score=1.0),
        Evidence(claim_id="2", source_url="https://science.com", title="Boiling Point", content="Water boils at 100C.", credibility_score=1.0)
    ]

@pytest.fixture
def mock_author():
    return AuthorProfile(
        author_name="John Doe",
        historical_score=80,
        total_articles=10,
        reliability_assessment="Generally reliable",
        trust_level="High"
    )

@pytest.mark.asyncio
async def test_reason_returns_fact_check_report(reasoning_agent, mock_claims, mock_evidences, mock_author, monkeypatch):
    # Mock the LLM client response
    mock_report = FactCheckReport(
        article_title="Test Article",
        article_summary="An article about the moon and water.",
        claims_verified=[
            {"claim_id": "1", "verdict": "False", "reasoning": "Evidence says it's rock."},
            {"claim_id": "2", "verdict": "True", "reasoning": "Matches scientific fact."}
        ],
        author_background=mock_author,
        total_reliability_score=75,
        final_verdict="Mixed accuracy"
    )

    # Mock _get_client().chat.completions.create
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_report
    
    # Use monkeypatch to return our mock_client
    monkeypatch.setattr(reasoning_agent, "_get_client", lambda: mock_client)

    report = await reasoning_agent.reason(mock_claims, mock_evidences, mock_author)

    assert isinstance(report, FactCheckReport)
    assert report.total_reliability_score == 75
    assert len(report.claims_verified) == 2
    assert report.author_background.author_name == "John Doe"

@pytest.mark.asyncio
async def test_reasoning_logic_handles_author_profile(reasoning_agent, mock_claims, mock_evidences, mock_author, monkeypatch):
    # Mock the LLM client to verify the prompt contains author info
    captured_kwargs = {}
    
    def mock_create(**kwargs):
        captured_kwargs.update(kwargs)
        return FactCheckReport(
            article_summary="summary",
            claims_verified=[],
            author_background=mock_author,
            total_reliability_score=80,
            final_verdict="Reliable"
        )

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = mock_create
    monkeypatch.setattr(reasoning_agent, "_get_client", lambda: mock_client)

    await reasoning_agent.reason(mock_claims, mock_evidences, mock_author)

    # Check that author info was passed to the LLM (in the user message)
    user_content = captured_kwargs["messages"][1]["content"]
    assert "John Doe" in user_content
    assert "80" in user_content
    assert "Generally reliable" in user_content
