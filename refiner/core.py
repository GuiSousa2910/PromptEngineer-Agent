from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from google import genai
from google.genai import types

from .config import RefinerConfig
from .research import (
    ResearchDigest,
    format_digest_for_prompt,
    run_research,
    save_digest,
)
from .system_prompt import build_architect_prompt


@dataclass
class RefineResult:
    prompt: str
    research: Optional[ResearchDigest] = None
    research_path: Optional[str] = None


def build_client(config: RefinerConfig) -> genai.Client:
    return genai.Client(api_key=config.api_key)


def _architect_config(config: RefinerConfig) -> types.GenerateContentConfig:
    # Pass 2 never carries search tools: research is already done and injected as context.
    return types.GenerateContentConfig(
        system_instruction=build_architect_prompt(config.output_language),
        temperature=config.temperature,
        max_output_tokens=config.max_output_tokens,
        thinking_config=types.ThinkingConfig(thinking_budget=config.thinking_budget),
    )


def refine_prompt(
    draft: str,
    config: RefinerConfig,
    client: Optional[genai.Client] = None,
) -> RefineResult:
    if not draft or not draft.strip():
        raise ValueError("Draft prompt is empty.")
    client = client or build_client(config)

    digest: Optional[ResearchDigest] = None
    research_path: Optional[str] = None
    if config.research:
        digest = run_research(draft, config, client)
        if config.save_research:
            research_path = str(save_digest(digest, config.research_dir))

    # Explicit framing labels the user turn as "content to transform", not a command.
    # Research (long context) goes on top; the input/instruction goes last.
    framed = f"INPUT A REFINAR:\n\n{draft}"
    if digest is not None:
        contents = f"{format_digest_for_prompt(digest)}\n\n{framed}"
    else:
        contents = framed

    response = client.models.generate_content(
        model=config.model,
        contents=contents,
        config=_architect_config(config),
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Model returned empty output.")
    return RefineResult(prompt=text, research=digest, research_path=research_path)
