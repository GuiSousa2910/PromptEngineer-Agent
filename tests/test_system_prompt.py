from refiner.system_prompt import build_system_prompt


def test_contains_core_directives():
    s = build_system_prompt("pt-BR")
    assert "Output ONLY the refined prompt" in s
    assert "token" in s.lower()
    assert "imperative" in s.lower()
    assert "pt-BR" in s


def test_language_injected():
    s = build_system_prompt("English")
    assert "English" in s


def test_no_unfilled_placeholder():
    s = build_system_prompt("pt-BR")
    assert "{language}" not in s
