import pytest
import respx
from httpx import Response
from app.utils.content_extractor import ContentExtractor

@pytest.mark.asyncio
async def test_extract_raw_text():
    extractor = ContentExtractor()
    result = await extractor.extract("This is raw text")
    
    assert result["text"] == "This is raw text"
    assert result["title"] == "Raw Text"
    assert result["author"] == "Unknown"
    assert result["type"] == "text"

@pytest.mark.asyncio
@respx.mock
async def test_extract_url(respx_mock):
    url = "https://example.com/news"
    html_content = """
    <html>
        <head>
            <title>News Title</title>
            <meta name="author" content="Jane Doe">
        </head>
        <body>
            <style>.ads { color: red; }</style>
            <h1>Main Story</h1>
            <p>This is the news content.</p>
            <script>console.log('test');</script>
        </body>
    </html>
    """
    respx_mock.get(url).mock(return_value=Response(200, text=html_content))
    
    extractor = ContentExtractor()
    result = await extractor.extract(url)
    
    assert result["title"] == "News Title"
    assert result["author"] == "Jane Doe"
    assert result["type"] == "url"
    assert "Main Story" in result["text"]
    assert "This is the news content." in result["text"]
    assert "console.log" not in result["text"]
    assert ".ads" not in result["text"]

@pytest.mark.asyncio
@respx.mock
async def test_extract_url_no_title(respx_mock):
    url = "https://example.com/notitle"
    html_content = "<html><body>No title here</body></html>"
    respx_mock.get(url).mock(return_value=Response(200, text=html_content))
    
    extractor = ContentExtractor()
    result = await extractor.extract(url)
    
    assert result["title"] == "Untitled"
    assert result["author"] == "Unknown"
    assert result["text"] == "No title here"
    assert result["type"] == "url"
