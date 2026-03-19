from types import SimpleNamespace
import pytest
from app.extractors.pipeline_extractor import PipelineExtractor
from app.schemas.extraction import ExtractionOutput
from app.prompts.extraction_prompt import CLASSIFICATION_PROMPT, TYPE_SPECIFIC_PROMPTS, SYSTEM_PROMPT

class MockResponse:
    def __init__(self, content):
        self.choices = [SimpleNamespace(message=SimpleNamespace(content=content))]

class MockClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=SimpleNamespace())
        self.captured_calls = []

    def create(self, **kwargs):
        self.captured_calls.append(kwargs)
        if "response_model" in kwargs:
            # Stage 2: Extraction
            return kwargs["response_model"](
                document_type=kwargs.get("document_type", "general"),
                summary="Extracted summary",
                key_entities=["entity1"],
                action_items=[],
                deadlines=[],
                risks=[],
                metadata={}
            )
        else:
            # Stage 1: Classification
            return MockResponse("meeting_notes")

@pytest.fixture
def mock_pipeline_extractor(monkeypatch):
    mock_client = MockClient()
    monkeypatch.setattr(MockClient, "create", mock_client.create)
    
    # We need to mock the _get_client method of PipelineExtractor (which it inherits from LLMExtractor)
    monkeypatch.setattr("app.extractors.llm_extractor.LLMExtractor._get_client", lambda self: mock_client)
    
    extractor = PipelineExtractor()
    extractor.mock_client = mock_client
    return extractor

def test_detect_type_calls_llm_with_classification_prompt(mock_pipeline_extractor):
    mock_pipeline_extractor.mock_client.chat.completions.create = mock_pipeline_extractor.mock_client.create
    
    doc_type = mock_pipeline_extractor.detect_type("Some meeting text")
    
    assert doc_type == "meeting_notes"
    calls = mock_pipeline_extractor.mock_client.captured_calls
    assert len(calls) == 1
    assert calls[0]["messages"][0]["content"] == CLASSIFICATION_PROMPT
    assert calls[0]["messages"][1]["content"] == "Some meeting text"

def test_detect_type_returns_general_for_unknown_type(mock_pipeline_extractor):
    def unknown_type_create(**kwargs):
        mock_pipeline_extractor.mock_client.captured_calls.append(kwargs)
        return MockResponse("unknown_type")

    mock_pipeline_extractor.mock_client.chat.completions.create = unknown_type_create
    
    doc_type = mock_pipeline_extractor.detect_type("Some unknown text")
    
    assert doc_type == "general"

def test_extract_performs_two_stage_extraction(mock_pipeline_extractor):
    mock_pipeline_extractor.mock_client.chat.completions.create = mock_pipeline_extractor.mock_client.create
    
    # Mocking classification to return 'meeting_notes'
    # Mocking extraction to return ExtractionOutput
    
    result = mock_pipeline_extractor.extract("Some meeting text")
    
    assert result.document_type == "meeting_notes"
    calls = mock_pipeline_extractor.mock_client.captured_calls
    assert len(calls) == 2
    
    # First call: Classification
    assert calls[0]["messages"][0]["content"] == CLASSIFICATION_PROMPT
    
    # Second call: Extraction
    expected_system_prompt = f"{SYSTEM_PROMPT}\n\nType-Specific Instructions: {TYPE_SPECIFIC_PROMPTS['meeting_notes']}"
    assert calls[1]["messages"][0]["content"] == expected_system_prompt
    assert calls[1]["response_model"] == ExtractionOutput

def test_extract_falls_back_to_general_on_specialized_failure(mock_pipeline_extractor, monkeypatch):
    def failing_create(**kwargs):
        mock_pipeline_extractor.mock_client.captured_calls.append(kwargs)
        if "response_model" in kwargs and "Type-Specific Instructions" in kwargs["messages"][0]["content"]:            raise Exception("Specialized extraction failed")
        if "response_model" in kwargs:
             return ExtractionOutput(
                document_type="general",
                summary="General fallback summary",
                key_entities=[],
                action_items=[],
                deadlines=[],
                risks=[],
                metadata={}
            )
        return MockResponse("meeting_notes")

    monkeypatch.setattr(mock_pipeline_extractor.mock_client, "create", failing_create)
    mock_pipeline_extractor.mock_client.chat.completions.create = failing_create
    
    result = mock_pipeline_extractor.extract("Some meeting text")
    
    assert result.document_type == "general"
    assert result.summary == "General fallback summary"
    
    calls = mock_pipeline_extractor.mock_client.captured_calls
    assert len(calls) == 3 # 1. Classification, 2. Specialized (failed), 3. General (fallback)
