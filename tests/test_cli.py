from unittest.mock import patch
from refiner import cli


def test_reads_positional_and_prints(capsys, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    with patch("refiner.cli.refine_prompt", return_value="REFINED") as m:
        rc = cli.main(["my draft"])
    assert rc == 0
    assert "REFINED" in capsys.readouterr().out
    assert m.call_args.args[0] == "my draft"


def test_no_input_returns_2(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    with patch("sys.stdin.isatty", return_value=True):
        rc = cli.main([])
    assert rc == 2


def test_no_research_flag_sets_false(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    captured = {}

    def fake_refine(draft, config):
        captured["research"] = config.research
        return "x"

    with patch("refiner.cli.refine_prompt", side_effect=fake_refine):
        cli.main(["draft", "--no-research"])
    assert captured["research"] is False


def test_error_returns_1(monkeypatch, capsys):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    with patch("refiner.cli.refine_prompt", side_effect=RuntimeError("boom")):
        rc = cli.main(["draft"])
    assert rc == 1
    assert "boom" in capsys.readouterr().err
