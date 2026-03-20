import httpx
from bs4 import BeautifulSoup
from typing import Dict

class ContentExtractor:
    """
    Utility for extracting content from URLs or raw text.
    Handles basic HTML cleaning and metadata extraction.
    """
    async def extract(self, input_data: str) -> Dict[str, str]:
        """
        Extract content from either a URL or raw text.
        
        Args:
            input_data: A URL starting with 'http' or raw text.
            
        Returns:
            A dictionary containing 'text', 'title', and 'type'.
        """
        if input_data.startswith("http"):
            async with httpx.AsyncClient() as client:
                resp = await client.get(input_data, follow_redirects=True)
                # Ensure the response is successful
                resp.raise_for_status()
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Simple cleaning: remove script and style elements
                for s in soup(['script', 'style']):
                    s.decompose()
                
                # Extract text with space separator
                text = soup.get_text(separator=' ', strip=True)
                
                # Extract title, fallback to "Untitled"
                title = "Untitled"
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()
                
                # Basic author extraction
                author = "Unknown"
                author_meta = soup.find("meta", {"name": "author"}) or soup.find("meta", {"property": "article:author"})
                if author_meta and author_meta.get("content"):
                    author = author_meta["content"].strip()
                
                return {
                    "text": text,
                    "title": title,
                    "author": author,
                    "type": "url"
                }
        
        # Default for raw text
        return {
            "text": input_data,
            "title": "Raw Text",
            "author": "Unknown",
            "type": "text"
        }
