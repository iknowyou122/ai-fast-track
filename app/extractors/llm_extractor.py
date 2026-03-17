import instructor
from openai import OpenAI
from app.extractors.base import BaseExtractor
from app.schemas.extraction import ExtractionOutput
from app.config import config
from app.prompts.extraction_prompt import SYSTEM_PROMPT

class LLMExtractor(BaseExtractor):
    """
    Extractor using Large Language Models to perform structured extraction.
    """
    def __init__(self, model: str = None):
        """
        Initialize the LLMExtractor with a specific model.
        """
        self.client = instructor.patch(OpenAI(api_key=config.OPENAI_API_KEY))
        self.model = model or config.DEFAULT_MODEL

    def extract(self, text: str) -> ExtractionOutput:
        """
        Extract structured information from the given text using an LLM.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            response_model=ExtractionOutput,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        return response
