from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Claim(BaseModel):
    """
    Represents a single claim extracted from a news article.
    """
    id: str = Field(..., description="Unique identifier for the claim.")
    text: str = Field(..., description="The textual content of the claim.")
    category: str = Field(..., description="The category of the claim (e.g., factual, statistical, temporal).")
    context: Optional[str] = Field(None, description="Additional context from the article surrounding the claim.")

class Evidence(BaseModel):
    """
    Represents evidence supporting or contradicting a specific claim.
    """
    claim_id: str = Field(..., description="The ID of the claim this evidence relates to.")
    source_url: str = Field(..., description="The URL of the source providing the evidence.")
    title: str = Field(..., description="The title of the source article or document.")
    content: str = Field(..., description="A snippet or summary of the evidence content.")
    credibility_score: float = Field(1.0, description="A score indicating the credibility of the source, from 0 to 1.")

class AuthorProfile(BaseModel):
    """
    Represents the historical performance and reliability of an article author.
    """
    author_name: str = Field(..., description="The full name of the author.")
    historical_score: int = Field(50, description="A historical reliability score from 0 to 100.")
    total_articles: int = Field(0, description="The total number of articles written by this author in the system.")
    reliability_assessment: str = Field("Unknown", description="A qualitative assessment of the author's reliability.")
    trust_level: str = Field("Neutral", description="A categorization of the author's trust level (e.g., Low, Neutral, High).")

class ClaimVerification(BaseModel):
    """
    Represents the verification result for a single claim.
    """
    claim: str = Field(..., description="The original text of the claim.")
    verdict: str = Field(..., description="The verdict (e.g., Supported, Refuted, Partially Supported, Unverified).")
    reasoning: str = Field(..., description="The detailed reasoning based on evidence.")

class FactCheckReport(BaseModel):
    """
    The final report generated after verifying claims in an article.
    """
    article_title: Optional[str] = Field(None, description="The title of the original article.")
    article_date: Optional[str] = Field(None, description="The publication date of the article.")
    article_summary: str = Field(..., description="A concise summary of the article's main narrative.")
    claims_verified: List[ClaimVerification] = Field(..., description="A list of claims and their verification results.")
    author_background: AuthorProfile = Field(..., description="The reliability profile of the article's author.")
    total_reliability_score: int = Field(..., description="An overall reliability score for the article from 0 to 100.")
    final_verdict: str = Field(..., description="The final qualitative verdict on the article's factual accuracy.")
