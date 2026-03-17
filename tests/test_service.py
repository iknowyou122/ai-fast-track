import pytest
from app.services.extraction_service import ExtractionService
from app.extractors.mock_extractor import MockExtractor

def test_extraction_service_with_mock():
    mock_extractor = MockExtractor()
    service = ExtractionService(extractor=mock_extractor)
    
    text = "Important meeting tomorrow at 10 AM. Need to prepare the report."
    result = service.process(text)
    
    assert result.summary.startswith("This is a mock summary of:")
    assert "Mock Entity 1" in result.key_entities
    assert len(result.action_items) > 0
