from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from refiner import core
from refiner.config import RefinerConfig


def _cfg(**kw):
    return RefinerConfig.from_env(api_key="x", **kw)


def _resp(text, gm=None):
    return SimpleNamespace(text=text, candidates=[SimpleNamespace(grounding_metadata=gm)])


def test_refine_default_single_pass_no_tools():
    client = Mock()
    client.models.generate_content.return_value = _resp("Papel: X")
    result = core.refine_prompt("rascunho", _cfg(research=False), client=client)
    assert result.prompt == "Papel: X"
    assert result.research is None
    assert result.research_path is None
    assert client.models.generate_content.call_count == 1
    cfg = client.models.generate_content.call_args.kwargs["config"]
    assert not getattr(cfg, "tools", None)  # architect call never carries search tools


def test_refine_research_runs_two_passes(tmp_path):
    client = Mock()
    gm = SimpleNamespace(
        web_search_queries=["q1"],
        grounding_chunks=[SimpleNamespace(web=SimpleNamespace(title="T", uri="U"))],
    )
    client.models.generate_content.side_effect = [
        _resp("FATOS DA PESQUISA", gm=gm),   # Pass 1 (research)
        _resp("Papel: refinado"),            # Pass 2 (architect)
    ]
    result = core.refine_prompt("pesquise X", _cfg(research=True, research_dir=str(tmp_path)), client=client)
    assert client.models.generate_content.call_count == 2
    first_cfg = client.models.generate_content.call_args_list[0].kwargs["config"]
    second = client.models.generate_content.call_args_list[1].kwargs
    assert first_cfg.tools                          # Pass 1 has search
    assert not getattr(second["config"], "tools", None)  # Pass 2 has no tools
    assert "FATOS DA PESQUISA" in second["contents"]     # digest injected into Pass 2
    assert "INPUT A REFINAR" in second["contents"]
    assert result.prompt == "Papel: refinado"
    assert result.research is not None and result.research.queries == ["q1"]
    assert result.research_path and Path(result.research_path).exists()


def test_refine_research_can_skip_saving(tmp_path):
    client = Mock()
    client.models.generate_content.side_effect = [_resp("FATOS"), _resp("Papel: x")]
    result = core.refine_prompt(
        "pesquise X", _cfg(research=True, save_research=False, research_dir=str(tmp_path)), client=client
    )
    assert result.research is not None
    assert result.research_path is None
    assert not list(Path(tmp_path).glob("*.md"))


def test_refine_empty_draft_raises():
    try:
        core.refine_prompt("   ", _cfg(), client=Mock())
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_refine_empty_architect_response_raises():
    client = Mock()
    client.models.generate_content.return_value = _resp("")
    try:
        core.refine_prompt("draft", _cfg(research=False), client=client)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass
