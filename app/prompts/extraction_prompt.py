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
