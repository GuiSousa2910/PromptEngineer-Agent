from refiner.system_prompt import build_architect_prompt, build_research_prompt


def test_architect_core_directives():
    p = build_architect_prompt("pt-BR")
    assert "NUNCA" in p
    assert "tokens" in p
    assert "imperativa" in p


def test_architect_specialist_identity():
    p = build_architect_prompt("pt-BR")
    assert "PromptRefiner" in p
    assert "INPUT A REFINAR" in p


def test_architect_language_injected():
    p = build_architect_prompt("en-US")
    assert "en-US" in p
    assert "{language}" not in p


def test_architect_includes_fewshot():
    p = build_architect_prompt("pt-BR")
    assert "EXEMPLO 1" in p
    assert "EXEMPLO 2" in p


def test_architect_literal_braces_survive():
    p = build_architect_prompt("pt-BR")
    assert '{"nome"' in p  # JSON braces in example must survive


def test_architect_knows_research_block():
    p = build_architect_prompt("pt-BR")
    assert "<pesquisa_de_dominio>" in p


def test_research_prompt_persona_and_guardrails():
    p = build_research_prompt("pt-BR")
    assert "PESQUISADOR" in p
    assert "NÃO responda" in p
    assert "Vocabulário de domínio" in p


def test_research_prompt_language_injected():
    p = build_research_prompt("en-US")
    assert "en-US" in p
    assert "{language}" not in p
