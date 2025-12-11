from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any

class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> Tuple[str, int]:
        """
        Generate response from LLM.

        Returns:
            Tuple of (response_text, tokens_used)
        """
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT client."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        import openai
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(self, system_prompt: str, user_prompt: str, json_schema: Optional[Dict[str, Any]] = None) -> Tuple[str, int]:
        response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "schema": json_schema
                }
            }

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[  # type: ignore[list-item]
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=response_format, # type: ignore
            temperature=0.7,
        )
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0
        return content, tokens


class GeminiClient(BaseLLMClient):
    """Google Gemini client."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-lite"):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model,
            generation_config={"response_mime_type": "application/json"} # type: ignore
        )

    async def generate(self, system_prompt: str, user_prompt: str, json_schema: Optional[Dict[str, Any]] = None) -> Tuple[str, int]:
        import json
        full_prompt = f"{system_prompt}\n\n{user_prompt},\n\nJSON SCHEMA: {json.dumps(json_schema, ensure_ascii=False, indent=2)}"
        response = await self.model.generate_content_async(full_prompt)
        return response.text, 0


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude client."""

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def generate(self, system_prompt: str, user_prompt: str, json_schema: Optional[Dict[str, Any]] = None) -> Tuple[str, int]:
        import json
        full_system_prompt = system_prompt
        if json_schema:
            full_system_prompt += f"\n\nYou MUST respond with valid JSON matching this schema:\n{json.dumps(json_schema, ensure_ascii=False, indent=2)}"

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=full_system_prompt,
            messages=[{"role": "user", "content": user_prompt}],  # type: ignore[list-item]
        )
        content = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens
        return content, tokens
