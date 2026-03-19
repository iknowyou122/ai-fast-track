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
    def __init__(self, model: str = None, provider: str = None):
        """
        Initialize the LLMExtractor with a specific model.
        """
        self.provider = config.get_provider(provider)
        self.model = config.get_model(self.provider, model)
        self.client = None

    def _build_client(self):
        api_key = config.get_api_key(self.provider)

        if not api_key:
            if self.provider == "gemini":
                raise ValueError(
                    "Missing Gemini API key. Set GEMINI_API_KEY or GOOGLE_API_KEY."
                )

            raise ValueError("Missing OpenAI API key. Set OPENAI_API_KEY.")

        client_kwargs = {"api_key": api_key}
        base_url = config.get_base_url(self.provider)

        if base_url:
            client_kwargs["base_url"] = base_url

        return instructor.patch(OpenAI(**client_kwargs))

    def _get_client(self):
        if self.client is None:
            self.client = self._build_client()

        return self.client

    def extract(self, text: str) -> ExtractionOutput:
        """
        Extract structured information from the given text using an LLM.
        """
        response = self._get_client().chat.completions.create(
            model=self.model,
            response_model=ExtractionOutput,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        return response
