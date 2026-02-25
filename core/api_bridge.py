import os
import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from core.config import ConfigManager

class APIBridge:
    """
    Bridge for communicating with LLM APIs (OpenAI, Gemini via AITunnel, etc.)
    """
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self._client: Optional[AsyncOpenAI] = None
        self._refresh_client()
        
        # Subscribe to config changes if needed
        self.config.config_changed.connect(self._on_config_changed)

    def _refresh_client(self):
        """Initializes or refreshes the AsyncOpenAI client from config."""
        api_settings = self.config.get("api")
        self._client = AsyncOpenAI(
            api_key=api_settings.get("api_key", "YOUR_API_KEY"),
            base_url=api_settings.get("base_url", "https://api.aitunnel.ru/v1/"),
            timeout=api_settings.get("timeout", 30)
        )

    def _on_config_changed(self, key: str, value: Any):
        if key.startswith("api."):
            self._refresh_client()

    async def get_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Gets a completion from the LLM.
        """
        api_settings = self.config.get("api")
        model = kwargs.get("model", api_settings.get("model_name", "gpt-4o-mini"))
        temperature = kwargs.get("temperature", api_settings.get("temperature", 0.7))
        max_tokens = kwargs.get("max_tokens", api_settings.get("max_tokens", 512))
        
        try:
            response = await self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **{k: v for k, v in kwargs.items() if k not in ["model", "temperature", "max_tokens"]}
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            # TODO: Proper error handling and logging to UI
            print(f"API Error: {e}")
            return f"Error: {str(e)}"

    async def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Gets embedding for the given text using OpenAI API.
        """
        if model is None:
            model = self.config.get("memory.embedding_model", "text-embedding-3-small")
            
        try:
            response = await self._client.embeddings.create(
                input=[text],
                model=model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding Error: {e}")
            return []

    async def summarize(self, history: List[Dict[str, Any]]) -> str:
        """
        Summarizes the given conversation history.
        """
        if not history:
            return ""
            
        # Format history for summarization
        formatted_history = "\n".join([
            f"{m['role']}: {m['content']}" for m in history
        ])
        
        prompt = (
            "Summarize the following conversation history briefly but accurately. "
            "Keep important facts and the current state of the conversation.\n\n"
            f"History:\n{formatted_history}\n\nSummary:"
        )
        
        messages = [{"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
                    {"role": "user", "content": prompt}]
        
        # Use a faster/cheaper model for summarization if configured, otherwise default
        return await self.get_completion(messages, max_tokens=256)
