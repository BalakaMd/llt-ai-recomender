from typing import Optional, Tuple
import json

from pydantic import ValidationError

from app.schemas.response import TripPlan, ExplainResponse, ImproveResponse
from app.core.config import settings
from app.core.constants import LLMProvider
from app.services.llm_clients import (
    BaseLLMClient,
    OpenAIClient,
    GeminiClient,
    AnthropicClient,
)
from app.services.prompt_templates import ERROR_SYSTEM_PROMPT


class LLMEngine:
    """
    Multi-provider LLM Engine for generating travel itineraries.

    Supports OpenAI, Gemini, and Anthropic with automatic fallback.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or LLMProvider(settings.DEFAULT_LLM_PROVIDER)
        self.client = self._create_client()
        self.max_retries = 2

    def _create_client(self) -> BaseLLMClient:
        """Create LLM client based on provider."""
        if self.provider == LLMProvider.OPENAI:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            return OpenAIClient(settings.OPENAI_API_KEY)

        elif self.provider == LLMProvider.GEMINI:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured")
            return GeminiClient(settings.GEMINI_API_KEY)

        elif self.provider == LLMProvider.ANTHROPIC:
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            return AnthropicClient(settings.ANTHROPIC_API_KEY)

        raise ValueError(f"Unsupported provider: {self.provider}")

    async def generate_itinerary(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Tuple[TripPlan, int]:
        """
        Generate travel itinerary with validation and retry.

        Returns:
            Tuple of (TripPlan, tokens_used)
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            content = None
            try:
                content, tokens = await self.client.generate(system_prompt, user_prompt)

                # Parse and validate response
                trip_plan = TripPlan.model_validate_json(content)
                return trip_plan, tokens

            except ValidationError as e:
                last_error = e
                if attempt < self.max_retries:
                    # Add error context to prompt for self-correction
                    user_prompt = self._build_correction_prompt(content, str(e))
                    continue

            except json.JSONDecodeError as e:
                last_error = e
                if attempt < self.max_retries:
                    user_prompt = f"Your previous response was not valid JSON. Please return valid JSON only.\n\nOriginal request:\n{user_prompt}"
                    continue

        raise ValueError(f"Failed to generate valid itinerary after {self.max_retries + 1} attempts: {last_error}")

    async def generate_explanation(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Tuple[ExplainResponse, int]:
        """Generate explanation for a trip plan."""
        content, tokens = await self.client.generate(system_prompt, user_prompt)
        response = ExplainResponse.model_validate_json(content)
        return response, tokens

    async def generate_improvement(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Tuple[ImproveResponse, int]:
        """Generate improved trip plan."""
        content, tokens = await self.client.generate(system_prompt, user_prompt)
        response = ImproveResponse.model_validate_json(content)
        return response, tokens

    @staticmethod
    def _build_correction_prompt(invalid_response: str, error: str) -> str:
        """Build prompt for self-correction after validation error."""
        truncated_response = invalid_response[:1000] + "..." if len(invalid_response) > 1000 else invalid_response
        return ERROR_SYSTEM_PROMPT.format(invalid_response=truncated_response, error=error)
