# Configurable Extraction Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the current generic extraction tool to a domain-aware extraction engine using a two-stage LLM pipeline.

**Architecture:** A two-stage sequential LLM pipeline: (1) Classification stage to detect `document_type`, and (2) Specialized extraction stage using type-specific prompts.

**Tech Stack:** Python, Pydantic, Instructor (OpenAI/Gemini), Pytest.

---

### Task 1: Update Schema and Prompts

**Files:**
- Modify: `app/schemas/extraction.py`
- Modify: `app/prompts/extraction_prompt.py`
- Test: `tests/test_schema_updates.py`

- [ ] **Step 1: Update `app/schemas/extraction.py`**
  Add `document_type` and `metadata` to `ExtractionOutput`.
  ```python
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
  ```

- [ ] **Step 2: Update `app/prompts/extraction_prompt.py`**
  Add `CLASSIFICATION_PROMPT` and `TYPE_SPECIFIC_PROMPTS`.
  ```python
  SYSTEM_PROMPT = "You are an expert at extracting structured information from unstructured text."
  USER_PROMPT_TEMPLATE = "{text}"

  CLASSIFICATION_PROMPT = """
  Classify the following text into one of these types:
  - meeting_notes: Notes from a meeting, including attendees, decisions, and action items.
  - interview_notes: Notes from a job interview, focusing on candidate skills and impressions.
  - customer_requirements: Requirements provided by a customer for a project or feature.
  - email: Correspondence between individuals or organizations.
  - news: News articles or reports about current events.
  - general: Any other type of text.

  Return ONLY the type name.
  """

  TYPE_SPECIFIC_PROMPTS = {
      "meeting_notes": "Focus on participants, decisions made, and follow-up tasks.",
      "interview_notes": "Focus on candidate's technical skills, experience, and overall fit.",
      "customer_requirements": "Focus on specific features requested, user pain points, and technical constraints.",
      "email": "Focus on the primary intent of the sender and the expected next steps.",
      "news": "Focus on the main event, key figures involved, and any significant dates or locations.",
      "general": "Extract a balanced summary of the key points and entities."
  }
  ```

- [ ] **Step 3: Commit updates**
  ```bash
  git add app/schemas/extraction.py app/prompts/extraction_prompt.py
  git commit -m "feat: update schema and prompts for configurable pipeline"
  ```

### Task 2: Implement Pipeline Extractor

**Files:**
- Create: `app/extractors/pipeline_extractor.py`
- Test: `tests/test_pipeline_extractor.py`

- [ ] **Step 1: Create `app/extractors/pipeline_extractor.py`**
  Implement the two-stage extraction logic.
  ```python
  import instructor
  from openai import OpenAI
  from app.extractors.llm_extractor import LLMExtractor
  from app.schemas.extraction import ExtractionOutput
  from app.prompts.extraction_prompt import SYSTEM_PROMPT, CLASSIFICATION_PROMPT, TYPE_SPECIFIC_PROMPTS
  from app.config import config

  class PipelineExtractor(LLMExtractor):
      """
      Two-stage pipeline: (1) Detect type, (2) Specialized extraction.
      """
      def detect_type(self, text: str) -> str:
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
          except Exception:
              return "general"

      def extract(self, text: str) -> ExtractionOutput:
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
                  return self.extract_general(text)
              raise e

      def extract_general(self, text: str) -> ExtractionOutput:
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
  ```

- [ ] **Step 2: Commit implementation**
  ```bash
  git add app/extractors/pipeline_extractor.py
  git commit -m "feat: implement two-stage PipelineExtractor"
  ```

### Task 3: Update Extraction Service

**Files:**
- Modify: `app/services/extraction_service.py`
- Test: `tests/test_service.py`

- [ ] **Step 1: Update `app/services/extraction_service.py`**
  Change default extractor to `PipelineExtractor`.
  ```python
  from app.extractors.pipeline_extractor import PipelineExtractor
  # ... rest of imports

  class ExtractionService:
      def __init__(self, extractor=None):
          self.extractor = extractor or PipelineExtractor()
      # ... rest of class
  ```

- [ ] **Step 2: Run existing tests**
  ```bash
  pytest tests/test_service.py
  ```

- [ ] **Step 3: Commit changes**
  ```bash
  git add app/services/extraction_service.py
  git commit -m "feat: update service to use PipelineExtractor by default"
  ```

### Task 4: Final Validation and Testing

**Files:**
- Create: `tests/test_pipeline_integration.py`

- [ ] **Step 1: Write integration tests for different types**
  Verify that meeting notes and news articles trigger correct extraction logic.

- [ ] **Step 2: Run all tests**
  ```bash
  pytest tests/
  ```

- [ ] **Step 3: Final commit**
  ```bash
  git commit -m "test: add integration tests for configurable pipeline"
  ```
