import pytest
from unittest.mock import MagicMock, patch
from typing import Any, Generator
from app.extractors.pipeline_extractor import PipelineExtractor
from app.schemas.extraction import ExtractionOutput
from app.prompts.extraction_prompt import TYPE_SPECIFIC_PROMPTS

@pytest.fixture
def mock_openai_client() -> Generator[MagicMock, None, None]:
    """
    Fixture that patches LLMExtractor._get_client and returns a mock client.
    """
    with patch("app.extractors.llm_extractor.LLMExtractor._get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        yield mock_client

@pytest.fixture
def extractor() -> PipelineExtractor:
    """
    Fixture that returns a PipelineExtractor instance.
    """
    return PipelineExtractor()

def create_mock_class_response(doc_type: str) -> MagicMock:
    """
    Helper function to create a mock classification response.
    """
    mock_class_response = MagicMock()
    mock_class_response.choices = [MagicMock()]
    mock_class_response.choices[0].message.content = doc_type
    return mock_class_response

def test_pipeline_integration_meeting_notes(extractor: PipelineExtractor, mock_openai_client: MagicMock) -> None:
    """
    Test that meeting notes are correctly classified and extracted.
    """
    # Mocking classification response
    mock_class_response = create_mock_class_response("meeting_notes")
    
    # Mocking extraction response
    mock_extraction_output = ExtractionOutput(
        document_type="meeting_notes",
        summary="Meeting about testing",
        key_entities=["Alice", "Bob"],
        action_items=["Write integration tests"],
        deadlines=[],
        risks=[],
        metadata={}
    )
    
    # Configure the mock to return classification first, then extraction
    mock_openai_client.chat.completions.create.side_effect = [
        mock_class_response,
        mock_extraction_output
    ]
    
    text = "Attendees: Alice, Bob. Action: Write integration tests."
    result = extractor.extract(text)
    
    assert result.document_type == "meeting_notes"
    assert "Alice" in result.key_entities
    assert "Write integration tests" in result.action_items
    
    # Verify the correct system prompt was used in the second call
    calls = mock_openai_client.chat.completions.create.call_args_list
    assert len(calls) == 2
    system_prompt = calls[1].kwargs["messages"][0]["content"]
    assert TYPE_SPECIFIC_PROMPTS["meeting_notes"] in system_prompt

def test_pipeline_integration_news(extractor: PipelineExtractor, mock_openai_client: MagicMock) -> None:
    """
    Test that news articles are correctly classified and extracted.
    """
    mock_class_response = create_mock_class_response("news")
    
    mock_extraction_output = ExtractionOutput(
        document_type="news",
        summary="Stock market update",
        key_entities=["New York", "Tim Cook"],
        action_items=[],
        deadlines=[],
        risks=[],
        metadata={}
    )
    
    mock_openai_client.chat.completions.create.side_effect = [
        mock_class_response,
        mock_extraction_output
    ]
    
    text = "Today in New York, the stock market hit a record high. Tim Cook commented."
    result = extractor.extract(text)
    
    assert result.document_type == "news"
    assert "New York" in result.key_entities
    
    calls = mock_openai_client.chat.completions.create.call_args_list
    system_prompt = calls[1].kwargs["messages"][0]["content"]
    assert TYPE_SPECIFIC_PROMPTS["news"] in system_prompt

def test_pipeline_integration_email(extractor: PipelineExtractor, mock_openai_client: MagicMock) -> None:
    """
    Test that emails are correctly classified and extracted.
    """
    mock_class_response = create_mock_class_response("email")
    
    mock_extraction_output = ExtractionOutput(
        document_type="email",
        summary="Project meeting request",
        key_entities=["Alice", "Bob"],
        action_items=["Meet tomorrow at 10 AM"],
        deadlines=["Tomorrow 10 AM"],
        risks=[],
        metadata={}
    )
    
    mock_openai_client.chat.completions.create.side_effect = [
        mock_class_response,
        mock_extraction_output
    ]
    
    text = "Hi Bob, can we meet tomorrow at 10 AM to discuss the project? Thanks, Alice."
    result = extractor.extract(text)
    
    assert result.document_type == "email"
    assert "Meet tomorrow at 10 AM" in result.action_items
    
    calls = mock_openai_client.chat.completions.create.call_args_list
    system_prompt = calls[1].kwargs["messages"][0]["content"]
    assert TYPE_SPECIFIC_PROMPTS["email"] in system_prompt

def test_pipeline_integration_interview_notes(extractor: PipelineExtractor, mock_openai_client: MagicMock) -> None:
    """
    Test that interview notes are correctly classified and extracted.
    """
    mock_class_response = create_mock_class_response("interview_notes")
    
    mock_extraction_output = ExtractionOutput(
        document_type="interview_notes",
        summary="Technical interview for Alice",
        key_entities=["Alice", "Python", "Docker"],
        action_items=["Move to next round"],
        deadlines=[],
        risks=["Lacks some SQL knowledge"],
        metadata={}
    )
    
    mock_openai_client.chat.completions.create.side_effect = [
        mock_class_response,
        mock_extraction_output
    ]
    
    text = "Alice showed great Python and Docker skills. Candidate should move to next round."
    result = extractor.extract(text)
    
    assert result.document_type == "interview_notes"
    assert "Python" in result.key_entities
    assert "Lacks some SQL knowledge" in result.risks
    
    calls = mock_openai_client.chat.completions.create.call_args_list
    system_prompt = calls[1].kwargs["messages"][0]["content"]
    assert TYPE_SPECIFIC_PROMPTS["interview_notes"] in system_prompt

def test_pipeline_integration_customer_requirements(extractor: PipelineExtractor, mock_openai_client: MagicMock) -> None:
    """
    Test that customer requirements are correctly classified and extracted.
    """
    mock_class_response = create_mock_class_response("customer_requirements")
    
    mock_extraction_output = ExtractionOutput(
        document_type="customer_requirements",
        summary="Request for a new dashboard",
        key_entities=["Dashboard", "Real-time metrics"],
        action_items=["Draft proposal"],
        deadlines=["Next Friday"],
        risks=["Tight deadline"],
        metadata={}
    )
    
    mock_openai_client.chat.completions.create.side_effect = [
        mock_class_response,
        mock_extraction_output
    ]
    
    text = "We need a real-time metrics dashboard by next Friday."
    result = extractor.extract(text)
    
    assert result.document_type == "customer_requirements"
    assert "Real-time metrics" in result.key_entities
    assert "Next Friday" in result.deadlines
    
    calls = mock_openai_client.chat.completions.create.call_args_list
    system_prompt = calls[1].kwargs["messages"][0]["content"]
    assert TYPE_SPECIFIC_PROMPTS["customer_requirements"] in system_prompt

def test_pipeline_integration_general(extractor: PipelineExtractor, mock_openai_client: MagicMock) -> None:
    """
    Test that general text is correctly handled.
    """
    mock_class_response = create_mock_class_response("general")
    
    mock_extraction_output = ExtractionOutput(
        document_type="general",
        summary="Pangram example",
        key_entities=["fox", "dog"],
        action_items=[],
        deadlines=[],
        risks=[],
        metadata={}
    )
    
    mock_openai_client.chat.completions.create.side_effect = [
        mock_class_response,
        mock_extraction_output
    ]
    
    text = "The quick brown fox jumps over the lazy dog."
    result = extractor.extract(text)
    
    assert result.document_type == "general"
    
    calls = mock_openai_client.chat.completions.create.call_args_list
    system_prompt = calls[1].kwargs["messages"][0]["content"]
    assert TYPE_SPECIFIC_PROMPTS["general"] in system_prompt
