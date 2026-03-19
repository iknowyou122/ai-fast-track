import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GEMINI_BASE_URL = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    def get_provider(self, provider: str | None = None) -> str:
        selected_provider = (provider or self.LLM_PROVIDER or "openai").lower()

        if selected_provider not in {"openai", "gemini"}:
            raise ValueError(
                "Unsupported LLM provider. Use 'openai' or 'gemini'."
            )

        return selected_provider

    def get_model(self, provider: str, override: str | None = None) -> str:
        if override:
            return override

        if self.DEFAULT_MODEL:
            return self.DEFAULT_MODEL

        if provider == "gemini":
            return self.GEMINI_MODEL

        return self.OPENAI_MODEL

    def get_api_key(self, provider: str) -> str | None:
        if provider == "gemini":
            return self.GEMINI_API_KEY

        return self.OPENAI_API_KEY

    def get_base_url(self, provider: str) -> str | None:
        if provider == "gemini":
            return self.GEMINI_BASE_URL

        return self.OPENAI_BASE_URL

config = Config()
