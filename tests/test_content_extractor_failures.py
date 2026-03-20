import pytest
import respx
import httpx
from httpx import Response
from app.utils.content_extractor import ContentExtractor

@pytest.mark.asyncio
@respx.mock
async def test_extract_url_404(respx_mock):
    url = "https://example.com/404"
    respx_mock.get(url).mock(return_value=Response(404))
    
    extractor = ContentExtractor()
    result = await extractor.extract(url)
    
    assert result["type"] == "url"
    assert result["error"] is not None
    assert "404" in result["error"]

@pytest.mark.asyncio
@respx.mock
async def test_extract_url_timeout(respx_mock):
    url = "https://example.com/timeout"
    respx_mock.get(url).mock(side_effect=httpx.TimeoutException("Timeout occurred"))
    
    extractor = ContentExtractor()
    result = await extractor.extract(url)
    
    assert result["type"] == "url"
    assert result["error"] is not None
    assert "timeout" in result["error"].lower()
