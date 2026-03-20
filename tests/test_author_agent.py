import pytest
import os
import json
from app.agents.author_agent import AuthorAgent
from app.db.author_database import AuthorDatabase
from app.schemas.factcheck import AuthorProfile

@pytest.fixture
def temp_author_db(tmp_path):
    """
    Create a temporary JSON author database for testing.
    """
    db_file = tmp_path / "test_authors.json"
    test_data = {
        "Jane Doe": {
            "author_name": "Jane Doe",
            "historical_score": 85,
            "total_articles": 12,
            "reliability_assessment": "Generally reliable.",
            "trust_level": "High"
        }
    }
    with open(db_file, "w") as f:
        json.dump(test_data, f)
    
    return AuthorDatabase(str(db_file))

@pytest.mark.asyncio
async def test_author_agent_get_existing_profile(temp_author_db):
    """
    Verify AuthorAgent retrieves an existing profile correctly.
    """
    agent = AuthorAgent(temp_author_db)
    profile = await agent.get_profile("Jane Doe")
    
    assert profile.author_name == "Jane Doe"
    assert profile.historical_score == 85
    assert profile.trust_level == "High"

@pytest.mark.asyncio
async def test_author_agent_get_unknown_profile(temp_author_db):
    """
    Verify AuthorAgent returns a default profile for unknown authors.
    """
    agent = AuthorAgent(temp_author_db)
    profile = await agent.get_profile("Unknown Author")
    
    assert profile.author_name == "Unknown Author"
    assert profile.historical_score == 50
    assert profile.trust_level == "Neutral"
    assert "not found" in profile.reliability_assessment.lower()
