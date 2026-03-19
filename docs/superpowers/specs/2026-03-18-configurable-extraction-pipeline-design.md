# Configurable Extraction Pipeline Design

## Overview
Upgrade the current generic extraction logic to a "domain-aware" extraction engine. The new pipeline will include a two-stage process: classification of document type, followed by specialized extraction tailored to that type.

## Architecture
The extraction process will follow a two-stage sequential LLM pipeline:

1.  **Stage 1: Classification (Type Detection)**
    *   The LLM classifies the input text into one of the following `document_type`:
        *   `meeting_notes`: Focus on participants, decisions, and follow-ups.
        *   `interview_notes`: Focus on candidates, skills, and impressions.
        *   `customer_requirements`: Focus on feature requests, pain points, and constraints.
        *   `email`: Focus on sender/receiver intent and next steps.
        *   `news`: Focus on events, dates, and locations.
        *   `general`: Default fallback.
2.  **Stage 2: Specialized Extraction**
    *   A prompt registry maps the `document_type` to type-specific instructions and few-shot examples.
    *   The final extraction is performed using a single, comprehensive Pydantic schema.

## Components

### 1. Data Model (`app/schemas/extraction.py`)
A single, comprehensive schema for all document types.
```python
class ExtractionOutput(BaseModel):
    document_type: str = Field(..., description="The detected document type.")
    summary: str = Field(..., description="A concise summary tailored to the document type.")
    key_entities: List[str] = Field(..., description="Important names, organizations, or concepts.")
    action_items: List[str] = Field(..., description="Tasks or actions (if applicable).")
    deadlines: List[str] = Field(..., description="Specific dates or times for completion.")
    risks: List[str] = Field(..., description="Potential issues or concerns.")
    metadata: dict = Field(default_factory=dict, description="Additional type-specific information.")
```

### 2. Prompt Registry (`app/prompts/extraction_prompt.py`)
A central location for system prompts, including:
*   `CLASSIFICATION_PROMPT`: Instructions for identifying the document type.
*   `TYPE_SPECIFIC_PROMPTS`: A dictionary mapping `document_type` to specialized instructions.

### 3. Pipeline Extractor (`app/extractors/pipeline_extractor.py`)
A new extractor class that orchestrates the two stages:
*   `detect_type(text)`: Performs classification.
*   `extract_with_type(text, document_type)`: Performs specialized extraction.
*   **Failed Protection**: Fallback to `general` type if classification fails or is ambiguous.

## Error Handling & Failure Protection
*   If the specialized extraction fails (e.g., validation error), the system will retry with the `general` prompt.
*   The `metadata` field allows for flexibility if the LLM identifies information that doesn't fit the standard schema fields.

## Testing Strategy
*   Unit tests for each document type to ensure type-specific logic is applied (e.g., meeting notes vs. news).
*   Integration tests for the full pipeline from API/CLI to LLM.
*   Validation tests for the Pydantic schema to ensure "failed protection" works as expected.
