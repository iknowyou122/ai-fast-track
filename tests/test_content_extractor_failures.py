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
    with pytest.raises(httpx.HTTPStatusError):
        await extractor.extract(url)

@pytest.mark.asyncio
@respx.mock
async def test_extract_url_timeout(respx_mock):
    url = "https://example.com/timeout"
    respx_mock.get(url).mock(side_effect=httpx.TimeoutException("Timeout occurred"))
    
    extractor = ContentExtractor()
    with pytest.raises(httpx.TimeoutException):
        await extractor.extract(url)
