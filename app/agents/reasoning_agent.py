import json

from app.extractors.llm_extractor import LLMExtractor
from app.schemas.factcheck import AuthorProfile, Claim, Evidence, FactCheckReport

REASONING_SYSTEM_PROMPT = """
You are an expert Fact-Checking Reasoning Agent. Your task is to analyze a set of
claims against provided evidence and an author's historical profile to generate
a comprehensive Fact-Check Report.

CRITICAL INSTRUCTION:
- Work entirely in the ORIGINAL LANGUAGE of the article and claims.
- DO NOT translate claims, evidence, or reasoning into English or any other language.
- If the inputs are in Traditional Chinese, the output fields (article_summary, claim, verdict, reasoning, final_verdict) MUST be in Traditional Chinese.

Rules for reasoning:
1. For EACH claim in the CLAIMS list, compare it with the provided evidence.
2. Determine a verdict for each claim (e.g., Supported, Refuted, Partially Supported, or Unverified).
3. Populate the `claims_verified` list. You MUST include an entry for EVERY claim provided in the input CLAIMS list.
4. Calculate a 'total_reliability_score' (0-100) for the article based on:
   - The proportion of Supported vs Refuted/Misleading claims.
   - The author's historical reliability score.
   - The credibility of the evidence sources.
5. Provide a 'final_verdict' for the article.
6. Generate a concise 'article_summary'.

The author's profile should weight into the final reliability score.
If an author has a low historical score, be more skeptical of unverified claims.

Ensure the final response is a valid FactCheckReport object with all required fields, especially `claims_verified`.
"""


class ReasoningAgent(LLMExtractor):
    """
    Agent responsible for reasoning over claims and evidence to produce a final fact-check report.
    Inherits from LLMExtractor to leverage LLM capabilities for complex reasoning.
    """

    async def reason(
        self, claims: list[Claim], evidences: list[Evidence], author: AuthorProfile
    ) -> FactCheckReport:
        """
        Reason about the claims using the provided evidence and author profile.

        Args:
            claims: List of extracted claims.
            evidences: List of evidence related to the claims.
            author: Profile of the article's author.

        Returns:
            A FactCheckReport containing the final analysis and scoring.
        """

        # Prepare the data for the prompt
        claims_data = [claim.model_dump() for claim in claims]
        evidences_data = [evidence.model_dump() for evidence in evidences]
        author_data = author.model_dump()

        user_prompt = f"""
Please analyze the following information:

AUTHOR PROFILE:
{json.dumps(author_data, indent=2)}

CLAIMS:
{json.dumps(claims_data, indent=2)}

EVIDENCE:
{json.dumps(evidences_data, indent=2)}

Based on this, generate a FactCheckReport.
"""

        # Call the LLM
        # We use _get_client() from LLMExtractor and call chat.completions.create
        # with response_model=FactCheckReport.

        response = self._get_client().chat.completions.create(
            model=self.model,
            response_model=FactCheckReport,
            messages=[
                {"role": "system", "content": REASONING_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        return response
