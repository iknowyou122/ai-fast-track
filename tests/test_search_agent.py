import pytest
from app.agents.search_agent import SearchAgent
from app.schemas.factcheck import Claim

@pytest.mark.asyncio
async def test_search_agent_returns_evidence():
    """
    Verify that SearchAgent correctly returns evidence for a given claim.
    """
    agent = SearchAgent()
    claim = Claim(
        id="claim-1",
        text="Climate change is caused by human activity.",
        category="scientific",
        context="A discussion about environmental impact."
    )
    
    evidence_list = await agent.search(claim)
    
    assert len(evidence_list) > 0
    evidence = evidence_list[0]
    assert evidence.claim_id == claim.id
    assert "Mock Evidence Title" in evidence.title
    assert "climate change" in evidence.content.lower()
    assert evidence.credibility_score > 0
