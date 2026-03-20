import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.utils.content_extractor import ContentExtractor

@pytest.mark.asyncio
@patch("app.utils.content_extractor.AsyncWebCrawler")
async def test_extract_url_error_response(mock_crawler_class):
    # Setup mock to simulate a failed crawl (e.g., 404 handled by Crawl4AI)
    mock_crawler = AsyncMock()
    mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
    
    mock_result = MagicMock()
    mock_result.success = False
    mock_result.error_message = "404 Not Found"
    mock_crawler.arun.return_value = mock_result
    
    url = "https://example.com/404"
    extractor = ContentExtractor()
    result = await extractor.extract(url)
    
    assert result["type"] == "url"
    assert result["error"] is not None
    assert "404" in result["error"]

@pytest.mark.asyncio
@patch("app.utils.content_extractor.AsyncWebCrawler")
async def test_extract_url_timeout(mock_crawler_class):
    # Setup mock to simulate a timeout
    mock_crawler = AsyncMock()
    mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
    
    # Simulate asyncio.TimeoutError when calling arun
    mock_crawler.arun.side_effect = asyncio.TimeoutError()
    
    url = "https://example.com/timeout"
    extractor = ContentExtractor(timeout=0.1)
    result = await extractor.extract(url)
    
    assert result["type"] == "url"
    assert result["error"] is not None
    assert "Timeout" in result["error"]

@pytest.mark.asyncio
@patch("app.utils.content_extractor.AsyncWebCrawler")
async def test_extract_url_unexpected_exception(mock_crawler_class):
    # Setup mock to raise an unexpected exception
    mock_crawler = AsyncMock()
    mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
    mock_crawler.arun.side_effect = Exception("Unexpected connection error")
    
    url = "https://example.com/error"
    extractor = ContentExtractor()
    result = await extractor.extract(url)
    
    assert result["type"] == "url"
    assert "Unexpected connection error" in result["error"]
