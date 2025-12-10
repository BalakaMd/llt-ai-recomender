from abc import ABC, abstractmethod
from typing import Tuple


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
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        import openai
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate(self, system_prompt: str, user_prompt: str) -> Tuple[str, int]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0
        return content, tokens


class GeminiClient(BaseLLMClient):
    """Google Gemini client."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model,
            generation_config={"response_mime_type": "application/json"}
        )
    
    async def generate(self, system_prompt: str, user_prompt: str) -> Tuple[str, int]:
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = await self.model.generate_content_async(full_prompt)
        return response.text, 0


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude client."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
    
    async def generate(self, system_prompt: str, user_prompt: str) -> Tuple[str, int]:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        content = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens
        return content, tokens
