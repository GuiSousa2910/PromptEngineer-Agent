from __future__ import annotations

from typing import Optional

from google import genai
from google.genai import types

from .config import RefinerConfig
from .system_prompt import build_system_prompt


def build_client(config: RefinerConfig) -> genai.Client:
    return genai.Client(api_key=config.api_key)


def _build_generate_config(config: RefinerConfig) -> types.GenerateContentConfig:
    kwargs = dict(
        system_instruction=build_system_prompt(config.output_language),
        temperature=config.temperature,
        max_output_tokens=config.max_output_tokens,
        thinking_config=types.ThinkingConfig(thinking_budget=config.thinking_budget),
    )
    if config.research:
        kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    return types.GenerateContentConfig(**kwargs)


def refine_prompt(
    draft: str,
    config: RefinerConfig,
    client: Optional[genai.Client] = None,
) -> str:
    if not draft or not draft.strip():
        raise ValueError("Draft prompt is empty.")
    client = client or build_client(config)
    response = client.models.generate_content(
        model=config.model,
        contents=draft,
        config=_build_generate_config(config),
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Model returned empty output.")
    return text
