from typing import List
from app.schemas.factcheck import Evidence, Claim

class SearchAgent:
    """
    Agent responsible for searching for evidence related to a specific claim.
    Currently uses a mock implementation, but can be extended to use Tavily or Google Search.
    """
    async def search(self, claim: Claim) -> List[Evidence]:
        """
        Search for evidence for a given claim.
        
        Args:
            claim: The claim object to find evidence for.
            
        Returns:
            A list of Evidence objects.
        """
        # Implement mock search for now.
        # Future: Integrate with Tavily or Google Search.
        return [
            Evidence(
                claim_id=claim.id,
                source_url="https://mock-evidence-source.com/article1",
                title="Mock Evidence Title",
                content=f"This is mock evidence content that supports or refutes the claim: '{claim.text}'.",
                credibility_score=0.9
            )
        ]
