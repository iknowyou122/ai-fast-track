from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ExtractionOutput(BaseModel):
    """
    Structured extraction of unstructured text.
    """
    document_type: str = Field(..., description="The detected document type (e.g., meeting_notes, email, news, general).")
    summary: str = Field(..., description="A concise summary of the input text.")
    key_entities: List[str] = Field(..., description="A list of important names, organizations, or concepts mentioned.")
    action_items: List[str] = Field(..., description="A list of specific tasks or actions identified in the text.")
    deadlines: List[str] = Field(..., description="A list of any specific dates or times mentioned as deadlines.")
    risks: List[str] = Field(..., description="A list of potential issues, concerns, or risks identified.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional type-specific information extracted.")
