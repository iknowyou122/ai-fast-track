from app.schemas.extraction import ExtractionOutput
from app.prompts.extraction_prompt import CLASSIFICATION_PROMPT, TYPE_SPECIFIC_PROMPTS
import pytest

def test_extraction_output_schema_updates():
    """
    Verify that ExtractionOutput has document_type and metadata fields.
    """
    data = {
        "document_type": "meeting_notes",
        "summary": "This is a summary.",
        "key_entities": ["Entity 1"],
        "action_items": ["Action 1"],
        "deadlines": ["Tomorrow"],
        "risks": ["Risk 1"],
        "metadata": {"key": "value"}
    }
    
    output = ExtractionOutput(**data)
    
    assert output.document_type == "meeting_notes"
    assert output.summary == "This is a summary."
    assert output.metadata == {"key": "value"}

def test_extraction_prompts_updates():
    """
    Verify that CLASSIFICATION_PROMPT and TYPE_SPECIFIC_PROMPTS are defined.
    """
    assert isinstance(CLASSIFICATION_PROMPT, str)
    assert len(CLASSIFICATION_PROMPT) > 0
    assert "meeting_notes" in CLASSIFICATION_PROMPT
    
    assert isinstance(TYPE_SPECIFIC_PROMPTS, dict)
    assert "meeting_notes" in TYPE_SPECIFIC_PROMPTS
    assert "Focus on participants" in TYPE_SPECIFIC_PROMPTS["meeting_notes"]
