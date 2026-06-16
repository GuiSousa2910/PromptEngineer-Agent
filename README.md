# PromptEngineer-Agent

Especialista em refinamento de prompts: recebe um prompt rascunho e devolve **apenas**
um prompt otimizado — direto, detalhado, sem ambiguidade e token-eficiente — pronto
para colar em outro agente LLM (mais caro). Powered by the Gemini API.

Ele fica na frente de um segundo agente LLM: você cola um rascunho e ele re-engenheira
em um prompt mais claro e denso (papel, tarefa, restrições e formato de saída
explícitos), para que o agente a jusante entenda melhor e gaste menos tokens por
chamada. A pesquisa web (Google Search grounding) é opcional, via `--research`.

## Setup

    python -m pip install -e .
    cp .env.example .env   # then put your key in GEMINI_API_KEY

## CLI usage

    refine "Quero um texto sobre o impacto da IA na educacao"
    refine --research "..."                # add Google Search grounding (slower, may add detail)
    refine -f draft.txt                    # read draft from a file
    cat draft.txt | refine                 # read draft from stdin
    refine -m gemini-2.5-flash-lite "..."  # cheapest/fastest model

Output: only the refined prompt, on stdout (pipe it straight to your second agent).

## Python usage

    from refiner import RefinerConfig, refine_prompt

    cfg = RefinerConfig.from_env(research=True)        # opt-in: web grounding (reads GEMINI_API_KEY)
    refined = refine_prompt("o meu prompt rascunho", cfg)
    print(refined)

## Flags

| Flag | Default | Meaning |
|------|---------|---------|
| `--model / -m`     | gemini-2.5-flash | Gemini model id |
| `--no-research`    | research off | Disable Google Search grounding (default) |
| `--research`       | research off | Enable Google Search grounding (opt-in) |
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
