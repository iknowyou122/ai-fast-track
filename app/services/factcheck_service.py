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

    async def fact_check(self, input_data: str, progress_callback=None) -> FactCheckReport:
        """
        Perform a full fact-check on the provided input (URL or raw text).
        
        Args:
            input_data: A URL string or raw article text.
            progress_callback: Optional callable for reporting progress steps.
            
        Returns:
            A FactCheckReport containing the final analysis and verdict.
        """
        if progress_callback: progress_callback("🔍 [Task 1/4] 正在提取文章內容...")
        # 1. Extract content and metadata (title, author)
        extraction_result = await self.extractor.extract(input_data)
        if extraction_result.get("error"):
            pass
            
        article_text = extraction_result["text"]
        author_name = extraction_result["author"]

        if progress_callback: progress_callback("🧠 [Task 2/4] 正在拆解關鍵聲明 (Claims)...")
        # 2. Decompose article into verifiable claims
        claims: List[Claim] = self.decomposer.decompose(article_text)

        if progress_callback: progress_callback(f"🌐 [Task 3/4] 正在為 {len(claims)} 個聲明搜尋證據與分析作者...")
        # 3. Perform Search (for evidence) and Author Analysis in parallel
        search_tasks = [self.search_agent.search(claim) for claim in claims]
        author_task = self.author_agent.get_profile(author_name)
        
        results = await asyncio.gather(*search_tasks, author_task)
        
        evidences_nested: List[List[Evidence]] = results[:-1]
        author_profile = results[-1]
        
        all_evidences: List[Evidence] = [
            evidence for claim_evidences in evidences_nested 
            for evidence in claim_evidences
        ]

        if progress_callback: progress_callback("⚖️ [Task 4/4] 正在進行邏輯推理與可靠性評分...")
        # 4. Reason over claims, evidence, and author profile to produce the final report
        report: FactCheckReport = await self.reasoning_agent.reason(
            claims=claims, 
            evidences=all_evidences, 
            author=author_profile
        )

        # Ensure the report includes the article title and date from extraction
        if not report.article_title:
            report.article_title = extraction_result["title"]
        
        if not report.article_date:
            report.article_date = extraction_result["date"]

        return report
