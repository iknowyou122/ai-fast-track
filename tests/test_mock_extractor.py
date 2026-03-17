from app.extractors.mock_extractor import MockExtractor

def test_mock_extractor():
    extractor = MockExtractor()
    text = "Hello world"
    result = extractor.extract(text)
    
    assert result.summary == f"This is a mock summary of: {text}..."
    assert result.key_entities == ["Mock Entity 1", "Mock Entity 2"]
    assert result.deadlines == ["2026-01-01"]
