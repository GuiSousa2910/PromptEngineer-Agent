from unittest.mock import MagicMock
import pytest
from refiner.config import RefinerConfig
from refiner import core


def _cfg(**kw):
    return RefinerConfig(api_key="test-key", **kw)


def _fake_client(text):
    resp = MagicMock()
    resp.text = text
    client = MagicMock()
    client.models.generate_content.return_value = resp
    return client


def test_refine_returns_stripped_text():
    client = _fake_client("  REFINED  ")
    out = core.refine_prompt("draft", _cfg(), client=client)
    assert out == "REFINED"


def test_refine_passes_model_and_grounding_on():
    client = _fake_client("x")
    core.refine_prompt("draft", _cfg(model="gemini-2.5-flash", research=True), client=client)
    kwargs = client.models.generate_content.call_args.kwargs
    assert kwargs["model"] == "gemini-2.5-flash"
    assert kwargs["config"].tools  # grounding tool present


def test_refine_grounding_off_has_no_tools():
    client = _fake_client("x")
    core.refine_prompt("draft", _cfg(research=False), client=client)
    cfg = client.models.generate_content.call_args.kwargs["config"]
    assert not cfg.tools


def test_refine_empty_draft_raises():
    with pytest.raises(ValueError):
        core.refine_prompt("   ", _cfg(), client=MagicMock())


def test_refine_empty_response_raises():
    client = _fake_client("")
    with pytest.raises(RuntimeError):
        core.refine_prompt("draft", _cfg(), client=client)
