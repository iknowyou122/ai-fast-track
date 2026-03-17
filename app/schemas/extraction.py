from pydantic import BaseModel, Field
from typing import List

class ExtractionOutput(BaseModel):
    """
    Structured extraction of unstructured text.
    """
    summary: str = Field(..., description="A concise summary of the input text.")
    key_entities: List[str] = Field(..., description="A list of important names, organizations, or concepts mentioned.")
    action_items: List[str] = Field(..., description="A list of specific tasks or actions identified in the text.")
    deadlines: List[str] = Field(..., description="A list of any specific dates or times mentioned as deadlines.")
    risks: List[str] = Field(..., description="A list of potential issues, concerns, or risks identified.")
