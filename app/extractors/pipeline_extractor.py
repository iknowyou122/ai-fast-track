import instructor
from openai import OpenAI
from app.extractors.llm_extractor import LLMExtractor
from app.schemas.extraction import ExtractionOutput
from app.prompts.extraction_prompt import SYSTEM_PROMPT, CLASSIFICATION_PROMPT, TYPE_SPECIFIC_PROMPTS
from app.config import config
from app.utils.logger import logger

class PipelineExtractor(LLMExtractor):
    """
    A two-stage extraction pipeline that first classifies the document type 
    and then applies specialized extraction logic based on that type.
    """
    def detect_type(self, text: str) -> str:
        """
        Classify the input text into a specific document type using an LLM.
        
        Args:
            text: Input document content.
            
        Returns:
            The detected document type (e.g., 'meeting_notes', 'contract', 'bug_report')
            or 'general' if the type is unknown or an error occurs.
        """
        try:
            response = self._get_client().chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": CLASSIFICATION_PROMPT},
                    {"role": "user", "content": text}
                ]
            )
            detected_type = response.choices[0].message.content.strip().lower()
            return detected_type if detected_type in TYPE_SPECIFIC_PROMPTS else "general"
        except Exception as e:
            logger.warning(f"Type detection failed, falling back to 'general'. Error: {e}")
            return "general"

    def extract(self, text: str) -> ExtractionOutput:
        """
        Extract structured information by first detecting the document type 
        and then using a specialized prompt for that type.
        
        Args:
            text: Input document content.
            
        Returns:
            Extracted data as an ExtractionOutput object.
        """
        doc_type = self.detect_type(text)
        type_prompt = TYPE_SPECIFIC_PROMPTS.get(doc_type, TYPE_SPECIFIC_PROMPTS["general"])
        
        full_system_prompt = f"{SYSTEM_PROMPT}\n\nType-Specific Instructions: {type_prompt}"
        
        try:
            response = self._get_client().chat.completions.create(
                model=self.model,
                response_model=ExtractionOutput,
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": text}
                ]
            )
            # Ensure doc_type is set correctly in the output
            response.document_type = doc_type
            return response
        except Exception as e:
            # Fallback to general if specialized fails
            if doc_type != "general":
                logger.warning(f"Specialized extraction for '{doc_type}' failed. Falling back to general. Error: {e}")
                return self.extract_general(text)
            raise e

    def extract_general(self, text: str) -> ExtractionOutput:
        """
        Perform a general-purpose extraction without document-specific optimizations.
        
        Args:
            text: Input document content.
            
        Returns:
            Extracted data as an ExtractionOutput object with type 'general'.
        """
        response = self._get_client().chat.completions.create(
            model=self.model,
            response_model=ExtractionOutput,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        response.document_type = "general"
        return response
