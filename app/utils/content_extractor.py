import httpx
from bs4 import BeautifulSoup
from typing import Dict, TypedDict, Optional
import logging

logger = logging.getLogger(__name__)

class ContentExtractionResult(TypedDict):
    """Result structure for content extraction."""
    text: str
    title: str
    author: str
    type: str
    error: Optional[str]

class ContentExtractor:
    """
    Utility for extracting content from URLs or raw text.
    Handles basic HTML cleaning and metadata extraction.
    """
    
    DEFAULT_TITLE = "Untitled"
    DEFAULT_AUTHOR = "Unknown"
    
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }

    async def extract(self, input_data: str) -> ContentExtractionResult:
        """
        Extract content from either a URL or raw text.
        
        Args:
            input_data: A URL starting with 'http' or raw text.
            
        Returns:
            A ContentExtractionResult dictionary containing 'text', 'title', 'author', 'type', and 'error'.
        """
        if not input_data:
            return {
                "text": "",
                "title": self.DEFAULT_TITLE,
                "author": self.DEFAULT_AUTHOR,
                "type": "error",
                "error": "Input data is empty"
            }
            
        if input_data.startswith("http"):
            return await self._extract_from_url(input_data)
        
        return self._extract_from_text(input_data)

    async def _extract_from_url(self, url: str) -> ContentExtractionResult:
        """Helper to extract content from a URL."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                resp = await client.get(url, follow_redirects=True)
                # Ensure the response is successful
                resp.raise_for_status()
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Simple cleaning: remove script and style elements
                for s in soup(['script', 'style']):
                    s.decompose()
                
                # Extract text with space separator
                text = soup.get_text(separator=' ', strip=True)
                
                # Extract title, fallback to "Untitled"
                title = self._get_title(soup)
                
                # Basic author extraction
                author = self._get_author(soup)
                
                return {
                    "text": text,
                    "title": title,
                    "author": author,
                    "type": "url",
                    "error": None
                }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching {url}: {e}")
            return self._error_result(f"HTTP Error {e.response.status_code}", "url")
        except httpx.TimeoutException:
            logger.error(f"Timeout occurred while fetching {url}")
            return self._error_result("Connection timeout", "url")
        except Exception as e:
            logger.error(f"Unexpected error while fetching {url}: {e}")
            return self._error_result(str(e), "url")

    def _extract_from_text(self, text: str) -> ContentExtractionResult:
        """Helper to extract content from raw text."""
        return {
            "text": text,
            "title": "Raw Text",
            "author": self.DEFAULT_AUTHOR,
            "type": "text",
            "error": None
        }

    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract title from BeautifulSoup object."""
        # Try <title> tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        # Try og:title
        og_title = soup.find("meta", {"property": "og:title"})
        if og_title and og_title.get("content"):
            return str(og_title["content"]).strip()
            
        return self.DEFAULT_TITLE

    def _get_author(self, soup: BeautifulSoup) -> str:
        """Extract author from BeautifulSoup object."""
        # Common author tags
        author_tags = [
            ("meta", {"name": "author"}),
            ("meta", {"property": "article:author"}),
            ("meta", {"property": "og:author"}),
            ("meta", {"name": "twitter:creator"}),
        ]
        
        for tag, attrs in author_tags:
            found = soup.find(tag, attrs)
            if found and found.get("content"):
                return str(found["content"]).strip()
        
        return self.DEFAULT_AUTHOR

    def _error_result(self, error_msg: str, input_type: str) -> ContentExtractionResult:
        """Standard error result."""
        return {
            "text": "",
            "title": self.DEFAULT_TITLE,
            "author": self.DEFAULT_AUTHOR,
            "type": input_type,
            "error": error_msg
        }
