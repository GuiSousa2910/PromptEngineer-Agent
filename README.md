# PromptEngineer-Agent

Pre-processing agent: turns a rough draft prompt into a refined, token-efficient
prompt (pt-BR) for a downstream LLM agent. Powered by the Gemini API.

It sits in front of a second, more expensive LLM agent: feed it a rough draft,
and it cleans, tightens, structures, and fact-aligns that prompt — optionally
researching the entities it mentions via Google Search grounding — so the
downstream agent receives something direct, objective, detailed, and cheaper to
run per call.

## Setup

    python -m pip install -e .
    cp .env.example .env   # then put your key in GEMINI_API_KEY

## CLI usage

    refine "Quero um texto sobre o impacto da IA na educacao"
    refine --no-research "..."             # skip web research (faster/cheaper)
    refine -f draft.txt                    # read draft from a file
    cat draft.txt | refine                 # read draft from stdin
    refine -m gemini-2.5-flash-lite "..."  # cheapest/fastest model

Output: only the refined prompt, on stdout (pipe it straight to your second agent).

## Python usage

    from refiner import RefinerConfig, refine_prompt

    cfg = RefinerConfig.from_env(research=True)        # reads GEMINI_API_KEY
    refined = refine_prompt("o meu prompt rascunho", cfg)
    print(refined)

## Flags

| Flag | Default | Meaning |
|------|---------|---------|
| `--model / -m`     | gemini-2.5-flash | Gemini model id |
| `--no-research`    | research on | Disable Google Search grounding |
| `--research`       | research on | Force-enable Google Search grounding |
| `--temperature / -t` | 0.3 | Sampling temperature |
| `--max-tokens`     | 2048 | Max output tokens |
| `--thinking`       | 0 | Thinking budget (0 = off) |
| `--language / -l`  | pt-BR | Output language |
| `--api-key`        | env | Override GEMINI_API_KEY |

## Models

| Model | Input / Output (per 1M) | Notes |
|---|---|---|
| `gemini-2.5-flash-lite` | $0.10 / $0.40 | Cheapest, fastest |
| `gemini-2.5-flash` (default) | $0.30 / $2.50 | Balanced |
| `gemini-3.5-flash` | $1.50 / $9.00 | Strongest |

## Development

    python -m pip install -r requirements-dev.txt
    python -m pytest -q            # unit tests, no network (live test excluded)
    python -m pytest -m live -q    # gated live smoke test (needs GEMINI_API_KEY)
