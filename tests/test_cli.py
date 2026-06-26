from types import SimpleNamespace
from unittest.mock import patch

from refiner import cli


def test_no_input_returns_2(capsys):
    with patch("sys.stdin.isatty", return_value=True):
        assert cli.main([]) == 2
    assert "no draft" in capsys.readouterr().err.lower()


def test_stdout_is_prompt_only(capsys):
    result = SimpleNamespace(prompt="Papel: X", research=None, research_path=None)
    with patch("refiner.cli.refine_prompt", return_value=result), \
         patch("refiner.cli.RefinerConfig.from_env", return_value=SimpleNamespace()):
        assert cli.main(["rascunho"]) == 0
    out = capsys.readouterr()
    assert out.out.strip() == "Papel: X"


def test_research_path_printed_to_stderr(capsys):
    result = SimpleNamespace(prompt="P", research=object(), research_path="research/x.md")
    with patch("refiner.cli.refine_prompt", return_value=result), \
         patch("refiner.cli.RefinerConfig.from_env", return_value=SimpleNamespace()):
        assert cli.main(["draft"]) == 0
    err = capsys.readouterr().err
    assert "research/x.md" in err


def test_parser_accepts_new_flags():
    args = cli.build_parser().parse_args(["d", "--research-dir", "out", "--no-save-research"])
    assert args.research_dir == "out"
    assert args.save_research is False


def test_flags_wire_into_config(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    captured = {}

    def fake_refine(draft, config):
        captured["config"] = config
        return SimpleNamespace(prompt="x", research=None, research_path=None)

    with patch("refiner.cli.refine_prompt", side_effect=fake_refine):
        cli.main(["draft", "--no-research", "--research-dir", "out", "--no-save-research"])
    cfg = captured["config"]
    assert cfg.research is False
    assert cfg.research_dir == "out"
    assert cfg.save_research is False


def test_error_returns_1(capsys):
    with patch("refiner.cli.RefinerConfig.from_env", side_effect=ValueError("boom")):
        assert cli.main(["draft"]) == 1
    assert "boom" in capsys.readouterr().err
