from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


class AIRunStatus(str, Enum):
    """Status of AI generation run."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
