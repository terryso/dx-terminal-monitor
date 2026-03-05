"""
LLM Client Module for Story 8-0

Provides OpenAI-compatible API client for LLM interactions.
Supports GLM-4, OpenAI, and other compatible endpoints.
"""

import logging
import os
from dataclasses import dataclass

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM client."""

    api_key: str
    base_url: str
    model: str
    timeout: int


class LLMClient:
    """OpenAI-compatible LLM client for chat completions.

    Supports GLM-4 (Zhipu AI), OpenAI, and other compatible APIs.

    Args:
        config: Optional LLMConfig instance. If not provided, reads from env.

    Example:
        client = LLMClient()
        response = await client.chat(
            system_prompt="You are a helpful assistant.",
            user_message="Hello!"
        )
    """

    def __init__(self, config: LLMConfig | None = None):
        if config:
            self.config = config
        else:
            self.config = self._load_from_env()

        self._session: aiohttp.ClientSession | None = None

    def _load_from_env(self) -> LLMConfig:
        """Load configuration from environment variables."""
        api_key = os.getenv("LLM_API_KEY", "")
        if not api_key:
            logger.warning("LLM_API_KEY not configured - LLM features will be disabled")

        return LLMConfig(
            api_key=api_key,
            base_url=os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            model=os.getenv("LLM_MODEL", "glm-4"),
            timeout=int(os.getenv("LLM_TIMEOUT", "60")),
        )

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def chat(self, system_prompt: str, user_message: str) -> str:
        """Send a chat completion request to the LLM.

        Args:
            system_prompt: System message to set the AI's behavior
            user_message: User's input message

        Returns:
            The assistant's response text, or error message string

        Example:
            response = await client.chat(
                system_prompt="You are a crypto trading advisor.",
                user_message="Should I buy ETH now?"
            )
        """
        if not self.config.api_key:
            logger.error("LLM_API_KEY not configured")
            return "Error: LLM API key not configured"

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }

        try:
            session = await self._get_session()
            url = f"{self.config.base_url}/chat/completions"

            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    choices = data.get("choices", [])
                    if choices and len(choices) > 0:
                        message = choices[0].get("message", {})
                        content = message.get("content", "")
                        if content:
                            return content
                        else:
                            logger.error("Empty content in LLM response")
                            return "Error: Empty response from LLM"
                    else:
                        logger.error("No choices in LLM response: %s", data)
                        return "Error: Invalid LLM response format"
                elif resp.status == 401:
                    logger.error("LLM API authentication failed (401)")
                    return "Error: LLM API authentication failed"
                elif resp.status == 429:
                    logger.error("LLM API rate limit exceeded (429)")
                    return "Error: LLM API rate limit exceeded"
                else:
                    text = await resp.text()
                    logger.error("LLM API error (%d): %s", resp.status, text[:200])
                    return f"Error: LLM API returned status {resp.status}"

        except TimeoutError:
            logger.error("LLM API request timed out after %ds", self.config.timeout)
            return f"Error: LLM request timed out after {self.config.timeout}s"
        except aiohttp.ClientError as e:
            logger.error("LLM API network error: %s", e)
            return f"Error: Network error - {e}"
        except Exception as e:
            logger.error("LLM API unexpected error: %s", e)
            return f"Error: Unexpected error - {e}"

    def __repr__(self) -> str:
        return f"LLMClient(model={self.config.model}, base_url={self.config.base_url})"
