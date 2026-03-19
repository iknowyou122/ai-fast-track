from app.extractors.pipeline_extractor import PipelineExtractor
from app.schemas.extraction import ExtractionOutput

class ExtractionService:
    """
    Orchestration layer for the AI Structured Extraction Tool.
    """
    def __init__(self, extractor=None):
        """
        Initialize the service with an extractor.
        """
        self.extractor = extractor or PipelineExtractor()

    def process(self, text: str) -> ExtractionOutput:
        """
        Process the input text through the extraction pipeline.
        """
        if not text.strip():
            raise ValueError("Input text cannot be empty.")

        try:
            result = self.extractor.extract(text)
            return result
        except Exception as e:
            raise RuntimeError(f"Extraction failed: {str(e)}")
