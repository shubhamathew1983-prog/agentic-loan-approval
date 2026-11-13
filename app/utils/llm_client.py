import logging
from typing import Optional

import anthropic

from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Thin async wrapper around the Anthropic messages API."""

    def __init__(self):
        settings = get_settings()
        self._api_key = settings.anthropic_api_key
        self._model = settings.llm_model
        self._temperature = settings.llm_temperature
        self._max_tokens = settings.llm_max_tokens
        self._client: Optional[anthropic.AsyncAnthropic] = None

        if self._api_key:
            self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
        else:
            logger.warning("[LLM] ANTHROPIC_API_KEY not set — LLM calls will be skipped")

    async def generate(self, prompt: str) -> str:
        """Call Claude and return the response text, or '' on any failure."""
        if not self._client:
            return ""

        try:
            logger.info(f"[LLM] Calling {self._model} (max_tokens={self._max_tokens})")
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            logger.info(f"[LLM] Response received ({len(text)} chars)")
            return text

        except anthropic.AuthenticationError:
            logger.error("[LLM] Authentication failed — check ANTHROPIC_API_KEY")
            return ""
        except anthropic.RateLimitError:
            logger.warning("[LLM] Rate limit hit — falling back to template")
            return ""
        except Exception as exc:
            logger.error(f"[LLM] Unexpected error: {exc}")
            return ""


_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
