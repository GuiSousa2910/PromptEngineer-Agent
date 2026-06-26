from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.1  # low = deterministic instruction-following; was 0.3
DEFAULT_MAX_OUTPUT_TOKENS = 2048
DEFAULT_THINKING_BUDGET = 0  # 0 = disable thinking → lowest latency/cost
DEFAULT_RESEARCH = False  # web research is opt-in (--research); keeps output lean
DEFAULT_OUTPUT_LANGUAGE = "pt-BR"
DEFAULT_RESEARCH_DIR = "research"
DEFAULT_SAVE_RESEARCH = True  # persist the research digest to disk for later consultation
ENV_API_KEY = "GEMINI_API_KEY"


@dataclass
class RefinerConfig:
    api_key: str
    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS
    thinking_budget: int = DEFAULT_THINKING_BUDGET
    research: bool = DEFAULT_RESEARCH
    output_language: str = DEFAULT_OUTPUT_LANGUAGE
    research_dir: str = DEFAULT_RESEARCH_DIR
    save_research: bool = DEFAULT_SAVE_RESEARCH

    @classmethod
    def from_env(cls, **overrides) -> "RefinerConfig":
        api_key = overrides.pop("api_key", None) or os.environ.get(ENV_API_KEY)
        if not api_key:
            raise ValueError(
                f"Missing API key. Set {ENV_API_KEY} env var, pass --api-key, "
                f"or set api_key=... ."
            )
        clean = {k: v for k, v in overrides.items() if v is not None}
        return cls(api_key=api_key, **clean)
