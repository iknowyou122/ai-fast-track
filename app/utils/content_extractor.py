from typing import Dict, TypedDict, Optional
import logging
from crawl4ai import AsyncWebCrawler
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

logger = logging.getLogger(__name__)

class ContentExtractionResult(TypedDict):
    """Result structure for content extraction."""
    text: str
    title: str
    author: str
    date: str
    type: str
    error: Optional[str]

class ContentExtractor:
    """
    Utility for extracting content from URLs or raw text.
    Handles basic HTML cleaning and metadata extraction using Crawl4AI.
    """
    
    DEFAULT_TITLE = "Untitled"
    DEFAULT_AUTHOR = "Unknown"
    DEFAULT_DATE = "Unknown"
    
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    async def extract(self, input_data: str) -> ContentExtractionResult:
        """
        Extract content from either a URL or raw text.
        
        Args:
            input_data: A URL starting with 'http' or raw text.
            
        Returns:
            A ContentExtractionResult dictionary containing 'text', 'title', 'author', 'date', 'type', and 'error'.
        """
        if not input_data:
            return {
                "text": "",
                "title": self.DEFAULT_TITLE,
                "author": self.DEFAULT_AUTHOR,
                "date": self.DEFAULT_DATE,
                "type": "error",
                "error": "Input data is empty"
            }
            
        if input_data.startswith("http"):
            return await self._extract_from_url(input_data)
        
        return self._extract_from_text(input_data)

    async def _extract_from_url(self, url: str) -> ContentExtractionResult:
        """Helper to extract content from a URL using Crawl4AI."""
        try:
            md_generator = DefaultMarkdownGenerator()
            
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    url=url,
                    magic=True,
                    markdown_generator=md_generator
                )
                
                if not result.success:
                    return self._error_result(result.error_message or "Unknown crawl error", "url")
                
                # Extract metadata from Crawl4AI result
                metadata = result.metadata or {}
                title = metadata.get("title") or self.DEFAULT_TITLE
                author = metadata.get("author") or self.DEFAULT_AUTHOR
                date = metadata.get("date") or self.DEFAULT_DATE
                
                return {
                    "text": result.markdown or "",
                    "title": title,
                    "author": author,
                    "date": date,
                    "type": "url",
                    "error": None
                }
        except Exception as e:
            logger.error(f"Unexpected error while fetching {url}: {e}")
            return self._error_result(str(e), "url")

    def _extract_from_text(self, text: str) -> ContentExtractionResult:
        """Helper to extract content from raw text."""
        return {
            "text": text,
            "title": "Raw Text",
            "author": self.DEFAULT_AUTHOR,
            "date": self.DEFAULT_DATE,
            "type": "text",
            "error": None
        }

    def _error_result(self, error_msg: str, input_type: str) -> ContentExtractionResult:
        """Standard error result."""
        return {
            "text": "",
            "title": self.DEFAULT_TITLE,
            "author": self.DEFAULT_AUTHOR,
            "date": self.DEFAULT_DATE,
            "type": input_type,
            "error": error_msg
        }
