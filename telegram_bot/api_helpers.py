"""OpenRouter chat client used by the Telegram AI chatbot."""
import logging
from typing import Dict, List, Optional

import httpx

from .config import OPENROUTER_APP_NAME, OPENROUTER_MODEL, OPENROUTER_SITE_URL

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def truncate_response(text: str, max_length: int = 150) -> str:
    """Truncate to keep responses extremely short and natural."""
    text = text.strip()
    
    # If already short, return as-is
    if len(text) <= max_length:
        return text
    
    # Find first sentence break
    for delimiter in ['\n\n', '\n', '. ', '.\n', '! ', '?\n']:
        idx = text.find(delimiter)
        if idx != -1 and idx < max_length:
            truncated = text[:idx].strip()
            if truncated and len(truncated) > 5:
                return truncated
    
    # Fallback: truncate at max_length at word boundary
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > max_length - 30:
        truncated = truncated[:last_space]
    return truncated.strip()


async def call_openrouter_chat(
    messages: List[Dict[str, str]],
    api_key: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    timeout: int = 30,
) -> str:
    if not api_key:
        raise ValueError("OpenRouter API key is missing")

    payload = {
        "model": model or OPENROUTER_MODEL,
        "messages": messages,
        "temperature": temperature if temperature is not None else 0.9,  # Default to 0.9 for human-like behavior
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": OPENROUTER_SITE_URL,
        "X-Title": OPENROUTER_APP_NAME,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            choices = data.get("choices") if isinstance(data, dict) else None
            if choices and isinstance(choices, list):
                message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
                content = message.get("content")
                if content:
                    # Truncate to keep responses short and natural
                    return truncate_response(content.strip())

            raise RuntimeError(f"Unexpected OpenRouter response format: {data}")

    except httpx.HTTPStatusError as exc:
        logger.exception("OpenRouter API returned an error: %s", exc)
        raise
    except Exception as exc:
        logger.exception("Error calling OpenRouter API: %s", exc)
        raise
