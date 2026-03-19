from __future__ import annotations
from typing import Optional

from app.extractors.base import BaseExtractor
from app.extractors.pipeline_extractor import PipelineExtractor
from app.schemas.extraction import ExtractionOutput

class ExtractionService:
    """
    Orchestration layer for the AI Structured Extraction Tool.
    
    This service acts as the primary interface for processing text and
    managing the extraction pipeline.
    """
    def __init__(self, extractor: Optional[BaseExtractor] = None) -> None:
        """
        Initialize the service with an optional extractor.
        
        Args:
            extractor: A specific extractor implementation to use. 
                       Defaults to PipelineExtractor if None.
        """
        self.extractor = extractor or PipelineExtractor()

    def process(self, text: str) -> ExtractionOutput:
        """
        Process the input text through the extraction pipeline.
        
        Args:
            text: The unstructured text to extract information from.
            
        Returns:
            ExtractionOutput containing the structured data.
            
        Raises:
            ValueError: If the input text is empty or only whitespace.
            RuntimeError: If the extraction process fails.
        """
        if not text.strip():
            raise ValueError("Input text cannot be empty.")

        try:
            result = self.extractor.extract(text)
            return result
        except Exception as e:
            raise RuntimeError(f"Extraction failed: {str(e)}")
