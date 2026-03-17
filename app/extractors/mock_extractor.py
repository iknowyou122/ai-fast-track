from app.extractors.base import BaseExtractor
from app.schemas.extraction import ExtractionOutput

class MockExtractor(BaseExtractor):
    """
    Mock extractor for testing purposes.
    """
    def extract(self, text: str) -> ExtractionOutput:
        """
        Return mock extraction data.
        """
        return ExtractionOutput(
            summary=f"This is a mock summary of: {text[:20]}...",
            key_entities=["Mock Entity 1", "Mock Entity 2"],
            action_items=["Mock Action 1"],
            deadlines=["2026-01-01"],
            risks=["Mock Risk"]
        )
