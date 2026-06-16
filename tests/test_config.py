import pytest
from refiner.config import RefinerConfig, DEFAULT_MODEL


def test_defaults_from_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    c = RefinerConfig.from_env()
    assert c.api_key == "k"
    assert c.model == DEFAULT_MODEL
    assert c.research is True
    assert c.output_language == "pt-BR"
    assert c.thinking_budget == 0


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError):
        RefinerConfig.from_env()


def test_overrides_applied(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    c = RefinerConfig.from_env(model="gemini-2.5-flash-lite", research=False)
    assert c.model == "gemini-2.5-flash-lite"
    assert c.research is False


def test_none_overrides_ignored(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    c = RefinerConfig.from_env(model=None, temperature=None)
    assert c.model == DEFAULT_MODEL


def test_explicit_api_key_wins(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    c = RefinerConfig.from_env(api_key="direct")
    assert c.api_key == "direct"


def test_public_exports():
    import refiner
    assert hasattr(refiner, "RefinerConfig")
    assert hasattr(refiner, "refine_prompt")
    assert hasattr(refiner, "build_client")
