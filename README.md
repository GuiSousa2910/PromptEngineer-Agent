# PromptEngineer-Agent

Especialista em refinamento de prompts: recebe um prompt rascunho e devolve **apenas**
um prompt otimizado — direto, detalhado, sem ambiguidade e token-eficiente — pronto
para colar em outro agente LLM (mais caro). Powered by the Gemini API.

Ele fica na frente de um segundo agente LLM: você cola um rascunho e ele re-engenheira
em um prompt mais claro e denso (papel, tarefa, restrições e formato de saída
explícitos), para que o agente a jusante entenda melhor e gaste menos tokens por
chamada. A pesquisa web (Google Search grounding) é opcional, via `--research`.

## Como funciona

- **Modo padrão** (sem `--research`): uma chamada ao modelo (persona "arquiteto")
  transforma o rascunho em um prompt refinado e token-eficiente.
- **Modo pesquisa** (`--research`): pipeline de 2 passos.
  1. **Pesquisa** — uma chamada com Google Search gera um *digest* de domínio
     (vocabulário, entidades, números, restrições) e captura as queries e fontes.
     O digest é salvo em `research/AAAA-MM-DD-HHMMSS-<slug>.md` para você consultar.
  2. **Arquitetura** — uma segunda chamada (sem busca) recebe o digest como contexto
     `<pesquisa_de_dominio>` e produz o prompt refinado baseado na pesquisa.

A saída padrão (stdout) contém **apenas o prompt refinado** (pronto para pipe/cópia).
O caminho do arquivo de pesquisa é informado em stderr.

## Setup

    python -m pip install -e .
    cp .env.example .env   # then put your key in GEMINI_API_KEY

## CLI usage

    refine "Quero um texto sobre o impacto da IA na educacao"
    refine --research "..."                # 2-pass: pesquisa -> arquitetura (salva digest)
    refine --research --research-dir docs/r "..."  # escolhe onde salvar o digest
    refine --research --no-save-research "..."      # pesquisa, sem gravar arquivo
    refine -f draft.txt                    # read draft from a file
    cat draft.txt | refine                 # read draft from stdin
    refine -m gemini-2.5-flash-lite "..."  # cheapest/fastest model

stdout: apenas o prompt refinado (pipe direto pro seu segundo agente).
stderr: no modo `--research`, o caminho do digest salvo (`[research saved to ...]`).

    refine --research "pesquise mochilas para artigo pessoal de avião" > prompt.txt
    cat research/*.md   # consultar a pesquisa que embasou o prompt

## Python usage

    from refiner import RefinerConfig, refine_prompt

    cfg = RefinerConfig.from_env(research=True)        # opt-in: pipeline de pesquisa (reads GEMINI_API_KEY)
    result = refine_prompt("o meu prompt rascunho", cfg)
    print(result.prompt)                               # o prompt refinado
    if result.research:                                # ResearchDigest | None
        print(result.research.queries, result.research.sources)
        print(result.research_path)                    # caminho do .md salvo (ou None)

## Flags

| Flag | Default | Meaning |
|------|---------|---------|
| `--model / -m`     | gemini-2.5-flash | Gemini model id |
| `--no-research`    | research off | Modo padrão, 1 chamada (sem pesquisa) |
| `--research`       | research off | Pipeline de pesquisa em 2 passos (opt-in) |
| `--research-dir`   | research/ | Onde salvar os digests de pesquisa |
| `--no-save-research` | salva | Pesquisa, mas não grava o arquivo do digest |
| `--temperature / -t` | 0.1 | Sampling temperature |
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
