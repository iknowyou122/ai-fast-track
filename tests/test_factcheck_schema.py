import pytest
from app.schemas.factcheck import Claim, Evidence, AuthorProfile, FactCheckReport

def test_claim_model():
    """Verify Claim model can be instantiated with valid data."""
    claim_data = {
        "id": "claim-001",
        "text": "The economy grew by 5% in 2023.",
        "category": "statistical",
        "context": "Reported during the annual meeting."
    }
    claim = Claim(**claim_data)
    assert claim.id == "claim-001"
    assert claim.category == "statistical"

def test_evidence_model():
    """Verify Evidence model can be instantiated with valid data."""
    evidence_data = {
        "claim_id": "claim-001",
        "source_url": "https://stats.gov/economy-2023",
        "title": "Annual Economic Report 2023",
        "content": "Official statistics confirm 5.1% growth.",
        "credibility_score": 0.95
    }
    evidence = Evidence(**evidence_data)
    assert evidence.claim_id == "claim-001"
    assert evidence.credibility_score == 0.95

def test_author_profile_model():
    """Verify AuthorProfile model can be instantiated with valid data."""
    author_data = {
        "author_name": "Jane Smith",
        "historical_score": 85,
        "total_articles": 42,
        "reliability_assessment": "High",
        "trust_level": "Trusted"
    }
    author = AuthorProfile(**author_data)
    assert author.author_name == "Jane Smith"
    assert author.historical_score == 85

def test_fact_check_report_model():
    """Verify FactCheckReport model can be instantiated with valid data."""
    author_data = {
        "author_name": "Jane Smith",
        "historical_score": 85,
        "total_articles": 42,
        "reliability_assessment": "High",
        "trust_level": "Trusted"
    }
    report_data = {
        "article_title": "Economic Boom",
        "article_summary": "A detailed analysis of 2023 growth.",
        "claims_verified": [
            {"claim_id": "claim-001", "verdict": "True", "confidence": 0.98}
        ],
        "author_background": author_data,
        "total_reliability_score": 90,
        "final_verdict": "Mostly True"
    }
    report = FactCheckReport(**report_data)
    assert report.article_title == "Economic Boom"
    assert report.author_background.author_name == "Jane Smith"
    assert len(report.claims_verified) == 1
