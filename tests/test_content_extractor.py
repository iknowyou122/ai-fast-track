import pytest
import respx
import httpx
from httpx import Response
from unittest.mock import AsyncMock, patch, MagicMock
from app.utils.content_extractor import ContentExtractor

@pytest.mark.asyncio
async def test_extract_raw_text():
    extractor = ContentExtractor()
    result = await extractor.extract("This is raw text")
    
    assert result["text"] == "This is raw text"
    assert result["title"] == "Raw Text"
    assert result["author"] == "Unknown"
    assert result["type"] == "text"
    assert result["error"] is None

@pytest.mark.asyncio
async def test_extract_empty_input():
    extractor = ContentExtractor()
    result = await extractor.extract("")
    
    assert result["type"] == "error"
    assert "empty" in result["error"]

@pytest.mark.asyncio
@patch("app.utils.content_extractor.AsyncWebCrawler")
async def test_extract_url_with_crawl4ai(mock_crawler_class):
    # Setup mock
    mock_crawler = AsyncMock()
    mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
    
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.error_message = None
    mock_result.markdown = "This is the news content."
    mock_result.metadata = {
        "title": "News Title",
        "author": "Jane Doe",
        "date": "2023-10-27"
    }
    mock_crawler.arun.return_value = mock_result
    
    url = "https://example.com/news"
    extractor = ContentExtractor()
    result = await extractor.extract(url)
    
    assert result["title"] == "News Title"
    assert result["author"] == "Jane Doe"
    assert result["date"] == "2023-10-27"
    assert result["type"] == "url"
    assert result["error"] is None
    assert "This is the news content." in result["text"]
    
    # Verify Magic Mode and Markdown strategy were used
    args, kwargs = mock_crawler.arun.call_args
    assert kwargs["magic"] is True
    assert "markdown_generator" in kwargs

@pytest.mark.asyncio
@patch("app.utils.content_extractor.AsyncWebCrawler")
async def test_extract_url_traditional_chinese(mock_crawler_class):
    # Setup mock with Traditional Chinese content
    mock_crawler = AsyncMock()
    mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
    
    chinese_text = "這是繁體中文內容。不應該被翻譯。"
    mock_result = MagicMock()
    mock_result.markdown = chinese_text
    mock_result.metadata = {
        "title": "繁體標題",
        "author": "張三",
        "date": "2023-10-27"
    }
    mock_crawler.arun.return_value = mock_result
    
    url = "https://example.com/chinese"
    extractor = ContentExtractor()
    result = await extractor.extract(url)
    
    assert result["title"] == "繁體標題"
    assert result["author"] == "張三"
    assert result["text"] == chinese_text
    assert result["error"] is None

@pytest.mark.asyncio
@patch("app.utils.content_extractor.AsyncWebCrawler")
async def test_extract_url_error(mock_crawler_class):
    # Setup mock to raise error
    mock_crawler = AsyncMock()
    mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
    mock_crawler.arun.side_effect = Exception("Crawl failed")
    
    url = "https://example.com/error"
    extractor = ContentExtractor()
    result = await extractor.extract(url)
    
    assert result["type"] == "url"
    assert "Crawl failed" in result["error"]
    assert result["text"] == ""
