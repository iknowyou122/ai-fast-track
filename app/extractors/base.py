from abc import ABC, abstractmethod
from app.schemas.extraction import ExtractionOutput

class BaseExtractor(ABC):
    """
    Abstract base class for all extractors.
    """
    @abstractmethod
    def extract(self, text: str) -> ExtractionOutput:
        """
        Extract structured information from the given text.
        """
        pass
