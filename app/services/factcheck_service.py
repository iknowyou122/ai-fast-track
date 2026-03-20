import asyncio
from typing import List

from app.utils.content_extractor import ContentExtractor
from app.agents.decomposer import DecomposerAgent
from app.agents.search_agent import SearchAgent
from app.agents.author_agent import AuthorAgent
from app.agents.reasoning_agent import ReasoningAgent
from app.schemas.factcheck import FactCheckReport, Claim, Evidence
from app.db.author_database import BaseAuthorDB


class FactCheckCoordinator:
    """
    Orchestrates the full fact-checking pipeline.
    Chains: Content Extraction -> Decomposition -> (Parallel Search/Author Analysis) -> Reasoning.
    """

    def __init__(self, author_db: BaseAuthorDB):
        """
        Initialize the coordinator with all necessary agents and utilities.
        """
        self.extractor = ContentExtractor()
        self.decomposer = DecomposerAgent()
        self.search_agent = SearchAgent()
        self.author_agent = AuthorAgent(db=author_db)
        self.reasoning_agent = ReasoningAgent()

    async def fact_check(self, input_data: str) -> FactCheckReport:
        """
        Perform a full fact-check on the provided input (URL or raw text).
        
        Args:
            input_data: A URL string or raw article text.
            
        Returns:
            A FactCheckReport containing the final analysis and verdict.
        """
        # 1. Extract content and metadata (title, author)
        extraction_result = await self.extractor.extract(input_data)
        if extraction_result.get("error"):
            # If extraction failed, we can still proceed with raw text if possible,
            # or raise an exception. For now, we'll use whatever text was extracted.
            pass
            
        article_text = extraction_result["text"]
        author_name = extraction_result["author"]

        # 2. Decompose article into verifiable claims
        # Note: decompose is synchronous in the provided implementation.
        claims: List[Claim] = self.decomposer.decompose(article_text)

        # 3. Perform Search (for evidence) and Author Analysis in parallel
        # We gather evidence for each claim concurrently.
        search_tasks = [self.search_agent.search(claim) for claim in claims]
        
        # Also retrieve author profile concurrently
        author_task = self.author_agent.get_profile(author_name)
        
        # Use asyncio.gather to run all search tasks and the author task in parallel
        results = await asyncio.gather(*search_tasks, author_task)
        
        # Unpack results: results[:-1] are lists of evidence, results[-1] is author profile
        evidences_nested: List[List[Evidence]] = results[:-1]
        author_profile = results[-1]
        
        # Flatten evidence list
        all_evidences: List[Evidence] = [
            evidence for claim_evidences in evidences_nested 
            for evidence in claim_evidences
        ]

        # 4. Reason over claims, evidence, and author profile to produce the final report
        report: FactCheckReport = await self.reasoning_agent.reason(
            claims=claims, 
            evidences=all_evidences, 
            author=author_profile
        )

        # Ensure the report includes the article title from extraction
        if not report.article_title:
            report.article_title = extraction_result["title"]

        return report
