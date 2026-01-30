from __future__ import annotations

import time

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

import config


def _get_client() -> OpenAI:
    return OpenAI(api_key=config.OPENAI_API_KEY)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=8),
    reraise=True,
)
def generate_document(
    system_prompt: str,
    user_prompt: str,
    model: str = config.DEFAULT_MODEL,
) -> str:
    """Call OpenAI API to generate a single document."""
    client = _get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=config.MAX_TOKENS,
    )
    content = response.choices[0].message.content
    if not content or not content.strip():
        raise ValueError("Leere Antwort vom Modell erhalten, versuche erneut")
    time.sleep(config.DELAY_BETWEEN_CALLS)
    return content
