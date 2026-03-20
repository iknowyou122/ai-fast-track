import asyncio
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
            from crawl4ai import CrawlerRunConfig
            
            # Configure high-precision extraction targeting common news containers
            run_config = CrawlerRunConfig(
                magic=True,
                cache_mode="BYPASS",
                # Targeting Yahoo and general news article bodies
                css_selector=".caas-body, article, main, .article-content",
                markdown_generator=DefaultMarkdownGenerator(
                    options={"ignore_links": False, "ignore_images": True}
                )
            )
            
            async with AsyncWebCrawler() as crawler:
                # Use asyncio.wait_for to enforce the timeout
                result = await asyncio.wait_for(
                    crawler.arun(
                        url=url,
                        config=run_config
                    ),
                    timeout=self.timeout
                )
                
                if not result.success:
                    return self._error_result(result.error_message or "Unknown crawl error", "url")
                
                # Extract metadata from Crawl4AI's parsed structure
                metadata = result.metadata or {}
                
                # Title resolution: prioritize common meta tags
                title = (
                    metadata.get("og:title") or 
                    metadata.get("title") or 
                    metadata.get("dc.title") or 
                    self.DEFAULT_TITLE
                )
                
                # Author resolution
                author = (
                    metadata.get("author") or 
                    metadata.get("article:author") or 
                    metadata.get("og:author") or 
                    metadata.get("twitter:creator") or 
                    self.DEFAULT_AUTHOR
                )
                
                # Date resolution
                date = (
                    metadata.get("article:published_time") or 
                    metadata.get("published_time") or 
                    metadata.get("date") or 
                    metadata.get("og:pubdate") or 
                    self.DEFAULT_DATE
                )
                
                return {
                    "text": result.markdown or "",
                    "title": str(title),
                    "author": str(author),
                    "date": str(date),
                    "type": "url",
                    "error": None
                }
        except asyncio.TimeoutError:
            logger.error(f"Timeout while fetching {url} (limit: {self.timeout}s)")
            return self._error_result(f"Timeout while fetching {url}", "url")
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
