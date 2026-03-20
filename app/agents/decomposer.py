from typing import List
from app.schemas.factcheck import Claim
from app.extractors.llm_extractor import LLMExtractor

# Define a specific prompt for decomposition.
DECOMPOSITION_PROMPT = """
You are an expert journalist. Extract all verifiable claims from the following text.
A verifiable claim is a statement that can be proven true or false with evidence.
For each claim, provide:
- id: A unique identifier for the claim (e.g., claim-1).
- text: The actual claim.
- category: One of [factual, statistical, temporal, relational].
- context: Brief context from the text.
"""

class DecomposerAgent(LLMExtractor):
    """
    Agent that decomposes text into verifiable claims.
    """
    def decompose(self, text: str) -> List[Claim]:
        """
        Decompose text into structured Claim objects.
        """
        response = self._get_client().chat.completions.create(
            model=self.model,
            response_model=List[Claim],
            messages=[
                {"role": "system", "content": DECOMPOSITION_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        return response
